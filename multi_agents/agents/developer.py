import os
import sys
import json
import re
import logging
from typing import Dict, Any, Tuple, List, Optional

# Ensure parent directories are in sys.path
# This specific sys.path manipulation might need adjustment based on actual project structure
# For now, assuming 'llm.py' and 'state.py' are discoverable via standard Python path or PYTHONPATH
# If 'agent_base' is in the same directory as 'llm' and 'state', one less sys.path.append might be needed.
# current_dir = os.path.dirname(os.path.abspath(__file__))
# sys.path.append(os.path.dirname(current_dir)) # For 'agent_base', 'llm', 'state'
# sys.path.append(os.path.dirname(os.path.dirname(current_dir))) # For 'multi_agents' if running from root

# Simplified sys.path for now, assuming standard project structure where 'multi_agents' is a package
# or the execution context handles paths correctly.
# If 'from llm import LLM' fails, these paths need to be revisited.
project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
if project_root not in sys.path:
    sys.path.insert(0, project_root)

from agent_base import Agent
from llm import LLM # Assuming llm.py is in multi_agents/
from state import State # Assuming state.py is in multi_agents/
import subprocess

logger = logging.getLogger(__name__)
# Configure logger if not configured by a higher-level script
if not logger.handlers:
    logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')


PREFIX_CODE_CONTENT = """import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
import os
import warnings

warnings.filterwarnings('ignore')

# Example of how a script might ensure it can find modules in its parent or project root if needed.
# This might be useful if the script itself needs to import other custom modules from the project.
# current_script_path = os.path.dirname(os.path.abspath(__file__))
# project_root_path = os.path.abspath(os.path.join(current_script_path, '..', '..')) # Adjust depth as needed
# if project_root_path not in sys.path:
#     sys.path.insert(0, project_root_path)

def generated_code_function():
"""  # Note: python_code will be appended here, indented

SUFFIX_CODE_CONTENT = """

if __name__ == "__main__":
    try:
        generated_code_function()
        print('[SCRIPT_EXECUTION_SUCCESS]')
    except Exception as e:
        print(f'[SCRIPT_EXECUTION_ERROR] An error occurred: {str(e)}')
        import traceback
        print(traceback.format_exc())
"""


class Developer(Agent):
    def __init__(self, model: str, type: str):
        super().__init__(
            role="developer",
            description="You are skilled at writing Python code to perform data analysis tasks based on a given plan and context.",
            model=model,
            type=type,
        )
        # self.llm is initialized in the Agent base class

    def _run_code(self, state: State, script_path: str) -> Dict[str, Any]:
        output_dir = state.restore_dir # This is already task-specific
        output_filename = "execution_output.txt"
        error_filename = "execution_error.txt"
        
        path_to_output = os.path.join(output_dir, output_filename)
        path_to_error = os.path.join(output_dir, error_filename)

        run_status = {
            "status": "pending",
            "output_file": path_to_output,
            "error_file": path_to_error,
            "stdout": "",
            "stderr": "",
            "returncode": None,
            "timeout_occurred": False
        }

        if not os.path.exists(script_path):
            logger.error(f"Script not found for execution: {script_path}")
            run_status["status"] = "error"
            run_status["stderr"] = "Script file not found."
            try:
                with open(path_to_error, 'w', encoding='utf-8') as f_err:
                    f_err.write("Script file not found for execution.")
            except IOError as e_io:
                logger.error(f"Failed to write to error file {path_to_error}: {e_io}")
            return run_status

        timeout_seconds = 600 # Default
        # Example: Adjust timeout based on phase (can be made more sophisticated)
        if state.phase and ('Analysis' in state.phase or 'Profiling' in state.phase):
            timeout_seconds = 1200
        elif state.phase and 'Model' in state.phase:
            timeout_seconds = 2400
        
        logger.info(f"Executing script: {script_path} with timeout: {timeout_seconds}s in CWD: {output_dir}")
        
        try:
            process = subprocess.run(
                ['python3', '-W', 'ignore', os.path.basename(script_path)],
                capture_output=True,
                text=True,
                timeout=timeout_seconds,
                cwd=output_dir, # Run script in its own output directory
                preexec_fn=os.setsid # For better process control on Linux
            )
            run_status["stdout"] = process.stdout
            run_status["stderr"] = process.stderr
            run_status["returncode"] = process.returncode

            if process.returncode == 0:
                run_status["status"] = "success"
                logger.info(f"Script executed successfully: {script_path}")
                if "[SCRIPT_EXECUTION_ERROR]" in process.stdout:
                    logger.warning(f"Script {script_path} had return code 0 but SCRIPT_EXECUTION_ERROR marker was found in stdout.")
                    run_status["status"] = "error" # Override if error marker present despite rc=0
                    if not run_status["stderr"]: # Populate stderr from stdout if it's empty
                         run_status["stderr"] = "Error marker found in stdout, see execution_output.txt for details."

                if os.path.exists(path_to_error) and run_status["status"] == "success":
                    try:
                        os.remove(path_to_error)
                    except OSError as e_os:
                        logger.warning(f"Could not remove previous error file {path_to_error}: {e_os}")
            else:
                run_status["status"] = "error"
                logger.error(f"Script execution failed with return code {process.returncode}: {script_path}")
                logger.error(f"Stderr: {process.stderr}")

        except subprocess.TimeoutExpired as e_timeout:
            run_status["status"] = "error"
            run_status["timeout_occurred"] = True
            timeout_stderr = f"Code execution timed out after {timeout_seconds} seconds."
            logger.error(f"Script execution timed out: {script_path}")
            if e_timeout.stdout: run_status["stdout"] = e_timeout.stdout.decode(errors='ignore') if isinstance(e_timeout.stdout, bytes) else e_timeout.stdout
            # Prepend timeout message to any existing stderr from the process before timeout
            existing_stderr = (e_timeout.stderr.decode(errors='ignore') if isinstance(e_timeout.stderr, bytes) else e_timeout.stderr) if e_timeout.stderr else ""
            run_status["stderr"] = timeout_stderr + "\n" + existing_stderr

        except Exception as e_exc: 
            run_status["status"] = "error"
            run_status["stderr"] = f"An unexpected error occurred during subprocess.run: {str(e_exc)}"
            logger.error(f"Unexpected error during script execution {script_path}: {e_exc}")

        try:
            with open(path_to_output, 'w', encoding='utf-8') as f_out:
                f_out.write(run_status["stdout"] if run_status["stdout"] else "")
        except IOError as e_io:
            logger.error(f"Failed to write to output file {path_to_output}: {e_io}")

        if run_status["status"] == "error" and run_status["stderr"]:
            try:
                with open(path_to_error, 'w', encoding='utf-8') as f_err:
                    f_err.write(run_status["stderr"])
            except IOError as e_io:
                logger.error(f"Failed to write to error file {path_to_error}: {e_io}")
        
        return run_status

    def _extract_python_code(self, markdown_text: str) -> str:
        """
        Extracts Python code from a markdown string.
        Handles ```python ... ``` and ``` ... ``` blocks.
        """
        # Prioritize ```python ... ```
        match_python = re.search(r"```python\s*([\s\S]+?)\s*```", markdown_text)
        if match_python:
            return match_python.group(1).strip()
        
        # Fallback for ``` ... ```
        match_generic = re.search(r"```\s*([\s\S]+?)\s*```", markdown_text)
        if match_generic:
            potential_code = match_generic.group(1).strip()
            # Basic heuristic to check if it's likely Python code
            # This could be improved with more sophisticated checks if needed
            if any(kw in potential_code for kw in ['import ', 'def ', 'class ', 'print(', ' = ', ' for ', ' if ']):
                logger.info("Found a generic code block, assuming it's Python.")
                return potential_code
            else:
                logger.warning("Found a generic code block, but it doesn't strongly resemble Python. Returning it anyway.")
                return potential_code # Or decide to return "" if stricter parsing is needed
            
        logger.warning("No Python code block (```python ... ``` or ``` ... ```) found in the LLM response.")
        return ""

    def action(self, state: State) -> Dict[str, Any]:
        """
        Generates Python code based on the planner's output and reader's context.
        Saves the generated code and LLM interaction details, then executes the code.
        """
        logger.info(f"Developer agent starting action for phase: {state.phase}")

        planner_agent_payload: Dict[str, Any] = {}
        for agent_output_wrapper in reversed(state.memory):
            if isinstance(agent_output_wrapper, dict):
                if "planner" in agent_output_wrapper and not planner_agent_payload:
                    if isinstance(agent_output_wrapper["planner"], dict):
                        planner_agent_payload = agent_output_wrapper["planner"]
                        break
        
        analysis_plan_str = planner_agent_payload.get("analysis_plan", "")
        if not analysis_plan_str:
            logger.error("No valid analysis plan found from Planner in state memory.")
            return {
                "status": "failure", "error_message": "No valid analysis plan.",
                "generated_code": "", "raw_llm_reply": "", "execution_details": {}
            }

        tasks = [t.strip() for t in analysis_plan_str.strip().split('\n') if t.strip().startswith('-')]
        task_to_perform = tasks[0][1:].strip() if tasks else analysis_plan_str.strip()
        if not task_to_perform:
            logger.error("Analysis plan is effectively empty.")
            return {
                "status": "failure", "error_message": "Analysis plan empty.",
                "generated_code": "", "raw_llm_reply": "", "execution_details": {}
            }
        logger.info(f"Developer addressing task: {task_to_perform}")

        business_context = "No business context found."
        data_summary = "No data summary found."
        try:
            output_subdir = state.config.get('workflow_options', {}).get('output_subdirectory', '_analysis_insights')
            insights_filename = state.config.get('logging', {}).get('insights_filename', 'insights_log.md')
            insights_log_path = os.path.join(state.data_dir, output_subdir, insights_filename)
            if os.path.exists(insights_log_path):
                with open(insights_log_path, 'r', encoding='utf-8') as f_insights:
                    log_content = f_insights.read()
                reader_block_match = re.search(r"## Phase: ContextualSetupAndScan \(reader Agent Output\)(.*?)(?=## Phase:|$)", log_content, re.DOTALL | re.IGNORECASE)
                if reader_block_match:
                    reader_block_content = reader_block_match.group(1)
                    bc_match = re.search(r"\*\*Business Context:\*\*\s*\n(.*?)(?=\n\*\*|\n###|\n##|\n---|$)", reader_block_content, re.DOTALL | re.IGNORECASE)
                    if bc_match: business_context = bc_match.group(1).strip()
                    ds_match = re.search(r"\*\*Data Files Overview:\*\*\s*\n(.*?)(?=\n\*\*|\n###|\n##|\n---|$)", reader_block_content, re.DOTALL | re.IGNORECASE)
                    if ds_match: data_summary = ds_match.group(1).strip()
        except Exception as e:
            logger.error(f"Error reading insights_log.md: {e}")

        prompt = (
            f"You are a Python coding assistant. Your task is to generate Python code for the following data analysis task.\n"
            f"Ensure your code is self-contained, uses common libraries like pandas and numpy, and is ready to run.\n"
            f"The code will be executed within a function wrapper, so avoid top-level `if __name__ == '__main__':` blocks in your direct output.\n"
            f"Prioritize generating actionable business insights, such as identifying trends, patterns, correlations, or anomalies in the data. While basic data cleaning might be necessary if data quality issues impede analysis, the primary goal is to uncover valuable information that can inform business decisions. If the 'Analysis Plan Task to Implement' is specifically about data cleaning or preparation, focus on that. Otherwise, aim for insightful analysis.\n"
        f"Produce outputs that clearly communicate these insights. This includes printing statistical summaries and key observations to standard output, and generating informative visualizations (e.g., bar charts, line plots, scatter plots, heatmaps as appropriate for the data and task). Save all generated plots to files in the `data_directory_path` (which will be provided as a variable) and print a confirmation message to standard output stating the filename of the saved plot.\n\n"
            f"**Business Context:**\n{business_context}\n\n"
            f"**Data Summary/Available Data:**\n{data_summary}\n\n"
            f"**Data Directory Path:**\n{state.data_dir}\n\n"
            f"**Analysis Plan Task to Implement:**\n{task_to_perform}\n\n"
            f"When loading data files (e.g., CSVs), assume a variable `data_directory_path` is predefined in the execution scope and contains the 'Data Directory Path' shown above. "
            f"Construct full paths to data files using this variable and `os.path.join()`. For example, to load `orders.csv`, use `pd.read_csv(os.path.join(data_directory_path, 'orders.csv'))`.\n"
            f"Please include basic error handling, such as try-except blocks around file I/O operations and critical data processing steps.\n"
            f"Please provide ONLY the Python code block for this task, without any surrounding explanations unless they are comments within the code."
        )

        result: Dict[str, Any] = {
            "status": "pending",
            "task_addressed": task_to_perform,
            "generated_code": "",
            "generated_code_path": None,
            "raw_llm_reply": "",
            "error_message": None,
            "execution_details": {}
        }

        llm_raw_reply = ""
        extracted_code = ""
        llm_history_for_file = [{"role": "user", "content": prompt}]

        try:
            llm_raw_reply, _ = self.llm.generate(prompt, history=[])
            llm_history_for_file.append({"role": "assistant", "content": llm_raw_reply})
            extracted_code = self._extract_python_code(llm_raw_reply)
            result["raw_llm_reply"] = llm_raw_reply
            result["generated_code"] = extracted_code
        except Exception as e:
            logger.error(f"LLM call failed: {e}")
            result["status"] = "failure"
            result["error_message"] = f"LLM call failed: {e}"
            return result

        output_dir = state.restore_dir
        os.makedirs(output_dir, exist_ok=True)

        try:
            with open(os.path.join(output_dir, "developer_llm_interaction.json"), "w", encoding="utf-8") as f:
                json.dump(llm_history_for_file, f, indent=4)
            with open(os.path.join(output_dir, "developer_raw_reply.md"), "w", encoding="utf-8") as f:
                f.write(llm_raw_reply)
        except IOError as e:
            logger.warning(f"Failed to write some developer output log files: {e}")

        if not extracted_code:
            logger.warning("Developer: No code was extracted from LLM response.")
            result["status"] = "failure_no_code_extracted"
            result["error_message"] = "No code extracted from LLM response."
            return result

        script_filename = "single_phase_code.py"
        script_path = os.path.join(output_dir, script_filename)
        generated_code_saved = False

        indented_python_code = "\n".join([f"    {line}" for line in extracted_code.split('\n')])
        # Inject the data_directory_path variable assignment into the prefix
        # Ensure it's within the generated_code_function scope if PREFIX_CODE_CONTENT defines it there
        # For simplicity, let's assume PREFIX_CODE_CONTENT ends with 'def generated_code_function():\n'
        # and we want to add the path assignment inside this function.
        # A more robust way would be to find the end of imports or start of the function.
        prefix_with_datadir = PREFIX_CODE_CONTENT + f"    data_directory_path = r'{state.data_dir}'\n"
        full_script_content = f"{prefix_with_datadir}{indented_python_code}{SUFFIX_CODE_CONTENT}"

        try:
            with open(script_path, "w", encoding="utf-8") as f:
                f.write(full_script_content)
            logger.info(f"Developer agent saved wrapped generated code to: {script_path}")
            generated_code_saved = True
            result["generated_code_path"] = script_path
        except IOError as e:
            logger.error(f"Failed to save generated code to {script_path}: {e}")
            result["status"] = "error"
            result["error_message"] = f"Failed to save generated code: {e}"
            return result

        if generated_code_saved:
            logger.info(f"Attempting to execute generated code: {script_path}")
            execution_details = self._run_code(state, script_path)
            result["execution_details"] = execution_details
            if execution_details.get("status") != "success":
                result["status"] = "error_in_execution"
                result["error_message"] = f"Code executed with errors or timed out. Check execution_error.txt in {output_dir}"
            else:
                result["status"] = "success"
        else:
            logger.warning("Code was not saved, skipping execution.")
            result["status"] = "error" # Treat as error if code not saved
            result["error_message"] = "Code generated but not saved, execution skipped."
            result["execution_details"] = {"status": "skipped", "message": "Code not saved."}
        
        logger.info(f"Developer agent finished action for task: {task_to_perform} with status: {result['status']}")
        return result

if __name__ == '__main__':
    # Example Usage (for testing purposes)
    
    # Mock LLM and State for testing
    class MockLLM:
        def generate(self, prompt_text: str, history: Optional[List[Dict[str, str]]] = None, max_tokens: int = 1024) -> Tuple[str, List[Dict[str, str]]]:
            print("\n----- MOCK LLM PROMPT -----")
            print(prompt_text)
            print("----- END MOCK LLM PROMPT -----\n")
            # Simulate LLM response with a Python code block
            response_text = """
Some introductory text that should be ignored by the parser.
```python
# This is a sample Python script generated by MockLLM
import pandas as pd

def perform_analysis():
    print("Mock analysis: Loading and displaying dummy data...")
    data = {'column_A': [10, 20, 30], 'column_B': ['X', 'Y', 'Z']}
    df = pd.DataFrame(data)
    print(df.head())
    print("Mock analysis complete.")

if __name__ == '__main__':
    perform_analysis()
```
Some concluding text that should also be ignored.
"""
            current_history = history if history is not None else []
            updated_history = current_history + [{"role": "assistant", "content": response_text}]
            return response_text, updated_history

    class MockState:
        def __init__(self, data_dir_name: str = "mock_data_dir", context_file_name: str = "mock_context.txt"):
            self.phase = "TestAnalysisPhase"
            base_test_dir = os.path.join(os.getcwd(), "temp_dev_agent_test_outputs")
            self.data_dir = os.path.join(base_test_dir, data_dir_name)
            self.context_file = os.path.join(base_test_dir, context_file_name)
            self.restore_dir = os.path.join(base_test_dir, "outputs", self.phase, "developer_run_0")
            os.makedirs(self.restore_dir, exist_ok=True)
            
            self.memory: List[Dict[str, Any]] = [
                {"reader": {
                    "business_context_summary": "The main business objective is to analyze customer engagement patterns.",
                    "data_summary": "Available data: 'user_activity.csv' with columns ['user_id', 'timestamp', 'activity_type', 'session_duration']."
                }},
                {"planner": {
                    "analysis_plan": "- Load 'user_activity.csv'.\n- Calculate average session duration.\n- Identify the most common activity type."
                }}
            ]


    # Setup logging for the test run
    logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    logger.info("Starting Developer agent test scenario...")

    # Create a dummy data_dir for the test if it doesn't exist (though not directly used by this agent)
    # test_data_dir = "temp_developer_test_data"
    # os.makedirs(test_data_dir, exist_ok=True)
    
    # Instantiate the developer with a mock LLM
    developer_agent = Developer(model="mock_gpt_model", type="api") # type 'api' or 'local'
    developer_agent.llm = MockLLM() # type: ignore  # Override the LLM instance with the mock

    # Create a mock state
    mock_state_instance = MockState() # type: ignore

    # Run the developer's action
    result = developer_agent.action(mock_state_instance) # type: ignore[arg-type]

    # Print the result
    print("\n----- DEVELOPER AGENT TEST RESULT -----")
    print(json.dumps(result, indent=4))

    if result.get("status") == "success" and result.get("generated_code"):
        print("\n----- GENERATED CODE (from test result) -----")
        print(result["generated_code"])
        
        # Verify files were created
        print(f"\nVerify output files in: {mock_state_instance.restore_dir}")
        assert os.path.exists(os.path.join(mock_state_instance.restore_dir, "developer_llm_interaction.json"))
        assert os.path.exists(os.path.join(mock_state_instance.restore_dir, "developer_raw_reply.md"))
        assert os.path.exists(os.path.join(mock_state_instance.restore_dir, "generated_code.py"))
        print("Output files successfully verified.")
    else:
        print("\nDeveloper agent action did not complete successfully or no code was generated.")
        if result.get("error_message"):
            print(f"Error: {result['error_message']}")

    # Clean up dummy directory (optional, but good practice)
    # import shutil
    # base_test_dir_to_remove = os.path.join(os.getcwd(), "temp_dev_agent_test_outputs")
    # if os.path.exists(base_test_dir_to_remove):
    #     shutil.rmtree(base_test_dir_to_remove)
    #     print(f"Cleaned up temporary test directory: {base_test_dir_to_remove}")
    logger.info("Developer agent test scenario finished.")
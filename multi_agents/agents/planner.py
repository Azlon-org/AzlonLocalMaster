from typing import Dict, Any
import json
import logging
import sys
import os

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)
sys.path.append('..')
sys.path.append('../..')
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from agent_base import Agent
# from utils import read_file # Not directly used by planner anymore
from llm import LLM
from state import State
# Prompts will be simplified or redefined
# from prompts.prompt_base import *
# from prompts.prompt_planner import *

class Planner(Agent):
    def __init__(self, model: str, type: str):  
        super().__init__(
            role="planner",
            description="You are good at planning tasks and creating roadmaps.",
            model=model,
            type=type
        )


    def _execute(self, state: State, role_prompt: str) -> Dict[str, Any]:
        history = []
        generated_plan = ""

        # 1. Retrieve Reader's output from state memory
        reader_output = {}
        if state.memory and isinstance(state.memory[-1], dict) and "Reader" in state.memory[-1]:
            reader_output = state.memory[-1]["Reader"]
        
        business_context_summary = reader_output.get("parsed_context_summary", "No business context summary found.")
        data_summary = reader_output.get("parsed_data_summary", "No data summary found.")
        initial_observations = reader_output.get("parsed_initial_observations", "No initial observations found.")
        data_files_preview = reader_output.get("data_files_preview", "No data files preview found.")

        # Read insights_log.md
        insights_log_content = "No insights log found or an error occurred."
        insights_log_status = "Not read"
        try:
            output_subdir = state.config.get('workflow_options', {}).get('output_subdirectory', '_analysis_insights')
            insights_filename = state.config.get('logging', {}).get('insights_filename', 'insights_log.md')
            insights_log_path = os.path.join(state.data_dir, output_subdir, insights_filename)
            if os.path.exists(insights_log_path):
                with open(insights_log_path, 'r') as f:
                    insights_log_content = f.read()
                insights_log_status = "Successfully read"
                if not insights_log_content.strip():
                    insights_log_content = "Insights log is empty."
                    insights_log_status = "Read (empty)"
            else:
                insights_log_content = "Insights log does not exist yet."
                insights_log_status = "Not found"
        except Exception as e:
            logger.error(f"Error reading insights_log.md for Planner: {e}")
            insights_log_content = f"Error reading insights_log.md: {e}"
            insights_log_status = "Error reading"

        # Consolidate information for the planner's prompt
        input_for_planner = (
            f"Business Context Summary:\n{business_context_summary}\n\n"
            f"Data Summary:\n{data_summary}\n\n"
            f"Initial Observations from Reader:\n{initial_observations}\n\n"
            f"Current Insights Log:\n{insights_log_content}\n\n"
            f"Data Files Preview:\n{data_files_preview}"
        )

        # 2. LLM Interaction (Simplified)
        history.append({"role": "system", "content": f"{role_prompt} {self.description}"})
        
        # Placeholder for a new, more generic planning prompt
        prompt_template = (
            "You are an expert data analysis planner. Based on the following information provided by the Reader agent, "
            "your task is to create a high-level strategic plan for analyzing the data to generate business insights. "
            "The plan should be a list of key questions to answer, hypotheses to test, or specific analysis tasks to perform. "
            "Present the plan as a markdown list.\n\n"
            "READER'S SUMMARY AND OBSERVATIONS:\n{reader_summary}\n\n"
            "ANALYSIS PLAN (Markdown List):"
        )
        
        llm_input = prompt_template.format(reader_summary=input_for_planner)
        
        raw_plan_reply = ""
        try:
            raw_plan_reply, history = self.llm.generate(llm_input, history, max_tokens=4096)
            # Assuming _parse_markdown extracts the main content if LLM returns markdown
            generated_plan = self._parse_markdown(raw_plan_reply) 
        except Exception as e:
            logger.error(f"LLM generation failed for Planner agent: {e}")
            raw_plan_reply = f"LLM generation failed: {e}"
            generated_plan = "Failed to generate plan due to LLM error."

        # 3. Save outputs
        os.makedirs(state.restore_dir, exist_ok=True)
        with open(os.path.join(state.restore_dir, f'{self.role}_llm_history.json'), 'w') as f:
            json.dump(history, f, indent=4)
        with open(os.path.join(state.restore_dir, f'{self.role}_raw_plan_reply.txt'), 'w') as f:
            f.write(raw_plan_reply)
        with open(os.path.join(state.restore_dir, 'markdown_plan.txt'), 'w') as f:
            f.write(generated_plan)

        logger.info(f"State {state.phase} - Agent {self.role} finishes working.")
        
        # 4. Return results for state memory
        return {
            self.role: {
                "status": "success" if not generated_plan.startswith("Failed") else "failure",
                "input_summary_for_llm": input_for_planner,
                "llm_raw_reply": raw_plan_reply,
                "generated_plan": generated_plan,
            "analysis_plan": generated_plan,  # Add for Developer agent compatibility
                "insights_log_status_at_planning": insights_log_status,
                "insights_log_preview_at_planning": insights_log_content[:500] + ('...' if len(insights_log_content) > 500 else '')
            }
        }

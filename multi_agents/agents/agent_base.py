# agents/agent_base.py

from typing import Dict, Any
import json
import re
import logging
import sys 
import os
import pdb
import glob
import pandas as pd

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)
sys.path.append('..')
sys.path.append('../..')
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from utils import read_file, PREFIX_MULTI_AGENTS
from llm import LLM
from state import State
from prompts.prompt_base import *
from typing import Tuple, List
from multi_agents.memory import Memory
from multi_agents.tools.retrieve_doc import RetrieveTool
from multi_agents.llm import OpenaiEmbeddings, LLM
from api_handler import load_api_config


class Agent:
    def __init__(self, role: str, description: str, model: str, type: str):
        self.role = role
        self.description = description
        self.llm = LLM(model, type)
        self.model = model
        logger.info(f'Agent {self.role} is created with model {model}.')

    def _gather_experience_with_suggestion(self, state: State) -> str:
        experience_with_suggestion = ""
        for i, each_state_memory in enumerate(state.memory[:-1]):
            act_agent_memory = each_state_memory.get(self.role, {}) # 获取过去state中当前agent的memory
            result = act_agent_memory.get("result", "")
            reviewer_memory = each_state_memory.get("reviewer", {}) # 获取过去state中reviewer的memory
            suggestion = reviewer_memory.get("suggestion", {}).get(f"agent {self.role}", "")
            score = reviewer_memory.get("score", {}).get(f"agent {self.role}", 3)
            experience_with_suggestion += PROMPT_EACH_EXPERIENCE_WITH_SUGGESTION.format(index=i, experience=result, suggestion=suggestion, score=score)
            if self.role == 'developer':
                path_to_error = os.path.join(state.restore_dir, 'error.txt') # Use phase_output_dir (restore_dir)
                path_to_not_pass_info = os.path.join(state.restore_dir, 'not_pass_information.txt') # Use phase_output_dir (restore_dir)
                if os.path.exists(path_to_error):
                    with open(path_to_error, 'r') as f:
                        error_message = f.read()
                    experience_with_suggestion += f"\n<ERROR MESSAGE>\n{error_message}\n</ERROR MESSAGE>"
                elif os.path.exists(path_to_not_pass_info):
                    with open(path_to_not_pass_info, 'r') as f:
                        not_pass_info = f.read()
                    experience_with_suggestion += f"\n<NOT PASS INFORMATION>\n{not_pass_info}\n</NOT PASS INFORMATION"
        return experience_with_suggestion
    
    def _read_data(self, state: State, num_lines: int = 11) -> str:
        def read_sample(file_path: str, num_lines) -> str:
            """
            读取文件的前 num_lines 行内容并返回为字符串。
            """
            sample_lines = []
            with open(file_path, 'r', encoding='utf-8') as f:
                for i, line in enumerate(f):
                    if i >= num_lines:
                        break
                    sample_lines.append(line)
            return "".join(sample_lines)
        
        submission_columns = pd.read_csv(os.path.join(state.data_dir, 'sample_submission.csv')).columns.tolist() # Use data_dir
        target_columns = submission_columns[1:]
        result = f"\n#############\n# TARGET VARIABLE #\n{target_columns}"
        if state.phase in ["Understand Background", "Preliminary Exploratory Data Analysis", "Data Cleaning", "ContextualSetupAndScan", "InitialDataProfiling"]:
            train_data_sample = read_sample(os.path.join(state.data_dir, 'train.csv'), num_lines) # Use data_dir
            test_data_sample = read_sample(os.path.join(state.data_dir, 'test.csv'), num_lines) # Use data_dir
            result += f"\n#############\n# TRAIN DATA WITH FEATURES #\n{train_data_sample}\n#############\n# TEST DATA WITH FEATURES #\n{test_data_sample}"
        elif state.phase in ["In-depth Exploratory Data Analysis", "Feature Engineering", "IterativeAnalysisLoop"]:
            # Assuming cleaned files are in data_dir for now, consistent with original logic for source files
            cleaned_train_data_sample = read_sample(os.path.join(state.data_dir, 'cleaned_train.csv'), num_lines) # Use data_dir
            cleaned_test_data_sample = read_sample(os.path.join(state.data_dir, 'cleaned_test.csv'), num_lines) # Use data_dir
            result += f"\n#############\n# CLEANED TRAIN DATA WITH FEATURES #\n{cleaned_train_data_sample}\n#############\n# CLEANED TEST DATA WITH FEATURES #\n{cleaned_test_data_sample}"
        elif state.phase in ["Model Building, Validation, and Prediction", "FinalInsightCompilation"]:
            # Assuming processed files are in data_dir for now
            processed_train_data_sample = read_sample(os.path.join(state.data_dir, 'processed_train.csv'), num_lines) # Use data_dir
            processed_test_data_sample = read_sample(os.path.join(state.data_dir, 'processed_test.csv'), num_lines) # Use data_dir
            submission_sample = read_sample(os.path.join(state.data_dir, 'sample_submission.csv'), num_lines) # Use data_dir
            result += f"\n#############\n# PROCESSED TRAIN DATA WITH FEATURES #\n{processed_train_data_sample}\n#############\n# PROCESSED TEST DATA WITH FEATURES #\n{processed_test_data_sample}\n#############\n# SUBMISSION FORMAT #\n{submission_sample}"
            # competition_info.txt is likely specific to old structure, using state.context_file now or a general info file
            # For now, attempting to read from state.context_file if it exists, otherwise using a placeholder
            competition_info_path = os.path.join(state.data_dir, state.context_file if state.context_file else 'competition_info.txt')
            if os.path.exists(competition_info_path):
                 with open(competition_info_path, 'r') as f:
                    competition_info = f.read()
            else:
                competition_info = "Evaluation metric information not found."
                logger.warning(f"Could not find competition_info.txt or context_file at {competition_info_path}")
            prompt_extract_metric = f"# TASK #\nPlease extract the evaluation metric from the competition information: {competition_info}\n#############\n# RESPONSE: MARKDOWN FORMAT #\n```markdown\n# Evaluation Metric\n[evaluation metric for the competition]\n```"
            raw_reply, _ = self.llm.generate(prompt_extract_metric, history=[], max_tokens=4096)
            metric = self._parse_markdown(raw_reply)
            result += f"\n#############\n# EVALUATION METRIC #\n{metric}"
        return result

    def _data_preview(self, state: State, num_lines: int) -> str:
        data_used_in_preview = self._read_data(state, num_lines=num_lines)
        input = PROMPT_DATA_PREVIEW.format(data=data_used_in_preview)
        raw_reply, _ = self.llm.generate(input, [], max_tokens=4096)
        data_preview = self._parse_markdown(raw_reply)

        with open(f'{state.restore_dir}/data_preview.txt', 'w') as f:
            f.write(data_preview)
        return data_preview

    def _parse_json(self, raw_reply: str) -> Dict[str, Any]:
        def try_json_loads(data: str) -> Dict[str, Any]:
            try:
                return json.loads(data)
            except json.JSONDecodeError as e:
                logging.error(f"JSON decoding error: {e}")
                return {} # Return empty dict on error to match type hint

        raw_reply = raw_reply.strip()
        logger.info(f"Attempting to extract JSON from raw reply.")
        json_match = re.search(r'```json(.*)```', raw_reply, re.DOTALL) # 贪婪模式捕获
        
        if json_match:
            reply_str = json_match.group(1).strip()
            reply = try_json_loads(reply_str)
            if reply is not None:
                return reply
        
        logger.info(f"Failed to parse JSON from raw reply, attempting reorganization.")
        if self.role == 'developer':
            json_reply, _ = self.llm.generate(PROMPT_REORGANIZE_EXTRACT_TOOLS.format(information=raw_reply), history=[], max_tokens=4096)
        else:
            # pdb.set_trace()
            json_reply, _ = self.llm.generate(PROMPT_REORGANIZE_JSON.format(information=raw_reply), history=[], max_tokens=4096)
        
        json_match = re.search(r'```json(.*?)```', json_reply, re.DOTALL)
        if json_match:
            reply_str = json_match.group(1).strip()
            reply = try_json_loads(reply_str) # try_json_loads now returns {} on error
            
            if reply: # Check if reply is not an empty dict (i.e., was successful)
                return reply
        
        logging.error("Final attempt to parse JSON failed. Returning empty dict.")
        return {} # Ensure a dict is always returned

        return reply
    
    def _parse_markdown(self, raw_reply: str) -> str:
        # Try to find a ```markdown ... ``` block
        markdown_match = re.search(r'```markdown\s*([\s\S]*?)\s*```', raw_reply, re.DOTALL)
        if markdown_match:
            return markdown_match.group(1).strip()

        # If not found, try to find any generic ``` ... ``` code block
        generic_match = re.search(r'```(?:\w*\n)?([\s\S]*?)\s*```', raw_reply, re.DOTALL)
        if generic_match:
            # This might capture the language tag if present on the first line, e.g., ```python
            # We strip it if it looks like a language tag common in markdown
            content = generic_match.group(1).strip()
            # A simple check to remove a language hint if it's the first line of the block
            # common_languages = ['python', 'json', 'text', 'bash', 'shell', 'markdown', 'yaml', 'sql']
            # first_line = content.split('\n', 1)[0].strip()
            # if first_line.lower() in common_languages:
            #     content = content.split('\n', 1)[1] if '\n' in content else ''
            return content.strip()

        # If no code blocks are found, log a warning and return the raw reply
        logging.warning(f"No specific markdown code block (```markdown ... ``` or ``` ... ```) found in raw reply. Returning raw reply. Reply was: '{raw_reply[:200]}...' ")
        return raw_reply

    def _json_to_markdown(self, json_data):
        md_output = f"## {json_data['name']}\n\n"
        md_output += f"**Name:** {json_data['name']}  \n"
        md_output += f"**Description:** {json_data['description']}  \n"
        md_output += f"**Applicable Situations:** {json_data['applicable_situations']}\n\n"

        md_output += "**Parameters:**\n"
        for param, details in json_data['parameters'].items():
            md_output += f"- `{param}`:\n"
            md_output += f"  - **Type:** `{details['type'] if isinstance(details['type'], str) else ' | '.join(f'`{t}`' for t in details['type'])}`\n"
            md_output += f"  - **Description:** {details['description']}\n"
            if 'enum' in details:
                md_output += f"  - **Enum:** {' | '.join(f'`{e}`' for e in details['enum'])}\n"
            if 'default' in details:
                md_output += f"  - **Default:** `{details['default']}`\n"

        md_output += f"\n**Required:** {', '.join(f'`{r}`' for r in json_data['required'])}  \n"
        md_output += f"**Result:** {json_data['result']}  \n"
        
        md_output += "**Notes:**\n"
        for note in json_data['notes']:
            md_output += f"- {note}\n"

        if 'example' in json_data:
            md_output += "**Example:**\n"
            md_output += f"  - **Input:**\n"
            for key, value in json_data['example']['input'].items():
                md_output += f"    - `{key}`: {value}\n"
            md_output += f"  - **Output:**\n"
            for key, value in json_data['example']['output'].items():
                md_output += f"    - `{key}`: {value}\n"

        md_output += "\n---\n"
        return md_output

    def _get_tools(self, state: State) -> Tuple[str, List[str]]:                
        # embeddings = OpenaiEmbeddings(api_key=load_api_config()[0], base_url=load_api_config()[1]) # Commented out: No active embedding calls
        # memory = RetrieveTool(self.llm, embeddings, doc_path='multi_agents/tools/ml_tools_doc', collection_name='tools') # Commented out
        # # update the memory
        # memory.create_db_tools() # Commented out
        logger.info("Agent._get_tools: Embedding and RetrieveTool functionality is currently disabled.")

        # state_name = state.dir_name # Deprecated
        # phase_to_dir and phase_to_ml_tools are deprecated from config.json
        # all_tool_names will be derived from state.config['available_tools_catalog']
        all_tool_names = []
        if state.config and 'available_tools_catalog' in state.config:
            for category in state.config['available_tools_catalog'].values():
                if isinstance(category, list):
                    all_tool_names.extend(category)
        else:
            logger.warning("'available_tools_catalog' not found in state.config or state.config is None.")

        if self.role == 'developer' and state.phase in ['Data Cleaning', 'Feature Engineering', 'Model Building, Validation, and Prediction'] and len(all_tool_names) > 0:
            logger.info(f"Extracting tools' description for developer in phase: {state.phase}")
            with open(os.path.join(state.phase_output_dir, 'markdown_plan.txt'), 'r') as file:
                markdown_plan = file.read()
            input = PROMPT_EXTRACT_TOOLS.format(document=markdown_plan, all_tool_names=all_tool_names)
            raw_reply, _ = self.llm.generate(input, history=[], max_tokens=4096)
            with open(os.path.join(state.phase_output_dir, 'extract_tools_reply.txt'), 'w') as file:
                file.write(raw_reply)
            tool_names = self._parse_json(raw_reply)['tool_names']
        else:
            tool_names = all_tool_names

        tools = []
        for tool_name in tool_names:
            # conclusion = memory.query_tools(f'Use the {tool_name} tool.', state.phase) # state_name replaced with state.phase, but memory is disabled
            conclusion = f"Tool description for '{tool_name}' is unavailable (embeddings disabled)."
            tools.append(conclusion)

        if self.role == 'developer' and state.phase in ['Data Cleaning', 'Feature Engineering', 'Model Building, Validation, and Prediction', 'IterativeAnalysisLoop']:  
            with open(os.path.join(state.phase_output_dir, f'tools_used_in_{state.phase}.md'), 'w') as file:
                file.write(''.join(tools))
        
        tools = ''.join(tools) if len(tool_names) > 0 else "There is no pre-defined tools used in this phase."
        return tools, tool_names

        # path_to_tools_doc = f'{PREFIX_MULTI_AGENTS}/tools/ml_tools_doc/{state.dir_name}_tools.md'
        # print(path_to_tools_doc)
        # if len(tool_names) > 0:
        #     if os.path.exists(path_to_tools_doc):
        #         with open(path_to_tools_doc, 'r') as file:
        #             tools = file.read()
        #     else:
        #         # Read the JSON file
        #         with open('multi_agents/function_to_schema.json', 'r') as file:
        #             schema_data = json.load(file)
        #         print(schema_data)
        #         for tool_name in tool_names:
        #             tools += self._json_to_markdown(schema_data[tool_name])
        #         with open(f'{PREFIX_MULTI_AGENTS}/tools/ml_tools_doc/{state.dir_name}_tools.md', 'w') as file:
        #             file.write(tools)
        # else:
        #     tools = "There is no pre-defined tools used in this phase."
        # return tools, tool_names

    def _get_feature_info(self, state: State) -> str:
        # Define file names for before and after the current phase
        phase_files = {
            "Preliminary Exploratory Data Analysis": ("train.csv", "test.csv", "train.csv", "test.csv"),
            "Data Cleaning": ("train.csv", "test.csv", "cleaned_train.csv", "cleaned_test.csv"),
            "In-depth Exploratory Data Analysis": ("cleaned_train.csv", "cleaned_test.csv", "cleaned_train.csv", "cleaned_test.csv"),
            "Feature Engineering": ("cleaned_train.csv", "cleaned_test.csv", "processed_train.csv", "processed_test.csv"),
            "Model Building, Validation, and Prediction": ("processed_train.csv", "processed_test.csv", "processed_train.csv", "processed_test.csv"),
            "InitialDataProfiling": ("placeholder_data.csv", None, "placeholder_processed.csv", None),  # Added to handle this phase
            "IterativeAnalysisLoop": ("placeholder_data.csv", None, "placeholder_processed.csv", None) # Added to handle this phase
        }

        before_train, before_test, after_train, after_test = phase_files.get(state.phase, (None, None, None, None))

        if before_train is None:
            raise ValueError(f"Unknown phase: {state.phase}")

        # Read the datasets
        # before_train is guaranteed to be a string here due to the check on line 285
        before_train_path = os.path.join(state.data_dir, before_train)
        before_train_df = pd.read_csv(before_train_path) if os.path.exists(before_train_path) else None
        if before_train_df is None:
            logging.error(f"Critical file not found: {before_train_path}. This might halt processing.")
            # Depending on desired behavior, could raise an error here or return an empty/error state

        before_test_df = None
        if before_test:
            before_test_path = os.path.join(state.data_dir, before_test)
            if os.path.exists(before_test_path):
                before_test_df = pd.read_csv(before_test_path)
            else:
                logging.warning(f"Optional file not found: {before_test_path}")
        
        after_train_df = None
        if after_train:
            after_train_path = os.path.join(state.data_dir, after_train)
            if os.path.exists(after_train_path):
                after_train_df = pd.read_csv(after_train_path)
            else:
                logging.warning(f"Optional file not found: {after_train_path}")

        after_test_df = None
        if after_test:
            after_test_path = os.path.join(state.data_dir, after_test)
            if os.path.exists(after_test_path):
                after_test_df = pd.read_csv(after_test_path)
            else:
                logging.warning(f"Optional file not found: {after_test_path}")
        
        # Get features before and after
        features_before = list(before_train_df.columns) if before_train_df is not None else []
        features_after = list(after_train_df.columns) if after_train_df is not None else []
        
        # Identify target variable
        target_variable = [] # Initialize as empty list
        if after_train_df is not None and after_test_df is not None:
            # Ensure features_after is up-to-date if after_train_df was loaded but features_after wasn't (e.g. if it was None initially)
            if not features_after and after_train_df is not None: features_after = list(after_train_df.columns)
            after_test_columns = list(after_test_df.columns)
            target_variable = list(set(features_after) - set(after_test_columns))
        elif after_train_df is not None:
            logging.warning("after_test_df is not available or not loaded, target variable identification might be incomplete or based on other conventions.")
            # Potentially add other logic here if target can be inferred differently
        else:
            logging.warning("after_train_df is not available or not loaded, cannot identify target variable through column comparison.")
        
        if len(target_variable) == 1:
            target_variable = target_variable[0]
        elif len(target_variable) > 1:
            logging.warning(f"Multiple potential target variables found: {target_variable}")
            target_variable = ', '.join(target_variable)
        else:
            logging.warning("No target variable found by comparing train and test columns")
            target_variable = "Unknown"

        feature_info = PROMPT_FEATURE_INFO.format(
            target_variable=target_variable, 
            features_before=features_before, 
            features_after=features_after
        )
        return feature_info


    def action(self, state: State) -> Dict[str, Any]:
        # pdb.set_trace()
        logger.info(f"State {state.phase} - Agent {self.role} is executing.")
        role_prompt = AGENT_ROLE_TEMPLATE.format(agent_role=self.role)
        return self._execute(state, role_prompt)

    def _execute(self, state: State, role_prompt: str) -> Dict[str, Any]:
        raise NotImplementedError("Subclasses should implement this!")


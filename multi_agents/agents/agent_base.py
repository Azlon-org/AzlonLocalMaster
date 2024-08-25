# agents/agent_base.py

from typing import Dict, Any
import json
import re
import logging
import sys 
import os
import pdb
import glob

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

sys.path.append('..')
sys.path.append('../..')
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from utils import read_file
from llm import LLM
from state import State
from prompts.prompt_base import *

class Agent:
    def __init__(self, role: str, description: str, model: str, type: str):
        self.role = role
        self.description = description
        self.llm = LLM(model, type)
        print(f'Agent {self.role} is created.')

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
                with open(f'{state.competition_dir}/{state.dir_name}/{state.dir_name}_error.txt', 'r') as f:
                    error_message = f.read()
                experience_with_suggestion += f"\n<ERROR MESSAGE>\n{error_message}\n</ERROR MESSAGE>"
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
        
        result = ""
        if state.phase in ["Preliminary Exploratory Data Analysis", "Data Cleaning"]:
            # train_data_sample = read_sample(f'{state.competition_dir}/train.csv', num_lines)
            # 包含train的文件路径 过滤掉包含 'cleaned_train' 和 'processed_train' 的文件 选择第一个符合条件的
            all_train_files = glob.glob(os.path.join(state.competition_dir, '*train*.csv'))
            filtered_train_files = [f for f in all_train_files if 'cleaned_train' not in f and 'processed_train' not in f]
            if filtered_train_files:
                train_file_path = filtered_train_files[0]
                train_data_sample = read_sample(train_file_path, num_lines)
            else:
                print("没有找到符合条件的文件")
                exit()
            train_data_sample = read_sample(train_file_path, num_lines)
            test_data_sample = read_sample(f'{state.competition_dir}/test.csv', num_lines)
            result += f"\n#############\n# TRAIN DATA WITH FEATURES #\n{train_data_sample}\n\n#############\n# TEST DATA WITH FEATURES #\n{test_data_sample}"
        elif state.phase in ["In-depth Exploratory Data Analysis", "Feature Engineering"]:
            cleaned_train_data_sample = read_sample(f'{state.competition_dir}/cleaned_train.csv', num_lines)
            cleaned_test_data_sample = read_sample(f'{state.competition_dir}/cleaned_test.csv', num_lines)
            result += f"\n#############\n# CLEANED TRAIN DATA WITH FEATURES #\n{cleaned_train_data_sample}\n\n#############\n# CLEANED TEST DATA WITH FEATURES #\n{cleaned_test_data_sample}"
        elif state.phase in ["Model Building, Validation, and Prediction"]:
            processed_train_data_sample = read_sample(f'{state.competition_dir}/processed_train.csv', num_lines)
            processed_test_data_sample = read_sample(f'{state.competition_dir}/processed_test.csv', num_lines)
            result += f"\n#############\n# PROCESSED TRAIN DATA WITH FEATURES #\n{processed_train_data_sample}\n\n#############\n# PROCESSED TEST DATA WITH FEATURES #\n{processed_test_data_sample}"

        return result


    def _parse_json(self, raw_reply: str) -> Dict[str, Any]:
        def try_json_loads(data: str) -> Dict[str, Any]:
            try:
                return json.loads(data)
            except json.JSONDecodeError as e:
                logging.error(f"JSON decoding error: {e}")
                return None

        raw_reply = raw_reply.strip()
        logging.info(f"Attempting to extract JSON from raw reply.")
        json_match = re.search(r'```json(.*?)```', raw_reply, re.DOTALL)
        
        if json_match:
            reply_str = json_match.group(1).strip()
            reply = try_json_loads(reply_str)
            if reply is not None:
                return reply
        
        logging.info(f"Failed to parse JSON from raw reply, attempting reorganization.")
        if self.role == "planner":
            json_reply, _ = self.llm.generate(REORGANIZE_REPLY_TYPE3.format(information=raw_reply), history=[], max_tokens=4096)
        elif self.role == "reviewer":
            json_reply, _ = self.llm.generate(REORGANIZE_REPLY_TYPE2.format(information=raw_reply), history=[], max_tokens=4096)
        else:
            json_reply, _ = self.llm.generate(REORGANIZE_REPLY_TYPE1.format(information=raw_reply), history=[], max_tokens=4096)
        
        json_match = re.search(r'```json(.*?)```', json_reply, re.DOTALL)
        if json_match:
            reply_str = json_match.group(1).strip()
            reply = try_json_loads(reply_str)
            
            if reply is not None:
                return reply
        
        logging.error("Final attempt to parse JSON failed.")
        reply = {}

        return reply

    def action(self, state: State) -> Dict[str, Any]:
        # pdb.set_trace()
        print(f"State {state.phase} - Agent {self.role} is executing.")
        role_prompt = AGENT_ROLE_TEMPLATE.format(agent_role=self.role)
        return self._execute(state, role_prompt)

    def _execute(self, state: State, role_prompt: str) -> Dict[str, Any]:
        raise NotImplementedError("Subclasses should implement this!")


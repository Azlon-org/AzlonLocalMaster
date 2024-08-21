from typing import Dict, Any
import json
import re
import logging
import sys 
import os

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

sys.path.append('..')
sys.path.append('../..')
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from agent_base import Agent
from utils import read_file, PREFIX_MULTI_AGENTS
from LLM import LLM
from State import State
from prompts.prompt_base import *
from prompts.prompt_reader import *

class Reader(Agent):
    def __init__(self, model: str, type: str):
        super().__init__(
            role="reader",
            description="You are good at reading document, summarizing information and outputting it in JSON format.",
            model=model,
            type=type
        )
    
    def _execute(self, state: State, role_prompt: str) -> Dict[str, Any]:
        path_to_overview = f'{PREFIX_MULTI_AGENTS}/competition/{state.competition}/overview.txt'
        overview = read_file(path_to_overview)
        history = []
        round = 0
        # Understand Background 读取overview.txt，生成competition_info.txt
        if len(state.memory) == 1: # 如果之前没有memory，说明是第一次执行
            history.append({"role": "system", "content": f"{role_prompt} {self.description}"})
            # pdb.set_trace()
            while True:
                if round == 0:
                    task = PROMPT_READER_TASK
                    input = PROMPT_READER.format(steps_in_context=state.context, task=task)
                elif round == 1: input = f"\n#############\n# OVERVIEW #\n{overview}"
                elif round == 2: break
                raw_reply, history = self.llm.generate(input, history, max_tokens=4096)
                round += 1
        else: # 如果之前有memory，拼接之前memory中reader的结果作为experience
            self.description = "You are good at reading document, summarizing information and outputting it in JSON format." \
                            "You have advanced reasoning abilities and can improve your answers through reflection."
            experience_with_suggestion = self._gather_experience_with_suggestion(state)
            history.append({"role": "system", "content": f"{role_prompt} {self.description}"})
            while True:
                if round == 0:
                    task = PROMPT_READER_TASK
                    input = PROMPT_READER_WITH_EXPERIENCE.format(steps_in_context=state.context, task=task, experience_with_suggestion=experience_with_suggestion)
                elif round == 1: input = f"\n#############\n# OVERVIEW #\n{overview}"
                elif round == 2: break
                raw_reply, history = self.llm.generate(input, history, max_tokens=4096)
                round += 1
        result = raw_reply
        reply = self._parse_json(raw_reply)

        try:
            summary = reply["final_answer"]
        except KeyError:
            logging.info("Final answer not found in reply.")
            summary = reply

        with open(f'{state.competition_dir}/competition_info.json', 'w') as f:
            json.dump(summary, f, indent=4)
        with open(f'{state.restore_dir}/{self.role}_reply.txt', 'w') as f:
            f.write(raw_reply)
        input_used_in_review = f"   <overview>\n{overview}\n    </overview>"

        print(f"State {state.phase} - Agent {self.role} finishes working.")
        return {self.role: {"history": history, "role": self.role, "description": self.description, "task": task, "input": input_used_in_review, "summary": summary, "result": result}}

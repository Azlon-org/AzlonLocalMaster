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
from llm import LLM
from state import State
from prompts.prompt_base import *
from prompts.prompt_summarizer import *

class Summarizer(Agent):
    def __init__(self, model: str, type: str):  
        super().__init__(
            role="summarizer",
            description="You are good at summarizing the trajectory of multiple agents, synthesize report and summarize key information.",
            model=model,
            type=type
        )

    def _generate_prompt_round1(self, state: State) -> str:
        prompt_round1 = ""
        current_memory = state.memory[-1]
        for role, memory in current_memory.items():
            trajectory = json.dumps(memory.get("history", []), indent=4)
            prompt_round1 += f"\n#############\n# TRAJECTORY OF AGENT {role.upper()} #\n{trajectory}"

        return prompt_round1

    def _execute(self, state: State, role_prompt: str) -> Dict[str, Any]:
        # 实现总结功能 阅读当前state的memory 生成report/message
        history = []
        round = 0
        history.append({"role": "system", "content": f"{role_prompt} {self.description}"})
        while True:
            if round == 0:
                input = PROMPT_SUMMARIZER_ROUND0.format(steps_in_context=state.context, step_name=state.phase)
            elif round == 1:
                prompt_round1 = self._generate_prompt_round1(state)
                input = prompt_round1
            elif round == 2:
                report = raw_reply
                input = "#############\n# SECOND TASK #\n" \
                        "Using the report you have written, identify and convey the most helpful information for the agents in the upcoming step. " \
                        "Deliver this information in the form of a clear and concise message to the agents." \
                        "#############\n# RESPONSE: JSON FORMAT #\n"
                input += PROMPT_SUMMARIZER_ROUND2_RESPONSE_FORMAT
            elif round == 3:
                raw_message = raw_reply
                break
            raw_reply, history = self.llm.generate(input, history, max_tokens=4096)
            round += 1

        message = self._parse_json(raw_message)
        # 保存history
        with open(f'{state.restore_dir}/{self.role}_history.json', 'w') as f:
            json.dump(history, f, indent=4)
        with open(f'{state.restore_dir}/{self.role}_reply.txt', 'w') as f:
            f.write(report+'\n\n\n'+raw_message)

        print(f"State {state.phase} - Agent {self.role} finishes working.")
        return {self.role: {"history": history, "report": report, "message": message}}
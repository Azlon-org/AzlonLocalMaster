from typing import Dict, Any
import json
import re
import logging
from LLM import LLM
from State import State
import sys 
import os

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

sys.path.append('..')
sys.path.append('../..')
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from agent_base import Agent
from utils import read_file, PREFIX_MULTI_AGENTS
from LLM import LLM
from prompts.prompt_base import *
from prompts.prompt_planner import *

class Planner(Agent):
    def __init__(self, model: str, type: str):  
        super().__init__(
            role="planner",
            description="You are good at planning tasks and creating roadmaps.",
            model=model,
            type=type
        )

    def _get_previous_plan_and_report(self, state: State):
        previous_plan = ""
        previous_phases = state.get_previous_phase(type="all")
        for previous_phase in previous_phases:
            previous_dir_name = state.phase_to_directory[previous_phase]
            previous_plan += f"## {previous_phase.upper()} ##\n"
            path_to_previous_plan = f'{state.competition_dir}/{previous_dir_name}/plan.json'
            if os.path.exists(path_to_previous_plan):
                with open(path_to_previous_plan, 'r') as f:
                    previous_plan += f.read()
                    previous_plan += '\n'
            else:
                previous_plan = "There is no plan in this step."
        path_to_previous_report = f'{state.competition_dir}/{previous_dir_name}/Report.txt'
        if os.path.exists(path_to_previous_report):
            previous_report = read_file(path_to_previous_report)
        else:
            previous_report = "There is no report in the previous step."
        return previous_plan, previous_report

    def _execute(self, state: State, role_prompt: str) -> Dict[str, Any]:
        # 实现规划功能
        history = []
        round = 0
        with open(f'{state.competition_dir}/competition_info.json', 'r') as f:
            competition_info = json.load(f)
        if len(state.memory) == 1: # 如果之前没有memory，说明是第一次执行
            history.append({"role": "system", "content": f"{role_prompt} {self.description}"})
            while True:
                if round == 0:
                    task = PROMPT_PLANNER_TASK.format(step_name=state.phase)
                    input = PROMPT_PLANNER.format(steps_in_context=state.context, step_name=state.phase, message=state.message, competition_info=competition_info, task=task)
                elif round == 1:
                    input = f"\n#############\n# PREVIOUS PLAN #\n{self._get_previous_plan_and_report(state)[0]}\n#############\n# PREVIOUS REPORT #\n{self._get_previous_plan_and_report(state)[1]}"
                    input += self._read_data(state)
                elif round == 2:
                    break
                raw_reply, history = self.llm.generate(input, history, max_tokens=4096)
                round += 1
        else:
            last_planner_score = state.memory[-2].get("reviewer", {}).get("score", {}).get("agent planner", 0)
            if last_planner_score >= 3: # 如果上一轮中planner的评分大于等于3，说明上一个planner的规划结果是可以接受的
                return {"planner": state.memory[-2]["planner"]}
            else:
                return {"planner": state.memory[-2]["planner"]}
                pass
        result = raw_reply
        reply = self._parse_json(raw_reply)

        try:
            plan = reply["final_answer"]
        except KeyError:
            logging.info("Final answer not found in reply.")
            plan = reply

        with open(f'{state.restore_dir}/plan.json', 'w') as f:
            json.dump(plan, f, indent=4) # 保存规划结果
        with open(f'{state.restore_dir}/{self.role}_reply.txt', 'w') as f:
            f.write(raw_reply)

        input_used_in_review = f"   <competition_info>\n{competition_info}\n    </competition_info>"

        print(f"State {state.phase} - Agent {self.role} finishes working.")
        return {self.role: {"history": history, "role": self.role, "description": self.description, "task": task, "input": input_used_in_review, "plan": plan, "result": result}}

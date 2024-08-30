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
            description="You are good at asking key questions and answer the questions from given information.",
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
    
    def _specified_prompt(self, state: State) -> str:
        pass

    def _execute(self, state: State, role_prompt: str) -> Dict[str, Any]:
        # 实现总结功能 阅读当前state的memory 生成report
        history = []
        history.append({"role": "system", "content": f"{role_prompt} {self.description}"})

        # 读取competition_info和plan
        with open(f'{state.competition_dir}/competition_info.txt', 'r') as f:
            competition_info = f.read()
        with open(f'{state.restore_dir}/markdown_plan.txt', 'r') as f:
            plan = f.read()

        # Design questions
        design_questions_history = []
        next_step_name = state.get_next_phase()
        input = PROMPT_SUMMARIZER_DESIGN_QUESITONS.format(steps_in_context=state.context, step_name=state.phase, next_step_name=next_step_name)
        _, design_questions_history = self.llm.generate(input, design_questions_history, max_tokens=4096)

        input = f"# COMPETITION INFO #\n{competition_info}\n#############\n# PLAN #\n{plan}"
        design_questions_reply, design_questions_history = self.llm.generate(input, design_questions_history, max_tokens=4096)
        with open(f'{state.restore_dir}/design_questions_reply.txt', 'w') as f:
            f.write(design_questions_reply)

        input = PROMPT_SUMMARIZER_REORGAINZE_QUESTIONS
        reorganize_questions_reply, design_questions_history = self.llm.generate(input, design_questions_history, max_tokens=4096)
        questions = self._parse_markdown(reorganize_questions_reply)
        with open(f'{state.restore_dir}/questions.txt', 'w') as f:
            f.write(questions)

        # Answer questions
        with open(f'{state.restore_dir}/single_step_code.txt', 'r') as f:
            code = f.read()
        with open(f'{state.restore_dir}/{state.dir_name}_output.txt', 'r') as f:
            output = f.read()
        with open(f'{state.restore_dir}/review.json', 'r') as f:
            review = json.load(f)

        answer_questions_history = []
        input = PROMPT_SUMMARIZER_ANSWER_QUESTIONS.format(steps_in_context=state.context, step_name=state.phase, questions=questions)
        _, answer_questions_history = self.llm.generate(input, answer_questions_history, max_tokens=4096)
        
        input = PROMPT_INFORMATION_FOR_ANSWER.format(competition_info=competition_info, plan=plan, code=code, output=output, review=review)
        answer_questions_reply, answer_questions_history = self.llm.generate(input, answer_questions_history, max_tokens=4096)
        with open(f'{state.restore_dir}/answer_questions_reply.txt', 'w') as f:
            f.write(answer_questions_reply)

        input = PROMPT_SUMMARIZER_REORGANIZE_ANSWERS
        reorganize_answers_reply, answer_questions_history = self.llm.generate(input, answer_questions_history, max_tokens=4096)
        report = self._parse_markdown(reorganize_answers_reply)
        with open(f'{state.restore_dir}/report.txt', 'w') as f:
            f.write(report)

        # 保存history
        with open(f'{state.restore_dir}/{self.role}_history.json', 'w') as f:
            json.dump(history, f, indent=4)

        print(f"State {state.phase} - Agent {self.role} finishes working.")
        return {self.role: {"history": history, "report": report}}
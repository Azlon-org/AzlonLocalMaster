import os
import sys
from typing import Dict, Any
import pdb
import json

sys.path.append('..')
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from LLM import LLM
from State import State
from prompt import AGENT_ROLE_TEMPLATE, PROMPT_SUMMARIZER_UNDERSTAND_BACKGROUND, PROMPT_SUMMARIZER_TASK_UNDERSTAND_BACKGROUND
from prompt import PROMPT_REVIEWER_ROUND1, PROMPT_REVIEWER_ROUND2_EACH_AGENT
from utils import read_file, PREFIX_MULTI_AGENTS

class Agent:
    def __init__(self, role: str, description: str, model: str, type: str):
        self.role = role
        self.description = description
        self.llm = LLM(model, type)
        print(f'Agent {self.role} is created.')

    def action(self, state: State) -> Dict[str, Any]:
        pdb.set_trace()
        print(f"State {state.phase} - Agent {self.role} is executing.")
        role_prompt = AGENT_ROLE_TEMPLATE.format(agent_role=self.role)
        return self._execute(state, role_prompt)

    def _execute(self, state: State, role_prompt: str) -> Dict[str, Any]:
        raise NotImplementedError("Subclasses should implement this!")

class Summarizer(Agent):
    def __init__(self, model: str, type: str):  
        super().__init__(
            role="summarizer",
            description="You are good at summarizing information and outputting it in JSON format.",
            model=model,
            type=type
        )

    def _execute(self, state: State, role_prompt: str) -> Dict[str, Any]:
        # 实现总结功能
        # Understand Background 读取overview.txt，生成competition_info.txt
        if state.phase == "Understand Background":
            path_to_overview = f'{PREFIX_MULTI_AGENTS}/competition/{state.competition}/overview.txt'
            overview = read_file(path_to_overview)
            history = []
            history.append({"role": "system", "content": f"{role_prompt} {self.description}"})
            round = 0
            # pdb.set_trace()
            while True:
                if round == 0:
                    task = PROMPT_SUMMARIZER_TASK_UNDERSTAND_BACKGROUND
                    input = PROMPT_SUMMARIZER_UNDERSTAND_BACKGROUND.format(steps_in_context=state.context, task=task)
                elif round == 1:
                    # 获取overview
                    input = f"\n#############\n# OVERVIEW #\n{overview}"
                elif round == 2:
                    break
                reply, history = self.llm.generate(input, history, max_tokens=4096)
                round += 1
            result = reply
            # summary = reply.split('```json')[1].split('```')[0].strip()
            summary = json.loads(reply.strip())['final_answer']
            # pdb.set_trace()
            with open(f'{PREFIX_MULTI_AGENTS}/competition/{state.competition}/competition_info.txt', 'w') as f:
                f.write(json.dumps(summary, indent=4))
            input_used_in_review = overview

        print(f"State {state.phase} - Agent {self.role} finishes working.")
        return {self.role: {"history": history, "role": self.role, "description": self.description, "task": task, "input": input_used_in_review, "result": result}}

class Planner(Agent):
    def __init__(self, model: str):  
        super().__init__(
            role="planner",
            description="You are good at planning tasks and creating roadmaps.",
            model=model
        )

    def _execute(self, state: State, role_prompt: str) -> Dict[str, Any]:
        # 实现规划功能
        return {self.role: "plan"}

class Developer(Agent):
    def __init__(self, model: str, type: str):  
        super().__init__(
            role="developer",
            description="You are skilled at writing and implementing code.",
            model=model,
            type=type
        )

    def _execute(self, state: State, role_prompt: str) -> Dict[str, Any]:
        # 实现开发功能
        return {self.role: "develop"}

class Debugger(Agent):
    def __init__(self, model: str, type: str):  
        super().__init__(
            role="debugger",
            description="You are expert at finding and fixing bugs in code.",
            model=model,
            type=type
        )

    def _execute(self, state: State, role_prompt: str) -> Dict[str, Any]:
        # 实现调试功能
        return {self.role: "debug"}

class Reviewer(Agent):
    def __init__(self, model: str, type: str):  
        super().__init__(
            role="reviewer",
            description="You are skilled at assessing the performance of one or more agents in completing a given task. Provide detailed scores for their performance and offer constructive suggestions to optimize their results.",
            model=model,
            type=type
        )

    def _generate_prompt_round2(self, state: State) -> str:
        prompt_round2 = ""
        for each_agent_memory in state.memory.values():
            role = each_agent_memory["role"]
            description = each_agent_memory["description"]
            task = each_agent_memory["task"]
            input = each_agent_memory["input"]
            result = each_agent_memory["result"]
            prompt_round2 += PROMPT_REVIEWER_ROUND2_EACH_AGENT.format(role=role.upper(), description=description, task=task, input=input, result=result)
        
        return prompt_round2
    
    def _execute(self, state: State, role_prompt: str) -> Dict[str, Any]:
        # 实现评价功能
        # 第二轮输入：state的memory中过去每个agent的role_description, task, input, result
        prompt_round2 = self._generate_prompt_round2(state)
        history = []
        history.append({"role": "system", "content": f"{role_prompt} {self.description}"})
        round = 0
        while True:
            if round == 0:
                input = PROMPT_REVIEWER_ROUND1.format(steps_in_context=state.context, step_name=state.phase)
            elif round == 1:
                input = prompt_round2
            elif round == 2:
                break
            reply, history = self.llm.generate(input, history, max_tokens=4096)
            round += 1
        result = reply
        review = json.loads(reply.strip())["final_answer"]
        final_score = review["final_score"]
        final_suggestion = review["final_suggestion"]
        pdb.set_trace()

        print(f"State {state.phase} - Agent {self.role} finishes working.")
        return {self.role: {"history": history, "score": final_score, "suggestion": final_suggestion, "result": result}}

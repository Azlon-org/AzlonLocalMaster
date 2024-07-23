import os
import sys
from typing import Dict, Any

sys.path.append('..')
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from LLM import LLM
from State import State
from prompt import AGENT_ROLE_TEMPLATE

class Agent:
    def __init__(self, role: str, description: str, model: str):
        self.role = role
        self.description = description
        self.llm = LLM(model)
        print(f'Agent {self.role} is created.')

    def step(self, state: State) -> Dict[str, Any]:
        role_prompt = AGENT_ROLE_TEMPLATE.format(self.role)
        return self._execute(state, role_prompt)

    def _execute(self, state: State, role_prompt: str) -> Dict[str, Any]:
        raise NotImplementedError("Subclasses should implement this!")

class Summarizer(Agent):
    def __init__(self, model: str):  
        super().__init__(
            role="summarizer",
            description="You are good at summarizing the information in a file and outputting it in JSON format.",
            model=model
        )

    def _execute(self, state: State, role_prompt: str) -> Dict[str, Any]:
        # 实现总结功能
        history = []
        history.append({"role": "system", "content": f"{role_prompt} {self.description}"})
        round = 2
        
        return {self.role: "summary"}

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
    def __init__(self, model: str):  
        super().__init__(
            role="developer",
            description="You are skilled at writing and implementing code.",
            model=model
        )

    def _execute(self, state: State, role_prompt: str) -> Dict[str, Any]:
        # 实现开发功能
        return {self.role: "develop"}

class Debugger(Agent):
    def __init__(self, model: str):  
        super().__init__(
            role="debugger",
            description="You are expert at finding and fixing bugs in code.",
            model=model
        )

    def _execute(self, state: State, role_prompt: str) -> Dict[str, Any]:
        # 实现调试功能
        return {self.role: "debug"}

class Reviewer(Agent):
    def __init__(self, model: str):  
        super().__init__(
            role="reviewer",
            description="You are skilled at reviewing and providing feedback on code and documents.",
            model=model
        )

    def _execute(self, state: State, role_prompt: str) -> Dict[str, Any]:
        # 实现评价功能
        return {self.role: "review"}

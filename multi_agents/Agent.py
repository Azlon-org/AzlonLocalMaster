import os
import sys
from typing import Dict, Any
import pdb
import json

sys.path.append('..')
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from LLM import LLM
from State import State
from prompt import REORGANIZE_REPLY
from prompt import AGENT_ROLE_TEMPLATE, PROMPT_SUMMARIZER_UNDERSTAND_BACKGROUND, PROMPT_SUMMARIZER_TASK_UNDERSTAND_BACKGROUND
from prompt import PROMPT_EACH_EXPERIENCE_WITH_SUGGESTION, PROMPT_SUMMARIZER_UNDERSTAND_BACKGROUND_WITH_EXPERIENCE
from prompt import PROMPT_PLANNER_TASK, PROMPT_PLANNER
from prompt import PROMPT_DEVELOPER_TASK, PROMPT_DEVELOPER_CONSTRAINTS, PROMPT_DEVELOPER
from prompt import PROMPT_REVIEWER_ROUND0, PROMPT_REVIEWER_ROUND1_EACH_AGENT
from utils import read_file, PREFIX_MULTI_AGENTS, load_config

class Agent:
    def __init__(self, role: str, description: str, model: str, type: str):
        self.role = role
        self.description = description
        self.llm = LLM(model, type)
        print(f'Agent {self.role} is created.')

    def _gather_experience_with_suggestion(self, state: State) -> str:
        experience_with_suggestion = ""
        for i, each_state_memory in enumerate(state.memory):
            act_agent_memory = each_state_memory.get(self.role, {}) # 获取过去state中当前agent的memory
            result = act_agent_memory.get("result", "")
            reviewer_memory = each_state_memory.get("reviewer", {}) # 获取过去state中reviewer的memory
            suggestion = reviewer_memory.get("suggestion", "")
            score = reviewer_memory.get("score", 3)
            experience_with_suggestion += PROMPT_EACH_EXPERIENCE_WITH_SUGGESTION.format(index=i, experience=result, suggestion=suggestion, score=score)
        return experience_with_suggestion

    def _parse_json(self, raw_reply: str) -> Dict[str, Any]:
        try:
            reply = json.loads(raw_reply.strip())
        except Exception as e:
            print(f"Error in json loads reply: {e}")
            print(f"raw_reply: \n{raw_reply}")
            try:
                reply_str = raw_reply.split('```json')[1].split('```')[0].strip()
                reply = json.loads(reply_str)
            except Exception as e:
                print(f"Error in json loads reply_str: {e}")
                json_reply, _ = self.llm.generate(REORGANIZE_REPLY.format(information=raw_reply), history=[], max_tokens=4096)
                try:
                    reply = json_reply.split('```json')[1].split('```')[0].strip()
                    reply = json.loads(reply)
                except Exception as e:
                    print(f"Error in json loads json_reply: {e}")
                    reply = {}
        return reply

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
            round = 0
            if len(state.memory) == 1: # 如果之前没有memory，说明是第一次执行
                history.append({"role": "system", "content": f"{role_prompt} {self.description}"})
                # pdb.set_trace()
                while True:
                    if round == 0:
                        task = PROMPT_SUMMARIZER_TASK_UNDERSTAND_BACKGROUND
                        input = PROMPT_SUMMARIZER_UNDERSTAND_BACKGROUND.format(steps_in_context=state.context, task=task)
                    elif round == 1: input = f"\n#############\n# OVERVIEW #\n{overview}"
                    elif round == 2: break
                    raw_reply, history = self.llm.generate(input, history, max_tokens=4096)
                    round += 1
            else: # 如果之前有memory，拼接之前memory中summarizer的结果作为experience
                self.description = "You are good at summarizing information and outputting it in JSON format. " \
                                "You have advanced reasoning abilities and can improve your answers through reflection."
                experience_with_suggestion = self._gather_experience_with_suggestion(state)
                history.append({"role": "system", "content": f"{role_prompt} {self.description}"})
                while True:
                    if round == 0:
                        task = PROMPT_SUMMARIZER_TASK_UNDERSTAND_BACKGROUND
                        input = PROMPT_SUMMARIZER_UNDERSTAND_BACKGROUND_WITH_EXPERIENCE.format(steps_in_context=state.context, task=task, experience_with_suggestion=experience_with_suggestion)
                    elif round == 1: input = f"\n#############\n# OVERVIEW #\n{overview}"
                    elif round == 2: break
                    raw_reply, history = self.llm.generate(input, history, max_tokens=4096)
                    round += 1
            result = raw_reply
            reply = self._parse_json(raw_reply)
            summary = reply["final_answer"]
            with open(f'{state.competition_dir}/competition_info.json', 'w') as f:
                json.dump(summary, f, indent=4)
            with open(f'{state.restore_dir}/{self.role}_reply.txt', 'w') as f:
                f.write(raw_reply)
            input_used_in_review = overview

        print(f"State {state.phase} - Agent {self.role} finishes working.")
        return {self.role: {"history": history, "role": self.role, "description": self.description, "task": task, "input": input_used_in_review, "summary": summary, "result": result}}

class Planner(Agent):
    def __init__(self, model: str, type: str):  
        super().__init__(
            role="planner",
            description="You are good at planning tasks and creating roadmaps.",
            model=model,
            type=type
        )

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
                    input = PROMPT_PLANNER.format(steps_in_context=state.context, step_name=state.phase, competition_info=competition_info, task=task)
                elif round == 1:
                    break
                raw_reply, history = self.llm.generate(input, history, max_tokens=4096)
                round += 1
        else:
            pass
        result = raw_reply
        reply = self._parse_json(raw_reply)
        plan = reply["final_answer"]
        # pdb.set_trace()
        with open(f'{state.restore_dir}/plan.json', 'w') as f:
            json.dump(plan, f, indent=4) # 保存规划结果
        with open(f'{state.restore_dir}/{self.role}_reply.txt', 'w') as f:
            f.write(raw_reply)

        print(f"State {state.phase} - Agent {self.role} finishes working.")
        return {self.role: {"history": history, "role": self.role, "description": self.description, "task": task, "plan": plan, "result": result}}

class Developer(Agent):
    def __init__(self, model: str, type: str):  
        super().__init__(
            role="developer",
            description="You are skilled at writing and implementing code according to plan.",
            model=model,
            type=type
        )

    def _generate_prompt_round1(self, state: State) -> str:
        prompt_round1 = ""
        if state.phase in ["Preliminary Exploratory Data Analysis", "Data Cleaning"]:
            train_data = read_file(f'{state.competition_dir}/train.csv')
            sample_train_data = train_data[:11]
            test_data = read_file(f'{state.competition_dir}/test.csv')
            sample_test_data = test_data[:11]
            prompt_round1 = f"\n#############\n# TRAIN DATA WITH FEATURES #\n{sample_train_data}\n\n#############\n# TEST DATA WITH FEATURES #\n{sample_test_data}"
        elif state.phase in ["In-depth Exploratory Data Analysis", "Feature Engineering"]:
            pass
        elif state.phase in ["Model Building, Validation, and Prediction"]:
            pass

        return prompt_round1

    def _execute(self, state: State, role_prompt: str) -> Dict[str, Any]:
        # 实现开发功能
        history = []
        round = 0
        restore_path = state.restore_dir
        competition_path = state.competition_dir
        task = PROMPT_DEVELOPER_TASK
        constraints = PROMPT_DEVELOPER_CONSTRAINTS.format(restore_path=restore_path, competition_path=competition_path, step_name=state.phase)
        with open(f'{state.competition_dir}/competition_info.json', 'r') as f:
            competition_info = json.load(f)
        plan = state.memory[-1]["planner"]["plan"]
        if len(state.memory) == 1: # 如果之前没有memory，说明是第一次执行
            history.append({"role": "system", "content": f"{role_prompt} {self.description}"})
            while True:
                if round == 0:
                    input = PROMPT_DEVELOPER.format(steps_in_context=state.context, step_name=state.phase, competition_info=competition_info, plan=plan, constraints=constraints, task=task)
                elif round == 1:
                    prompt_round1 = self._generate_prompt_round1(state)
                    input = prompt_round1
                elif round == 2:
                    break
                raw_reply, history = self.llm.generate(input, history, max_tokens=4096)
                round += 1
        else:
            pass
        with open(f'{state.restore_dir}/{self.role}_reply.txt', 'w') as f:
            f.write(raw_reply)
        return {}

class Debugger(Agent):
    def __init__(self, model: str, type: str):  
        super().__init__(
            role="debugger",
            description="You are expert at fixing bugs in code.",
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

    def _generate_prompt_round1(self, state: State) -> str:
        prompt_round1 = ""
        for each_agent_memory in state.memory[-1].values(): # 取当前state的memory
            role = each_agent_memory["role"]
            description = each_agent_memory["description"]
            task = each_agent_memory["task"]
            input = each_agent_memory["input"]
            result = each_agent_memory["result"]
            prompt_round1 += PROMPT_REVIEWER_ROUND1_EACH_AGENT.format(role=role.upper(), description=description, task=task, input=input, result=result)
        
        return prompt_round1
    
    def _execute(self, state: State, role_prompt: str) -> Dict[str, Any]:
        # 实现评价功能
        # 第二轮输入：state的memory中过去每个agent的role_description, task, input, result
        prompt_round1 = self._generate_prompt_round1(state)
        history = []
        history.append({"role": "system", "content": f"{role_prompt} {self.description}"})
        round = 0
        while True:
            if round == 0:
                input = PROMPT_REVIEWER_ROUND0.format(steps_in_context=state.context, step_name=state.phase)
            elif round == 1:
                input = prompt_round1
            elif round == 2:
                break
            raw_reply, history = self.llm.generate(input, history, max_tokens=4096)
            round += 1
        result = raw_reply
        reply = self._parse_json(raw_reply)
        review = reply["final_answer"]
        final_score = review["final_score"]
        final_suggestion = review["final_suggestion"]
        # pdb.set_trace()
        with open(f'{state.restore_dir}/review.json', 'w') as f:
            json.dump(review, f, indent=4)
        with open(f'{state.restore_dir}/{self.role}_reply.txt', 'w') as f:
            f.write(raw_reply)

        print(f"State {state.phase} - Agent {self.role} finishes working.")
        return {self.role: {"history": history, "score": final_score, "suggestion": final_suggestion, "result": result}}

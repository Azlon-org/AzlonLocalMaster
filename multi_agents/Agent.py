import os
import sys
from typing import Dict, List, Tuple, Any
import pdb
import json
import re
import copy
import shutil
import subprocess

sys.path.append('..')
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from LLM import LLM
from State import State
from prompt import REORGANIZE_REPLY
from prompt import AGENT_ROLE_TEMPLATE, PROMPT_READER, PROMPT_READER_TASK
from prompt import PROMPT_EACH_EXPERIENCE_WITH_SUGGESTION, PROMPT_READER_WITH_EXPERIENCE
from prompt import PROMPT_PLANNER_TASK, PROMPT_PLANNER
from prompt import PROMPT_DEVELOPER_TASK, PROMPT_DEVELOPER_CONSTRAINTS, PROMPT_DEVELOPER, PROMPT_DEVELOPER_DEBUG
from prompt import PROMPT_REVIEWER_ROUND0, PROMPT_REVIEWER_ROUND1_EACH_AGENT
from prompt import PROMPT_SUMMARIZER_ROUND0, PROMPT_SUMMARIZER_ROUND2_RESPONSE_FORMAT
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
            suggestion = reviewer_memory.get("final_suggestion", "").get(f"agent_{self.role}", "")
            score = reviewer_memory.get("final_score", 3).get(f"agent_{self.role}", 3)
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
                assert 'final_answer' in reply # 保证是正确的json格式
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
        summary = reply["final_answer"]
        with open(f'{state.competition_dir}/competition_info.json', 'w') as f:
            json.dump(summary, f, indent=4)
        with open(f'{state.restore_dir}/{self.role}_reply.txt', 'w') as f:
            f.write(raw_reply)
        input_used_in_review = f"   <overview>\n{overview}\n    </overview>"

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

    def _get_previous_plan(self, state: State) -> Dict[str, Any]:
        previous_phase = state.get_previous_phase()
        previous_dir_name = state.phase_to_directory[previous_phase]
        path_to_previous_plan = f'{state.competition_dir}/{previous_dir_name}/plan.json'
        if os.path.exists(path_to_previous_plan):
            with open(path_to_previous_plan, 'r') as f:
                previous_plan = json.load(f)
        else:
            previous_plan = "There is no plan in the previous step."
        return previous_plan

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
                    input = f"\n#############\n# PREVIOUS PLAN #\n{self._get_previous_plan(state)}"
                elif round == 2:
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

        input_used_in_review = f"   <competition_info>\n{competition_info}\n    </competition_info>"

        print(f"State {state.phase} - Agent {self.role} finishes working.")
        return {self.role: {"history": history, "role": self.role, "description": self.description, "task": task, "input": input_used_in_review, "plan": plan, "result": result}}

class Developer(Agent):
    def __init__(self, model: str, type: str):  
        super().__init__(
            role="developer",
            description="You are skilled at writing and implementing code according to plan.",
            model=model,
            type=type
        )

    def _is_previous_code(self, state: State) -> Tuple[bool, str, str]:
        previous_phase = state.get_previous_phase()
        previous_dir_name = state.phase_to_directory[previous_phase]
        path_to_previous_code = f'{state.competition_dir}/{previous_dir_name}/{previous_dir_name}_code.py'
        path_to_previous_run_code = f'{state.competition_dir}/{previous_dir_name}/{previous_dir_name}_run_code.py'
        return os.path.exists(path_to_previous_code), path_to_previous_code, path_to_previous_run_code

    def _delete_output_in_code(self, state: State, previous_code) -> str:
        previous_run_code = copy.deepcopy(previous_code)
        for i, line in enumerate(previous_run_code):
            if line.strip().startswith('for') and previous_run_code[i+1].strip().startswith('print'):
                previous_run_code[i] = ''
            elif line.strip().startswith('print'):
                previous_run_code[i] = ''
            elif line.strip().startswith('plt.show'):
                previous_run_code[i] = ''
            elif line.strip().startswith('plt.save'):
                previous_run_code[i] = ''
        # 删除空行
        previous_run_code = [line for line in previous_run_code if line != '']
        return previous_run_code

    def _generate_code_file(self, state: State, raw_reply) -> Tuple[str, str]:
        is_previous_code, path_to_previous_code, _ = self._is_previous_code(state)
        if is_previous_code:
            with open(path_to_previous_code, 'r', encoding='utf-8') as f_1:
                previous_code = f_1.readlines()
                previous_code = previous_code[:-2] # 删除最后两行
                previous_code = previous_code[1:] # 删除第一行
            previous_run_code = self._delete_output_in_code(state, previous_code) # 删除output
        else:
            previous_code = []
            previous_run_code = []
        # code with output
        path_to_code = f'{state.restore_dir}/{state.dir_name}_code.py'
        path_to_run_code = f'{state.restore_dir}/{state.dir_name}_run_code.py'

        # Extract code from the file
        pattern = r"```python(.*?)```\n"
        matches = re.findall(pattern, raw_reply, re.DOTALL)
        code_lines = []
        # pdb.set_trace()
        for match in matches:
            code_lines.extend(match.split('\n'))
        
        # Enclose the code in a function
        code_lines = [f"    {line}\n" for line in code_lines]
        code_with_output_lines = ["def generated_code_function():\n"] + previous_code + code_lines
        run_code_lines = ["def generated_code_function():\n"] + previous_run_code + code_lines

        # Write the code to a python file
        with open(path_to_code, 'w', encoding='utf-8') as f_w:
            f_w.write("".join(code_with_output_lines))
            f_w.write('\n\nif __name__ == "__main__":\n    generated_code_function()')
        # Write the run code to a python file
        with open(path_to_run_code, 'w', encoding='utf-8') as f_w:
            f_w.write("".join(run_code_lines))
            f_w.write('\n\nif __name__ == "__main__":\n    generated_code_function()')
        
        return path_to_code, path_to_run_code

    def _run_code(self, state: State, path_to_run_code: str) -> str:
        # Delete previous images files
        if 'eda' in state.restore_dir:
            images_dir = f'{state.restore_dir}/images/'
            for filename in os.listdir(images_dir):
                image_path = os.path.join(images_dir, filename)
                try:
                    if os.path.isfile(image_path) or os.path.islink(image_path):
                        os.remove(image_path)  # Delete file
                    elif os.path.isdir(image_path):
                        shutil.rmtree(image_path)  # Delete directory
                except Exception as e:
                    print(f"Failed to delete {image_path}. Reason: {e}")
            print(f"All files in directory '{images_dir}' have been deleted successfully.")

        # Run the code
        result = subprocess.run(['python3', path_to_run_code], capture_output=True, text=True)
        error_flag = False
        path_to_error = f'{state.restore_dir}/{state.dir_name}_error.txt'
        path_to_output = f'{state.restore_dir}/{state.dir_name}_output.txt'
        if result.stderr:
            print("Error encountered during code execution.")
            with open(path_to_error, 'w') as f:
                f.write(result.stderr)
            error_flag = True
        else:
            print("Code executed successfully without errors.")
            try:
                # Delete error file.
                os.remove(path_to_error)
                print(f"File '{path_to_error}' has been deleted successfully.")
            except FileNotFoundError:
                print(f"File '{path_to_error}' doesn't exist, you don't need to delete it.")

        # Write the output to a file
        with open(path_to_output, 'w') as file:
            file.write(result.stdout)

        return error_flag
    
    def _debug_code(self, state: State, debug_history: list, raw_reply: str) -> str:
        is_previous_code, path_to_previous_code, _ = self._is_previous_code(state)
        if is_previous_code:
            with open(path_to_previous_code, 'r', encoding='utf-8') as f_1:
                previous_code = f_1.readlines()
            # 放在prompt里的previous code要做处理
            previous_code = previous_code[:-2] # 删除最后两行
            previous_code = previous_code[1:] # 删除第一行
            for i, line in enumerate(previous_code):
                # 删除每行第一个'\t'
                if line.startswith('\t'):
                    previous_code[i] = line[1:]
            previous_code = "\n".join(previous_code)
        else:
            previous_code = "There is no code file in the previous phase."
        # Extract code from the file
        pattern = r"```python(.*?)```\n"
        matches = re.findall(pattern, raw_reply, re.DOTALL)
        code_lines = []
        for match in matches:
            code_lines.extend(match.split('\n'))
        wrong_code = "\n".join(code_lines) # 这里的code是有错误的
        # 读取error和output
        path_to_error = f'{state.restore_dir}/{state.dir_name}_error.txt'
        path_to_output = f'{state.restore_dir}/{state.dir_name}_output.txt'
        error_messages = read_file(path_to_error)
        output_messages = read_file(path_to_output)
        input = PROMPT_DEVELOPER_DEBUG.format(previous_code=previous_code, wrong_code=wrong_code, output_messages=output_messages, error_messages=error_messages)

        reply, debug_history = self.llm.generate(input, debug_history, max_tokens=4096)
        return reply, debug_history

    def _generate_prompt_round1(self, state: State) -> str:
        prompt_round1 = ""
        # 读取上一个阶段的code
        is_previous_code, path_to_previous_code, _ = self._is_previous_code(state)
        if is_previous_code:
            with open(path_to_previous_code, 'r', encoding='utf-8') as f_1:
                previous_code = f_1.readlines()
            # 放在prompt里的previous code要做处理
            previous_code = previous_code[:-2] # 删除最后两行
            previous_code = previous_code[1:] # 删除第一行
            for i, line in enumerate(previous_code):
                # 删除每行第一个'\t'
                if line.startswith('\t'):
                    previous_code[i] = line[1:]
            previous_code = "\n".join(previous_code)
        else:
            previous_code = "There is no code file in the previous phase."
        prompt_round1 += f"\n#############\n# CODE FROM PREVIOUS PHASE #\n{previous_code}"

        # 读取train.csv和test.csv
        if state.phase in ["Preliminary Exploratory Data Analysis", "Data Cleaning"]:
            train_data = read_file(f'{state.competition_dir}/train.csv')
            sample_train_data = train_data[:11]
            test_data = read_file(f'{state.competition_dir}/test.csv')
            sample_test_data = test_data[:11]
            prompt_round1 += f"\n#############\n# TRAIN DATA WITH FEATURES #\n{sample_train_data}\n\n#############\n# TEST DATA WITH FEATURES #\n{sample_test_data}"
        elif state.phase in ["In-depth Exploratory Data Analysis", "Feature Engineering"]:
            pass
        elif state.phase in ["Model Building, Validation, and Prediction"]:
            pass

        return prompt_round1

    def _execute(self, state: State, role_prompt: str) -> Dict[str, Any]:
        # 实现开发和调试功能
        history = []
        debug_history = []
        round = 0
        max_tries = 5
        restore_path = state.restore_dir
        competition_path = state.competition_dir
        task = PROMPT_DEVELOPER_TASK
        constraints = PROMPT_DEVELOPER_CONSTRAINTS.format(restore_path=restore_path, competition_path=competition_path, step_name=state.phase)
        with open(f'{state.competition_dir}/competition_info.json', 'r') as f:
            competition_info = json.load(f)
        plan = state.memory[-1]["planner"]["plan"]
        if len(state.memory) == 1: # 如果之前没有memory，说明是第一次执行
            history.append({"role": "system", "content": f"{role_prompt} {self.description}"})
            while round <= 1+max_tries:
                if round == 0:
                    input = PROMPT_DEVELOPER.format(steps_in_context=state.context, step_name=state.phase, message=state.message, competition_info=competition_info, plan=plan, constraints=constraints, task=task)
                    raw_reply, history = self.llm.generate(input, history, max_tokens=4096)
                elif round == 1:
                    prompt_round1 = self._generate_prompt_round1(state)
                    input = prompt_round1
                    raw_reply, history = self.llm.generate(input, history, max_tokens=4096)
                    with open(f'{state.restore_dir}/{self.role}_reply.txt', 'w') as f:
                        f.write(raw_reply)
                elif round >= 2:
                    print(f"The {round-1}th try.")
                    path_to_code, path_to_run_code = self._generate_code_file(state, raw_reply)
                    error_flag = self._run_code(state, path_to_run_code)
                    if error_flag:
                        raw_reply, debug_history = self._debug_code(state, debug_history, raw_reply) # 这里我先把develop和debug解耦 后续便于加上retrieve history然后debug
                    else:
                        break
                round += 1
        else:
            pass

        with open(f'{state.restore_dir}/debug_history.json', 'w') as f:
            json.dump(debug_history, f, indent=4)

        if round <= 1+max_tries:
            print(f"State {state.phase} - Agent {self.role} finishes working.")
        else:
            print(f"State {state.phase} - Agent {self.role} finishes working with error.")

        input_used_in_review = f"   <competition_info>\n{competition_info}\n    </competition_info>\n   <plan>\n{plan}\n    </plan>"
        return {self.role: {"history": history, "role": self.role, "description": self.description, "task": task, "input": input_used_in_review, "result": raw_reply}}
    

class Reviewer(Agent):
    def __init__(self, model: str, type: str):  
        super().__init__(
            role="reviewer",
            description="You are skilled at assessing the performance of one or more agents in completing a given task. Provide detailed scores for their performance and offer constructive suggestions to optimize their results.",
            model=model,
            type=type
        )

    def _merge_dicts(self, dicts: List[Dict[str, Any]]) -> Dict[str, Any]:
        merged_dict = {"final_suggestion": {}, "final_score": {}}
        for d in dicts:
            for key in d["final_suggestion"]:
                merged_dict["final_suggestion"][key] = d["final_suggestion"][key]
            for key in d["final_score"]:
                merged_dict["final_score"][key] = d["final_score"][key]
        return merged_dict

    def _generate_prompt_for_agents(self, state: State) -> List[str]:
        prompt_for_agents = []
        evaluated_agents = list(state.memory[-1].keys()) # 获取过去state的memory中的所有agent
        print(f"Evaluating agents: {evaluated_agents}")
        for each_agent_memory in state.memory[-1].values(): # 取当前state的memory
            role = each_agent_memory["role"]
            description = each_agent_memory["description"]
            task = each_agent_memory["task"]
            input = each_agent_memory["input"]
            result = each_agent_memory["result"]
            prompt_for_agent = PROMPT_REVIEWER_ROUND1_EACH_AGENT.format(role=role.upper(), description=description, task=task, input=input, result=result)
            prompt_for_agents.append(prompt_for_agent)
        return prompt_for_agents
    
    def _execute(self, state: State, role_prompt: str) -> Dict[str, Any]:
        # 实现评价功能
        # 第二轮输入：state的memory中过去每个agent的role_description, task, input, result
        prompt_for_agents = self._generate_prompt_for_agents(state)
        history = []
        all_raw_reply = []
        history.append({"role": "system", "content": f"{role_prompt} {self.description}"})
        round = 0
        while round <= len(prompt_for_agents):
            if round == 0:
                input = PROMPT_REVIEWER_ROUND0.format(steps_in_context=state.context, step_name=state.phase)
            elif round >= 1:
                input = prompt_for_agents[round-1]
            raw_reply, history = self.llm.generate(input, history, max_tokens=4096)
            if round >= 1:
                all_raw_reply.append(raw_reply)
            round += 1

        all_reply = []
        # pdb.set_trace()
        for each_raw_reply in all_raw_reply:
            reply = self._parse_json(each_raw_reply)
            all_reply.append(reply['final_answer'])

        review = self._merge_dicts(all_reply)
        final_score = review['final_score']
        final_suggestion = review['final_suggestion']
        # pdb.set_trace()
        with open(f'{state.restore_dir}/review.json', 'w') as f:
            json.dump(review, f, indent=4)
        with open(f'{state.restore_dir}/{self.role}_reply.txt', 'w') as f:
            f.write("\n\n\n".join(all_raw_reply))

        print(f"State {state.phase} - Agent {self.role} finishes working.")
        return {self.role: {"history": history, "score": final_score, "suggestion": final_suggestion, "result": review}}


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
        if len(state.memory) == 1: # 如果之前没有memory，说明是第一次执行
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
        with open(f'{state.restore_dir}/{self.role}_reply.txt', 'w') as f:
            f.write(report+'\n\n\n'+raw_message)

        print(f"State {state.phase} - Agent {self.role} finishes working.")
        return {self.role: {"history": history, "report": report, "message": message}}
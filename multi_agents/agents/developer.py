from typing import Dict, Any, Tuple
import json
import re
import logging
import sys 
import os
import copy
import subprocess
import shutil
import pdb

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

sys.path.append('..')
sys.path.append('../..')
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from agent_base import Agent
from utils import read_file, PREFIX_MULTI_AGENTS
from llm import LLM
from state import State
from prompts.prompt_base import *
from prompts.prompt_developer import *
from tools import *

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
        previous_run_code = copy.deepcopy(previous_code) # 深拷贝 防止修改原始数据
        keywords = ('sns.', '.plot', '.hist', '.plt')

        # 第一次扫描：识别 for 循环，整段替换
        for_loop_list = []
        in_for_loop = False
        # pdb.set_trace()
        for i, line in enumerate(previous_run_code):
            if line.startswith('    for'):
                tmp_loop = []
                indent = line[:len(line) - len(line.lstrip())]  # 获取缩进部分
                tmp_loop.append(i) # 记录for循环的起始行
                # print(i)
                in_for_loop = True
            elif in_for_loop and line.startswith(indent) and not line.startswith('    '+indent) and len(line.strip()) > 0:
                tmp_loop.append(i) # 记录for循环的终止行
                # print(i)
                in_for_loop = False
                for_loop_list.append(tmp_loop)

        # if len(for_loop_list) > 0:
        #     logging.info(f"for_loop_list: {for_loop_list}")

        # 逆序替换 for 循环为 '    pass'
        for start, end in for_loop_list[::-1]:
            loop_code = "\n".join(previous_run_code[start:end])
            if any(keyword in loop_code for keyword in keywords):  # 如果 for 循环中包含关键字
                previous_run_code[start:end] = ['    pass\n']  # 替换相应行

        # 第二次扫描：替换 print 和 plt.show / plt.save 行，保留缩进
        # pdb.set_trace()
        start_signs = ('print', 'plt')
        for i, line in enumerate(previous_run_code):
            stripped_line = line.lstrip()
            if stripped_line.startswith(start_signs) or any(keyword in stripped_line for keyword in keywords):
                indent = line[:len(line) - len(stripped_line)]  # 获取缩进部分
                previous_run_code[i] = indent + 'pass\n'
        
        # 第三次扫描：合并连续的 pass 行
        new_code = []
        pass_found = False
        
        for line in previous_run_code:
            if line.strip() == 'pass':
                if not pass_found:  # 第一次遇到 pass
                    new_code.append(line)
                    pass_found = True
            else:
                new_code.append(line)
                pass_found = False
        
        return new_code

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
        with open(f'{state.restore_dir}/single_step_code.txt', 'w') as f: # 保存单步的code 用于debug
            f.write("".join(code_lines))
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
        timeout_flag = False
        error_flag = False
        path_to_error = f'{state.restore_dir}/{state.dir_name}_error.txt'
        path_to_output = f'{state.restore_dir}/{state.dir_name}_output.txt'

        # timeout
        if 'eda' in state.phase:
            timeout = 120
            timeout_info = "Your code is running out of time, please consider resource availability and reduce the number of data analysis plots drawn."
        elif 'model' in state.phase:
            timeout = 300
            timeout_info = "Your code is running out of time, please consider resource availability and try fewer models."
        else:
            timeout = 60
            timeout_info = "Your code is running out of time, please consider resource availability or other factors."
        try:
            result = subprocess.run(['python3', '-W', 'ignore', path_to_run_code], capture_output=True, text=True, timeout=timeout)
        except subprocess.TimeoutExpired:
            print("Code execution timed out.")
            with open(path_to_error, 'w') as f:
                f.write(timeout_info)
            with open(path_to_output, 'w') as f:
                f.write("")
            error_flag = True
            return error_flag
        
        # errors
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

    def _conduct_unit_test(self, state: State) -> None:
        test_tool = TestTool(memory=None, model='gpt-4o', type='api')
        not_pass_flag = False
        not_pass_tests = test_tool.execute_tests(state) # [(test1_number, test1_information), ...] 全通过返回[]
        not_pass_information = ""
        if not_pass_tests:
            not_pass_flag = True
            print("Unit tests failed.")
            for test_number, test_information in not_pass_tests:
                print(f"Test {test_number}: {test_information}")
                not_pass_information += "\n## TEST CASE NUMBER {test_number} ##\n{test_information}"
        else:
            not_pass_information = "All unit tests passed."
        return not_pass_flag, not_pass_information

    def _debug_code(self, state: State, error_flag: bool, not_pass_flag: bool, not_pass_information: str, raw_reply: str) -> str:
        # prepare debug information, and then debug
        is_previous_code, path_to_previous_code, _ = self._is_previous_code(state)
        if is_previous_code:
            with open(path_to_previous_code, 'r', encoding='utf-8') as f_1:
                previous_code = f_1.readlines()
            # 放在prompt里的previous code要做处理
            previous_code = previous_code[:-2] # 删除最后两行
            previous_code = previous_code[1:] # 删除第一行
            for i, line in enumerate(previous_code):
                # 删除每行第一个'\t'或者是连续的四个空格
                if line.startswith('\t'):
                    previous_code[i] = line[1:]
                elif line.startswith('    '):
                    previous_code[i] = line[4:]
            previous_code = "".join(previous_code)
        else:
            previous_code = "There is no code file in the previous phase."
        # Extract code from the file
        pattern = r"```python(.*?)```"
        matches = re.findall(pattern, raw_reply, re.DOTALL)
        code_lines = []
        for match in matches:
            code_lines.extend(match.split('\n'))
        wrong_code = "\n".join(code_lines) # 这里的code是有错误的
        # 读取error和output
        path_to_error = f'{state.restore_dir}/{state.dir_name}_error.txt'
        path_to_output = f'{state.restore_dir}/{state.dir_name}_output.txt'
        if os.path.exists(path_to_error):
            error_messages = read_file(path_to_error)
        else:
            error_messages = "There is no error message in the previous phase."
        output_messages = read_file(path_to_output)

        logging.info("Start debugging the code.")
        debug_tool = DebugTool(model='gpt-4o', type='api')
        if error_flag:
            reply, single_round_debug_history = debug_tool.debug_code_with_error(state, previous_code, wrong_code, error_messages)
        elif not_pass_flag:
            reply, single_round_debug_history = debug_tool.debug_code_with_no_pass_test(state, previous_code, wrong_code, not_pass_information)

        return reply, single_round_debug_history

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
        prompt_round1 += self._read_data(state)

        return prompt_round1

    def _execute(self, state: State, role_prompt: str) -> Dict[str, Any]:
        # 实现开发和调试功能
        history = []
        debug_history = []
        test_history = []
        round = 0
        max_tries = 5
        error_flag = False
        not_pass_flag = False
        not_pass_information = ""
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
                    with open(f'{state.restore_dir}/{self.role}_first_reply.txt', 'w') as f:
                        f.write(raw_reply)
                elif round >= 2:
                    print(f"The {round-1}th try.")
                    path_to_code, path_to_run_code = self._generate_code_file(state, raw_reply)
                    error_flag = self._run_code(state, path_to_run_code)
                    if error_flag and round <= 1+max_tries:
                        # 每一轮单独debug
                        raw_reply, single_round_debug_history = self._debug_code(state, error_flag, not_pass_flag, not_pass_information, raw_reply) # 这里我先把develop和debug解耦 后续便于加上retrieve history然后debug
                        debug_history.append(copy.deepcopy(single_round_debug_history)) # 好像没必要深拷贝
                    else:
                        break
                round += 1
            
            if not error_flag:
                # 进行unit test
                test_round = 0
                while test_round < max_tries:
                    not_pass_flag, not_pass_information = self._conduct_unit_test(state)
                    if not_pass_flag:
                        raw_reply, test_history = self._debug_code(state, error_flag, not_pass_flag, not_pass_information, raw_reply)
                    else:
                        break
                    test_round += 1

        else:
            self.description = "You are skilled at writing and implementing code according to plan." \
                            "You have advanced reasoning abilities and can improve your answers through reflection."
            experience_with_suggestion = self._gather_experience_with_suggestion(state)
            history.append({"role": "system", "content": f"{role_prompt} {self.description}"})
            while round <= 2+max_tries:
                if round == 0:
                    input = PROMPT_DEVELOPER_WITH_EXPERIENCE_ROUND0.format(steps_in_context=state.context, step_name=state.phase, message=state.message, competition_info=competition_info, plan=plan, constraints=constraints, task=task, experience_with_suggestion=experience_with_suggestion)
                    raw_reply, history = self.llm.generate(input, history, max_tokens=4096)
                elif round == 1:
                    prompt_round1 = self._generate_prompt_round1(state)
                    input = prompt_round1
                    raw_reply, history = self.llm.generate(input, history, max_tokens=4096)
                    with open(f'{state.restore_dir}/{self.role}_first_mid_reply.txt', 'w') as f:
                        f.write(raw_reply)
                elif round == 2:
                    input = PROMPT_DEVELOPER_WITH_EXPERIENCE_ROUND2
                    raw_reply, history = self.llm.generate(input, history, max_tokens=4096)
                    with open(f'{state.restore_dir}/{self.role}_first_reply.txt', 'w') as f:
                        f.write(raw_reply)
                elif round >= 3:
                    print(f"The {round-2}th try.")
                    path_to_code, path_to_run_code = self._generate_code_file(state, raw_reply)
                    error_flag = self._run_code(state, path_to_run_code)
                    if error_flag and round < 2+max_tries:
                        raw_reply, single_round_debug_history = self._debug_code(state, error_flag, not_pass_flag, not_pass_information, raw_reply)
                        debug_history.append(copy.deepcopy(single_round_debug_history))
                    else:
                        break
                round += 1

            if not error_flag:
                # 进行unit test
                test_round = 0
                while test_round < max_tries:
                    not_pass_flag, not_pass_information = self._conduct_unit_test(state)
                    if not_pass_flag:
                        raw_reply, test_history = self._debug_code(state, error_flag, not_pass_flag, not_pass_information, raw_reply)
                    else:
                        break
                    test_round += 1

        # 保存history
        with open(f'{state.restore_dir}/{self.role}_history.json', 'w') as f:
            json.dump(history, f, indent=4)
        with open(f'{state.restore_dir}/debug_history.json', 'w') as f:
            json.dump(debug_history, f, indent=4)
        with open(f'{state.restore_dir}/test_history.json', 'w') as f:
            json.dump(test_history, f, indent=4)

        execution_flag = True
        if os.path.exists(f'{state.restore_dir}/{state.dir_name}_error.txt'):
            execution_flag = False
            print(f"State {state.phase} - Agent {self.role} finishes working with error.")
        else:
            print(f"State {state.phase} - Agent {self.role} finishes working.")

        input_used_in_review = f"   <competition_info>\n{competition_info}\n    </competition_info>\n   <plan>\n{plan}\n    </plan>"
        return {self.role: {"history": history, "role": self.role, "description": self.description, "task": task, "input": input_used_in_review, "result": raw_reply, "status": execution_flag}}
    
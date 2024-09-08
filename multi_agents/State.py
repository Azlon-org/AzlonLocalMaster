import os
import sys
import json
import pdb

sys.path.append('..')
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from typing import List, Dict, Any
from utils import PREFIX_MULTI_AGENTS, load_config
from prompts.prompt_base import PHASES_IN_CONTEXT_PREFIX

class State:
    def __init__(self, phase, competition, message="There is no message."):
        self.phase = phase
        self.memory = [{}]   # 用于记录State内部的信息 只存相同phase的 当前State的memory在最后一个
        self.message = message  # 来自上一个State的信息 
        self.current_step = 0  # 在State内部控制步数
        self.score = 0     # 用于记录当前State的评分
        self.finished = False
        self.agents = load_config(f'{PREFIX_MULTI_AGENTS}/config.json')['phase_to_agents'][self.phase] # 用于记录当前State的Agent
        self.competition = competition
        self.context = ""   # 用于记录当前State的context
        self.phase_to_directory = load_config(f'{PREFIX_MULTI_AGENTS}/config.json')['phase_to_directory'] # 记录每个阶段的目录
        self.phase_to_unit_tests = load_config(f'{PREFIX_MULTI_AGENTS}/config.json')['phase_to_unit_tests'] # 记录每个阶段的单元测试
        self.rulebook_parameters = load_config(f'{PREFIX_MULTI_AGENTS}/config.json')['rulebook_parameters'] # 记录每个阶段的规则手册参数
        self.restore_dir = ""   # 用于记录当前State的文件保存路径
        self.competition_dir = f'{PREFIX_MULTI_AGENTS}/competition/{self.competition}' # 用于记录当前competition的路径（import data的路径）
        self.dir_name = self.phase_to_directory[self.phase]

    def __str__(self):
        return f"State: {self.phase}, Current Step: {self.current_step}, Current Agent: {self.agents[self.current_step]}, Finished: {self.finished}"

    def make_context(self):
        self.context = PHASES_IN_CONTEXT_PREFIX.replace("# {competition_name}", self.competition)
        phases = load_config(f'{PREFIX_MULTI_AGENTS}/config.json')['phases']
        for i, phase in enumerate(phases):
            self.context += f"{i+1}. {phase}\n"
    
    def get_state_info(self):
        # if self.phase == 'Feature Engineering':
        #     state_info = f"After Data Cleaning, you already have file `cleaned_train.csv' and `cleaned_test.csv`. Do feature engineering to them to get `processed_train.csv` and `processed_test.csv`"
        # elif self.phase == 'Model Building, Validation, and Prediction':
        #     state_info = f"After Feature Engineering, you already have file `processed_train.csv` and `processed_test`.csv. Use `processed_train.csv` to train your model and predict on `processed_test.csv`."
        # else:
        #     state_info = ""
        state_info = ""
        return state_info

    def generate_rules(self):
        rules = ""
        if self.rulebook_parameters[self.phase]['status']:
            default_rules = self.rulebook_parameters[self.phase]['default_rules_with_parameters']
            rules = ""
            for key, values in default_rules.items():
                if sum(values[0]) == 0:
                    continue
                rules += f"If you need to {key}, please follow the following rules:\n"
                for i, rule in enumerate(values[1:]):
                    if values[0][i] == 1:
                        formatted_rule = rule[0].format(placeholder=rule[1])
                        rules += f"- {formatted_rule}\n"
                rules += "\n"
        else:
            rules = "There is no rule for this stage."
        with open(f'{self.restore_dir}/user_rules.txt', 'w') as f:
            f.write(rules)

        return rules

    # 创建当前State的目录
    def make_dir(self):
        path_to_dir = f'{self.competition_dir}/{self.dir_name}'
        if not os.path.exists(path_to_dir):
            os.makedirs(path_to_dir)
        if 'eda' in self.dir_name and not os.path.exists(f'{path_to_dir}/images'):
            os.makedirs(f'{path_to_dir}/images')
        self.restore_dir = path_to_dir

    def get_previous_phase(self, type: str="code"):
        phases = load_config(f'{PREFIX_MULTI_AGENTS}/config.json')['phases']
        current_phase_index = phases.index(self.phase)
        if type == 'code':
            if self.phase == 'Data Cleaning':
                previous_phase = 'Understand Background'
            elif self.phase == 'Feature Engineering':
                previous_phase = 'Data Cleaning'
            # elif self.phase == 'Model Building, Validation, and Prediction':
            #     previous_phase = 'Understand Background'
            else:
                previous_phase = phases[current_phase_index - 1]
        elif type == 'plan':
            previous_phase = phases[:current_phase_index]
        elif type == 'report':
            previous_phase = phases[current_phase_index - 1]
        else:
            raise Exception(f"Unknown type: {type}")
        return previous_phase

    def get_next_phase(self):
        phases = load_config(f'{PREFIX_MULTI_AGENTS}/config.json')['phases']
        current_phase_index = phases.index(self.phase)
        if current_phase_index < len(phases) - 1:
            next_phase = phases[current_phase_index + 1]
        else:
            next_phase = None
        return next_phase

    # 更新State内部的信息
    def update_memory(self, memory): 
        print(f"{self.agents[self.current_step]} updates internal memory in Phase: {self.phase}.")
        self.memory[-1].update(memory)

    # 存储memory
    def restore_memory(self):
        with open(f'{self.restore_dir}/memory.json', 'w') as f:
            json.dump(self.memory, f, indent=4)
        print(f"Memory in Phase: {self.phase} is restored.")

    def restore_report(self):
        report = self.memory[-1].get('summarizer', {}).get('report', '')
        if len(report) > 0:
            with open(f'{self.restore_dir}/report.txt', 'w') as f:
                f.write(report)
            print(f"Report in Phase: {self.phase} is restored.")
        else:
            print(f"No report in Phase: {self.phase} to restore.")

    def send_message(self):
        message_to_next_state = self.memory[-1].get('summarizer', {}).get('message', '')
        return message_to_next_state

    def next_step(self):
        self.current_step += 1

    def set_score(self):
        final_score = self.memory[-1]['reviewer']['score'] # 从memory中获取reviewer的评分
        total = 0.0
        for score in final_score.values():
            total += float(score)
        self.score = total / len(final_score)
        # if not self.memory[-1].get('developer', {}).get('status', True): # 如果developer执行失败, score为0
        #     self.score = 0

    def check_finished(self):
        if self.current_step == len(self.agents):
            self.finished = True
        return self.finished
import os
import sys
import json
import pdb

sys.path.append('..')
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from typing import List, Dict, Any
from utils import PREFIX_MULTI_AGENTS, load_config
from prompt import STEPS_IN_CONTEXT_TEMPLATE

class State:
    def __init__(self, phase, message="There is no message."):
        self.phase = phase
        self.memory = [{}]   # 用于记录State内部的信息 只存相同phase的 当前State的memory在最后一个
        self.message = message  # 来自上一个State的信息 
        self.current_step = 0  # 在State内部控制步数
        self.score = 0     # 用于记录当前State的评分
        self.finished = False
        self.agents = load_config(f'{PREFIX_MULTI_AGENTS}/config.json')['phase_to_agents'][self.phase] # 用于记录当前State的Agent
        self.competition = load_config(f'{PREFIX_MULTI_AGENTS}/config.json')['competition'] 
        self.context = STEPS_IN_CONTEXT_TEMPLATE.format(competition_name=self.competition.replace('_', ' '))
        self.phase_to_directory = load_config(f'{PREFIX_MULTI_AGENTS}/config.json')['phase_to_directory'] # 记录每个阶段的目录
        self.restore_dir = ""   # 用于记录当前State的文件保存路径
        self.competition_dir = f'{PREFIX_MULTI_AGENTS}/competition/{self.competition}' # 用于记录当前competition的路径（import data的路径）
        self.dir_name = self.phase_to_directory[self.phase]

    def __str__(self):
        return f"State: {self.phase}, Current Step: {self.current_step}, Current Agent: {self.agents[self.current_step]}, Finished: {self.finished}"

    # 创建当前State的目录
    def make_dir(self):
        path_to_dir = f'{self.competition_dir}/{self.dir_name}'
        if not os.path.exists(path_to_dir):
            os.makedirs(path_to_dir)
        if 'eda' in self.dir_name and not os.path.exists(f'{path_to_dir}/images'):
            os.makedirs(f'{path_to_dir}/images')
        self.restore_dir = path_to_dir

    def get_previous_phase(self, type: str="last"):
        phases = load_config(f'{PREFIX_MULTI_AGENTS}/config.json')['phases']
        current_phase_index = phases.index(self.phase)
        if type == 'last':
            previous_phase = phases[current_phase_index - 1]
        elif type == 'all':
            previous_phase = phases[:current_phase_index]
        else:
            raise Exception(f"Unknown type: {type}")
        return previous_phase

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
            with open(f'{self.restore_dir}/Report.txt', 'w') as f:
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
            total += score
        self.score = total / len(final_score)
        # if not self.memory[-1].get('developer', {}).get('status', True): # 如果developer执行失败, score为0
        #     self.score = 0

    def check_finished(self):
        if self.current_step == len(self.agents):
            self.finished = True
        return self.finished
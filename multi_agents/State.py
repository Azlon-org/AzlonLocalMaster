import os
import sys
import json

sys.path.append('..')
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from typing import List, Dict, Any
from utils import PREFIX_MULTI_AGENTS, load_config
from prompt import STEPS_IN_CONTEXT_TEMPLATE

class State:
    def __init__(self, phase, task, workflow=[], message=""):
        self.phase = phase
        self.task = task
        self.workflow = workflow
        self.memory = {}   # 用于记录State内部的信息
        self.message = message  # 用于传递不同State之间的信息 
        self.report = ""   # 用于记录当前State的总结报告
        self.current_step = 0  # 在State内部控制步数
        self.score = 0     # 用于记录当前State的评分
        self.finished = False
        self.agents = load_config(f'{PREFIX_MULTI_AGENTS}/config.json')['state_to_agents'][self.phase] # 用于记录当前State的Agent
        self.competition = load_config(f'{PREFIX_MULTI_AGENTS}/config.json')['competition'] 
        self.context = STEPS_IN_CONTEXT_TEMPLATE.format(competition_name=self.competition.replace('_', ' '))

    # 更新State内部的信息
    def update_memory(self, memory): 
        print(f"{self.agents[self.current_step]} updates internal memory in Phase: {self.phase}.")
        self.memory.update(memory)

    def restore_memory(self, memory):
        pass

    def send_message(self, message):
        self.message = message

    def get_message(self):
        return self.message

    def get_report(self):
        return self.report

    def next_step(self):
        self.current_step += 1

    def check_finished(self):
        if self.current_step == len(self.agents):
            self.finished = True
            self.score = self.memory['reviewer']['score'] # 从memory中获取reviewer的评分
        return self.finished
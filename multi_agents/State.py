import os
import sys
import json

sys.path.append('..')
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from typing import List, Dict, Any
from utils import PREFIX_MULTI_AGENTS

class State:
    def __init__(self, phase, task, agents_team, workflow=[], message=""):
        self.phase = phase
        self.task = task
        self.workflow = workflow
        self.memory = {}   # 用于记录State内部的信息
        self.message = message  # 用于传递不同State之间的信息 
        self.report = ""   # 用于记录当前State的总结报告
        self.current_step = 0  # 在State内部控制步数
        self.point = 0     # 用于记录当前State的评分
        self.finished = False
        self.agents = [agents_team[0]] if phase == 'Understand Background' else agents_team # 用于记录当前State的Agent

    def update_memory(self, memory):
        self.memory.update(memory)

    def set_message(self, message):
        self.message = message

    def get_message(self):
        return self.message

    def write_report(self, report):
        self.report = report

    def get_report(self):
        return self.report

    def next_step(self):
        self.current_step += 1

    def check_finished(self):
        if self.current_step >= len(self.agents):
            self.finished = True
        return self.finished
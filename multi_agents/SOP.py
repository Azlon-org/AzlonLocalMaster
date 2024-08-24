import os
import sys

sys.path.append('..')
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from utils import PREFIX_MULTI_AGENTS, load_config
from typing import Dict, Tuple, List, Optional
from agents import *
from state import State
import pdb
import copy

class SOP:
    def __init__(self, competition: str):
        self.competition = competition
        self.state_records = []
        self.current_state = None
        self.max_iterations = 3  # 最大迭代次数
        self.phases = load_config(f'{PREFIX_MULTI_AGENTS}/config.json')['phases'] # 任务阶段
        self.phase_to_iterations = load_config(f'{PREFIX_MULTI_AGENTS}/config.json')['phase_to_iterations'] # 记录每个阶段迭代次数

    def _create_agents(self, agent_name: str) -> Agent:
        if agent_name == "Reader":
            return Reader('gpt-4o', 'api')
        elif agent_name == "Planner":
            return Planner('gpt-4o', 'api')
        elif agent_name == "Developer":
            return Developer('gpt-4o', 'api')
        elif agent_name == "Reviewer":
            return Reviewer('gpt-4o', 'api')
        elif agent_name == "Summarizer":
            return Summarizer('gpt-4o', 'api')
        else:
            raise Exception(f"Unknown agent: {agent_name}")

    # 执行完当前state，并返回新的state
    def step(self, state: State) -> Tuple[str, State]:
        state.make_dir() # 创建当前State的目录
        print(f"Current State: {state}")
        agents = state.agents # 获取当前State中的Agents

        # pdb.set_trace()
        while not state.finished:
            current_agent_name = agents[state.current_step % len(agents)] # 获取当前Agent名字
            current_agent = self._create_agents(current_agent_name) # 创建当前Agent
            
            # agent执行action方法，返回result，result是字典，key是agent的role，value是agent的执行结果等信息
            action_result = current_agent.action(state)
            state.update_memory(action_result)
            state.next_step()

            if state.check_finished(): # 如果State完成，尝试更新State，只要step数达到就尝试更新，但不一定成功
                state.set_score() # 设置State的评分
                state_info, new_state = self.update_state(state)
                if state_info == 'Success':
                    state.restore_memory()
                    state.restore_report()

        return state_info, new_state

    def update_state(self, state: State) -> Tuple[str, Optional[State]]:
        # 更新State，根据新的参数创建新的State
        self.state_records.append(copy.deepcopy(state)) # 深拷贝state 并加入state_records 可用于计算iterations

        if state.phase == "Model Building, Validation, and Prediction":
            if state.score < 3 and self.phase_to_iterations[state.phase] < self.max_iterations:
                # 如果Model Building, Validation, and Prediction评分低于3，并且还能继续迭代，返回Feature Engineering
                # next_phase = "Feature Engineering"
                self.phase_to_iterations[state.phase] += 1
                next_phase = state.phase # 如果评分低于3，继续当前阶段
                update_state_info = "Repeat"
                new_state = State(phase=state.phase) 
                new_state.memory = copy.deepcopy(state.memory) # 深拷贝memory
                new_state.memory.append({})  # 在列表中加入一个空dict
            else:
                if state.score >= 3:
                    # Model Building, Validation, and Prediction通过，完成此阶段
                    next_phase = "Complete"
                    update_state_info = "Complete"
                    new_state = None
                else:
                    update_state_info = "Fail"
                    new_state = None
        else:
            if state.phase == "Feature Engineering":
                if len(self.state_records) >=2 and self.state_records[-2].phase == "Model Building, Validation, and Prediction":
                    pass
                else:
                    self.phase_to_iterations[state.phase] += 1
            # 其他步骤
            else:
                self.phase_to_iterations[state.phase] += 1 # 记录已经迭代的次数 假设已经迭代三次，我要知道，第三次是否成功
            if state.score < 3 and self.phase_to_iterations[state.phase] < self.max_iterations:
                next_phase = state.phase # 如果评分低于3，继续当前阶段
                update_state_info = "Repeat"
                new_state = State(phase=state.phase) 
                new_state.memory = copy.deepcopy(state.memory) # 深拷贝memory
                new_state.memory.append({})  # 在列表中加入一个空dict
            else:
                if state.score >= 3: # 如果评分大于等于3，进入下一个阶段
                    update_state_info = "Success"
                    next_phase = self.get_next_phase(state.phase)
                    new_state = State(phase=next_phase, message=state.send_message())
                else:
                    update_state_info = "Fail"
                    new_state = None
            next_phase = self.get_next_phase(state.phase)

        return update_state_info, new_state

    def get_next_phase(self, current_phase: str) -> str:
        phases = self.phases
        next_index = phases.index(current_phase) + 1
        return phases[next_index] if next_index < len(phases) else "Complete"

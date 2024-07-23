import os
import sys

sys.path.append('..')
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

import utils
from typing import Dict, Tuple, List, Optional
from Agent import Agent
from State import State

class SOP:
    def __init__(self, competition: str):
        self.competition = competition
        self.finished = False
        self.state_records = []
        self.current_state = None
        self.max_iterations = 3  # 最大迭代次数
        self.phases = [
            "Understand Background", 
            "Preliminary Exploratory Data Analysis", 
            "Data Cleaning", 
            "In-depth Exploratory Data Analysis", 
            "Feature Engineering", 
            "Model Building, Validation, and Prediction"
        ]
        self.phases_to_iterations = {
            "Understand Background": 0,
            "Preliminary Exploratory Data Analysis": 0,
            "Data Cleaning": 0,
            "In-depth Exploratory Data Analysis": 0,
            "Feature Engineering": 0,
            "Model Building, Validation, and Prediction": 0
        }

    # 执行完当前state，并返回新的state
    def step(self, state: State, agents_team: List[Agent]) -> Tuple[Agent, State]:
        agents = state.agents # 获取当前State中的Agents

        while not state.finished:
            current_agent = agents[state.current_step % len(agents)] # 获取当前Agent
            assert type(current_agent) == Agent
            
            # agent执行step方法，返回action，action是字典，key是agent的role，value是agent的执行结果
            action = current_agent.step(state)
            state.update_memory(action)
            state.next_step()

            if state.check_finished(): # 如果State完成，尝试更新State
                state_info, new_state = self.update_state(state, agents_team)

        return state_info, new_state

    def check_finished(self, state: State) -> bool:
        # 检查项目是否完成，根据任务阶段和迭代次数确定
        if self.current_iteration >= self.max_iterations:
            return True
        # 根据具体条件判断当前State是否完成
        if state.phase == "Model Building, Validation, and Prediction" and self.modeling_iterations >= self.max_modeling_iterations:
            return True
        return False

    def update_state(self, state: State, agents_team: List[Agent]) -> Tuple[str, Optional[State]]:
        # 更新State，根据新的参数创建新的State
        self.state_records.append(state) # SOP执行时的State记录 可用来计算iteration

        if state.phase == "Model Building, Validation, and Prediction":
            if state.point < 3 and self.phases_to_iterations[state.phase] < self.max_iterations:
                # 如果Model Building, Validation, and Prediction评分低于3，并且还能继续迭代，返回Feature Engineering
                next_phase = "Feature Engineering"
                self.phases_to_iterations[state.phase] += 1
            else:
                # Model Building, Validation, and Prediction通过，完成此阶段
                next_phase = "Complete"
                new_state = None
        else:
            # 其他步骤
            self.phases_to_iterations[state.phase] += 1 # 记录已经迭代的次数 假设已经迭代三次，我要知道，第三次是否成功
            if state.point < 3 and self.phases_to_iterations[state.phase] < self.max_iterations:
                next_phase = state.phase # 如果评分低于3，继续当前阶段
            else:
                if state.point >= 3:
                    update_state_info = "Success"
                    next_phase = self.get_next_phase(state.phase)
                else:
                    update_state_info = "Fail"
                    new_state = None
            next_phase = self.get_next_phase(state.phase)

        return update_state_info, new_state

    def get_next_phase(self, current_phase: str) -> str:
        phases = self.phases
        next_index = phases.index(current_phase) + 1
        return phases[next_index] if next_index < len(phases) else "Complete"

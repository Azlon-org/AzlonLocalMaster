import os
import sys

sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from multi_agents.state import State
from multi_agents.sop import SOP
from utils import PREFIX_MULTI_AGENTS, load_config
import pdb

if __name__ == '__main__':
    competition = load_config(f'{PREFIX_MULTI_AGENTS}/config.json')['competition']
    sop = SOP(competition)
    # start_state = State(phase="Understand Background")
    # start_state = State(phase="Preliminary Exploratory Data Analysis")
    # start_state = State(phase="Data Cleaning")
    # start_state = State(phase="In-depth Exploratory Data Analysis")
    start_state = State(phase="Feature Engineering")
    # start_state = State(phase="Model Building, Validation, and Prediction")
    start_message = ""
    new_state = start_state

    # pdb.set_trace()
    print(f"Start SOP for competition: {competition}")
    # 主循环
    while True:
        current_state = new_state
        state_info, new_state = sop.step(state=current_state) # 这一步执行完当前state，返回新的state
        if state_info == 'Fail':
            print("Failed to update state.")
            exit()
        if state_info == 'Complete':
            print(f"Competition {competition} SOP is completed.")
            break
    
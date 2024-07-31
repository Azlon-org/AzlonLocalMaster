import os
import sys

sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from multi_agents.State import State
from multi_agents.SOP import SOP
from utils import PREFIX_MULTI_AGENTS, load_config
import pdb

if __name__ == '__main__':
    competition = load_config(f'{PREFIX_MULTI_AGENTS}/config.json')['competition']
    sop = SOP(competition)
    start_state = State(phase="Understand Background", task="summarize competition info")
    start_message = ""
    new_state = start_state
    new_message = start_message

    pdb.set_trace()
    # 主循环
    while not sop.finished:
        current_state = new_state
        current_message = new_message
        state_info, new_state, new_message = sop.step(state=current_state, message=current_message) # 这一步执行完当前state，返回新的state
        if state_info == 'Fail':
            print("Failed to update state.")
            exit()
        sop.check_finished(current_state)
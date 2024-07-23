import os
import sys

sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from multi_agents.LLM import LLM
from multi_agents.State import State
from multi_agents.Agent import Summarizer, Planner, Developer, Debugger, Reviewer
from multi_agents.SOP import SOP
import pdb

if __name__ == '__main__':
    summarizer = Summarizer()
    planner = Planner()
    developer = Developer()
    debugger = Debugger()
    reviewer = Reviewer()
    agents_team = [summarizer, planner, developer, debugger, reviewer]

    competition = 'titanic'
    sop = SOP(competition)
    start_state = State(phase="Understand Background", task="summarize competition info", agents_team=agents_team)

    pdb.set_trace()
    # 主循环
    while not sop.finished:
        state_info, new_state = sop.step(start_state, agents_team) # 这一步执行完当前state，返回新的state
        if state_info == 'Fail':
            print("Failed to update state.")
            exit()
        current_state = new_state
        sop.check_finished(current_state)

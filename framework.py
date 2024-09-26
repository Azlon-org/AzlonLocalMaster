import os
import sys

sys.path.append(os.path.dirname(os.path.abspath(__file__)))
from multi_agents.state import State
from multi_agents.sop import SOP
from utils import PREFIX_MULTI_AGENTS, load_config
import pdb
import argparse
import logging

import sys

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Run SOP for a competition.')
    parser.add_argument('--competition', type=str, default='titanic', help='Competition name')
    args = parser.parse_args()
    competition = args.competition

    sop = SOP(competition)
    start_state = State(phase="Understand Background", competition=competition)
    # start_state = State(phase="Preliminary Exploratory Data Analysis", competition=competition)
    # start_state = State(phase="Data Cleaning", competition=competition)
    # start_state = State(phase="In-depth Exploratory Data Analysis", competition=competition)
    # start_state = State(phase="Feature Engineering", competition=competition)
    # start_state = State(phase="Model Building, Validation, and Prediction", competition=competition)
    start_message = ""
    new_state = start_state

    # Configure logging
    logging.basicConfig(
        level=logging.INFO,  # Set the logging level to INFO
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',  # Log message format
        handlers=[
            logging.FileHandler(f"{PREFIX_MULTI_AGENTS}/competition/{competition}/{competition}.log"),  # Log to a file named 'project.log'
            logging.StreamHandler(sys.stdout)  # Also log to the console
        ]
    )

    logging.info(f"Start SOP for competition: {competition}")
    while True:
        current_state = new_state
        state_info, new_state = sop.step(state=current_state)
        if state_info == 'Fail':
            logging.error("Failed to update state.")
            exit()
        if state_info == 'Complete':
            logging.info(f"Competition {competition} SOP is completed.")
            break  
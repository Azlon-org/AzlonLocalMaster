import os
import sys
from typing import Optional

sys.path.append(os.path.dirname(os.path.abspath(__file__)))
from multi_agents.state import State
from multi_agents.sop import SOP
from utils import PREFIX_MULTI_AGENTS, load_config
import pdb
import argparse
import logging

import sys

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Run SOP for a business data analysis.')
    parser.add_argument('--data_dir', type=str, required=True, help='Directory containing the data to analyze.')
    parser.add_argument('--context_file', type=str, required=True, help='Path to the business context file.')
    parser.add_argument('--model', type=str, default='gpt-4.1', help='Model name (e.g., gpt-4.1, gpt-4.1-mini)')
    args = parser.parse_args()

    # Determine the initial phase from config.json
    # This requires SOP to be instantiated first to load config, or load config separately here.
    # For simplicity, let's assume SOP loads it and we can get it after instantiation, or hardcode for now.
    # To avoid circular dependency or premature config loading, let's load config here for initial phase.
    temp_config = load_config(f'{PREFIX_MULTI_AGENTS}/config.json')
    initial_phase = temp_config['phases'][0] if temp_config.get('phases') else "ContextualSetupAndScan"

    sop = SOP(data_dir=args.data_dir, context_file=args.context_file, model=args.model)
    # Use a placeholder derived from data_dir for parts of State that might still expect 'competition'
    competition_placeholder = os.path.basename(args.data_dir.rstrip('/'))
    start_state = State(phase=initial_phase, data_dir=args.data_dir, context_file=args.context_file, competition_placeholder=competition_placeholder)
    # start_state = State(phase="Preliminary Exploratory Data Analysis", competition=competition)
    # start_state = State(phase="Data Cleaning", competition=competition)
    # start_state = State(phase="In-depth Exploratory Data Analysis", competition=competition)
    # start_state = State(phase="Feature Engineering", competition=competition)
    # start_state = State(phase="Model Building, Validation, and Prediction", competition=competition)
    start_message = ""
    current_state_obj: Optional[State] = start_state

    # logger
    root_logger = logging.getLogger()
    root_logger.setLevel(logging.INFO)

    # Ensure the output directory for logs exists (it's inside the data_dir/_analysis_insights)
    # The specific log filename can be made more dynamic or configurable later.
    # Using competition_placeholder for the log file name for now.
    output_log_dir = os.path.join(args.data_dir, sop.config.get('workflow_options', {}).get('output_subdirectory', '_analysis_insights'))
    os.makedirs(output_log_dir, exist_ok=True)
    log_file_name = sop.config.get('logging', {}).get('detailed_log_filename', f"{competition_placeholder}_detailed.log")
    log_file_path = os.path.join(output_log_dir, log_file_name)

    file_handler = logging.FileHandler(log_file_path)
    file_handler.setLevel(logging.INFO)
    
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setLevel(logging.INFO)
    
    formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    file_handler.setFormatter(formatter)
    console_handler.setFormatter(formatter)
    
    root_logger.addHandler(file_handler)
    root_logger.addHandler(console_handler)

    root_logger.info(f"Starting SOP for data in: {args.data_dir} with context: {args.context_file}")
    while current_state_obj is not None:
        # import pdb; pdb.set_trace()
        # At this point, current_state_obj is guaranteed to be a State object due to the while loop condition.
        exec_state_info, next_state_obj = sop.step(current_state_obj)
        current_state_obj = next_state_obj # Update current_state_obj for the next iteration's check

        if exec_state_info == "Complete":
            logging.info(f"Workflow for {args.data_dir} SOP is completed.")
            break
        elif exec_state_info == "Fail":
            logging.error("Failed to update state.")
            exit()
        elif exec_state_info == "Repeat":
            # The loop will continue with current_state_obj which is the repeated state from sop.step
            logging.info(f"Repeating phase: {current_state_obj.phase if current_state_obj else 'N/A'}")
        elif current_state_obj is None: # This case implies exec_state_info was 'Success' but next state is None (end of defined phases)
            logging.info("Workflow completed as no next state was provided.")
            break

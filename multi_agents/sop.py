import os
import sys
from typing import Dict, Tuple, List, Optional
import copy
import logging

sys.path.append('..')
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from utils import PREFIX_MULTI_AGENTS, load_config
from .agents.reader import Reader
from .agents.planner import Planner
from .agents.developer import Developer
from .agents.critic import Critic
from .agents.reviewer import Reviewer
from .agents.summarizer import Summarizer
from state import State

class SOP:
    def __init__(self, data_dir: str, context_file: str, model: str):
        self.data_dir = data_dir
        self.context_file = context_file
        self.llm_model = model.replace("_", "-") # Renamed for clarity
        self.state_records = []
        self.current_state = None
        self.config = self._load_configuration()
        self.role_prompts = self.config.get("role_prompts", {})
        self.agent_configs = self.config.get("agent_configs", {})
        self.iterative_analysis_iterations = 0 # Counter for IterativeAnalysisLoop
        # Placeholder for competition, to be fully removed later. 
        # Needed if State or other parts still use it for path construction before full refactor.
        self.competition_placeholder = os.path.basename(data_dir.rstrip('/'))

    def _load_configuration(self) -> Dict:
        # Loads the entire new config.json structure
        config = load_config(f'{PREFIX_MULTI_AGENTS}/config.json')
        return config

    def _create_agent(self, agent_name: str):
        # TODO: Map new conceptual agent names (DataProfiler, DataAnalyst) to actual agent classes 
        # or ensure these classes exist. For now, mapping them to Developer/Reader as placeholders.
        llm_type = 'api' # Default LLM type

        if agent_name == "Reader":
            agent = Reader(model=self.llm_model, type=llm_type)
        elif agent_name == "Planner":
            agent = Planner(model=self.llm_model, type=llm_type)
        elif agent_name == "Developer" or agent_name == "DataProfiler" or agent_name == "DataAnalyst": # DataProfiler and DataAnalyst are conceptual, map to Developer for now
            agent = Developer(model=self.llm_model, type=llm_type)
        elif agent_name == "Critic":
            agent = Critic(model=self.llm_model, type=llm_type)
        elif agent_name == "Reviewer":
            agent = Reviewer(model=self.llm_model, type=llm_type)
        elif agent_name == "Summarizer":
            agent = Summarizer(model=self.llm_model, type=llm_type)
        else:
            logging.error(f"Unknown agent name: {agent_name}")
            return None
        return agent

    # 执行完当前state，并返回新的state
    def step(self, state: State) -> Tuple[str, Optional[State]]:
        logging.info(f"Current State: {state}")
        state.make_dir()
        state.make_context()
        
        while not state.finished:
            # import pdb; pdb.set_trace()
            current_agent_name = state.get_current_agent()
            # print(f"Current Agent: {current_agent_name}")
            current_agent = self._create_agent(current_agent_name)
            
            if current_agent is None:
                raise ValueError(f"Unknown agent: {current_agent_name}")
            
            action_result = current_agent.action(state)
            state.update_memory(action_result)
            state.next_step()

            if state.check_finished():
                # state.set_score() # Score is no longer used for state transitions here
                exec_state_info, new_state = self.update_state(state)
                # state.restore_memory() # Memory restoration logic might need review based on new workflow
        
        return exec_state_info, new_state

    def update_state(self, state: State) -> Tuple[str, Optional[State]]:
        self.state_records.append(copy.deepcopy(state))
        current_phase = state.phase

        if current_phase == "IterativeAnalysisLoop":
            self.iterative_analysis_iterations += 1
            max_iterations = self.config.get('workflow_options', {}).get('max_iterations_iterative_analysis', 3)
            if self.iterative_analysis_iterations >= max_iterations:
                logging.info(f"Max iterations reached for {current_phase}. Moving to next phase.")
                next_phase = self.get_next_phase(current_phase)
                self.iterative_analysis_iterations = 0 # Reset for potential future use
                if next_phase == "Complete":
                    return "Complete", None
                else:
                    return "Success", State(phase=next_phase, data_dir=self.data_dir, context_file=self.context_file, competition_placeholder=self.competition_placeholder)
            else:
                logging.info(f"Repeating {current_phase} (Iteration {self.iterative_analysis_iterations})")
                return "Repeat", self._create_repeat_state(state) # Repeat current phase
        else:
            # For non-iterative phases, move to the next phase upon completion
            next_phase = self.get_next_phase(current_phase)
            if next_phase == "Complete":
                return "Complete", None
            else:
                return "Success", State(phase=next_phase, data_dir=self.data_dir, context_file=self.context_file, competition_placeholder=self.competition_placeholder)

    def _create_repeat_state(self, state: State) -> State:
        # Creates a new state for the same phase, typically for iteration.
        # The new state inherits the memory of the completed state.
        logging.debug(f"Creating repeat state for phase: {state.phase}")
        new_state = State(phase=state.phase, data_dir=self.data_dir, context_file=self.context_file, competition_placeholder=self.competition_placeholder)
        # Carry over memory. The agent's action should append to the latest memory entry or use it as context.
        new_state.memory = copy.deepcopy(state.memory) 
        # It's often useful to start a new dictionary for the new agent interaction within the repeated phase
        if not state.memory or state.get_current_agent() == new_state.agents[0]: # if memory is empty or it's start of agent sequence
             new_state.memory.append({}) # Add a new dict for the current iteration step if needed by agent logic
        return new_state

    def get_next_phase(self, current_phase: str) -> str:
        phases = self.config['phases']
        next_index = phases.index(current_phase) + 1
        return phases[next_index] if next_index < len(phases) else "Complete"

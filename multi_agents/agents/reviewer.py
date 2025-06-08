from typing import Dict, Any, List
import json
import re
import logging
import sys 
import os
import pdb

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)
sys.path.append('..')
sys.path.append('../..')
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

import json
import logging
from agent_base import Agent # Assuming Agent is intended, though AgentBase is defined in agent_base.py
from utils import read_file, PREFIX_MULTI_AGENTS
from llm import LLM
from state import State
from prompts.prompt_base import *
from prompts.prompt_reviewer import *

logger = logging.getLogger(__name__)

class Reviewer(Agent):
    def __init__(self, model: str, type: str):  
        super().__init__(
            role="reviewer",
            description="You are skilled at assessing the performance of one or more agents in completing a given task. Provide detailed scores for their performance and offer constructive suggestions to optimize their results.",
            model=model,
            type=type
        )

    # Helper function to get agent description from config
    def _get_agent_description(self, agent_name_from_memory: str, config: dict) -> str:
        # Agent names in config are typically capitalized (e.g., "Planner", "Critic")
        # Agent roles (and thus keys in memory dict) are often lowercase (e.g., "planner", "critic")
        agent_name_in_config = agent_name_from_memory.capitalize()
        
        description = config.get('agent_configurations', {}).get(agent_name_in_config, {}).get('description')
        if description:
            return description
        
        # Fallback if not in agent_configurations (though it should ideally be there)
        # This part could be expanded if role_prompts also reliably store descriptions
        # For example, some prompts in role_prompts might be structured dicts with a 'description' key.
        # For now, we rely on agent_configurations.

        # Check if the direct agent_name_from_memory (lowercase) exists as a key, 
        # in case some configs use lowercase keys.
        description_lc = config.get('agent_configurations', {}).get(agent_name_from_memory, {}).get('description')
        if description_lc:
            return description_lc
            
        return f"Description for {agent_name_in_config} not found in agent_configurations."

    def _merge_dicts(self, dicts: List[Dict[str, Any]], state: State) -> Dict[str, Any]:
        merged_dict = {"final_suggestion": {}, "final_score": {}}

        # 定义需要统一的key
        if state.phase == 'Understand Background':
            key_mapping = {
                "reader": "agent reader"
            }
        else:
            key_mapping = {
                "planner": "agent planner",
                "developer": "agent developer"
            }
        
        try:
            for d in dicts:
                for key in d["final_suggestion"]:
                    normalized_key = key.lower()
                    for k, v in key_mapping.items():
                        if k in normalized_key:
                            normalized_key = v
                            break
                    merged_dict["final_suggestion"][normalized_key] = d["final_suggestion"][key]
                for key in d["final_score"]:
                    normalized_key = key.lower()
                    for k, v in key_mapping.items():
                        if k in normalized_key:
                            normalized_key = v
                            break
                    merged_dict["final_score"][normalized_key] = d["final_score"][key]
        except Exception as e:
            logging.error(f"Error: {e}")
            pdb.set_trace()
        
        return merged_dict

    def _generate_prompt_for_agents(self, state: State) -> List[str]:
        prompt_for_agents = []
        if not state.memory or not state.memory[-1]:
            logger.warning("Reviewer: No memory found for the current phase to review.")
            return []

        phase_memory = state.memory[-1]  # This is the dictionary for the current phase
        logger.info(f"Reviewer: Processing phase memory keys for review: {list(phase_memory.keys())}")

        for agent_name, agent_data in phase_memory.items():
            if not isinstance(agent_data, dict):
                logger.debug(f"Reviewer: Skipping key '{agent_name}' in phase memory as its value is not a dict (type: {type(agent_data)}). This is likely not a structured agent output.")
                continue

            # agent_name is the role (e.g., "critic") and agent_data is its output dict (e.g., {"status": ..., "critique_generated": ...})
            role_for_prompt = agent_name.upper()
            agent_description = self._get_agent_description(agent_name, state.config)

            task_str = f"The {agent_name} agent performed its duties for the phase: {state.phase}."
            input_str = "Based on the current context, previous outputs, and the insights log."
            result_str = "No specific primary result identified in agent's output dictionary."

            # Heuristically extract task/result based on common patterns from other agents
            if agent_name == "planner":
                task_str = agent_data.get("task_addressed", agent_data.get("task", f"Generate a plan for phase: {state.phase}"))
                result_str = agent_data.get("generated_plan", agent_data.get("plan_details", "Plan not found in planner's output."))
            elif agent_name == "developer":
                task_str = agent_data.get("task_addressed", agent_data.get("task", f"Develop code/solution for phase: {state.phase}"))
                generated_code_content = agent_data.get("generated_code")
                if generated_code_content:
                    result_str = generated_code_content
                else:
                    code_path = agent_data.get('code_saved_path', 'Path not specified.')
                    result_str = f"Code file path: {code_path}"
                if result_str == f"Code file path: Path not specified." and not generated_code_content:
                     result_str = "Generated code or path not found in developer's output."
            elif agent_name == "critic":
                task_str = f"Critique the output of: {agent_data.get('critique_target', 'previous work')}"
                result_str = agent_data.get("critique_generated", "Critique not found in critic's output.")
            elif agent_name == "summarizer":
                task_str = f"Summarize the activities and findings for phase: {state.phase}"
                result_str = agent_data.get("report", agent_data.get("summary_text", "Summary not found in summarizer's output."))
            # Add other agents as needed, ensuring agent_name matches the key used by the agent in its return dict.

            if result_str == "No specific primary result identified in agent's output dictionary." or not result_str:
                try:
                    result_str = json.dumps(agent_data, indent=2, default=str)
                except TypeError:
                    result_str = str(agent_data)
            
            current_prompt = PROMPT_REVIEWER_ROUND1_EACH_AGENT.format(
                role=role_for_prompt or "UNKNOWN_ROLE",
                description=agent_description or "No description available.",
                task=task_str or "Task not specified.",
                input=input_str or "Input not specified.",
                result=result_str or "Result not available."
            )
            prompt_for_agents.append(current_prompt)
            
        if not prompt_for_agents:
            logger.warning("Reviewer: No agent outputs suitable for review were found in the current phase memory after filtering.")
            
        return prompt_for_agents
    
    def _execute(self, state: State, role_prompt: str) -> Dict[str, Any]:
        # 实现评价功能
        # 第二轮输入：state的memory中过去每个agent的role_description, task, input, result
        # pdb.set_trace()
        prompt_for_agents = self._generate_prompt_for_agents(state)
        history = []
        all_raw_reply = []
        history.append({"role": "system", "content": f"{role_prompt}{self.description}"})
        round = 0
        while round <= 3 * len(prompt_for_agents) - 1:
            if round % 3 == 0:
                input = PROMPT_REVIEWER_ROUND0.format(phases_in_context=state.context, phase_name=state.phase)
            elif round % 3 == 1:
                input = prompt_for_agents[round//3 - 1]
            elif round % 3 == 2:
                input = PROMPT_REVIEWER_ROUND2
            raw_reply, history = self.llm.generate(input, history, max_tokens=4096)
            if round % 3 == 2:
                all_raw_reply.append(raw_reply)
            round += 1

        all_reply = []
        # pdb.set_trace()
        for each_raw_reply in all_raw_reply:
            reply = self._parse_json(each_raw_reply)
            try:
                all_reply.append(reply['final_answer'])
            except KeyError:
                # pdb.set_trace()
                all_reply.append(reply)

        # 保存history
        with open(f'{state.restore_dir}/{self.role}_history.json', 'w') as f:
            json.dump(history, f, indent=4)
        with open(f'{state.restore_dir}/{self.role}_reply.txt', 'w') as f:
            f.write("\n\n\n".join(all_raw_reply))

        review = self._merge_dicts(all_reply, state)
        final_score = review['final_score']
        final_suggestion = review['final_suggestion']
        # developer代码执行失败 评分为0
        if state.memory[-1].get("developer", {}).get("status", True) == False:
            final_score["agent developer"] = 0
            review["final_suggestion"]["agent developer"] = "The code execution failed. Please check the error message and write code again."
        # pdb.set_trace()
        with open(f'{state.restore_dir}/review.json', 'w') as f:
            json.dump(review, f, indent=4)

        print(f"State {state.phase} - Agent {self.role} finishes working.")
        return {
            self.role: {
                "history": history, 
                "score": final_score, 
                "suggestion": final_suggestion, 
                "result": review
            }
        }


from typing import Dict, Any
import json
import logging
import sys
import os

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
sys.path.append(os.path.join(os.path.dirname(os.path.abspath(__file__)), '..'))

from agent_base import Agent
from state import State
from llm import LLM # LLM is used for critique generation

class Critic(Agent):
    def __init__(self, model: str, type: str):
        super().__init__(
            role="critic",
            description="You are adept at critically evaluating plans, summaries, and insights, providing constructive feedback.",
            model=model,
            type=type
        )

    def _execute(self, state: State, role_prompt: str) -> Dict[str, Any]:
        history = []
        critique_text = "Critique not generated yet."
        target_agent_output = "No specific output identified for critique."
        insights_log_content = "Insights log not read yet."
        insights_log_status = "Not read"

        # 1. Determine insights log path
        output_subdir = state.config.get('workflow_options', {}).get('output_subdirectory', '_analysis_insights')
        insights_filename = state.config.get('logging', {}).get('insights_filename', 'insights_log.md')
        insights_log_path = os.path.join(state.data_dir, output_subdir, insights_filename)
        os.makedirs(os.path.dirname(insights_log_path), exist_ok=True)

        # 2. Read insights_log.md for context
        try:
            if os.path.exists(insights_log_path):
                with open(insights_log_path, 'r') as f:
                    insights_log_content = f.read()
                insights_log_status = "Successfully read"
                if not insights_log_content.strip():
                    insights_log_content = "Insights log is empty."
                    insights_log_status = "Read (empty)"
            else:
                insights_log_content = "Insights log does not exist yet (Critic)."
                insights_log_status = "Not found (Critic)"
        except Exception as e:
            logger.error(f"Critic: Error reading insights_log.md: {e}")
            insights_log_content = f"Critic: Error reading insights_log.md: {e}"
            insights_log_status = "Error reading (Critic)"

        # 3. Identify what to critique (e.g., previous agent's output)
        # This logic will need to be more sophisticated.
        # For now, let's assume it critiques the last significant entry in state.memory or a specific field.
        if state.memory and isinstance(state.memory[-1], dict):
            previous_agent_outputs = state.memory[-1]
            if "Planner" in previous_agent_outputs and previous_agent_outputs["Planner"].get("generated_plan"):
                target_agent_output = previous_agent_outputs["Planner"].get("generated_plan")
                critique_focus = "the generated plan"
            elif "Summarizer" in previous_agent_outputs and previous_agent_outputs["Summarizer"].get("report"):
                target_agent_output = previous_agent_outputs["Summarizer"].get("report")
                critique_focus = "the generated summary/report"
            else:
                target_agent_output = json.dumps(previous_agent_outputs, indent=2)
                critique_focus = "the previous agent's general output"
        else:
            critique_focus = "the overall current state or lack of specific prior output"

        # 4. Formulate prompt and generate critique using LLM
        # Formulate prompt and generate critique using LLM
        critique_prompt_template = (
            "You are a meticulous Critic. Your task is to review the provided information and offer a constructive critique.\n\n"
            "EXISTING INSIGHTS LOG:\n{insights_log}\n\n"
            "ITEM TO CRITIQUE ({item_focus}):\n{item_to_critique}\n\n"
            "CRITIQUE FOCUS AREAS: {focus_areas}\n\n"
            "Based on all the above, provide your critique as a concise, actionable paragraph. "
            "Identify strengths and weaknesses, and suggest specific improvements if applicable."
        )

        default_focus = state.config.get('agent_configurations', {}).get('Critic', {}).get('default_critique_focus', 'Clarity, Actionability, and Potential Biases')
        llm_input = critique_prompt_template.format(
            insights_log=insights_log_content,
            item_focus=critique_focus,
            item_to_critique=target_agent_output,
            focus_areas=default_focus
        )
        history.append({"role": "system", "content": f"{role_prompt} {self.description}"}) # Add system prompt from AgentBase

        try:
            raw_critique_reply, history = self.llm.generate(llm_input, history, max_tokens=1024)
            # Assuming critique is textual, parse_markdown might be too aggressive if LLM returns plain text.
            # Let's try to get the direct reply first, or a specific part if structured.
            # For now, using the raw reply, assuming it's the critique itself.
            critique_text = self._parse_markdown(raw_critique_reply) # self._parse_markdown can be used if LLM is asked for markdown
            if not critique_text.strip():
                critique_text = raw_critique_reply # Fallback if parsing yields empty
            logger.info(f"Critic agent generated critique for {critique_focus}")
        except Exception as e:
            logger.error(f"Critic: LLM generation failed: {e}")
            critique_text = f"Failed to generate critique for {critique_focus} due to LLM error: {e}"
            # Ensure history is preserved for logging even on failure
            history.append({"role": "assistant", "content": critique_text}) # Log error as assistant's reply

        # 5. Append critique to insights_log.md
        try:
            with open(insights_log_path, 'a') as f_insights:
                f_insights.write(f"\n\n## Critique by Critic Agent (Phase: {state.phase})\n\n")
                f_insights.write(f"**Target of Critique:** {critique_focus}\n")
                f_insights.write(f"**Critique:**\n{critique_text}\n\n")
                f_insights.write("---\n")
            logger.info(f"Appended Critic's critique for phase '{state.phase}' to {insights_log_path}")
        except Exception as e:
            logger.error(f"Critic: Failed to append critique to {insights_log_path}: {e}")

        # 6. Save outputs (optional, as main output is to insights_log.md)
        os.makedirs(state.restore_dir, exist_ok=True)
        with open(os.path.join(state.restore_dir, f'{self.role}_critique_details.txt'), 'w') as f:
            f.write(f"Target: {critique_focus}\nOutput Critiqued:\n{target_agent_output}\n\nCritique Generated:\n{critique_text}")

        logger.info(f"State {state.phase} - Agent {self.role} finishes working.")

        return {
            self.role: {
                "status": "success",
                "critique_generated": critique_text,
                "critique_target": critique_focus,
                "insights_log_status_at_critique": insights_log_status
            }
        }

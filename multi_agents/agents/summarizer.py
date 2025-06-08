from typing import Dict, Any
import json
import re
import logging
import sys 
import os

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)
sys.path.append('..')
sys.path.append('../..')
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from agent_base import Agent
from utils import read_file, PREFIX_MULTI_AGENTS
from llm import LLM
from state import State
from prompts.prompt_base import *
from prompts.prompt_summarizer import *
from tools import *

class Summarizer(Agent):
    def __init__(self, model: str, type: str):  
        super().__init__(
            role="summarizer",
            description="You are good at asking key questions and answer the questions from given information.",
            model=model,
            type=type
        )

    def _generate_prompt_round1(self, state: State) -> str:
        prompt_round1 = ""
        current_memory = state.memory[-1]
        for role, memory in current_memory.items():
            trajectory = json.dumps(memory.get("history", []), indent=4)
            prompt_round1 += f"\n#############\n# TRAJECTORY OF AGENT {role.upper()} #\n{trajectory}"

        return prompt_round1
    
    def _get_insight_from_visualization(self, state: State) -> str:
        images_dir = f"{state.restore_dir}/images"
        if not os.path.exists(images_dir):
            return "There is no image in this phase."
        else:
            images = os.listdir(images_dir)
        count_of_image = 0
        for image in images:
            if image.endswith('png'):
                count_of_image += 1
        if len(images) == 0 or count_of_image == 0:
            return "There is no image in this phase."
        images_str = "\n".join(images)
        num_of_chosen_images = min(5, len(images))
        chosen_images = []
        input = PROMPT_SUMMARIZER_IMAGE_CHOOSE.format(phases_in_context=state.context, phase_name=state.phase, num=num_of_chosen_images+3, images=images_str)
        raw_reply, _ = self.llm.generate(input, [], max_tokens=4096)
        with open(f'{state.restore_dir}/chosen_images_reply.txt', 'w') as f:
            f.write(raw_reply)
        try:
            raw_chosen_images = self._parse_json(raw_reply)['images']
            for image in raw_chosen_images:
                if image in images:
                    chosen_images.append(image)
                    if len(chosen_images) == num_of_chosen_images:
                        break
        except Exception as e:
            logging.error(f"Error parsing JSON: {e}")
            for image in images:
                if image in raw_reply:
                    chosen_images.append(image)
                    if len(chosen_images) == num_of_chosen_images:
                        break

        image_to_text_tool = ImageToTextTool(model='gpt-4.1', type='api')
        images_to_descriptions = image_to_text_tool.image_to_text(state, chosen_images)
        insight_from_visualization = ""
        for image, description in images_to_descriptions.items():
            insight_from_visualization += f"## IMAGE: {image} ##\n{description}\n"
        with open(f'{state.restore_dir}/insight_from_visualization.txt', 'w') as f:
            f.write(insight_from_visualization)

        return insight_from_visualization

    def _generate_research_report(self, state: State) -> str:
        output_subdir_name = state.config.get('workflow_options', {}).get('output_subdirectory', '_analysis_insights')
        previous_dirs = ['pre_eda', 'data_cleaning', 'deep_eda', 'feature_engineering', 'model_build_predict'] # These are phase names
        previous_report = ""
        for phase_name_dir in previous_dirs:
            # Reports from previous phases should ideally be in insights_log.md already.
            # This function might need to read from insights_log.md or be re-evaluated.
            # For now, attempting to read from individual phase output directories if they exist.
            # The path would be data_dir/output_subdir_name/phase_name_dir/report.txt
            report_path = os.path.join(state.data_dir, output_subdir_name, phase_name_dir, 'report.txt')
            if os.path.exists(report_path):
                with open(report_path, 'r') as f:
                    report_content = f.read()
                    previous_report += f"## {phase_name_dir.replace('_', ' ').upper()} ##\n{report_content}\n"
            else:
                logger.info(f"Previous report not found at {report_path} for phase {phase_name_dir}")

        _, research_report_history = self.llm.generate(PROMPT_SUMMARIZER_RESEARCH_REPORT, [], max_tokens=4096)
        raw_research_report, research_report_history = self.llm.generate(previous_report, research_report_history, max_tokens=4096)
        try:
            research_report = self._parse_markdown(raw_research_report)
        except Exception as e:
            research_report = raw_research_report
        return research_report

    def _execute(self, state: State, role_prompt: str) -> Dict[str, Any]:
        # Determine insights log path
        output_subdir = state.config.get('workflow_options', {}).get('output_subdirectory', '_analysis_insights')
        insights_filename = state.config.get('logging', {}).get('insights_filename', 'insights_log.md')
        insights_log_path = os.path.join(state.data_dir, output_subdir, insights_filename)
        os.makedirs(os.path.dirname(insights_log_path), exist_ok=True)

        # 实现总结功能 阅读当前state的memory 生成report
        if state.memory[-1].get("developer", {}).get("status", True) == False:
            print(f"State {state.phase} - Agent {self.role} gives up summarizing because the code execution failed.")
            return {self.role: {"history": [], "report": ""}}

        history = []
        history.append({"role": "system", "content": f"{role_prompt} {self.description}"})

        # 读取background_info和plan
        background_info = state.background_info
        state_info = state.get_state_info()
        with open(f'{state.restore_dir}/markdown_plan.txt', 'r') as f:
            plan = f.read()

        # Design questions
        design_questions_history = []
        next_phase_name = state.get_next_phase()
        input = PROMPT_SUMMARIZER_DESIGN_QUESITONS.format(phases_in_context=state.context, phase_name=state.phase, next_phase_name=next_phase_name)
        _, design_questions_history = self.llm.generate(input, design_questions_history, max_tokens=4096)

        input = f"# INFO #\n{background_info}\n{state_info}\n#############\n# PLAN #\n{plan}"
        design_questions_reply, design_questions_history = self.llm.generate(input, design_questions_history, max_tokens=4096)
        with open(f'{state.restore_dir}/design_questions_reply.txt', 'w') as f:
            f.write(design_questions_reply)

        input = PROMPT_SUMMARIZER_REORGAINZE_QUESTIONS
        reorganize_questions_reply, design_questions_history = self.llm.generate(input, design_questions_history, max_tokens=4096)
        questions = self._parse_markdown(reorganize_questions_reply)
        with open(f'{state.restore_dir}/questions.txt', 'w') as f:
            f.write(questions)
        history.append(design_questions_history)

        # Answer questions
        with open(f'{state.restore_dir}/single_phase_code.py', 'r') as f:
            code = f.read()
        output_file_path = os.path.join(state.restore_dir, f'{state.phase}_output.txt')
        # Check if output file exists, provide placeholder if not
        if not os.path.exists(output_file_path):
            logger.warning(f"Output file not found: {output_file_path}. Using empty string for output.")
            output = "Output file not found or not generated for this phase."
        else:
            with open(output_file_path, 'r') as f:
                output = f.read()
                if len(output) > 1000: # 如果output太长，则截断
                    output = output[:1000]

        review_content = "No review available for this phase."
        review_file_path = os.path.join(state.restore_dir, 'review.json')
        if os.path.exists(review_file_path):
            try:
                with open(review_file_path, 'r', encoding='utf-8') as f:
                    review_data = json.load(f)
                review_content = review_data.get('critique', "Critique section missing in review.json.")
                logger.info(f"Successfully read and parsed {review_file_path}.")
            except json.JSONDecodeError:
                logger.warning(f"Could not decode JSON from {review_file_path}. Using default review content.")
                review_content = f"Review file {review_file_path} found but contained invalid JSON."
            except Exception as e:
                logger.warning(f"Error reading {review_file_path}: {e}. Using default review content.")
                review_content = f"Error reading review file {review_file_path}: {e}."
        else:
            logger.info(f"{review_file_path} not found. Proceeding without review content for this phase.")

        answer_questions_history = []
        input = PROMPT_SUMMARIZER_ANSWER_QUESTIONS.format(phases_in_context=state.context, phase_name=state.phase, questions=questions)
        _, answer_questions_history = self.llm.generate(input, answer_questions_history, max_tokens=4096)
        
        insight_from_visualization = self._get_insight_from_visualization(state)
        input = PROMPT_INFORMATION_FOR_ANSWER.format(background_info=background_info, state_info=state_info, plan=plan, code=code, output=output, insight_from_visualization=insight_from_visualization, review=review_content)
        answer_questions_reply, answer_questions_history = self.llm.generate(input, answer_questions_history, max_tokens=4096)
        with open(f'{state.restore_dir}/answer_questions_reply.txt', 'w') as f:
            f.write(answer_questions_reply)

        input = PROMPT_SUMMARIZER_REORGANIZE_ANSWERS
        reorganize_answers_reply, answer_questions_history = self.llm.generate(input, answer_questions_history, max_tokens=4096)
        report = self._parse_markdown(reorganize_answers_reply)
        feature_info = self._get_feature_info(state)
        report = feature_info + report
        with open(f'{state.restore_dir}/report.txt', 'w') as f:
            f.write(report)
        history.append(answer_questions_history)

        # Append the generated report to insights_log.md
        try:
            with open(insights_log_path, 'a') as f_insights:
                f_insights.write(f"\n\n## Summary Report for Phase: {state.phase} (by Summarizer)\n\n")
                f_insights.write(report)
                f_insights.write("\n\n---\n")
            logger.info(f"Appended Summarizer report for phase '{state.phase}' to {insights_log_path}")
        except Exception as e:
            logger.error(f"Failed to append Summarizer report to {insights_log_path}: {e}")

        if state.phase == 'Model Building, Validation, and Prediction':
            research_report = self._generate_research_report(state)
            # Append research_report to insights_log.md as well
            try:
                with open(insights_log_path, 'a') as f_insights:
                    f_insights.write(f"\n\n## Research Report (by Summarizer for phase {state.phase})\n\n")
                    f_insights.write(research_report)
                    f_insights.write("\n\n---\n")
                logger.info(f"Appended research report to {insights_log_path}")
                # Optionally, still save it to its own file in restore_dir if needed for other purposes
                with open(os.path.join(state.restore_dir, 'research_report.md'), 'w') as f_research:
                    f_research.write(research_report)
            except Exception as e:
                logger.error(f"Failed to append or write research report: {e}")

        # 保存history
        with open(f'{state.restore_dir}/{self.role}_history.json', 'w') as f:
            json.dump(history, f, indent=4)

        print(f"State {state.phase} - Agent {self.role} finishes working.")
        return {self.role: {"history": history, "report": report}}
from typing import Dict, Any, List
import json
import re
import logging
import sys 
import os
import pandas as pd

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)
sys.path.append('..')
sys.path.append('../..')
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from agent_base import Agent
from utils import read_file # PREFIX_MULTI_AGENTS might be removed if not used elsewhere
from llm import LLM
from state import State
# Prompts will be simplified or redefined
# from prompts.prompt_base import *
# from prompts.prompt_reader import *

class Reader(Agent):
    def __init__(self, model: str, type: str):
        super().__init__(
            role="reader",
            description="You are good at reading document and summarizing information.",
            model=model,
            type=type
        )
    def _scan_and_preview_data_files(self, data_dir: str, supported_extensions: List[str], output_subdirectory_to_skip: str, num_lines_preview: int = 5) -> str:
        preview_parts = []
        try:
            for root, _, files in os.walk(data_dir):
                # Skip the agent's own output directory to avoid reading its own past results
                if output_subdirectory_to_skip and output_subdirectory_to_skip in root:
                    continue

                for file in files:
                    file_ext = os.path.splitext(file)[1].lower()
                    if file_ext in supported_extensions:
                        file_path = os.path.join(root, file)
                        try:
                            preview_parts.append(f"\n--- File: {file_path} ({file_ext}) ---")
                            if file_ext == '.csv':
                                df = pd.read_csv(file_path)
                            elif file_ext in ['.xls', '.xlsx']:
                                df = pd.read_excel(file_path)
                            else:
                                preview_parts.append("Unsupported file type for detailed preview, but detected.")
                                continue
                            
                            preview_parts.append(f"Shape: {df.shape}")
                            preview_parts.append(f"Columns: {df.columns.tolist()}")
                            preview_parts.append("Head:")
                            preview_parts.append(df.head(num_lines_preview).to_string())
                        except Exception as e:
                            preview_parts.append(f"Error reading or previewing file {file_path}: {e}")
        except Exception as e:
            logger.error(f"Error scanning data directory {data_dir}: {e}")
            preview_parts.append(f"Error scanning data directory: {e}")
        
        if not preview_parts:
            return "No data files found or accessible in the specified directory with supported extensions."
        return "\n".join(preview_parts)

    def _execute(self, state: State, role_prompt: str) -> Dict[str, Any]:
        history = []
        raw_reply = ""
        summary = ""
        data_summary = ""
        context_summary = ""
        initial_observations = ""
        insights_log_content = ""
        insights_log_status = ""

        # 0. Determine Insights Log Path and Read/Initialize
        try:
            output_subdir = state.config.get('workflow_options', {}).get('output_subdirectory', '_analysis_insights')
            insights_filename = state.config.get('logging', {}).get('insights_filename', 'insights_log.md')
            insights_log_path = os.path.join(state.data_dir, output_subdir, insights_filename)
            os.makedirs(os.path.dirname(insights_log_path), exist_ok=True) # Ensure directory exists

            if os.path.exists(insights_log_path):
                with open(insights_log_path, 'r') as f:
                    insights_log_content = f.read()
                if not insights_log_content.strip():
                    insights_log_content = "# Insights Log\n\n--- Initialized ---\n\n"
                    with open(insights_log_path, 'w') as f:
                        f.write(insights_log_content)
                    insights_log_status = "Initialized (was empty)"
                else:
                    insights_log_status = "Successfully read"
            else:
                insights_log_content = "# Insights Log\n\n--- Initialized ---\n\n"
                with open(insights_log_path, 'w') as f:
                    f.write(insights_log_content)
                insights_log_status = "Created and initialized"
        except Exception as e:
            logger.error(f"Error handling insights_log.md: {e}")
            insights_log_content = f"Error handling insights_log.md: {e}"
            insights_log_status = "Error"

        # 1. Read Business Context File
        try:
            business_context_content = read_file(state.context_file)
            if not business_context_content:
                business_context_content = "No business context file provided or file is empty."
                logger.warning(f"Context file {state.context_file} is empty or not found.")
        except Exception as e:
            logger.error(f"Error reading context file {state.context_file}: {e}")
            business_context_content = f"Error reading business context file: {e}"

        # 2. Scan and Preview Data Files
        agent_config = state.config.get('agent_config', {}).get(self.role, {})
        supported_extensions = agent_config.get('supported_file_extensions', ['.csv', '.xlsx'])
        output_subdirectory_to_skip = state.config.get('workflow_options', {}).get('output_subdirectory', '_analysis_insights')
        data_files_preview = self._scan_and_preview_data_files(state.data_dir, supported_extensions, output_subdirectory_to_skip)

        # 3. LLM Interaction (Simplified)
        history.append({"role": "system", "content": f"{role_prompt} {self.description}"})
        
        # Placeholder for a new, more generic prompt
        # This prompt should guide the LLM to summarize context, data, and provide observations.
        prompt_template = (
            "You are a data reader and summarizer. Your task is to understand the provided business context and data files, "
            "then provide a concise summary of both, followed by any initial observations or potential areas of interest for analysis.\n\n"
            "BUSINESS CONTEXT:\n{context}\n\n"
            "EXISTING INSIGHTS LOG:\n{insights_log}\n\n"
            "DATA FILES PREVIEW:\n{data_preview}\n\n"
            "Please review all provided information (business context, existing insights, and data previews). Then, provide a concise summary of the business context and data files, and list any new initial observations or potential areas of interest for analysis based on the data previews, considering the existing insights."
        )
        
        llm_input = prompt_template.format(context=business_context_content, insights_log=insights_log_content, data_preview=data_files_preview)
        
        try:
            raw_reply, history = self.llm.generate(llm_input, history, max_tokens=4096)
            # Assuming _parse_markdown extracts the main content if LLM returns markdown
            parsed_reply = self._parse_markdown(raw_reply) 
            # For now, let's assume the parsed_reply contains all info. 
            # A more robust solution would be to ask LLM for structured output (JSON) or parse sections.
            summary = parsed_reply 
            context_summary = "Summary of business context (derived from LLM output - see insights_log.md for full details)."
            data_summary = "Summary of data files (derived from LLM output - see insights_log.md for full details)."
            initial_observations = "Initial observations (derived from LLM output - see insights_log.md for full details)."

        except Exception as e:
            logger.error(f"LLM generation failed for Reader agent: {e}")
            raw_reply = f"LLM generation failed: {e}"
            summary = "Failed to generate summary due to LLM error."

        # Append Reader's detailed summary to insights_log.md
        if summary and not summary.startswith("Failed to generate summary"):
            try:
                with open(insights_log_path, 'a', encoding='utf-8') as f_log:
                    log_entry_header = f"\n\n---\n## Phase: {state.phase} ({self.role} Agent Output)\n\n"
                    f_log.write(log_entry_header)
                    # Ensure summary itself doesn't start with redundant headers if LLM provides them already
                    # The LLM output for Reader (e.g. '### Summary of Business Context:') is desired here.
                    f_log.write(summary.strip())
                    f_log.write("\n---\n")
                logger.info(f"Appended Reader's summary to {insights_log_path}")
            except Exception as e:
                logger.error(f"Failed to append Reader's summary to {insights_log_path}: {e}")

        # 4. Save outputs
        os.makedirs(state.restore_dir, exist_ok=True)
        with open(os.path.join(state.restore_dir, f'{self.role}_llm_history.json'), 'w') as f:
            json.dump(history, f, indent=4)
        with open(os.path.join(state.restore_dir, f'{self.role}_raw_reply.txt'), 'w') as f:
            f.write(raw_reply)
        with open(os.path.join(state.restore_dir, f'{self.role}_summary.txt'), 'w') as f:
            f.write(summary)

        logger.info(f"State {state.phase} - Agent {self.role} finishes working.")
        
        # 5. Return results for state memory
        return {
            self.role: {
                "status": "success" if not summary.startswith("Failed") else "failure",
                "business_context_status": "Error reading file" if business_context_content.startswith("Error reading business context file:") else ("Empty or not found" if business_context_content == "No business context file provided or file is empty." else "Successfully read"),
                "data_files_preview": data_files_preview,
                "llm_raw_reply": raw_reply,
                "summary_from_llm": summary,
                "parsed_context_summary": context_summary, # Placeholder, ideally from structured LLM output
                "parsed_data_summary": data_summary,       # Placeholder
                "parsed_initial_observations": initial_observations, # Placeholder
                "insights_log_status": insights_log_status,
                "insights_log_preview": insights_log_content[:500] + ('...' if len(insights_log_content) > 500 else '')
            }
        }
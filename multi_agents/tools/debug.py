import os
import pandas as pd
import json
import chromadb
import sys
import re

sys.path.append('..')
sys.path.append('../..')
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from memory import Memory, transfer_text_to_json
from llm import OpenaiEmbeddings, LLM
from state import State
from utils import load_config
from prompts.prompt_developer import *

# 在developer中把information准备好，debug写成解耦的，只负责debug，不负责信息准备

class DebugTool:
    def __init__(
        self,
        model: str = 'gpt-4o',
        type: str = 'api'       
    ):
        self.llm = LLM(model, type)

    def debug_code_with_error(self, state: State, previous_code: str, wrong_code: str, error_messages: str, not_pass_information: str) -> str:
        single_round_debug_history = []
        # locate error
        input = PROMPT_DEVELOPER_DEBUG_LOCATE.format(
            previous_code=previous_code,
            wrong_code=wrong_code,
            error_messages=error_messages,
        )
        raw_reply, locate_history = self.llm.generate(input, [], max_tokens=4096)
        single_round_debug_history.append(locate_history)
        with open(f'{state.restore_dir}/debug_locate_error.txt', 'w') as f:
            f.write(raw_reply)

        # extract code
        pattern = r"```python(.*?)```"
        error_code_matches = re.findall(pattern, raw_reply, re.DOTALL)
        exact_error_code_snippet = error_code_matches[-1]

        # fix bug
        input = PROMPT_DEVELOPER_DEBUG_FIX.format(
            exact_error_code_snippet=exact_error_code_snippet,
            error_messages=error_messages
        )
        raw_reply, fix_bug_history = self.llm.generate(input, [], max_tokens=4096)
        single_round_debug_history.append(fix_bug_history)
        with open(f'{state.restore_dir}/debug_fix_bug.txt', 'w') as f:
            f.write(raw_reply)

        # extract code
        correct_code_matches = re.findall(pattern, raw_reply, re.DOTALL)
        code_snippet_after_correction = correct_code_matches[-1]

        # merge code
        input = PROMPT_DEVELOPER_DEBUG_MERGE.format(
            wrong_code=wrong_code,
            exact_error_code_snippet=exact_error_code_snippet,
            code_snippet_after_correction=code_snippet_after_correction
        )
        raw_reply, merge_code_history = self.llm.generate(input, [], max_tokens=4096)
        single_round_debug_history.append(merge_code_history)
        with open(f'{state.restore_dir}/debug_merge_code.txt', 'w') as f:
            f.write(raw_reply)

        with open(f'{state.restore_dir}/single_round_debug_history.json', 'w') as f:
            json.dump(single_round_debug_history, f, indent=4)

        return raw_reply, single_round_debug_history

    def debug_code_with_no_pass_test(self, debug_history, previous_code: str, wrong_code: str, not_pass_information: str) -> str:
        pass
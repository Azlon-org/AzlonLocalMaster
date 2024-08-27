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
        self.debug_times = 0

    def debug_code_with_error(self, state: State, all_error_messages: list, previous_code: str, wrong_code: str, error_messages: str) -> str:
        self.debug_times += 1
        single_round_debug_history = []
        # locate error
        input = PROMPT_DEVELOPER_DEBUG_LOCATE.format(
            previous_code=previous_code,
            wrong_code=wrong_code,
            error_messages=error_messages
        )
        locate_reply, locate_history = self.llm.generate(input, [], max_tokens=4096)
        single_round_debug_history.append(locate_history)
        with open(f'{state.restore_dir}/debug_locate_error.txt', 'w') as f:
            f.write(locate_reply)

        if self.debug_times >= 3:
            input = PROMPT_DEVELOPER_DEBUG_ASK_FOR_HELP.format(i=self.debug_times, all_error_messages=all_error_messages)
            help_reply, help_history = self.llm.generate(input, [], max_tokens=4096)
            single_round_debug_history.append(help_history)
            with open(f'{state.restore_dir}/debug_ask_for_help.txt', 'w') as f:
                f.write(help_reply)
            if "HELP" in help_reply:
                return "HELP", single_round_debug_history

        # extract code
        pattern = r"```python(.*?)```"
        error_code_matches = re.findall(pattern, locate_reply, re.DOTALL)
        most_relevant_code_snippet = error_code_matches[-1]

        # fix bug
        input = PROMPT_DEVELOPER_DEBUG_FIX.format(
            most_relevant_code_snippet=most_relevant_code_snippet,
            error_messages=error_messages
        )
        fix_reply, fix_bug_history = self.llm.generate(input, [], max_tokens=4096)
        single_round_debug_history.append(fix_bug_history)
        with open(f'{state.restore_dir}/debug_fix_bug.txt', 'w') as f:
            f.write(fix_reply)

        # extract code
        correct_code_matches = re.findall(pattern, fix_reply, re.DOTALL)
        code_snippet_after_correction = correct_code_matches[-1]

        # merge code
        input = PROMPT_DEVELOPER_DEBUG_MERGE.format(
            wrong_code=wrong_code,
            most_relevant_code_snippet=most_relevant_code_snippet,
            code_snippet_after_correction=code_snippet_after_correction
        )
        merge_reply, merge_code_history = self.llm.generate(input, [], max_tokens=4096)
        single_round_debug_history.append(merge_code_history)
        with open(f'{state.restore_dir}/debug_merge_code.txt', 'w') as f:
            f.write(merge_reply)

        with open(f'{state.restore_dir}/single_round_debug_history.json', 'w') as f:
            json.dump(single_round_debug_history, f, indent=4)

        return merge_reply, single_round_debug_history

    def debug_code_with_no_pass_test(self, state: State, previous_code: str, code_with_problem: str, not_pass_information: str) -> str:
        single_round_test_history = []
        # locate error
        input = PROMPT_DEVELOPER_TEST_LOCATE.format(
            previous_code=previous_code,
            code_with_problem=code_with_problem,
            not_pass_information=not_pass_information
        )
        raw_reply, test_locate_history = self.llm.generate(input, [], max_tokens=4096)
        input = PROMPT_DEVELOPER_TEST_REORGANIZE_LOCATE_ANSWER
        code_snippets_with_problem, test_locate_history = self.llm.generate(input, test_locate_history, max_tokens=4096)
        single_round_test_history.append(test_locate_history)
        with open(f'{state.restore_dir}/test_locate_problem.txt', 'w') as f:
            f.write(code_snippets_with_problem)

        # fix bug
        input = PROMPT_DEVELOPER_TEST_FIX.format(
            code_snippets_with_problem=code_snippets_with_problem,
            not_pass_information=not_pass_information
        )
        raw_reply, test_fix_history = self.llm.generate(input, [], max_tokens=4096)
        single_round_test_history.append(test_fix_history)
        input = PROMPT_DEVELOPER_TEST_REORGANIZE_FIX_ANSWER
        code_snippets_after_correction, test_fix_history = self.llm.generate(input, test_fix_history, max_tokens=4096)
        with open(f'{state.restore_dir}/test_fix_problem.txt', 'w') as f:
            f.write(code_snippets_after_correction)


        # merge code
        input = PROMPT_DEVELOPER_TEST_MERGE.format(
            code_with_problem=code_with_problem,
            code_snippets_with_problem=code_snippets_with_problem,
            code_snippets_after_correction=code_snippets_after_correction
        )
        raw_reply, merge_code_history = self.llm.generate(input, [], max_tokens=4096)
        single_round_test_history.append(merge_code_history)
        with open(f'{state.restore_dir}/test_merge_code.txt', 'w') as f:
            f.write(raw_reply)

        with open(f'{state.restore_dir}/single_round_test_history.json', 'w') as f:
            json.dump(single_round_test_history, f, indent=4)

        return raw_reply, single_round_test_history
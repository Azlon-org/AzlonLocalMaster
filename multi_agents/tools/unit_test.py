import os
import pandas as pd
import json
import chromadb
import sys

sys.path.append('..')
sys.path.append('../..')
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from memory import Memory, transfer_text_to_json
from LLM import OpenaiEmbeddings, LLM
from State import State
from utils import load_config


class TestTool:
    def __init__(
        self, 
        memory: Memory = None,
        model: str = 'gpt-4o',
        type: str = 'api'
    ):
        self.llm = LLM(model, type)
        self.memory = memory
        # self.summary_ducument = summary_ducument

    def _execute_tests(self, state: State):
        not_pass_tests = []
        test_function_names = state.phase_to_unit_tests[state.phase]
        for func_name in test_function_names:
            if hasattr(self, func_name): # if the function exists
                func = getattr(self, func_name)
                result = func(state) # return 执行结果, 测试编号, 测试信息
                if not result[0]: # if the test failed
                    not_pass_tests.append(result)
                    print(f"Test '{func_name}' failed: {result[2]}")
                else:
                    print(f"Test '{func_name}' succeeded") # assert result
            else:
                print(f"Function '{func_name}' not found in TestTool class")
        return not_pass_tests

    def test_example(self, state: State):
        return True, 1, "cool example"
    
    
    def test_document_exist(self, state: State):
        '''
        check if the csv document exists in the data_dir
        '''
        # check in the state.competition_dir, if the document exists
        # read all the files in the directory
        files = os.listdir(state.competition_dir)
        if state.phase == "Model Building, Validation, and Prediction":
            content = "submission"
        elif state.phase == "Data Cleaning":
            content = "cleaned"
        else:
            return True, 2, "Don't need to check the document in this phase"

        for file in files:
            if f"{content}" in file:
                return True, 2, f"{content} data exists"
        
        return False, 2, f"{content} data does not exist"
    
    def test_no_duplicate_cleaned_train(self, state: State):
        '''
        Check if there are any duplicate rows in the csv
        '''
        df = pd.read_csv(f"{state.competition_dir}/cleaned_train.csv")
        duplicates = df.duplicated().sum()

        if duplicates == 0:
            return True, 3, "No duplicate rows in cleaned_train.csv"
        else:
            return False, 3, "There are duplicate rows in the cleaned_train.csv"

    def test_no_duplicate_cleaned_test(self, state: State):
        '''
        Check if there are any duplicate rows in the csv
        '''
        df = pd.read_csv(f"{state.competition_dir}/cleaned_test.csv")
        duplicates = df.duplicated().sum()

        if duplicates == 0:
            return True, 4, "No duplicate rows in cleaned_test.csv"
        else:
            return False, 4, "There are duplicate rows in the cleaned_test.csv"

    def test_no_duplicate_submission(self, state: State):
        '''
        Check if there are any duplicate rows in the csv
        '''
        files = os.listdir(state.competition_dir)
        for file in files:
            if f"submission" in file:
                df = pd.read_csv(f"{state.competition_dir}/{file}")
                duplicates = df.duplicated().sum()

                if duplicates == 0:
                    return True, 5, "No duplicate rows in submission.csv"
                else:
                    return False, 5, "There are duplicate rows in the submission.csv"

    def test_submission_columns(self, state: State):
        _, file = self.test_no_duplicate_submission()
        df = pd.read_csv(f"{state.competition_dir}/{file}")
        sub_columns = df.columns.values.tolist()
        print(sub_columns)

        prompt = '''Concluse the and the column names of a csv document. Just output in the following format: "name 1", "name 2", ... , "name n"!
text: 
{text}
'''
        with open(f"{state.competition_dir}/{state.phase}/summarizer_reply.txt", 'r') as f:
            text = f.read()
        json_data = transfer_text_to_json(text)
        # trasnfer json data to list of strings
        # print(json_data['final_answer'])
        text = json_data['final_answer']
        
        prompt = prompt.format(text=text['Submission_Format'])
        reply, _ = self.llm.generate(prompt, history=None)
        # convert the reply to a list
        reply = reply.split(", ")
        reply = [name.replace('"', '') for name in reply]
        reply = [name.replace("\n", '') for name in reply]
        reply = [name.replace(" ", '') for name in reply]
        
        if set(sub_columns) == set(reply):
            return True, 6, "The columns are correct"
        else:
            return False, 6, "The columns are not correct"


if __name__ == '__main__':
    # llm = LLM('gpt-4o', 'api')
    # reply, history = llm.generate('try me a joke', history=None)
    # print(reply)
    test_tool = TestTool(memory=None, model='gpt-4o', type='api')
    test_tool._execute_tests()

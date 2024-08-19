import os
import pandas as pd
import json
import chromadb

from memory import Memory, transfer_text_to_json
from LLM import OpenaiEmbeddings, LLM


class TestTool:
    def __init__(
        self, current_state: str = "Model Building, Validation, and Prediction", 
        project_path: str = "/Users/qianbo.zang/Documents/AutoKaggleMaster/multi_agents/competition/titanic",
        memory: Memory = None,
        llm: LLM = None,
    ):
        with open("multi_agents/config.json", 'r', encoding='utf-8') as f:
            config = json.load(f)
            self.phase_to_iterations = config["phase_to_unit_test"]
        self.current_state = current_state
        self.project_path = project_path
        self.llm = llm
        self.memory = memory
        # self.summary_ducument = summary_ducument

        self.test_function_names = self.phase_to_iterations[current_state]

    def _execute_tests(self):
        for func_name in self.test_function_names:
            if hasattr(self, func_name):
                func = getattr(self, func_name)
                result = func()
                print(f"Result of {func_name}: {result}") # assert result
            else:
                print(f"Function '{func_name}' not found in TestTool class")


    def test_example(self):
        return "cool example"
    
    
    def test_document_exist(self):
        '''
        check if the csv document exists in the data_dir
        '''
        # check in the self.project_path, if the document exists
        # read all the files in the directory
        files = os.listdir(self.project_path)
        if self.current_state == "Model Building, Validation, and Prediction":
            content = "submission"
        elif self.current_state == "Data Cleaning":
            content = "cleaned"
        else:
            assert False, "Don't need to check the document in this phase"

        for file in files:
            if f"{content}" in file:
                return True, file
        
        assert False, f"{content} data does not exist"
    
    def test_no_duplicate_cleaned_train(self):
        '''
        Check if there are any duplicate rows in the csv
        '''
        df = pd.read_csv(f"{self.project_path}/cleaned_train.csv")
        duplicates = df.duplicated().sum()

        assert duplicates == 0, "There are duplicate rows in the cleaned_train.csv"

    def test_no_duplicate_cleaned_test(self):
        '''
        Check if there are any duplicate rows in the csv
        '''
        df = pd.read_csv(f"{self.project_path}/cleaned_test.csv")
        duplicates = df.duplicated().sum()

        assert duplicates == 0, "There are duplicate rows in the cleaned_test.csv"

    def test_no_duplicate_submission(self):
        '''
        Check if there are any duplicate rows in the csv
        '''
        files = os.listdir(self.project_path)
        for file in files:
            if f"submission" in file:
                df = pd.read_csv(f"{self.project_path}/{file}")
                duplicates = df.duplicated().sum()

                if duplicates == 0:
                    return True, file
                else:
                    assert False, file

    def test_submission_columns(self):
        _, file = self.test_no_duplicate_submission()
        df = pd.read_csv(f"{self.project_path}/{file}")
        sub_columns = df.columns.values.tolist()
        print(sub_columns)

        prompt = '''Concluse the and the column names of a csv document. Just output in the following format: "name 1", "name 2", ... , "name n"!
text: 
{text}
'''
        with open(f"{self.project_path}/understand_background/summarizer_reply.txt", 'r') as f:
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
            return True, "The columns are correct"
        else:
            assert False, "The columns are not correct"


if __name__ == '__main__':
    llm = LLM('gpt-4o', 'api')
    # reply, history = llm.generate('try me a joke', history=None)
    # print(reply)
    test_tool = TestTool(llm=llm)
    test_tool._execute_tests()

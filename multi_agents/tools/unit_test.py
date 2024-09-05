import os
import pandas as pd
import json
import chromadb
import sys

sys.path.append('..')
sys.path.append('../..')
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# from memory import Memory, transfer_text_to_json
from memory import Memory
from llm import OpenaiEmbeddings, LLM
from state import State
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

    def execute_tests(self, state: State):
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
                result = True, 0, f"Function '{func_name}' not found in TestTool class"
        return not_pass_tests

    def test_example(self, state: State):
        return True, 1, "This is an example of unit test detection without focusing on the example"
    
    
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
        elif state.phase == "Feature Engineering":
            content = "processed"
        else:
            return True, 2, "Don't need to check the document in this phase"

        for file in files:
            if f"{content}" in file:
                return True, 2, f"The {content} file has been processed, please continue to the next step of the process"
        
        return False, 2, f"The {content} file to be processed is lost and the process cannot be continued"
    
    def test_no_duplicate_cleaned_train(self, state: State):
        '''
        Check if there are any duplicate rows in the csv
        '''
        df = pd.read_csv(f"{state.competition_dir}/cleaned_train.csv")
        duplicates = df.duplicated().sum()

        if duplicates == 0:
            return True, 3, "No duplicate rows in cleaned_train.csv"
        else:
            return False, 3, f"There are {duplicates} duplicate rows in the cleaned_train.csv"

    def test_no_duplicate_cleaned_test(self, state: State):
        '''
        Check if there are any duplicate rows in the csv
        '''
        df = pd.read_csv(f"{state.competition_dir}/cleaned_test.csv")
        duplicates = df.duplicated().sum()

        if duplicates == 0:
            return True, 4, "No duplicate rows in cleaned_test.csv"
        else:
            return False, 4, f"There are {duplicates} duplicate rows in the cleaned_test.csv"

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
                    return False, 5, f"There are {duplicates} duplicate rows in the submission.csv"

#     def test_submission_columns(self, state: State):
#         _, file = self.test_no_duplicate_submission(state)
#         df = pd.read_csv(f"{state.competition_dir}/{file}")
#         sub_columns = df.columns.values.tolist()
#         print(sub_columns)

#         prompt = '''Concluse the and the column names of a csv document. Just output in the following format: "name 1", "name 2", ... , "name n"!
# text: 
# {text}
# '''
#         with open(f"{state.competition_dir}/{state.phase}/summarizer_reply.txt", 'r') as f:
#             text = f.read()
#         json_data = transfer_text_to_json(text)
#         # trasnfer json data to list of strings
#         # print(json_data['final_answer'])
#         text = json_data['final_answer']
        
#         prompt = prompt.format(text=text['submission_Format'])
#         reply, _ = self.llm.generate(prompt, history=None)
#         # convert the reply to a list
#         reply = reply.split(", ")
#         reply = [name.replace('"', '') for name in reply]
#         reply = [name.replace("\n", '') for name in reply]
#         reply = [name.replace(" ", '') for name in reply]
        
#         if set(sub_columns) == set(reply):
#             return True, 6, "The columns are correct"
#         else:
#             return False, 6, "The columns are not correct"

    def test_readable_cleaned_train(self, state: State):
        path = f"{state.competition_dir}/cleaned_train.csv"
        with open(path, 'r') as file:
            if file.readable():
                return True, 7, "cleaned_train.csv is readable, please continue to the next step of the process"
            else:
                return False, 7, "cleaned_train.csv could not be read, please try to reprocess it"

    def test_readable_cleaned_test(self, state: State):
        path = f"{state.competition_dir}/cleaned_test.csv"
        with open(path, 'r') as file:
            if file.readable():
                return True, 8, "cleaned_test.csv is readable, please continue to the next step of the process"
            else:
                return False, 8, "cleaned_test.csv could not be read, please try to reprocess it"

    def test_readable_submission(self, state: State):
        files = os.listdir(state.competition_dir)
        for file in files:
            if f"submission" in file:
                path = f"{state.competition_dir}/{file}"
                with open(path, 'r') as file:
                    if file.readable():
                        return True, 9, "submission.csv is readable, please continue to the next step of the process"
                    else:
                        return False, 9, "submission.csv is not readable, please try to reprocess it"

    def test_cleaned_train_no_missing_values(self, state: State):
        path = f"{state.competition_dir}/cleaned_train.csv"
        df = pd.read_csv(path)
        missing_columns = df.columns[df.isnull().any()].tolist()
        if df.isnull().sum().sum() == 0:
            return True, 10, "The cleaned_train.csv file has no missing values, please continue to the next step of the process"
        else:
            return False, 10, f"There are missing values in the cleaned_train.csv file. The columns with missing values are: {', '.join(missing_columns)}"

    def test_cleaned_test_no_missing_values(self, state: State):
        path = f"{state.competition_dir}/cleaned_test.csv"
        df = pd.read_csv(path)
        missing_columns = df.columns[df.isnull().any()].tolist()
        if df.isnull().sum().sum() == 0:
            return True, 11, "The cleaned_test.csv file has no missing values, please continue to the next step of the process"
        else:
            return False, 11, f"There are missing values in the cleaned_test.csv file. The columns with missing values are: {', '.join(missing_columns)}"

    def test_submission_no_missing_values(self, state: State):
        files = os.listdir(state.competition_dir)
        for file in files:
            if "submission" in file and "sample" not in file:
                path = f"{state.competition_dir}/{file}"
                df = pd.read_csv(path)
                missing_columns = df.columns[df.isnull().any()].tolist()
                if df.isnull().sum().sum() == 0:
                    return True, 12, "The submission.csv file has no missing values, please continue to the next step of the process"
                else:
                    return False, 12, f"There are missing values in the submission.csv file. The columns with missing values are: {', '.join(missing_columns)}"

    def test_image_num(self, state: State):
        image_count = 0
        if "Preliminary Exploratory Data Analysis" in state.phase:
            path = f"{state.competition_dir}/pre_eda/images"
        elif "In-depth Exploratory Data Analysis" in state.phase:
            path = f"{state.competition_dir}/deep_eda/images"
        else:
            return True, 13, "No need to check the number of images at this stage, please continue to the next step of the process"
            # 遍历指定目录
        for entry in os.scandir(path):
            if entry.is_file() and entry.name.lower().endswith(('.png', '.jpg', '.jpeg', '.bmp', '.gif', '.tiff')):
                image_count += 1
        if image_count > 10:
            return False, 13, f"The number of images in the path is {image_count}, greater than 10, please re-process to reduce the number of images to 10 or less."
        else:
            return True, 13, "Number of images is less than or equal to 10, unit test passed, please continue to the next step of the process"
    
    def test_file_num_submission(self, state: State):
        path = f"{state.competition_dir}/sample_submission.csv"
        df = pd.read_csv(path)
        files = os.listdir(state.competition_dir)
        for file in files:
            if "submission" in file and "sample" not in file:
                path1 = f"{state.competition_dir}/{file}"
                df1 = pd.read_csv(path1)
                if len(df) == len(df1):
                    return True, 14, "submission.csv and sample_submission.csv files have the same number of rows, unit test passed"
                else:
                    return False, 14, f"submission.csv and sample_submission.csv files have different number of rows. submission.csv has {len(df1)} rows, while sample_submission.csv has {len(df)} rows."
    
    def test_column_names_submission(self, state: State):
        path = f"{state.competition_dir}/sample_submission.csv"
        df = pd.read_csv(path)
        files = os.listdir(state.competition_dir)
        for file in files:
            if "submission" in file and "sample" not in file:
                path1 = f"{state.competition_dir}/{file}"
                df1 = pd.read_csv(path1)
                # 比较两个 DataFrame 的列名集合是否相同
                if list(df.columns) == list(df1.columns):
                    return True, 15, "submission.csv and sample_submission.csv files have the same column names, unit test passed"
                else:
                    return False, 15, f"submission.csv and sample_submission.csv files have different column names or different column order. submission.csv has columns: {set(df1.columns)}, while sample_submission.csv has columns: {set(df.columns)}."

    def test_submission_first_column(self, state: State):
        path = f"{state.competition_dir}/sample_submission.csv"
        df = pd.read_csv(path)
        files = os.listdir(state.competition_dir)
        false_info = ""
        for file in files:
            if "submission" in file and "sample" not in file:
                path1 = f"{state.competition_dir}/{file}"
                df1 = pd.read_csv(path1)
                # 比较两个 DataFrame 的第一列值是否相同
                if df.iloc[:, 0].equals(df1.iloc[:, 0]):
                    return True, 16, "submission.csv and sample_submission.csv files have the same first column values"
                else:
                    false_info = "submission.csv should have the same first column values as sample_submission.csv file"
                    false_info += f'''
This is the first 10 lines of submission.csv:
{df1.head(10)}
This is the first 10 lines of sample_submission.csv:
{df.head(10)}
If you use some transformation on the features in submission.csv, please make sure you have reversed the transformation before submitting the file.
Here is an example that specific transformation applied on features (ID, SalePrice) in submisson.csv is **not reversed**, which is wrong:
<example>
- submission.csv:
Id,SalePrice
1.733237550296372,-0.7385090666351347
1.7356102231920547,-0.2723912737214865
...
- sample_submission.csv:
Id,SalePrice
1461,169277.0524984
1462,187758.393988768
</example>
'''
                    return False, 16, false_info
    
    def test_column_names_cleaned_train(self, state: State):
        path = f"{state.competition_dir}/cleaned_train.csv"
        path1 = f"{state.competition_dir}/train.csv"
        df = pd.read_csv(path)
        df1 = pd.read_csv(path1)
        if list(df.columns) == list(df1.columns):
            return True, 17, "cleaned_train.csv and train.csv files have the same column names, unit test passed"
        else:
            return False, 17, f"cleaned_train.csv and train.csv files should have same column names and same column order. cleaned_train.csv has columns: {set(df1.columns)}, while train.csv has columns: {set(df.columns)}."
    
    def test_column_names_cleaned_test(self, state: State):
        path = f"{state.competition_dir}/cleaned_test.csv"
        path1 = f"{state.competition_dir}/test.csv"
        df = pd.read_csv(path)
        df1 = pd.read_csv(path1)
        if list(df.columns) == list(df1.columns):
            return True, 18, "cleaned_test.csv and test.csv files have the same column names, unit test passed"
        else:
            return False, 18, f"cleaned_test.csv and test.csv files should have same column names and same column order. cleaned_test.csv has columns: {set(df1.columns)}, while test.csv has columns: {set(df.columns)}."

    def test_column_names_processed_train(self, state: State):
        path = f"{state.competition_dir}/processed_train.csv"
        path1 = f"{state.competition_dir}/train.csv"
        df = pd.read_csv(path)
        df1 = pd.read_csv(path1)
        if list(df.columns) == list(df1.columns):
            return True, 19, "processed_train.csv and train.csv files have the same column names, unit test passed"
        else:
            return False, 19, f"processed_train.csv and train.csv files should have same column names and same column order. processed_train.csv has columns: {set(df1.columns)}, while train.csv has columns: {set(df.columns)}."
    
    def test_column_names_procesed_test(self, state: State):
        path = f"{state.competition_dir}/processed_test.csv"
        path1 = f"{state.competition_dir}/test.csv"
        df = pd.read_csv(path)
        df1 = pd.read_csv(path1)
        if list(df.columns) == list(df1.columns):
            return True, 20, "processed_test.csv and test.csv files have the same column names, unit test passed"
        else:
            return False, 20, f"processed_test.csv and test.csv files should have same column names and same column order. processed_test.csv has columns: {set(df1.columns)}, while test.csv has columns: {set(df.columns)}."
    
    def test_cleaned_train_first_column(self, state: State):
        path = f"{state.competition_dir}/cleaned_train.csv"
        df = pd.read_csv(path)
        path1 = f"{state.competition_dir}/train.csv"
        df1 = pd.read_csv(path1)
        # 比较两个 DataFrame 的第一列值是否相同
        if df.iloc[:, 0].equals(df1.iloc[:, 0]):
            return True, 21, "train.csv and cleaned_train.csv files have the same first column values"
        else:
            false_info = "cleaned_train.csv should have the same first column values as train.csv file"
            false_info += f'''
This is the first 10 lines of train.csv:
{df1.head(10)}
This is the first 10 lines of cleaned_train.csv:
{df.head(10)}
If you use some transformation on the features in train.csv, please make sure you have reversed the transformation before submitting the file.
Here is an example that specific transformation applied on features (ID, SalePrice) in cleaned_train.csv is **not reversed**, which is wrong:
<example>
- cleaned_train.csv:
Id,SalePrice
1.733237550296372,-0.7385090666351347
1.7356102231920547,-0.2723912737214865
...
- train.csv:
Id,SalePrice
1461,169277.0524984
1462,187758.393988768
</example>
'''
            return False, 21, false_info
        
    def test_cleaned_test_first_column(self, state: State):
        path = f"{state.competition_dir}/cleaned_test.csv"
        df = pd.read_csv(path)
        path1 = f"{state.competition_dir}/test.csv"
        df1 = pd.read_csv(path1)
        # 比较两个 DataFrame 的第一列值是否相同
        if df.iloc[:, 0].equals(df1.iloc[:, 0]):
            return True, 22, "test.csv and cleaned_test.csv files have the same first column values"
        else:
            false_info = "cleaned_test.csv should have the same first column values as test.csv file"
            false_info += f'''
This is the first 10 lines of test.csv:
{df1.head(10)}
This is the first 10 lines of cleaned_test.csv:
{df.head(10)}
If you use some transformation on the features in test.csv, please make sure you have reversed the transformation before submitting the file.
Here is an example that specific transformation applied on features (ID, SalePrice) in cleaned_test.csv is **not reversed**, which is wrong:
<example>
- cleaned_test.csv:
Id,SalePrice
1.733237550296372,-0.7385090666351347
1.7356102231920547,-0.2723912737214865
...
- test.csv:
Id,SalePrice
1461,169277.0524984
1462,187758.393988768
</example>
'''
            return False, 22, false_info
        
    def test_float_num_submission(self, state: State):
        path = f"{state.competition_dir}/submission.csv"
        path1 = f"{state.competition_dir}/sample_submission.csv"
        df = pd.read_csv(path)
        df1 = pd.read_csv(path1)
        # 检查每个浮点列的精度是否相同
        precision_issues = []
        for column in df.columns:
            if df[column].dtype in ['float64', 'float32'] and df1[column].dtype in ['float64', 'float32']:
                # 获取两个文件中列的最大精度
                precision1 = df[column].map(lambda x: len(str(x).split('.')[-1]) if '.' in str(x) else 0).max()
                precision2 = df1[column].map(lambda x: len(str(x).split('.')[-1]) if '.' in str(x) else 0).max()
                
                # 比较精度
                if precision1 != precision2:
                    precision_issues.append(f"Column '{column}' has different precisions: {precision1} vs {precision2}")

        if precision_issues:
            return False, 23, "Precision mismatch found in columns: " + ", ".join(precision_issues)
        else:
            return True, 23, "All float columns have matching precision, unit test passed"
    
    def test_file_size(self, state: State):
        max_size_mb = 100
        path = f"{state.competition_dir}/train.csv"
        file_size_mb = os.path.getsize(path) / (1024 * 1024)
        path = f"{state.competition_dir}/test.csv"
        file_size_mb += os.path.getsize(path) / (1024 * 1024)
        path = f"{state.competition_dir}/sample_submission.csv"
        file_size_mb += os.path.getsize(path) / (1024 * 1024)
        if file_size_mb < max_size_mb:
            return True, 24, "File size less than 100M, unit test passed"
        else:
            return False, 24, f"The three files are too large, the maximum allowed size is {max_size_mb}MB, the current size is {file_size_mb:.2f}MB."


if __name__ == '__main__':
    # llm = LLM('gpt-4o', 'api')
    # reply, history = llm.generate('try me a joke', history=None)
    # print(reply)
    test_tool = TestTool(memory=None, model='gpt-4o', type='api')
    test_tool._execute_tests()

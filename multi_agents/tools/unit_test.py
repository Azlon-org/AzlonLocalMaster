import os
import pandas as pd
import json
import chromadb
import sys
import re
import logging

sys.path.append('..')
sys.path.append('../..')
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# from memory import Memory, transfer_text_to_json
from memory import Memory
from llm import OpenaiEmbeddings, LLM
from state import State
from utils import load_config
from prompts.prompt_unit_test import *

class TestTool:
    def __init__(
        self, 
        memory: Memory = None,
        model: str = 'gpt-4o-mini',
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
                    if func_name == 'test_document_exist': # 如果文件不存在 直接返回 不进行后续unit test
                        return not_pass_tests
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
        Check if the required CSV documents exist in the data_dir.
        '''
        # Check in the state.competition_dir if the documents exist
        # Read all the files in the directory
        files = os.listdir(state.competition_dir)
        
        if state.phase == "Model Building, Validation, and Prediction":
            # Check for the existence of submission.csv
            required_file = "submission.csv"
            if required_file in files:
                return True, 2, f"{required_file} exists"
            else:
                return False, 2, f"{required_file} does not exist in {state.competition_dir}/"
        
        elif state.phase == "Data Cleaning":
            # Check for the existence of cleaned_train and cleaned_test
            required_files = ["cleaned_train", "cleaned_test"]
            required_files = ["cleaned_train.csv", "cleaned_test.csv"]
            missing_files = [file for file in required_files if not any(file in f for f in files)]
            
            if not missing_files:
                return True, 2, "cleaned_train.csv and cleaned_test.csv data exist"
            else:
                return False, 2, f"Missing files: {', '.join(missing_files)}, it should be saved in {state.competition_dir}/"
        
        elif state.phase == "Feature Engineering":
            # Check for the existence of processed_train and processed_test
            required_files = ["processed_train", "processed_test"]
            required_files = ["processed_train.csv", "processed_test.csv"]
            missing_files = [file for file in required_files if not any(file in f for f in files)]
            
            if not missing_files:
                return True, 2, "processed_train.csv and processed_test.csv data exist"
            else:
                return False, 2, f"Missing files: {', '.join(missing_files)}, it should be saved in {state.competition_dir}/"
        
        else:
            return True, 2, "Don't need to check the document in this phase"
    
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
            if f"submission.csv" in file:
                path = f"{state.competition_dir}/{file}"
                with open(path, 'r') as file:
                    if file.readable():
                        return True, 9, "submission.csv is readable, please continue to the next step of the process"
                    else:
                        return False, 9, "submission.csv is not readable, please try to reprocess it"

    def test_cleaned_train_no_missing_values(self, state: State):
        path = f"{state.competition_dir}/cleaned_train.csv"
        df = pd.read_csv(path)
        missing_info = df.isnull().sum()
        missing_columns = missing_info[missing_info > 0]
        
        if missing_columns.empty:
            return True, 10, "The cleaned_train.csv file has no missing values, please continue to the next step of the process"
        else:
            missing_details = []
            for col, count in missing_columns.items():
                percentage = (count / len(df)) * 100
                missing_details.append(f"{col}: {count} ({percentage:.2f}%)")
            
            return False, 10, f"There are missing values in the cleaned_train.csv file. Detailed missing value information:\n" + "\n".join(missing_details) + "\nDo NOT fill the missing values with another NaN-type value, such as 'None', 'NaN', or 'nan'."

    def test_cleaned_test_no_missing_values(self, state: State):
        path = f"{state.competition_dir}/cleaned_test.csv"
        df = pd.read_csv(path)
        missing_info = df.isnull().sum()
        missing_columns = missing_info[missing_info > 0]
        
        if missing_columns.empty:
            return True, 11, "The cleaned_test.csv file has no missing values, please continue to the next step of the process"
        else:
            missing_details = []
            for col, count in missing_columns.items():
                percentage = (count / len(df)) * 100
                missing_details.append(f"{col}: {count} ({percentage:.2f}%)")
            
            return False, 11, f"There are missing values in the cleaned_test.csv file. Detailed missing value information:\n" + "\n".join(missing_details) + "\nNOTE that apply the same methods as applied in cleaned_train.csv to deal with missing values."
    
    def test_processed_train_feature_number(self, state: State):
        def get_categorical_nunique_formatted(dataframe):
            categorical_columns = dataframe.select_dtypes(include=['object', 'category', 'bool']).columns
            nunique_counts = dataframe[categorical_columns].nunique().sort_values(ascending=False)
            formatted_output = "\n".join([f"{feature}    number of unique values: {count}" for feature, count in nunique_counts.items()])
            return formatted_output

        path = f"{state.competition_dir}/processed_train.csv"
        df = pd.read_csv(path)
        path_to_origin_train = f"{state.competition_dir}/cleaned_train.csv"
        df_origin = pd.read_csv(path_to_origin_train)
        result = "Valid"
        # input = PROMPT_TEST_PROCESSED_TRAIN_FEATURE_NUMBER.format(cleaned_features=df_origin.columns, processed_features=df.columns)
        # raw_reply, _ = self.llm.generate(input, history=None)
        # try:
        #     json_match = re.search(r'```json(.*)```', raw_reply, re.DOTALL)
        #     if json_match:
        #         json_str = json_match.group(1).strip()
        #         reply = json.loads(json_str)
        #         result = reply['result']
        #         reason = reply['reason']
        # except Exception as e:
        #     result = "Invalid"
        #     reason = ""
        if len(df.columns) <= 3 * len(df_origin.columns) and result == "Valid":
            return True, 12, f"The feature engineering phase is well performed."
        else:
            false_info = "There are too many features after handling features in the feature engineering phase."
            false_info += f'''processed_train.csv is the processed data of cleaned_train.csv after feature engineering.
During the feature engineering phase, improper feature handling has resulted in an excessive number of features. 
One possible reason is that during the feature processing, certain categorical features (such as brand, transmission, etc.) have too many categories, leading to a large number of features being generated after one-hot encoding.

Here is the information about the categorical features of cleaned_train.csv and their unique value counts:
Categorical features of cleaned_train.csv and their unique value counts:
{get_categorical_nunique_formatted(df_origin)}

Here is the information about the features of cleaned_train.csv:
{df_origin.columns}

Here is the information about the features of processed_train.csv:
{df.columns}
'''
            return False, 12, false_info

    def test_processed_test_feature_number(self, state: State):
        def get_categorical_nunique_formatted(dataframe):
            categorical_columns = dataframe.select_dtypes(include=['object', 'category', 'bool']).columns
            nunique_counts = dataframe[categorical_columns].nunique().sort_values(ascending=False)
            formatted_output = "\n".join([f"{feature}    number of unique values: {count}" for feature, count in nunique_counts.items()])
            return formatted_output

        path = f"{state.competition_dir}/processed_test.csv"
        df = pd.read_csv(path)
        path_to_origin_train = f"{state.competition_dir}/cleaned_test.csv"
        df_origin = pd.read_csv(path_to_origin_train)
        result = "Valid"
        if len(df.columns) <= 3 * len(df_origin.columns) and result == "Valid":
            return True, 13, f"The feature engineering phase is well performed."
        else:
            false_info = "There are too many features after handling features in the feature engineering phase."
            false_info += f'''processed_test.csv is the processed data of cleaned_test.csv after feature engineering.
During the feature engineering phase, improper feature handling has resulted in an excessive number of features. 
One possible reason is that during the feature processing, certain categorical features (such as brand, transmission, etc.) have too many categories, leading to a large number of features being generated after one-hot encoding.

Here is the information about the categorical features of cleaned_test.csv and their unique value counts:
Categorical features of cleaned_test.csv and their unique value counts:
{get_categorical_nunique_formatted(df_origin)}

Here is the information about the features of cleaned_test.csv:
{df_origin.columns}

Here is the information about the features of processed_test.csv:
{df.columns}
'''
            return False, 13, false_info

    def test_submission_no_missing_values(self, state: State):
        files = os.listdir(state.competition_dir)
        for file in files:
            if file == "submission.csv":
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
            if file == "submission.csv":
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
            if file == "submission.csv":
                path1 = f"{state.competition_dir}/{file}"
                df1 = pd.read_csv(path1)
                # 比较两个 DataFrame 的列名集合是否相同
                if list(df.columns) == list(df1.columns):
                    return True, 15, "submission.csv and sample_submission.csv files have the same column names, unit test passed"
                else:
                    return False, 15, f"submission.csv and sample_submission.csv files have different column names or different column order. submission.csv has columns: {set(df1.columns)}, while sample_submission.csv has columns: {set(df.columns)}."

    def test_submission_validity(self, state: State):
        # 检查submission.csv和sample_submission.csv的第一个列是否相同
        # 检查submission.csv的数值是否在sample_submission.csv的数值范围内
        # 要保证有submission.csv生成
        path = f"{state.competition_dir}/sample_submission.csv"
        df = pd.read_csv(path)
        files = os.listdir(state.competition_dir)
        false_info = ""
        path1 = f"{state.competition_dir}/submission.csv"
        df1 = pd.read_csv(path1)
        input = PROMPT_TEST_SUBMISSION_VALIDITY.format(sample_head=df.head(10), submission_head=df1.head(10))
        raw_reply, _ = self.llm.generate(input, history=None)
        try:
            json_match = re.search(r'```json(.*)```', raw_reply, re.DOTALL)
            if json_match:
                json_str = json_match.group(1).strip()
                reply = json.loads(json_str)
                result = reply['result']
                reason = reply['reason']
        except Exception as e:
            logging.error(f"JSON decoding error: {e}")
            result = "Invalid"
            reason = ""
        # 比较两个 DataFrame 的第一列值是否相同
        if df.iloc[:, 0].equals(df1.iloc[:, 0]) and result == "Valid":
            return True, 16, "submission.csv is valid."
        else:
            false_info = f"submission.csv is not valid. {reason}"
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

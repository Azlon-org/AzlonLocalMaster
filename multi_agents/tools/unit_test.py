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
        return True, 1, "cool example"
    
    
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
            required_files = ["cleaned_train.csv", "cleaned_test.csv"]
            missing_files = [file for file in required_files if not any(file in f for f in files)]
            
            if not missing_files:
                return True, 2, "cleaned_train.csv and cleaned_test.csv data exist"
            else:
                return False, 2, f"Missing files: {', '.join(missing_files)}, it should be saved in {state.competition_dir}/"
        
        elif state.phase == "Feature Engineering":
            # Check for the existence of processed_train and processed_test
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
                return True, 7, "cleaned_train.csv is readable"
            else:
                return False, 7, "cleaned_train.csv is not readable"

    def test_readable_cleaned_test(self, state: State):
        path = f"{state.competition_dir}/cleaned_test.csv"
        with open(path, 'r') as file:
            if file.readable():
                return True, 8, "cleaned_test.csv is readable"
            else:
                return False, 8, "cleaned_test.csv is not readable"

    def test_readable_submission(self, state: State):
        files = os.listdir(state.competition_dir)
        for file in files:
            if f"submission" in file:
                path = f"{state.competition_dir}/{file}"
                with open(path, 'r') as file:
                    if file.readable():
                        return True, 9, "submission.csv is readable"
                    else:
                        return False, 9, "submission.csv is not readable"

    def test_cleaned_train_no_missing_values(self, state: State):
        path = f"{state.competition_dir}/cleaned_train.csv"
        df = pd.read_csv(path)
        if df.isnull().sum().sum() == 0:
            return True, 10, "The cleaned_train.csv file has no missing values"
        else:
            return False, 10, "There are missing values in the cleaned_train.csv file"

    def test_cleaned_test_no_missing_values(self, state: State):
        path = f"{state.competition_dir}/cleaned_test.csv"
        df = pd.read_csv(path)
        if df.isnull().sum().sum() == 0:
            return True, 11, "The cleaned_test.csv file has no missing values"
        else:
            return False, 11, "There are missing values in the cleaned_test.csv file"

    def test_submission_no_missing_values(self, state: State):
        files = os.listdir(state.competition_dir)
        for file in files:
            if "submission" in file and "sample" not in file:
                path = f"{state.competition_dir}/{file}"
                df = pd.read_csv(path)
                if df.isnull().sum().sum() == 0:
                    return True, 12, "The submission.csv file has no missing values"
                else:
                    return False, 12, "There are missing values in the submission.csv file"

    def test_image_num(self, state: State):
        image_count = 0
        if "Preliminary Exploratory Data Analysis" in state.phase:
            path = f"{state.competition_dir}/pre_eda/images"
        elif "In-depth Exploratory Data Analysis" in state.phase:
            path = f"{state.competition_dir}/deep_eda/images"
        else:
            return True, 13, "No need to check the number of images at this stage"
            # 遍历指定目录
        for entry in os.scandir(path):
            if entry.is_file() and entry.name.lower().endswith(('.png', '.jpg', '.jpeg', '.bmp', '.gif', '.tiff')):
                image_count += 1
        if image_count > 10:
            return False, 13, "Number of images is greater than 10"
        else:
            return True, 13, "Number of images is less than or equal to 10"
    
    def test_file_num(self, state: State):
        path = f"{state.competition_dir}/sample_submission.csv"
        df = pd.read_csv(path)
        files = os.listdir(state.competition_dir)
        for file in files:
            if "submission" in file and "sample" not in file:
                path1 = f"{state.competition_dir}/{file}"
                df1 = pd.read_csv(path1)
                if len(df) == len(df1):
                    return True, 14, "submission.csv and sample_submission.csv files have the same number of rows"
                else:
                    return False, 14, "submission.csv and sample_submission.csv files have different number of rows"
    
    def test_column_names(self, state: State):
        path = f"{state.competition_dir}/sample_submission.csv"
        df = pd.read_csv(path)
        files = os.listdir(state.competition_dir)
        for file in files:
            if "submission" in file and "sample" not in file:
                path1 = f"{state.competition_dir}/{file}"
                df1 = pd.read_csv(path1)
                # 比较两个 DataFrame 的列名集合是否相同
                if set(df.columns) == set(df1.columns):
                    return True, 15, "submission.csv and sample_submission.csv files have the same column names"
                else:
                    return False, 15, "submission.csv and sample_submission.csv files have different column names"

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
                
'''
4. 测试ID的唯一性
   - 确保 `id` 列中的值是唯一的，没有重复。

    ```python
    def test_submission_unique_ids():
        df = pd.read_csv('submission.csv')
        assert df['id'].is_unique, "id 列中有重复值"
    ```

5. 测试预测值的有效性
   - 检查 `prediction` 列中的值是否在合理范围内（例如是否为数值类型或是否在特定范围内）。

    ```python
    def test_submission_predictions_validity():
        df = pd.read_csv('submission.csv')
        assert df['prediction'].dtype in [int, float], "prediction 列中的值不是数值类型"
        assert df['prediction'].min() >= 0, "prediction 列中的值小于0"
        assert df['prediction'].max() <= 1, "prediction 列中的值大于1"
    ```

7. 测试文件编码
   - 确保 `submission.csv` 文件的编码格式正确（例如 UTF-8）。

    ```python
    def test_submission_encoding():
        with open('submission.csv', 'r', encoding='utf-8') as file:
            try:
                file.read()
            except UnicodeDecodeError:
                assert False, "submission.csv 文件不是 UTF-8 编码"
    ```

8. 文件大小检查
   - 确保 `submission.csv` 文件的大小在比赛允许的范围内。如果文件过大，可能会被拒绝上传或评分系统处理时出错。

    ```python
    def test_submission_file_size(max_size_mb):
        file_size_mb = os.path.getsize('submission.csv') / (1024 * 1024)
        assert file_size_mb <= max_size_mb, f"文件过大，最大允许大小为 {max_size_mb}MB，当前大小为 {file_size_mb:.2f}MB"
    ```

9. 预测结果格式一致性
   - 确保 `prediction` 列中的所有值都具有相同的格式，例如所有预测值均为浮点数或整数，或者所有字符串具有相同的模式。

    ```python
    def test_submission_predictions_format():
        df = pd.read_csv('submission.csv')
        assert all(isinstance(x, float) for x in df['prediction']), "prediction 列中存在非浮点数的值"
    ```

10. ID顺序检查
    - 在某些比赛中，`id` 列可能需要按特定顺序排列（例如按升序）。检查是否符合要求。

    ```python
    def test_submission_id_order():
        df = pd.read_csv('submission.csv')
        assert all(df['id'] == sorted(df['id'])), "id 列未按顺序排列"
    ```

11. 文件行尾换行符检查
    - 确保 `submission.csv` 文件中每一行的末尾都包含换行符，特别是在某些严格要求格式的比赛中。

    ```python
    def test_submission_line_endings():
        with open('submission.csv', 'rb') as file:
            lines = file.readlines()
            assert all(line.endswith(b'\n') for line in lines), "某些行未以换行符结束"
    ```

12. 列的顺序检查
    - 确保文件中的列按照比赛要求的顺序排列，有些比赛会严格要求列的顺序。

    ```python
    def test_submission_column_order():
        required_order = ['id', 'prediction']  # 根据具体比赛需求调整列顺序
        df = pd.read_csv('submission.csv')
        assert list(df.columns) == required_order, f"列顺序不正确，当前顺序为 {list(df.columns)}"
    ```

13. 文件的换行符格式
    - 确保使用适当的换行符格式（例如 Windows 的 CRLF 或 Unix 的 LF），特别是在特定格式要求的比赛中。

    ```python
    def test_submission_line_ending_format():
        with open('submission.csv', 'rb') as file:
            content = file.read()
            assert b'\r\n' in content or b'\n' in content, "文件中的换行符格式不正确"
    ```

14. 文件编码中的BOM
    - 检查文件是否包含不需要的字节顺序标记 (BOM)，它可能会导致评分系统误判。

    ```python
    def test_submission_no_bom():
        with open('submission.csv', 'rb') as file:
            content = file.read()
            assert not content.startswith(b'\xef\xbb\xbf'), "文件包含BOM (字节顺序标记)，可能导致问题"
    ```

15. 预测值精度
    - 确保 `prediction` 列中的数值具有适当的精度。例如，可能需要确保小数点后不超过一定位数。

    ```python
    def test_submission_prediction_precision(max_decimal_places):
        df = pd.read_csv('submission.csv')
        for value in df['prediction']:
            if isinstance(value, float):
                assert len(str(value).split('.')[1]) <= max_decimal_places, f"预测值精度超过 {max_decimal_places} 位"
    ```

16. 预测值的重复性
    - 确保预测值没有不合理的重复，这可能暗示模型出现了问题（如过度拟合或数据泄露）。

    ```python
    def test_submission_no_unreasonable_duplicates():
        df = pd.read_csv('submission.csv')
        duplicate_count = df['prediction'].duplicated().sum()
        assert duplicate_count < len(df) * 0.1, "预测值中有大量重复，这可能不合理"
    ```
'''


if __name__ == '__main__':
    # llm = LLM('gpt-4o', 'api')
    # reply, history = llm.generate('try me a joke', history=None)
    # print(reply)
    test_tool = TestTool(memory=None, model='gpt-4o', type='api')
    test_tool._execute_tests()

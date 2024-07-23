import sys
import os
import pdb
import json
import timeout_decorator

sys.path.append('..')
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from utils import read_file, multi_chat, read_image, extract_and_run_code, PREFIX_STRONG_BASELINE
from prompt import STEPS_IN_CONTEXT_TEMPLATE, PROMPT_ERROR_CORRECTION_TEMPLATE

@timeout_decorator.timeout(600)
def data_cleaning(competition, competition_info, i, store_history=False):
    prefix = PREFIX_STRONG_BASELINE
    competition_name = competition.replace('_', ' ')
    path_to_pre_eda = f'{prefix}/{competition}/submission_{i}/pre_eda'
    path_to_data_cleaning = f'{prefix}/{competition}/submission_{i}/data_cleaning'
    steps_in_context = STEPS_IN_CONTEXT_TEMPLATE.format(competition_name=competition_name)

    with open(f'/mnt/d/PythonProjects/AutoKaggleMaster/competition_to_files.json', 'r') as f:
        data = json.load(f)
    files = data[competition]
    file_str = ', '.join(files)

    PROMPT_DATA_CLEANING = f'''
# CONTEXT
{steps_in_context}
So far I have completed the first two steps to get competition information on Background/Files/Question/Target_Variable/Evaluation/Other ([COMPETITION INFORMATION]) and the code and explanation for the step Preliminary Exploratory Data Analysis (Preliminary EDA) ([PRELIMINARY EDA]). Currently working on the Data Cleaning step. Meanwhile, {file_str} are all in '{prefix}/{competition}/' folder.
#############
# COMPETITION INFORMATION #
{competition_info}
#############
# OBJECTIVE #
I will provide you with [COMPETITION INFORMATION], all the code, explanations and insight for the Preliminary Exploratory Data Analysis (Preliminary EDA) step, all the features of the data and the first 10 data entries of the training set. Please complete the Data Cleaning step, you must write the code with appropriate explanations and ensure the output new code is executable in the same Jupyter notebook with the previous tasks code have been executed, but do not run the code.
# CONSTRAINTS #
- Always use `print()` function if you need to print a value.
- Always validate and process data types during data handling. Before calculating the correlation matrix, make sure the dataset exclusively contains numeric data. If any non-numeric data is present, handle it appropriately by either removing or processing them.
- Always apply the same modifications to both the training and test sets.
    - Note that the test dataset does not have the target variable.
- Always copy the DataFrame before processing it and use the copy to process.
- Always save the cleaned training and test datasets as 'cleaned_train.csv' and 'cleaned_test.csv' respectively in '{prefix}/{competition}/submission_{i}/'.
- Always write some `assert` statements to check the correctness of the code and the success of Data Cleaning step.
#############
# RESPONSE: BLOCK (CODE & EXPLANATION) #
BLOCK 1:
CODE
EXPLANATION
BLOCK 2:
CODE
EXPLANATION
...
#############
# START ANALYSIS #
If you understand, please request the code, explanation and insight of step Preliminary Exploratory Data Analysis (Preliminary EDA) from me.
'''
    # path_to_train = f'{prefix}/{competition}/train.csv'
    train_files = []
    for file in os.listdir(f'{prefix}/{competition}/'):
        file_path = os.path.join(f'{prefix}/{competition}/', file)
        if 'train' in file and file.endswith('.csv') and os.path.isfile(file_path):
            train_files.append(file_path)
    assert len(train_files) == 1, "There should be only one training file in the competition folder."
    path_to_train = train_files[0]
    path_to_pre_eda_code = f'{path_to_pre_eda}/pre_eda_code.txt'
    path_to_pre_eda_insight = f'{path_to_pre_eda}/pre_eda_insight.txt'
    features = read_file(path_to_train)[0]
    train_first_10 = read_file(path_to_train)[1:11]
    pre_eda_code = read_file(path_to_pre_eda_code)
    pre_eda_insight = read_file(path_to_pre_eda_insight)
    EXAMPLES = f'''
#############
# PRELIMINARY EDA #
{pre_eda_code}
#############
# INSIGHT FROM PRELIMINARY EDA #
{pre_eda_insight}
#############
# ALL FEATURES #
{features}
#############
# FIRST 10 DATA ENTRIES #
{train_first_10}    
'''

    history = []
    round = 0
    max_tries = 5

    # Multi-round chat to complete the Data Cleaning step
    while round <= 1+max_tries:
        if round == 0:
            print("Step 3 is in progress.")
            user_input = PROMPT_DATA_CLEANING
            reply, history = multi_chat(user_input, history)
            print("Request for features, data samples and previous code.") 
        elif round == 1:
            user_input = EXAMPLES
            reply, history = multi_chat(user_input, history)
            print("Features, data samples and previous code are being sent to GPT-4O. Get code about Data Cleaning.")
            # print("GPT-4O:", reply)
        elif round > 1:
            data_cleaning_code = history[-1].get('content', "EMPTY REPLY.")
            pre_eda_code_clean = pre_eda_code.replace('print', '# print') \
                                            .replace('plt.save', '# plt.save') \
                                            .replace('plt.show', '# plt.show') # Comment out the print statements
            with open(f'{path_to_data_cleaning}/data_cleaning_code.txt', 'w', encoding='utf-8') as f_w:
                f_w.write(pre_eda_code_clean + '\n\n\n' +data_cleaning_code)

            print(f"The {round-1}th try.")
            error_flag = extract_and_run_code(competition, path_to_competition_step=path_to_data_cleaning) # Run the code and check for errors
            if error_flag:
                data_cleaning_error = read_file(f'{path_to_data_cleaning}/data_cleaning_error.txt')
                data_cleaning_output = read_file(f'{path_to_data_cleaning}/data_cleaning_output.txt')
                user_input = PROMPT_ERROR_CORRECTION_TEMPLATE.format(output_messages=data_cleaning_output, error_messages=data_cleaning_error)
                reply, history = multi_chat(user_input, history)
            else:
                break
        round += 1

    if store_history:
        with open(f'{path_to_data_cleaning}/data_cleaning_history.json', 'w', encoding='utf-8') as f_w:
            json.dump(history, f_w, ensure_ascii=False, indent=4)

    data_cleaning_flag = True
    if round < 2+max_tries:
        print("Success in Step 3.")
    else:
        print("Failure in Step 3.")
        data_cleaning_flag = False
    return data_cleaning_flag

if __name__ == '__main__':
    competition_info = {
        "background_analysis": {
            "competition_description": "This competition challenges participants to predict the final price of residential homes in Ames, Iowa, using a dataset that includes 79 explanatory variables. The competition is ideal for those with basic knowledge of R or Python and machine learning.",
            "dataset_acknowledgement": "The Ames Housing dataset, compiled by Dean De Cock, is used in this competition. It serves as a modern alternative to the Boston Housing dataset and is widely used for data science education.",
            "practice_skills": ["Creative feature engineering", "Advanced regression techniques like random forest and gradient boosting"]
        },
        "question_analysis": {
            "question_definition": "The task is to predict the sales price for each house in the test set.",
            "question_requirement": "Participants must predict the value of the SalePrice variable for each Id in the test set."
        },
        "target_variable_analysis": {
            "target_variable": "SalePrice",
            "description": "The target variable to predict is the SalePrice of each house."
        },
        "evaluation_analysis": {
            "evaluation_metric": "Submissions are evaluated using the Root-Mean-Squared-Error (RMSE) between the logarithm of the predicted value and the logarithm of the observed sales price. This log transformation ensures that errors in predicting expensive and cheap houses affect the result equally.",
            "submission_format": "The submission file must be in CSV format with a header and should follow this structure:\n\n```\nId,SalePrice\n1461,169000.1\n1462,187724.1233\n1463,175221\netc.\n```"
        },
        "other_analysis": {
            "competition_type": "This is a Getting Started competition on Kaggle, meant for beginners in data science and machine learning.",
            "resources": [
                "Getting Started Notebook: [starter notebook](https://www.kaggle.com/code/gusthema/house-prices-prediction-using-tfdf/notebook)",
                "Kaggle Learn: [Machine Learning Course](https://www.kaggle.com/learn/machine-learning)"
            ],
            "community_support": "Participants are encouraged to use the [House Prices discussion forum](https://www.kaggle.com/c/house-prices-advanced-regression-techniques/discussion) for support and collaboration."
        }
    }
    competition = 'house_prices'
    data_cleaning(competition, competition_info, i=0)
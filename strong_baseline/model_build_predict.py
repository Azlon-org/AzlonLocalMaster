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
def model_build_predict(competition, competition_info, i, store_history=False):
    competition_name = competition.replace('_', ' ')
    prefix = PREFIX_STRONG_BASELINE
    path_to_feature_engineering = f'{prefix}/{competition}/submission_{i}/feature_engineering'
    path_to_model_build_predict = f'{prefix}/{competition}/submission_{i}/model_build_predict'
    steps_in_context = STEPS_IN_CONTEXT_TEMPLATE.format(competition_name=competition_name)

    with open(f'/mnt/d/PythonProjects/AutoKaggleMaster/competition_to_files.json', 'r') as f:
        data = json.load(f)
    files = data[competition]
    file_str = ', '.join(files)

    PROMPT_MODEL_BUILD_PREDICT = f'''
# CONTEXT
{steps_in_context}
So far I have completed the previous five steps to get competition information on Background/Files/Question/Target_Variable/Evaluation/Other ([COMPETITION INFORMATION]), the code and explanation for Preliminary Exploratory Data Analysis (Preliminary EDA), Data Cleaning, In-depth Exploratory Data Analysis (In-depth EDA) and Feature Engineering. Currently working on the Model Building, Validation, and Prediction step. Meanwhile, processed_train.csv and processed_test.csv are in '{prefix}/{competition}/submission_{i}/', other files ({file_str}) are all in '{prefix}/{competition}/' folder.
#############
# COMPETITION INFORMATION #
{competition_info}
#############
# OBJECTIVE #
I will provide you with all the code and explanations for the [COMPETITION INFORMATION], Preliminary Exploratory Data Analysis (Preliminary EDA), Data Cleaning, In-depth Exploratory Data Analysis (In-depth EDA) and Feature Engineering steps, all the features of the data and the first 10 data entries of the processed training set. Please complete the Model Building, Validation, and Prediction step, you must write the code with appropriate explanations and make sure that the output new code is executable in the same Jupyter notebook as the previous task code has been executed, but do not run the code.
# CONSTRAINTS #
- If attribute like `Id` is in the test set, the prediction result should have exactly the same attribute (`Id` or attribute represents the index of the data entry) as the test set.
    - You MUST write code to ensure this requirement.
- Always use `print()` function if you need to print a value.
    - I commented out the print/plt.show/plt.savefig statements from the previous code to prevent interfering with the output of this step, you don't need to comment them out when writing the code.
- Always save the prediction result as 'submission.csv' in folder '{prefix}/{competition}/submission_{i}/'.
- Always write some `assert` statements to check the correctness of the code and the success of Model Building, Validation and Prediction step.
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
If you understand, please request the code and explanation of previous steps, all the features of the data, and the first 10 data entries of the processed training set from me.
'''
    path_to_processed_train = f'{prefix}/{competition}/submission_{i}/processed_train.csv'
    path_to_feature_engineering_code = f'{path_to_feature_engineering}/feature_engineering_code.txt'
    features = read_file(path_to_processed_train)[0]
    processed_train_first_10 = read_file(path_to_processed_train)[1:11]
    feature_engineering_code = read_file(path_to_feature_engineering_code)
    EXAMPLES = f'''
#############
# PRELIMINARY EDA & DATA CLEANING & In-depth EDA & FEATURE ENGINEERING #
{feature_engineering_code}
#############
# ALL FEATURES #
{features}
#############
# FIRST 10 DATA ENTRIES (PROCESSED) #
{processed_train_first_10}
'''
    history = []
    round = 0
    max_tries = 5

    # Multi-round chat to complete the Model Building, Validation, Prediction step
    while round <= 1+max_tries:
        if round == 0:
            print("Step 6 is in progress.")
            user_input = PROMPT_MODEL_BUILD_PREDICT
            reply, history = multi_chat(user_input, history)
            print("Request for features, data samples and previous code.") 
        elif round == 1:
            user_input = EXAMPLES
            reply, history = multi_chat(user_input, history)
            print("Features, data samples and previous code are being sent to GPT-4O. Get code about Model Building, Validation and Prediction.")
            # print("GPT-4O:", reply)
        elif round > 1:
            model_build_predict_code = history[-1].get('content', "EMPTY REPLY.")
            feature_engineering_code_clean = feature_engineering_code.replace('# print', 'print') \
                                            .replace('print', '# print') \
                                            .replace('# plt.save', 'plt.save') \
                                            .replace('plt.save', '# plt.save') \
                                            .replace('# plt.show', 'plt.show') \
                                            .replace('plt.show', '# plt.show') # Comment out the print statements
            with open(f'{path_to_model_build_predict}/model_build_predict_code.txt', 'w', encoding='utf-8') as f_w:
                f_w.write(feature_engineering_code_clean + '\n\n\n' + model_build_predict_code)

            print(f"The {round-1}th try.")
            error_flag = extract_and_run_code(competition, path_to_competition_step=path_to_model_build_predict) # Run the code and check for errors
            if error_flag:
                model_build_predict_error = read_file(f'{path_to_model_build_predict}/model_build_predict_error.txt')
                model_build_predict_output = read_file(f'{path_to_model_build_predict}/model_build_predict_output.txt')
                user_input = PROMPT_ERROR_CORRECTION_TEMPLATE.format(output_messages=model_build_predict_output, error_messages=model_build_predict_error)
                reply, history = multi_chat(user_input, history)
            else:
                break
        round += 1

    if store_history:
        with open(f'{path_to_model_build_predict}/model_build_predict_history.json', 'w', encoding='utf-8') as f_w:
            json.dump(history, f_w, ensure_ascii=False, indent=4)

    model_build_predict_flag = True
    if round < 2+max_tries:
        print("Success in Step 6.")
    else:
        print("Failure in Step 6.")
        model_build_predict_flag = False
    return model_build_predict_flag

if __name__ == '__main__':
    competition = 'house_prices'
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
    model_build_predict(competition, competition_info)
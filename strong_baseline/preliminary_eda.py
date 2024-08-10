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
def preliminary_eda(competition, competition_info, i, store_history=False):
    competition_name = competition.replace('_', ' ')
    prefix = PREFIX_STRONG_BASELINE
    path_to_pre_eda = f'{prefix}/{competition}/submission_{i}/pre_eda'
    steps_in_context = STEPS_IN_CONTEXT_TEMPLATE.format(competition_name=competition_name)

    with open(f'/mnt/d/PythonProjects/AutoKaggleMaster/competition_to_files.json', 'r') as f:
        data = json.load(f)
    files = data[competition]
    file_str = ', '.join(files)

    PROMPT_PRELIMINARY_EDA = f'''
# CONTEXT #
{steps_in_context}
Currently I have completed the first step of Background Understanding and got competition information ([COMPETITION INFORMATION]) on Background/Question/Target_Variable/Evaluation/Other and am proceeding with the step of Preliminary Exploratory Data Analysis (Preliminary EDA) step. Meanwhile, {file_str} are all in '{prefix}/{competition}/' folder.
#############
# COMPETITION INFORMATION #
{competition_info}
#############
# TASK #
I will provide you with [COMPETITION INFORMATION], all the features of the data and the first 10 data entries of the training set. Please complete the Preliminary Exploratory Data Analysis (Preliminary EDA) step, you must write the code and give proper explanations, but do not run the code.
#############
# CONSTRAINTS #
- Alway save data analysis charts with clear and meaningful titles in the '{path_to_pre_eda}/images/' folder.
- Always set `annot=False` if there are many features involved when drawing a heatmap.
- Always use `print()` function if you need to print a value.
- Always validate and process data types during data handling. Before calculating the correlation matrix, make sure the dataset exclusively contains numeric data. If any non-numeric data is present, handle it appropriately by either removing or processing them.
- Always apply the same modifications to both the training and test sets.
    - Note that the test dataset does not have the target variable.
- Always copy the DataFrame before processing it and use the copy to process.
- Always write some `assert` statements to check the correctness of the code and the success of Preliminary EDA step.
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
If you understand, please request all the features of the data, and the first 10 data entries of the training set from me.
'''
    train_files = []
    for file in os.listdir(f'{prefix}/{competition}/'):
        file_path = os.path.join(f'{prefix}/{competition}/', file)
        if 'train' in file and file.endswith('.csv') and os.path.isfile(file_path):
            train_files.append(file_path)
    assert len(train_files) == 1, "There should be only one training file in the competition folder."
    path_to_train = train_files[0]
    # path_to_train = f'{prefix}/{competition}/train.csv'
    features = read_file(path_to_train)[0]
    train_first_10 = read_file(path_to_train)[1:11]
    EXAMPLES = f'''
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

    # Multi-round chat to complete the Preliminary EDA step
    while round <= 1+max_tries:
        if round == 0:
            print("Step 2 is in progress.")
            user_input = PROMPT_PRELIMINARY_EDA  
            reply, history = multi_chat(user_input, history)
            print("Request for features and data samples.") 
        elif round == 1:
            user_input = EXAMPLES
            reply, history = multi_chat(user_input, history)
            print("Features and data samples are being sent to GPT-4O. Get code about Preliminary EDA.")
            # print("GPT-4O:", reply)
        elif round > 1:
            pre_eda_code = history[-1].get('content', "EMPTY REPLY.")
            with open(f'{path_to_pre_eda}/pre_eda_code.txt', 'w', encoding='utf-8') as f_w:
                f_w.write(pre_eda_code)

            print(f"The {round}th try.")
            error_flag = extract_and_run_code(competition, path_to_competition_step=path_to_pre_eda) # Run the code and check for errors
            if error_flag:
                pre_eda_error = read_file(f'{path_to_pre_eda}/pre_eda_error.txt')
                pre_eda_output = read_file(f'{path_to_pre_eda}/pre_eda_output.txt')
                user_input = PROMPT_ERROR_CORRECTION_TEMPLATE.format(output_messages=pre_eda_output, error_messages=pre_eda_error)
                reply, history = multi_chat(user_input, history)
            else:
                break
        round += 1

    if store_history:
        with open(f'{path_to_pre_eda}/pre_eda_history.json', 'w', encoding='utf-8') as f_w:
            json.dump(history, f_w, ensure_ascii=False, indent=4)

    pre_eda_flag = True
    if round < 2+max_tries:
        print("Success in Step 2.")
    else:
        print("Failure in Step 2.")
        pre_eda_flag = False
    return pre_eda_flag

def get_insight_pre_eda(competition, i):
    print("Getting insights from Preliminary EDA.")
    competition_name = competition.replace('_', ' ')
    prefix = PREFIX_STRONG_BASELINE
    path_to_pre_eda = f'{prefix}/{competition}/submission_{i}/pre_eda'
    path_to_pre_eda_images = f'{path_to_pre_eda}/images'
    image_files = []
    for file in os.listdir(path_to_pre_eda_images):
        image_files.append(file)

    steps_in_context = STEPS_IN_CONTEXT_TEMPLATE.format(competition_name=competition_name)
    PROMPT_ANALYZE_IMAGE_PRE_EDA = f'''
# CONTEXT #
{steps_in_context}
Currently I have completed the second step of Preliminary EDA and get some data analysis images.
#############
# TASK #
Please carefully analyze this data analysis chart and summarize the important information it contains to assist with the next step of Data Cleaning.
'''
    images_info = []
    if len(image_files) > 0: # If Step 2 generates data analysis images
        for image in image_files:
            image_analysis = {}
            image_path = f'{path_to_pre_eda_images}/{image}'
            reply = read_image(PROMPT_ANALYZE_IMAGE_PRE_EDA, image_path)
            image_analysis['image'] = image
            image_analysis['analysis'] = reply
            images_info.append(image_analysis)
    else:
        images_info = "No analysis."

    pre_eda_code = read_file(f'{path_to_pre_eda}/pre_eda_code.txt')
    pre_eda_output = read_file(f'{path_to_pre_eda}/pre_eda_output.txt')
    PROMPT_GET_INSIGHT_PRE_EDA = f'''
# CONTEXT #
{steps_in_context}
Currently I have completed the second step of Preliminary EDA, get some data analysis images and output information.
#############
# TASK #
I will provide you with code and explanations in Preliminary EDA step ([PRELIMINARY EDA CODE]), the output information after code execution ([PRELIMINARY EDA OUTPUT]) and detailed analysis about data analysis images ([ANALYSIS OF IMAGES]). Please summarize the insights obtained after this step is completed comprehensively but concisely to help with the next step of Data Cleaning (Less than 300 words).
#############
# PRELIMINARY EDA CODE #
{pre_eda_code}
#############
# PRELIMINARY EDA OUTPUT #
{pre_eda_output}
#############
# ANALYSIS OF IMAGES #
{images_info}
'''
    history = []
    user_input = PROMPT_GET_INSIGHT_PRE_EDA
    reply, history = multi_chat(user_input, history)

    with open(f'{path_to_pre_eda}/pre_eda_insight.txt', 'w', encoding='utf-8') as f_w:
        f_w.write(reply)

    return reply


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
    pre_eda_flag = preliminary_eda(competition, competition_info, i=0)
    pre_eda_insight = get_insight_pre_eda(competition, i=0)
    # print(pre_eda_insight)


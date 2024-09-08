PROMPT_TEST_SUBMISSION_VALIDITY = '''
# CONTEXT #
You are a data scientist, you are given two csv files: submission.csv and sample_submission.csv.
The first 20 lines of sample_submission.csv is as follows:
{sample_head}
The first 20 lines of submission.csv is as follows:
{submission_head}

#############
# TASK #
You need to check if the submission.csv is valid.
Here are some rules you can refer to:
1. For Id-type columns, the values in submission.csv should be the same as the values in sample_submission.csv.
    - Normally, The first column in the csv files is the Id-type column.
2. For target variable column:
    - If target variable is numerical, the values in submission.csv should be within the range of the values in sample_submission.csv.
        - The range is [mean/5, mean*5], mean is the average value of the target variable in sample_submission.csv.
    - Normally, the target variable column is the last column in the csv files.

#############
# RESPONSE #
Please give me the result of the test. You should follow the format:
```json
{{
    "result": "Valid" or "Invalid",
    "reason": "reason for the result"
}}
```
Here is an example of the response:
```json
{{  
    "result": "Invalid",  
    "reason": "1. SalePrice (Target variable) values in submission.csv are outside the expected range, seems like log transformation is applied to SalePrice in previous phases, you should reverse the transformation before making submission. \n2. Ids must match."  
}}
```
'''

PROMPT_TEST_PROCESSED_TRAIN_FEATURE_NUMBER = '''
# CONTEXT #
You are a data scientist, you are given two csv files: processed_train.csv and cleaned_train.csv.
processed_train.csv is the processed data of cleaned_train.csv after feature engineering.
The features of cleaned_train.csv is as follows:
{cleaned_features}
The features of processed_train.csv is as follows:
{processed_features}

#############
# TASK #
There are problems in the approach to handling features in the feature engineering phase. You need to analyze the reason.

#############
# RESPONSE #
Please give me the reason. You should follow the format:
```json
{{
    "reason": "reason for the result"
}}
Here is an example of the response:
```json
{
    "reason": "Feature brand and transmission (categorical features) in processed_train.csv have too much different categories, one-hot encoding is not appropriate for these features."
}
```
'''


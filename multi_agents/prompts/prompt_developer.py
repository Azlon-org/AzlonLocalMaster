PROMPT_DEVELOPER_TASK = '''
Develop a solution based on the plan provided by the Planner. Implement the specific tasks outlined in the plan, ensuring that the code is clear, concise, and efficient. You must consider the data types, project requirements, and resource constraints. Ensure that the code is well-documented and can be easily understood by others.
'''


PROMPT_DEVELOPER_CONSTRAINTS = '''
## FILE SAVE PATH ##
- Always save the image file in the `{restore_path}/images/` directory.
- Always save the data file in the `{competition_path}/` directory.
## FILE NAME ##
- Always name the image file with clear and meaningful names related to the content which makes it easy to understand.
- Always choose the correct name for data file from the following options: `cleaned_train.csv`, `cleaned_test.csv`, `processed_train.csv`, `processed_test.csv`. Note you are in step: {step_name}.
## RESOURCE CONSTRAINTS ##
- Always consider the runtime and efficiency of your code when writing code, especially for data visualization, handling large datasets, or complex algorithms.
<example>
Data visualization: When using libraries such as seaborn or matplotlib to create plots, consider turning off unnecessary details (e.g., annot=False in heatmaps), especially when the number of data points is large.
</example>
- Always consider resource constraints and limit the number of generated images to ensure that they do not exceed 10 when performing Exploratory Data Analysis (EDA), 
    - **Note that the generated images should be LIMITED to the most critical visualizations that provide valuable insights.**
## CODING RULES ##
- Always use `print()` function if you need to print a value. 
- Always use `plt.close()` to close the figure after saving the image.
- Always make sure that the data types of each column in the dataset are correct before performing any data computation, analysis, or other operations.
<example>
- Before calculating a correlation matrix, confirm that the dataset only contains numerical data. If there is non-numerical data, handle it appropriately, such as by removing or converting it to numerical data.
- Before performing data merging or joining operations, ensure that the data types of all relevant columns are consistent to avoid errors caused by type mismatches.
</example>
- At each critical step of writing code, always reasonable `assert` statements to verify the correctness of the code segments and the successful execution of step {step_name}.
<example>
After data cleaning, you can use assert statements to check whether the cleaned dataset is empty or if the data types of specific columns meet expectations.
</example>
- Always ensure that the same modifications, such as feature scaling, missing value handling, and categorical variable encoding, are applied to both the training set and the test set when handling datasets. 
    - Note that the test dataset typically does not include the target variable, so special care must be taken when applying target encoding or feature engineering that depends on the target variable.
- Always copy the DataFrame before processing it and use the copy to process.
'''

# <example>   
# When using the matplotlib library for visualizing multiple subplots, if you need to display relationships between multiple variables, you can set up subplots within a single figure window instead of generating separate plots for each variable relationship. This approach not only makes effective use of visual space but also adheres to the rule of limiting the number of generated plots. For example, if there are 12 variable combinations, you can choose the most critical 10 combinations to display.
# </example>


PROMPT_DEVELOPER = '''
# CONTEXT #
{steps_in_context}
Currently, I am at step: {step_name}.
#############
# MESSAGE FROM LAST STEP #
{message}
#############
# COMPETITION INFORMATION #
{competition_info}
#############
# PLAN #
{plan}
#############
# CONSTRAINTS #
{constraints}
#############
# TASK #
{task}
#############
# RESPONSE: BLOCK (CODE & EXPLANATION) #
TASK 1:
THOUGHT PROCESS
CODE
EXPLANATION
TASK 2:
THOUGHT PROCESS
CODE
EXPLANATION
...
#############
# START CODING #
If you understand, please request the code and insight from previous steps, all the features of the data and 10 data samples in both training data and test data from me.
'''


PROMPT_DEVELOPER_WITH_EXPERIENCE_ROUND0_0 = '''
# CONTEXT #
{steps_in_context}
Currently, I am at step :{step_name}.
#############
# MESSAGE FROM LAST STEP #
{message}
#############
# COMPETITION INFORMATION #
{competition_info}
#############
# PLAN #
{plan}
#############
# CONSTRAINTS #
{constraints}
#############
# TASK #
{task} In the past, you have attempted this task multiple times. However, due to errors in your answers or insufficient quality, you have not succeeded. I will provide you with your previous attempts' experiences and a professional reviewer's suggestions for improvement (PREVIOUS EXPERIENCE WITH SUGGESTION). Based on these, please learn from previous experience, try again to mitigate similar failures and successfully complete the task.
You must follow these subtasks:
1. Analyze the previous experience and suggestions. Think about what went wrong and how you can improve.
2. Develop a new solution based on the previous experience and suggestions.
#############
# PREVIOUS EXPERIENCE WITH SUGGESTION #
{experience_with_suggestion}
#############
# RESPONSE #
Subtask 1: Analyze the previous experience and suggestions. Think about what went wrong and how you can improve.
You should ONLY focus on Subtask1.
Let's work **Subtask1** out in a step by step way.
#############
# START ANALYSIS #
If you understand, please request the code and insight from previous steps, all the features of the data and 10 data samples in both training data and test data from me. Then you can start analyzing the previous experience and suggestions.
'''


PROMPT_DEVELOPER_WITH_EXPERIENCE_ROUND0_2 = '''
#############
# RESPONSE: BLOCK (CODE & EXPLANATION) #
Subtask 2: Develop a new solution based on the previous experience and suggestions.
TASK 1:
THOUGHT PROCESS
CODE
EXPLANATION
TASK 2:
THOUGHT PROCESS
CODE
EXPLANATION
...
#############
# START CODING #
'''


# PROMPT_DEVELOPER_DEBUG = '''
# # CONTEXT #
# I'm getting an error executing the code you generated.
# #############
# # TASK #
# Please modify the code according to the error messages ([ERROR MESSAGES]). You must follow these steps:
# 1. Analyze and find out which code block causes the error.
# 2. Think about how to correct the code block.
# 3. Correct the wrong code block.
# 4. Output the all the code blocks after correction.
# Note that you are not allowed to output PREVIOUS CODE repeatedly.
# #############
# # PREVIOUS CODE #
# {previous_code}
# #############
# # WRONG CODE #
# {wrong_code}
# #############
# # ERROR MESSAGES #
# {error_messages}
# #############
# # NOT PASS TEST CASE #
# {not_pass_information}
# #############
# # CODE AFTER CORRECTION #
# '''

PROMPT_DEVELOPER_DEBUG_LOCATE = '''
# CONTEXT #
I'm getting an error executing the code you generated.
#############
# TASK #
Please locate the error in the code and output the most relevant code snippet causes error (5 to 10 lines in length). I will provide you with the previous code, code contains error and error messages.
NOTE that if assert statements just reports the error, you must find out the most relevant code snippet which makes the assert statement fail, not output the assert statement itself.
    - However, if you believe the assert statement is redundant, you can output it.
NOTE that the **last** code snippet in your response should be the **most relevant code snippet causes error** that I ask you to output.
DO NOT correct the error in this step. Just analyze and locate the error.
#############
# PREVIOUS CODE #
{previous_code}
#############
# CODE CONTAINS ERROR #
{wrong_code}
#############
# ERROR MESSAGES #
{error_messages}
#############
# RESPONSE: MOST RELEVANT CODE SNIPPET CAUSES ERROR #
Let's work this out in a step by step way. 
'''

PROMPT_DEVELOPER_DEBUG_ASK_FOR_HELP = '''
# INPORTANT NOTE #
This is the {i}-th time you try to fix the error. Remember You can ONLY try 4 times in total. 
Please review all error messages collected from your previous attempts. 
If they are similar, it means you are not making progress, and you should ask for help to avoid wasting time and resource.
#############
# ALL ERROR MESSAGES #
{all_error_messages}
#############
# RESPONSE #
You can ask for help by output the following messages:
1. HELP
2. I NEED HELP
'''

PROMPT_DEVELOPER_DEBUG_FIX = '''
# CONTEXT #
I have an error code snippet with error messages. 
#############
# TASK #
Please correct the error code snippet according to the error messages. You must follow these steps:
1. Think about how to correct the error code snippet.
2. Correct the error code snippet.
NOTE that the **last** code snippet in your response should be the **code snippet after correction** that I ask you to output.
#############
# ERROR CODE SNIPPET #
{most_relevant_code_snippet}
#############
# ERROR MESSAGES #
{error_messages}
#############
# RESPONSE: CODE SNIPPET AFTER CORRECTION #
Let's work this out in a step by step way.
'''

PROMPT_DEVELOPER_DEBUG_MERGE = '''
# CONTEXT #
When running the code you generated, I encountered some errors. I have analyzed and located the erroneous code snippet and have corrected it to produce the correct code snippet.
#############
# TASK #
- CODE CONTAINS ERROR: The original code you generated contains an error.
- ERROR CODE SNIPPET: The code snippet from your original code that causes the error, as identified through analysis.
- CODE SNIPPET AFTER CORRECTION: The correct code snippet obtained after fixing the ERROR CODE SNIPPET.
Please replace the ERROR CODE SNIPPET in CODE CONTAINS ERROR with the CODE SNIPPET AFTER CORRECTION to produce the fully corrected code.
#############
# CODE CONTAINS ERROR #
{wrong_code}
#############
# ERROR CODE SNIPPET #
{most_relevant_code_snippet}
#############
# CODE SNIPPET AFTER CORRECTION #
{code_snippet_after_correction}
#############
# RESPONSE: ALL CORRECT CODE #
'''



PROMPT_DEVELOPER_TEST_LOCATE = '''
# CONTEXT #
Your code has some tests that don't pass.
#############
# TASK #
For EACH test that does not pass, please analyze the code with problem, figure out which code snippet causes the test not pass, and output the problematic code snippet (5 to 10 lines in length). 
I will provide you with the previous code, code with problem and not pass tests' information.
NOTE that in your each analysis for each test, the **last** code snippet in your response should be the **problematic code snippet** that I ask you to output.
#############
# PREVIOUS CODE #
{previous_code}
#############
# CODE WITH PROBLEM #
{code_with_problem}
#############
# NOT PASS TEST CASES #
{not_pass_information}
#############
# RESPONSE #
Let's work this out in a step by step way.
'''

PROMPT_DEVELOPER_TEST_REORGANIZE_LOCATE_ANSWER = '''
# TASK #
Please reorganize the code snippets that you have identified as problematic in the previous step. 
#############
# RESPONSE: CODE SNIPPETS WITH PROBLEM #
You should ONLY output the each code snippet with problem, without any other content.
Here is the template you can use:
## CODE SNIPPET 1 WITH PROBLEM ##
```python
code snippet 1 with problem
```
## CODE SNIPPET 2 WITH PROBLEM ##
```python
code snippet 2 with problem
```
...
'''

PROMPT_DEVELOPER_TEST_FIX = '''
# CONTEXT #
Your code has a couple tests that don't pass.
#############
# TASK #
Please correct the some code snippets with problem according to the not pass tests' information.
You must follow these steps:
1. Think about how to correct the code snippets with problem.
2. Correct the code snippets with problem.
#############
# CODE SNIPPETS WITH PROBLEM #
{code_snippets_with_problem}
#############
# NOT PASS TEST CASES #
{not_pass_information}
#############
# RESPONSE #
Let's work this out in a step by step way.
'''

PROMPT_DEVELOPER_TEST_REORGANIZE_FIX_ANSWER = '''
# TASK #
Please reorganize the code snippets that you have corrected in the previous step.
#############
# RESPONSE: CODE SNIPPETS AFTER CORRECTION #
You should ONLY output the each code snippet after correction, without any other content.
NOTE that you should output the code snippets after correction in the order of the code snippets with problems, they have to correspond to each other.
Here is the template you can use:
## CODE SNIPPET 1 AFTER CORRECTION ##
```python
code snippet 1 after correction
```
## CODE SNIPPET 2 AFTER CORRECTION ##
```python
code snippet 2 after correction
```
...
'''

PROMPT_DEVELOPER_TEST_MERGE = '''
# CONTEXT #
Your code has a couple tests that don't pass. I have analyzed and located the code snippets with problem and have corrected them to produce the correct code snippets.
#############
# TASK #
- CODE WITH PROBLEM: The original code you generated which failed some tests.
- CODE SNIPPETS WITH PROBLEM: Precise code snippets from your original code that causes problem, as identified through analysis.
- CODE SNIPPETS AFTER CORRECTION: The correct code snippets obtained after fixing the CODE SNIPPETS WITH PROBLEM.
Please replace the CODE SNIPPETS WITH PROBLEM in CODE WITH PROBLEM with the CODE SNIPPETS AFTER CORRECTION to produce the fully corrected code.
#############
# CODE WITH PROBLEM #
{code_with_problem}
#############
# CODE SNIPPETS WITH PROBLEM #
{code_snippets_with_problem}
#############
# CODE SNIPPETS AFTER CORRECTION #
{code_snippets_after_correction}
#############
# RESPONSE: ALL CORRECT CODE #
'''
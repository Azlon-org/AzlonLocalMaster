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
<example>   
When using the matplotlib library for visualizing multiple subplots, if you need to display relationships between multiple variables, you can set up subplots within a single figure window instead of generating separate plots for each variable relationship. This approach not only makes effective use of visual space but also adheres to the rule of limiting the number of generated plots. For example, if there are 12 variable combinations, you can choose the most critical 10 combinations to display.
</example>
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


PROMPT_DEVELOPER_WITH_EXPERIENCE_ROUND0 = '''
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
Let's work this out in a step by step way.
#############
# START ANALYSIS #
If you understand, please request the code and insight from previous steps, all the features of the data and 10 data samples in both training data and test data from me. Then you can start analyzing the previous experience and suggestions.
'''


PROMPT_DEVELOPER_WITH_EXPERIENCE_ROUND2 = '''
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


PROMPT_DEVELOPER_DEBUG = '''
# CONTEXT #
I'm getting an error executing the code you generated.
#############
# TASK #
please modify the code according to the error messages ([ERROR MESSAGES]). You must follow these steps:
1. Analyze and find out which code block causes the error.
2. Think about how to correct the code block.
4. Correct the wrong code block.
3. Output the all the code blocks after correction.
Note that you are not allowed to output PREVIOUS CODE repeatedly.
#############
# PREVIOUS CODE #
{previous_code}
#############
# WRONG CODE #
{wrong_code}
#############
# ERROR MESSAGES #
{error_messages}
#############
# CODE AFTER CORRECTION #
'''
AGENT_ROLE_TEMPLATE = '''
You are an excellent {agent_role}.
'''

STEPS_IN_CONTEXT_TEMPLATE = '''
I am working on a data science competition called "# {competition_name}". I plan to complete it by following these steps:
1. Understand Background
2. Preliminary Exploratory Data Analysis (Preliminary EDA)
3. Data Cleaning
4. In-depth Exploratory Data Analysis (In-depth EDA)
5. Feature Engineering
6. Model Building, Validation, and Prediction
'''

PROMPT_EACH_EXPERIENCE_WITH_SUGGESTION = '''
## EXPERIENCE {index}##
<EXPERIENCE>
{experience}
</EXPERIENCE>
<SUGGESTION>
{suggestion}
</SUGGESTION>
<SCORE>
{score}
</SCORE>
'''

REORGANIZE_REPLY = '''
# TASK #
Please reorganize the following information into a JSON format (quote in ```json ```). You need to organize the information in a clear and concise manner, ensuring that the content is logically structured and easy to understand. You must ensure that the information is complete and accurate.
#############
# INFORMATION #
{information}
#############
# RESPONSE: JSON FORMAT #
{{
    "thought_process": list=[
        {{
            "question": str="The input question you must answer",
            "thought": str="You should always think about what to do next",
            "action": str="Describe the action you plan to take",
            "action_input": str="The specific input for the action",
            "observation": str="The expected or actual result of the action"
        }}
    ],
    "final_thought": str="Further reflection based on the observation, summarizing the final answer",
    "final_answer": str="The final answer to the original input question"
}}
#############
# START REORGANIZING #
'''

PROMPT_READER_TASK = '''
Conduct a comprehensive analysis of the competition overview, understand the background of the topic, understand how to use different files, clarify the definition and requirements of the problem, obtain information about the data, and identify the target variable, evaluation metrics and submission format. Gather important information regarding Background/Files/Question/Target_Variable/Evaluation/Other aspects.
'''

PROMPT_READER = '''
# CONTEXT #
{steps_in_context}
Currently, I am at step: Background Understand.
#############
# TASK #
{task} 
#############
# RESPONSE: JSON FORMAT #
{{
    "thought_process": list=[
        {{
            "question": str="The input question you must answer",
            "thought": str="You should always think about what to do next",
            "action": str="Describe the action you plan to take",
            "action_input": str="The specific input for the action",
            "observation": str="The expected or actual result of the action"
        }}
    ],
    "final_thought": str="Further reflection based on the observation, summarizing the final answer",
    "final_answer": str="The final answer to the original input question"
}}
#############
# START ANALYSIS #
If you understand, please request the Overview of this data science competition from me.
'''

PROMPT_READER_WITH_EXPERIENCE = '''
# CONTEXT #
{steps_in_context}
Currently, I am at step one: Background Understand.
#############
# TASK #
{task} In the past, you have attempted this task multiple times. However, due to errors in your answers or insufficient quality, you have not succeeded. I will provide you with your previous attempts' experiences and a professional reviewer's suggestions for improvement (PREVIOUS EXPERIENCE WITH SUGGESTION). Based on these, please formulate a new, concise high-level plan to mitigate similar failures and successfully complete the task.
#############
# PREVIOUS EXPERIENCE WITH SUGGESTION #
{experience_with_suggestion}
#############
# RESPONSE: JSON FORMAT #
{{
    "thought_process": list=[
        {{
            "question": str="The input question you must answer",
            "thought": str="You should always think about what to do next",
            "action": str="Describe the action you plan to take",
            "action_input": str="The specific input for the action",
            "observation": str="The expected or actual result of the action"
        }}
    ],
    "final_thought": str="Further reflection based on the observation, summarizing the final answer",
    "final_answer": str="The final answer to the original input question"
}}
#############
# START ANALYSIS #
If you understand, please request the Overview of this data science competition from me.
'''


PROMPT_PLANNER_TASK = '''
Design a reasonable, clear, detailed and efficient plan for the current development step: {step_name}. The Developer will develop according to the specific tasks in your plan. Start by outlining the task objectives, then specify the methods to be used, considering factors such as data types, project requirements, and resource constraints.
<example> In the data cleaning step, you can detail how to handle missing values and other data integrity issues. </example>
You need to clearly delineate the tasks specific to this step and avoid tasks related to other steps.
<example> In the in-depth EDA step, focus on analyzing the distribution and statistical properties of features without deleting or reducing features (which belongs to the feature engineering step). </example>
Consider dependencies, resource availability, and time constraints. Ensure your plan can address these factors and remain adaptable to unforeseen challenges.
'''

PROMPT_PLANNER = '''
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
# TASK #
{task}
#############
# RESPONSE: JSON FORMAT #
{{
    "thought_process": list=[
        {{
            "question": str="The input question you must answer",
            "thought": str="You should always think about what to do next",
            "action": str="Describe the action you plan to take",
            "action_input": str="The specific input for the action",
            "observation": str="The expected or actual result of the action"
        }}
    ],
    "final_thought": str="Further reflection based on the observation, summarizing the final answer",
    "final_answer": list=[
        {{
            "task": str="The specific task to be performed",
            "method": list=["Methods to be used"],
        }}
    ]
}}
#############
# START PLANNING #
'''


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
<example>
When using the matplotlib library for visualizing multiple subplots, if you need to display relationships between multiple variables, you can set up subplots within a single figure window instead of generating separate plots for each variable relationship. This approach not only makes effective use of visual space but also adheres to the rule of limiting the number of generated plots. For example, if there are 12 variable combinations, you can choose the most critical 10 combinations to display.
</example>
## CODING RULES ##
- Always use `print()` function if you need to print a value. 
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


PROMPT_DEVELOPER_DEBUG = '''
# CONTEXT #
I'm getting an error executing the code you generated.
#############
# TASK #
please modify the code according to the output messages ([OUTPUT MESSAGES]) and error messages ([ERROR MESSAGES]). You must follow these steps:
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
# OUTPUT MESSAGES #
{output_messages}
#############
# ERROR MESSAGES #
{error_messages}
#############
# CODE AFTER CORRECTION #
'''



PROMPT_REVIEWER_ROUND0 = '''
# CONTEXT #
{steps_in_context}
Each step is done by multiple agents to collaborate. Currently, you are evaluating the performance of the agents in Step: {step_name}.
#############
# TASK #
Please assess the performance of multiple agents in completing Step: {step_name}. I will provide descriptions of the agents, the tasks they performed, and their outcomes. You need to assign a score from 1 to 5, with 1 indicating very poor performance and 5 indicating excellent performance. Additionally, please provide specific suggestions for improving the agents' performance if necessary (If an agent is good enough, don't give any suggestion).
#############
# RESPONSE: JSON FORMAT #
{{
    "thought_process": list=[
        {{
            "question": str="The input question you must answer",
            "thought": str="You should always think about what to do next",
            "action": str="Describe the action you plan to take",
            "action_input": str="The specific input for the action",
            "observation": str="The expected or actual result of the action"
        }}
    ],
    "final_thought": str="Further reflection based on the observation, summarizing the final answer",
    "final_answer": {{
	    "final_suggestion": {{
            str="agent name": str="Specific suggestions for improving the performance of the agent"
        }},
        "final_score": {{
            str="agent name": int="The final score you assign to the evaluated agent, only one score in range 1-5"
        }}
    }}
}}
#############
# START EVALUATION #
If you are ready, please request from me the role, description, input, task and execution result of the agent to be evaluated.
'''

PROMPT_REVIEWER_ROUND1_EACH_AGENT = '''
#############
# AGENT {role} TO BE EVALUATED #
<DESCRIPTION>
{description}
</DESCRIPTION>
<TASK>
{task}
</TASK>
<INPUT>
{input}
</INPUT>
<EXECUTION RESULT>
{result}
</EXECUTION RESULT>
'''


PROMPT_SUMMARIZER_ROUND0 = '''
# CONTEXT #
{steps_in_context}
Currently, I am at step: {step_name}.
#############
# FIRST TASK #
Please thoroughly review the trajectory of all agents performing tasks in the current step and compile a detailed report summarizing the following key information:
1. The current step being performed.
2. The plan designed by the planner to complete this step.
3. A detailed account of how the developer implemented the plan:
    - Describe the methods and approaches used for each task in the plan.
4. The reviewer's evaluations and suggestions for the agents.
#############
# RESPONSE: MARKDOWN FORMAT #
# START SUMMARIZE REPORT #
If you are ready, please request from me the trajectory of all agents performing tasks in the current step.
'''

PROMPT_SUMMARIZER_ROUND2_RESPONSE_FORMAT = '''
{{
    "thought_process": list=[
        {{
            "question": str="The input question you must answer",
            "thought": str="You should always think about what to do next",
            "action": str="Describe the action you plan to take",
            "action_input": str="The specific input for the action",
            "observation": str="The expected or actual result of the action"
        }}
    ],
    "final_thought": str="Further reflection based on the observation, summarizing the final answer",
    "final_answer": {{
        "Agent Planner": str="Key message sent to Agent Planner in the next step",
        "Agent Developer": str="Key message sent to Agent Developer in the next step"
    }}
}}
'''
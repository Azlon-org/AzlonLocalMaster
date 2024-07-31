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

PROMPT_SUMMARIZER_UNDERSTAND_BACKGROUND = '''
# CONTEXT #
{steps_in_context}
Currently, I am at step one: Background Understand.
#############
# TASK #
{task}
#############
# RESPONSE: JSON FORMAT #
{{
    "thought_process": [
        {{
            "question": "The input question you must answer",
            "thought": "You should always think about what to do next",
            "action": "Describe the action you plan to take",
            "action_input": "The specific input for the action",
            "observation": "The expected or actual result of the action"
        }}
    ],
    "final_thought": "Further reflection based on the observation, summarizing the final answer",
    "final_answer": "The final answer to the original input question"
}}
#############
# START ANALYSIS #
If you understand, please request the Overview of this data science competition from me.
'''

PROMPT_SUMMARIZER_TASK_UNDERSTAND_BACKGROUND = '''
You should conduct a comprehensive analysis of the competition overview, understand the background of the topic, understand how to use different files, clarify the definition and requirements of the problem, obtain information about the data, and identify the target variable, evaluation metrics and submission format. Gather important information regarding Background/Files/Question/Target_Variable/Evaluation/Other aspects.
'''

PROMPT_REVIEWER_ROUND1 = '''
# CONTEXT #
{steps_in_context}
Each step is done by multiple agents to collaborate. Currently, you are evaluating the performance of the agents in Step: {step_name}.
#############
# TASK #
Please assess the performance of multiple agents in completing Step: {step_name}. I will provide descriptions of the agents, the tasks they performed, and their outcomes. You need to assign a score from 1 to 5, with 1 indicating very poor performance and 5 indicating excellent performance. Additionally, please provide specific suggestions for improving the agents' performance.
#############
# RESPONSE: JSON FORMAT #
{{
    "thought_process": [
        {{
            "question": "The input question you must answer",
            "thought": "You should always think about what to do next",
            "action": "Describe the action you plan to take",
            "action_input": "The specific input for the action",
            "observation": "The expected or actual result of the action"
        }}
    ],
    "final_thought": "Further reflection based on the observation, summarizing the final answer",
    "final_answer": {{
	    "final_score": "The final score you assign to the evaluated agents, only one score in range 1-5",
	    "final_suggestion": {{
            [agent_role]: "Specific suggestions for improving the performance of the agent"
        }}
    }}
}}
#############
# START EVALUATION #
If you are ready, please request from me the role, description, input, task and execution result of the agent to be evaluated.
'''

PROMPT_REVIEWER_ROUND2_EACH_AGENT = '''
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

# {{
# 	"background_analysis": [BACKGROUND_ANALYSIS],
#   "files_analysis": [FILES_ANALYSIS],
# 	"question_analysis": [QUESTION_DEFINITION], [QUESTION_REQUIREMENT],
# 	"target_variable_analysis": [TARGET_VARIABLE_ANALYSIS],
# 	"evaluation_analysis": [EVALUATION_ANALYSIS],
# 	"other_analysis": [OTHER_ANALYSIS],
# }}
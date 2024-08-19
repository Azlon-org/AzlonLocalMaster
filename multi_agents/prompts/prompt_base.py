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

REORGANIZE_REPLY_TYPE1 = '''
# TASK #
Please extract essential information and reorganize into a JSON format. You need to organize the information in a clear and concise manner, ensuring that the content is logically structured and easy to understand. You must ensure that the essential information is complete and accurate.
#############
# INFORMATION #
{information}
#############
# RESPONSE: JSON FORMAT #
```json
{{
    "final_thought": str="Summarize your understanding and confirm that you now have the final answer.",
    "final_answer": str="Provide the final answer to the original task."
}}
```
#############
# START REORGANIZING #
'''

REORGANIZE_REPLY_TYPE2 = '''
# TASK #
Please extract essential information and reorganize into a JSON format. You need to organize the information in a clear and concise manner, ensuring that the content is logically structured and easy to understand. You must ensure that the essential information is complete and accurate.
#############
# INFORMATION #
{information}
#############
# RESPONSE: JSON FORMAT #
```json
{{
    "final_thought": str="Summarize your understanding and confirm that you now have the final answer.",
    "final_answer": {{
	    "final_suggestion": {{
            str="agent name": str="Specific suggestions for improving the agent's performance"
        }},
        "final_score": {{
            str="agent name": int="The final score you assign to the evaluated agent, only one score in range 1-5"
        }}
    }}
}}
```
#############
# START REORGANIZING #
'''


REORGANIZE_REPLY_TYPE3 = '''
# TASK #
Please extract essential information and reorganize into a JSON format. You need to organize the information in a clear and concise manner, ensuring that the content is logically structured and easy to understand. You must ensure that the essential information is complete and accurate.
#############
# INFORMATION #
{information}
#############
# RESPONSE: JSON FORMAT #
```json
{{
    "final_thought": str="Summarize your understanding and confirm that you now have the final answer.",
    "final_answer": list=[
        {{
            "task": str="The specific task to be performed",
            "method": list=["Methods to be used"],
        }}
    ]
}}
```
#############
# START REORGANIZING #
'''

# ## Thought Process ##
# (This Thought/Action/Observation sequence may repeat as needed.)
# - Thought: str="Reflect on the current situation and consider how to proceed in fulfilling the user's requirements."
# - Action: str="Describe the action you plan to take to meet the user's needs."
# - Observation: str="Note the expected or actual results of the action."
# ## Final Thought ##
# str="Summarize your understanding and confirm that you now have the final answer."
# ## Final Answer ##
# str="Provide the final answer to the original task."
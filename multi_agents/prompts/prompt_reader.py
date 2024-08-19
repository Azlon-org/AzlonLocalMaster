PROMPT_READER_TASK = '''
Please conduct a comprehensive analysis of the competition, focusing on the following aspects:
1. Competition Overview: Understand the background and context of the topic.
2. Files: Analyze each provided file, detailing its purpose and how it should be used in the competition.
3. Problem Definition: Clarify the problem's definition and requirements.
4. Data Information: Gather detailed information about the data, including its structure and contents.
5. Target Variable: Identify the target variable that needs to be predicted or optimized.
6. Evaluation Metrics: Determine the evaluation metrics that will be used to assess the submissions.
7. Submission Format: Understand the required format for the final submission.
8. Other Key Aspects: Highlight any other important aspects that could influence the approach to the competition.
Ensure that the analysis is thorough, with a strong emphasis on understanding the purpose and usage of each file provided.
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
You must think carefully first and then provide a detailed response in JSON format. Your response should include the following key elements:
```json
{{
    "thought_process": list=[
        {{
            "thought": str="Reflect on the current situation and consider how to proceed in fulfilling the user's requirements.",
            "action": str="Describe the action you plan to take to meet the user's needs.",
            "observation": str="Note the expected or actual results of the action."
        }}
    ],
    "final_thought": str="Summarize your understanding and confirm that you now have the final answer.",
    "final_answer": str="Provide the final answer to the original task."
}}
```
#############
# START ANALYSIS #
If you understand, please request the overview of this data science competition from me.
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
You must think carefully first and then provide a detailed response in JSON format. Your response should include the following key elements:
```json
{{
    "thought_process": list=[
        {{
            "thought": str="Reflect on the current situation and consider how to proceed in fulfilling the user's requirements.",
            "action": str="Describe the action you plan to take to meet the user's needs.",
            "observation": str="Note the expected or actual results of the action."
        }}
    ],
    "final_thought": str="Further reflection based on the observation, summarizing the final answer",
    "final_answer": str="The final answer to the original input question"
}}
```
#############
# START ANALYSIS #
If you understand, please request the Overview of this data science competition from me.
'''
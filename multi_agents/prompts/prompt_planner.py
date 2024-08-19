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
    "final_answer": list=[
        {{
            "task": str="The specific task to be performed",
            "method": list=["Methods to be used"],
        }}
    ]
}}
```
#############
# START PLANNING #
If you understand, please request the report and plan from the previous step. These documents contain important information that will guide your planning. In addition to the report and plan, I will also provide some sample data for your analysis. This will help you create a more accurate and tailored plan for the current step. Your plan should closely follow the previous step, maintain logical consistency, and avoid any duplication of tasks.
'''
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
            "thought": str="Reflect on the current situation and consider how to proceed in fulfilling the user's requirements.",
            "action": str="Describe the action you plan to take to meet the user's needs.",
            "observation": str="Note the expected or actual results of the action."
        }}
    ],
    "final_thought": str="Further reflection based on the observation, summarizing the final answer",
    "final_answer": {{
        "Agent Planner": str="Key message sent to Agent Planner in the next step",
        "Agent Developer": str="Key message sent to Agent Developer in the next step"
    }}
}}
'''
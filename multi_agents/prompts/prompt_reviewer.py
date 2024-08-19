PROMPT_REVIEWER_ROUND0 = '''
# CONTEXT #
{steps_in_context}
Each step involves collaboration between multiple agents. You are currently evaluating the performance of agents in Step: {step_name}.
#############
# TASK #
Your task is to assess the performance of several agents in completing Step: {step_name}. I will provide descriptions of each agent, the tasks they performed, and the outcomes of those tasks. Please assign a score from 1 to 5 for each agent, with 1 indicating very poor performance and 5 indicating excellent performance. Additionally, provide specific suggestions for improving each agent's performance, if applicable. If an agent's performance is satisfactory, no suggestions are necessary.
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
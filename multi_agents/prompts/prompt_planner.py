PROMPT_PLANNER_TASK = '''
Please design plan that is clear and specific to each FEATURE for the current development phase: {phase_name}. The developer will execute tasks based on your plan. 
I will provide you with COMPETITION INFORMATION, RESOURCE CONSTRAINTS, and previous reports and plans.
In your response, briefly outline the task objectives, then specify the essential methods and constraints to consider. 
ONLY focus on tasks relevant to this phase, avoiding those belonging to other phases.
<example>
During the in-depth EDA phase, you CAN:
- Perform detailed univariate analysis on KEY features.
you CAN NOT:
- Modify any feature or modify data.
</example>
Ensure the plan addresses key dependencies, resource availability, and time constraints without overcomplicating the process.
NOTE that The plan should include a maximum of FOUR tasks, with clear methods and constraints, guiding developers to effectively execute the critical steps of the current phase.
NOTE that when you want to output some statistical information about the data, your FIRST choice should be output to terminal in TEXT format (print). Before you print statistics, first print a description of the statistics.
    - if the information is not easy to describe in text, then you can generate images.
NOTE that your method should be very detailed, for example, if the task is about how to clean data, your method should be specific to each feature (Omission NOT allowed) you are going to clean.
NOTE that when you design the plan, always take into account the methods and specific values mentioned in the USER RULES as the FIRST priority.
'''


PROMPT_PLANNER = '''
# CONTEXT #
{phases_in_context}
Currently, I am at phase: {phase_name}.
{state_info}
#############
# USER RULES #
{user_rules}

#############
# COMPETITION INFORMATION #
{competition_info}

#############
# RESOURCE CONSTRAINTS #
- Always consider the runtime and efficiency of your code when writing code, especially for data visualization, handling large datasets, or complex algorithms.
<example>
Data visualization: When using libraries such as seaborn or matplotlib to create plots, consider turning off unnecessary details (e.g., annot=False in heatmaps), especially when the number of data points is large.
</example>
- Always consider resource constraints and limit the number of generated images to ensure that they do not exceed 10 when performing Exploratory Data Analysis (EDA), 
    - **Note that the generated images should be LIMITED to the most critical visualizations that provide valuable insights.**

#############
# TASK #
{task}

#############
# RESPONSE #
Let's work this out in a step by step way.

#############
# START PLANNING #
If you understand, please request the report and plan from the previous phase. These documents contain important information that will guide your planning. In addition to the report and plan, I will also provide some sample data for your analysis. This will help you create a more accurate and tailored plan for the current phase. Your plan should closely follow the previous phase, maintain logical consistency, and avoid any duplication of tasks.
'''


PROMPT_PLNNAER_REORGANIZE_IN_MARKDOWN = '''
# TASK #
Please extract essential information from your answer and reorganize into a specified MARKDOWN format. You need to organize the information in a clear and concise manner, ensuring that the content is logically structured and easy to understand. You must ensure that the essential information is complete and accurate.

#############
# RESPONSE: MARKDOWN FORMAT #
Here is the MARKDOWN format you should follow:
```markdown
## PLAN
### STEP 1
Task: [The specific task to be performed]
Method and involved features: [Methods to be used and involved features]
Constraints: [Any constraints or considerations to keep in mind]

### STEP 2
Task: [The specific task to be performed]
Method and involved features: [Methods to be used and involved features]
Constraints: [Any constraints or considerations to keep in mind]

...
```

#############
# START REORGANIZING #
'''


PROMPT_PLNNAER_REORGANIZE_IN_JSON = '''
# TASK #
Please extract essential information from your answer and reorganize into a specified JSON format. You need to organize the information in a clear and concise manner, ensuring that the content is logically structured and easy to understand. You must ensure that the essential information is complete and accurate.

#############
# RESPONSE: JSON FORMAT #
Here is the JSON format you should follow:
```json
{{
    "final_answer": list=[
        {{
            "task": str="The specific task to be performed",
            "method and involved features": list=["Methods to be used and involved features"],
            "constraints": list=["Any constraints or considerations to keep in mind"]
        }}
    ]
}}
```

#############
# START REORGANIZING #
'''

# You can use the following template to guide your response:
# Thought: you should always think about what to do to complete the task
# Action: the action to take
# Observation: the result of the action
# ... (this Thought/Action/Action Input/Observation can repeat N times)
# Final Thought: I now know the final answer
# Final Answer: the final answer to the original input question


# ```json
# {{
#     "thought_process": list=[
#         {{
#             "thought": str="Reflect on the current situation and consider how to proceed in fulfilling the user's requirements.",
#             "action": str="Describe the action you plan to take to meet the user's needs.",
#             "observation": str="Note the expected or actual results of the action."
#         }}
#     ],
#     "final_thought": str="Summarize your understanding and confirm that you now have the final answer.",
#     "final_answer": list=[
#         {{
#             "task": str="The specific task to be performed",
#             "method": list=["Methods to be used"],
#         }}
#     ]
# }}
# ```

# ## Thought Process ##
# (This Thought/Action/Observation sequence may repeat as needed.)
# - Thought: str="Reflect on the current situation and consider how to proceed in fulfilling the user's requirements."
# - Action: str="Describe the action you plan to take to meet the user's needs."
# - Observation: str="Note the expected or actual results of the action."
# ## Final Thought ##
# str="Summarize your understanding and confirm that you now have the final answer."
# ## Final Answer ##
# str="Provide the final answer to the original task."

# Here is an example of planning for the preliminary EDA step:
# [
#     {{
#         "task": "Understand the Structure of the Data",
#         "method": [
#             "Load the train.csv and test.csv datasets",
#             "Display the first few rows of the datasets using head()",
#             "Use info() to get a summary of the datasets, including the number of non-null entries and data types",
#             "Use describe() to get basic statistical summaries of the numerical features"
#         ]
#     }},
#     {{
#         "task": "Identify and Visualize Missing Values",
#         "method": [
#             "Use isnull().sum() to count the number of missing values in each column"
#         ]
#     }},
#     {{
#         "task": "Detect Outliers and Analyze Relationships",
#         "method": [
#             "Use box plots to visualize the distribution of numerical features and identify outliers",
#             "Use correlation matrices to identify the strength and direction of relationships between numerical features and SalePrice"
#         ]
#     }}
# ]
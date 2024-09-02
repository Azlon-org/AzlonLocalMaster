PROMPT_SUMMARIZER_IMAGE_CHOOSE = '''
# CONTEXT #
{steps_in_context}

#############
# TASK #
Currently, you are in stage: {stage}.
According to the current stage, you need to choose {num} images from the following images, they should be most relevant to the current stage, and useful for the next stage.

#############
# IMAGES #
{images}

#############
# RESPONSE #
Please give me the image names that you choose. You should follow the format:
```json
{{
    "images": list=[
        "[image name 1]",
        "[image name 2]",
        "[image name 3]",
        ...
    ]
}}
```

#############
# START CHOOSING IMAGES #
Let's work this out in a step by step way.
'''


PROMPT_SUMMARIZER_DESIGN_QUESITONS = '''
# CONTEXT #
{steps_in_context}
Currently, I am at step: {step_name}.

#############
# TASK #
Your task is to design a series of questions that will be used to summarize the findings at the current step and provide guidance for the next step. 
The current competition step is: {step_name}  
The next step is: {next_step_name}

I will provide the competition information (COMPETITION INFO), the plan given by the planner for this step (PLAN).

Based on this information, design 5 key questions that are most worth focusing on and will be most helpful for the next step. These questions should:
1. Be targeted, specifically designed for the transition from {step_name} to {next_step_name}.
2. Summarize the key findings of the current step ({step_name}).
3. Provide guidance for the planner in formulating the execution plan in the next step ({next_step_name}).

<sample questions>  
(Assuming the step is Preliminary EDA and the next step is Data Cleaning)  
1. Which features have missing values, and what is the proportion of missing values?  
2. Are there any obvious outliers in the data? If so, which features do they mainly affect?  
3. What interesting findings did you have in this step? What do you think should be done in the next step to better complete this competition?  
...
</sample questions>

Please ensure that your questions have both breadth and depth, capable of comprehensively summarizing the work of the current step and providing valuable insights for the upcoming {next_step_name}. List the questions you design and briefly explain the purpose or importance of each question.

#############
# RESPONSE: MARKDOWN FORMAT #
NOTE that you only need design questions, do not answer the questions yourself.
Let's work this out in a step by step way.

#############
# START DESIGN QUESTIONS #
If you are ready, please request from me the COMPETITION INFO, PLAN.
'''

PROMPT_SUMMARIZER_REORGAINZE_QUESTIONS = '''
# TASK #
Please reorganize the questions that you have designed in the previous reply.

#############
# RESPONSE: MARKDOWN FORMAT #
```markdown
## QUESTIONS
### Question 1
[content of question 1]

### Question 2
[content of question 2]

### Question 3
[content of question 3]

### Question 4
[content of question 4]

### Question 5
[content of question 5]
```

#############
# START REORGANIZE QUESTIONS #
'''

PROMPT_SUMMARIZER_ANSWER_QUESTIONS = '''
# CONTEXT #
{steps_in_context}
Currently, I am at step: {step_name}.

#############
# TASK #
Please answer a series of questions that will help summarize the current step.
Your answer should be concise and detailed, for example, if the question is about how to clean data, your answer should be specific to each feature.
I will provide the competition information (COMPETITION INFO), the plan given by the planner for this stage (PLAN), the code written by the developer in this stage and the output of the code execution (CODE AND OUTPUT), insight from images you generated (INSIGHT FROM VISUALIZATION), as well as the reviewer's evaluation of the planner's and developer's task completion for this stage (REVIEW).
When answering each question, you can first consider which information you need to use, and then answer the question based on this information.

#############
# QUESTIONS #
{questions}

#############
# RESPONSE: MARKDOWN FORMAT #
Let's work this out in a step by step way.

#############
# START ANSWER QUESTIONS #
If you are ready, please request from me the COMPETITION INFO, PLAN, CODE AND OUTPUT, INSIGHT FROM VISUALIZATION, REVIEW.
'''

PROMPT_INFORMATION_FOR_ANSWER = '''
# COMPETITION INFO #
{competition_info}

#############
# PLAN #
{plan}

#############
# CODE AND OUTPUT #
## CODE ##
{code}

## OUTPUT ##
{output}

#############
# INSIGHT FROM VISUALIZATION #
{insight_from_visualization}

#############
# REVIEW #
{review}
'''

PROMPT_SUMMARIZER_REORGANIZE_ANSWERS = '''
# TASK #
Please reorganize the answers that you have given in the previous step, and synthesize them into a report.

#############
# RESPONSE: MARKDOWN FORMAT #
```markdown
# REPORT
## QUESTIONS AND ANSWERS  
### Question 1
[repeat question 1]
### Answer 1
[answer to question 1]

### Question 2
[repeat question 2]
### Answer 2

### Question 3
[repeat question 3]
### Answer 3
[answer to question 3]

### Question 4
[repeat question 4]
### Answer 4
[answer to question 4]

### Question 5
[repeat question 5]
### Answer 5
[answer to question 5]
</Markdown>

#############
# START REORGANIZE QUESTIONS #
'''
STEPS_IN_CONTEXT_TEMPLATE = '''
I am working on a data science competition called "# {competition_name}". I plan to complete it by following these steps:
1. Understand Background
2. Preliminary Exploratory Data Analysis (Preliminary EDA)
3. Data Cleaning
4. In-depth Exploratory Data Analysis (In-depth EDA)
5. Feature Engineering
6. Model Building, Validation, and Prediction
'''

PROMPT_ERROR_CORRECTION_TEMPLATE = '''
#############
# PROBLEM #
I'm getting an error executing the code you generated, please modify the code according to the output messages ([OUTPUT MESSAGES]) and error messages ([ERROR MESSAGES]). You must follow these steps:
1. Analyze and find out which code block causes the error.
2. Think about how to correct the code block.
3. Output all the code blocks and explanations after correction.
#############
# CONSTRAINTS #
You are only allowed to output all the code blocks and explanations after correction.
#############
# OUTPUT MESSAGES #
{output_messages}
#############
# ERROR MESSAGES #
{error_messages}
#############
# ALL CORRECTED BLOCKS (CODE & EXPLANATION) #
'''
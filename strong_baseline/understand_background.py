import sys
import os
import pdb
import timeout_decorator

sys.path.append('..')
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from utils import read_file, multi_chat, PREFIX_STRONG_BASELINE
from prompt import STEPS_IN_CONTEXT_TEMPLATE

@timeout_decorator.timeout(600)
def understand_background(competition, i):
    prefix = PREFIX_STRONG_BASELINE
    path_to_overview = f'{prefix}/{competition}/overview.txt'
    
    overview = read_file(path_to_overview)
    
    competition_name = competition.replace('_', ' ')
    steps_in_context = STEPS_IN_CONTEXT_TEMPLATE.format(competition_name=competition_name)

    PROMPT_UNDERSTAND_BACKGROUND = f'''
# CONTEXT #
{steps_in_context}
Currently, I am at step one: Background Understand.
#############
# OBJECTIVE #
I want you to conduct a comprehensive analysis of the competition overview, understand the background of the topic, understand how to use different files, clarify the definition and requirements of the problem, obtain information about the data, and identify the target variable, evaluation metrics and submission format. Gather important information regarding Background/Files/Question/Target_Variable/Evaluation/Other aspects.
#############
# RESPONSE: JSON FORMAT #
{{
	"background_analysis": [BACKGROUND_ANALYSIS],
    "files_analysis": [FILES_ANALYSIS],
	"question_analysis": [QUESTION_DEFINITION], [QUESTION_REQUIREMENT],
	"target_variable_analysis": [TARGET_VARIABLE_ANALYSIS],
	"evaluation_analysis": [EVALUATION_ANALYSIS],
	"other_analysis": [OTHER_ANALYSIS],
}}
#############
# START ANALYSIS #
If you understand, please request the Overview of this data science competition from me.
'''
    history = []
    round = 0
    while True:
        # print("You: ")
        if round == 0:
            user_input = PROMPT_UNDERSTAND_BACKGROUND  
            print("Step 1 is in progress.") 
        elif round == 1:
            user_input = f'''
#############
# OVERVIEW #  
{overview}          
'''
            print("Overview is being sent to GPT-4O.")
        elif round == 2:
            print("Step 1 is complete.")
            break
        reply, history = multi_chat(user_input, history)
        round += 1
        print("GPT-4O:", reply)

    # pdb.set_trace()
    competition_info = history[-1].get('content', "EMPTY REPLY.")
    # extract the competition_info from JSON format
    competition_info = competition_info.split('```json')[1].split('```')[0]
    with open(f'{prefix}/{competition}/submission_{i}/competition_info.txt', 'w') as f:
        f.write(competition_info)
    return competition_info

if __name__ == '__main__':
    competition = 'house_prices'
    competition_info = understand_background(competition)
    print(competition_info)
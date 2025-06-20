import os
import sys

sys.path.append('..')
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from typing import List, Tuple
from api_handler import APIHandler
from utils import multi_chat
from openai import OpenAI
import tiktoken

class LLM:
    def __init__(self, model: str, type: str):
        if type == 'api':
            self.api_handler = APIHandler(model)
        elif type == 'local':
            pass

    def generate(self, prompt: str, history: list, max_tokens=4096) -> Tuple[str, list]:
        # Generate text based on prompt
        return multi_chat(self.api_handler, prompt, history, max_tokens)
    
class OpenaiEmbeddings:
    def __init__(self, api_key: str, base_url: str = None, model: str = 'text-embedding-3-large'):
        # self.client = OpenAI(api_key=api_key, base_url=base_url) # Commented out: No active embedding calls
        self.model = model
        # print("WARNING: OpenaiEmbeddings client is not initialized due to API key limitations.") # Optional: for debugging

        
    def num_tokens_from_string(string: str, encoding_name: str = 'cl100k_base') -> int:
        '''
        Returns the number of tokens in a text string.
        '''
        encoding = tiktoken.get_encoding(encoding_name)
        num_tokens = len(encoding.encode(string))

        return num_tokens
        
    def encode(self, input: str):
        # try:
        #     response = self.client.embeddings.create(
        #         model=self.model, input=input, encoding_format='float'
        #     )
        # except:
        #     len_embeddings = self.num_tokens_from_string(input)
        #     # if one of the inputs exceed the limit, raise error
        #     if len_embeddings > 8191:
        #         raise Exception(f'Input exceeds the limit of <{self.model}>!')
        #     else:
        #         raise Exception('Embeddings generation failed!')
            
        # return response.data
        print(f"WARNING: OpenaiEmbeddings.encode called for input '{input[:50]}...', but embedding generation is disabled. Returning empty list.")
        return [] # Placeholder for disabled functionality


def test_openai_embeddings():
    # api_key = 'your_api_key' # Commented out
    # base_url = None # Commented out

    # openai_embeddings = OpenaiEmbeddings(api_key, base_url) # Commented out
    # inputs = ['Hello, world!', 'How are you?'] # Commented out
    # response = openai_embeddings.encode(inputs) # Commented out
    # print(response) # Commented out
    print("test_openai_embeddings is currently disabled.")


if __name__ == '__main__':
    # test_openai_embeddings() # Commented out
    pass

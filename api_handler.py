import openai
import time
import os
import base64
import pdb
import sys
import logging

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# os.environ['OPENAI_API_KEY'] = 'your_api_key'
DIR = os.path.dirname(os.path.abspath(__file__))

def generate_response(client, engine, messages, settings, type, timeout):
    # print("Generating response for engine:", engine)
    logging.info(f"Generating response for engine: {engine}")
    start_time = time.time()
    
    try:
        if type == 'text':
            response = client.chat.completions.create(
                messages = messages,
                model = engine,
                temperature = settings.get('temperature', 0.0),
                max_tokens = settings.get('max_tokens', 50),
                top_p = settings.get('top_p', 1.0),
                frequency_penalty = settings.get('frequency_penalty', 0.0),
                presence_penalty = settings.get('presence_penalty', 0.0),
                stop = settings.get('stop', None),
                timeout = settings.get('timeout', 30),
            )
        elif type == 'image':
            response = client.chat.completions.create(
                messages = messages,
                model = engine,
                temperature = settings.get('temperature', 0.0),
                timeout = settings.get('timeout', 30),
            )
    except Exception as e:
        # print(f"Error during API call: {e}")
        logging.error(f"Error during API call: {e}")
        raise
    
    end_time = time.time()
    # print("Finish! Time taken:", end_time - start_time)
    # logging.info(f"Finish! Time taken: {end_time - start_time}")
    return response

class APIHandler:
    def __init__(self, model):
        if model not in ['gpt-3.5-turbo', 'gpt-4-turbo', 'gpt-4o']:
            raise NotImplementedError(f"Model {model} not implemented.")
        self.engine = model
        # self.api_key = os.getenv("OPENAI_API_KEY")
        # self.base_url = None
        with open(f'{DIR}/api_key.txt', 'r') as f:
            api_config = f.readlines()
            self.api_key = api_config[0].strip()
            self.base_url = api_config[1].strip() if len(api_config) > 1 else None

        if not self.api_key:
            raise ValueError("API key not found. Please set the OPENAI_API_KEY environment variable.")
        
        self.client = openai.OpenAI(api_key=self.api_key, base_url=self.base_url)
        # self.client = openai.OpenAI(api_key=self.api_key)
    
    def get_output(self, messages, max_tokens, top_p=1.0, temperature=0.0, frequency_penalty=0.0, presence_penalty=0.0, stop=None, type='text'):
        settings = {
            'max_tokens': max_tokens,
            'temperature': temperature,
            'top_p': top_p,
            'frequency_penalty': frequency_penalty,
            'presence_penalty': presence_penalty,
            'stop': stop,
            'timeout': (max_tokens // 1000 + 1) * 30,
        }
        
        timeout = settings['timeout']
        # print(f'Timeout is setting to {timeout} seconds.')
        # logging.info(f'Timeout is setting to {timeout} seconds.')

        max_attempts = 5
        for attempt in range(max_attempts):
            try:
                response = generate_response(self.client, self.engine, messages, settings, type, timeout)
                if response.choices and response.choices[0].message and hasattr(response.choices[0].message, 'content'):
                    return response.choices[0].message.content
                else:
                    return "Error: Wrong response format."
            except (TimeoutError, openai.APIError, openai.APIConnectionError, openai.RateLimitError) as error:
                # print(f'Attempt {attempt + 1} of {max_attempts} failed with error: {error}')
                logging.error(f'Attempt {attempt + 1} of {max_attempts} failed with error: {error}')
                time.sleep(30)
                if attempt == max_attempts - 1:
                    return "Error: Max attempts reached."


if __name__ == '__main__':
    handler = APIHandler('gpt-3.5-turbo')
    messages=[
        {"role": "system", "content": "You are a helpful assistant."},
        {"role": "user", "content": "How are you today?"}
    ]
    max_tokens = 50
    output_text = handler.get_output(messages=messages, max_tokens=max_tokens)
    print(output_text)

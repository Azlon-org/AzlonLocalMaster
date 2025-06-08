import os
import pandas as pd
import json
import sys

sys.path.append('..')
sys.path.append('../..')
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# from memory import Memory, transfer_text_to_json
# from memory import Memory # Removed as it's no longer used
from llm import OpenaiEmbeddings, LLM
from state import State
from utils import load_config, read_image
from typing import List

class ImageToTextTool:
    def __init__(
        self, 
        model: str = 'gpt-4.1-mini',
        type: str = 'api'
    ):
        self.llm = LLM(model, type)
        # self.memory = memory # Removed

    def image_to_text(self, state: State, chosed_images: List[str]):
        input = "Please read this data analysis image and give me a detailed description of it." \
                "You should describe the image in detail, including the data, the distribution, the relationship between variables, etc." \
                "And you should also give me some insights based on the image."
        images_to_descriptions = {}
        for image in chosed_images:
            image_path = f"{state.restore_dir}/images/{image}"
            reply = read_image(input, image_path)
            images_to_descriptions[image] = reply

        return images_to_descriptions

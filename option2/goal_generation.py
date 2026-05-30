import numpy as np
import sys
import os
sys.path.append('../')
from option2.history import History
from option2.representation import Representation

from transformers import AutoProcessor, AutoModelForCausalLM
import time
class GoalGenerator:
    def __init__(self,history:History,
            representation:Representation=None):
        self.history = history
        self.representation = representation
        #Model to generate goals

        root = os.environ['DSDIR'] + '/HuggingFace_Models' 
        MODEL_ID = os.path.join(root,"deepseek-ai/DeepSeek-V3-Base")
        # Load model
        self.processor = AutoProcessor.from_pretrained(MODEL_ID)
        self.model = AutoModelForCausalLM.from_pretrained(
            MODEL_ID,
            dtype="auto",
            device_map="auto"
        )

    def __call__(self):
        time0 = time.time()
        # Prompt
        messages = [
            {"role": "system", "content": "You are a helpful assistant."},
            {"role": "user", "content": "Write a short joke about saving RAM."},
        ]
        
        # Process input
        text = processor.apply_chat_template(
            messages, 
            tokenize=False, 
            add_generation_prompt=True, 
            enable_thinking=False
        )
        inputs = self.processor(text=text, return_tensors="pt").to(self.model.device)
        input_len = inputs["input_ids"].shape[-1]
        
        # Generate output
        outputs = self.model.generate(**inputs, max_new_tokens=1024)
        response = self.processor.decode(outputs[0][input_len:], skip_special_tokens=False)
        
        # Parse output
        self.processor.parse_response(response)

        time1 = time.time()
        print(time1-time0)

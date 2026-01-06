from openai import OpenAI
from dotenv import load_dotenv
import os
import yaml

load_dotenv()

with open("prompts.yaml", "r") as f:
    prompts = yaml.safe_load(f)

class GenerateEmail():
    def __init__(self, model: str):
        # initialize client once
        self.client = OpenAI(
            base_url=os.getenv("OPENAI_API_BASE"),
            api_key=os.getenv("OPENAI_API_KEY"),
        )
        self.deployment_name = model
        self.action_set = {
            'tone',
            'shorten',
            'elaborate',
        }

    def _call_api(self, messages):
        # TODO: implement this function to call ChatCompletions
        response = self.client.chat.completions.create(
            model=self.deployment_name,
            messages=messages
        )
        print(response.choices[0].message.content)
        return response.choices[0].message.content
    
    def get_prompt(self, prompt_name, prompt_type='user', **kwargs):
        template = prompts[prompt_name][prompt_type]
        return template.format(**kwargs)
    
    def send_prompt(self, user_prompt: str, system_msg="You are a helpful assistant."):
        messages = [
            {"role": "system", "content": system_msg},
            {"role": "user", "content": user_prompt}
        ]
        return self._call_api(messages)
    
    def generate(self, action: str) -> list:
        # TODO: implement your backend logic with this method. Skeleton code is provided below.

        if action not in self.action_set:
            print("")


        if action == 'tone':
            # do something specifically for tone since it will ask for more settings
            # either sympathetic, professional, friendly
            pass

        args = {
            "selected_text": "Hello World!"
        }
        system_prompt = self.get_prompt(action, prompt_type='system', **args)
        user_prompt = self.get_prompt(action, **args)
        print("system prompt:", system_prompt)
        print("user prompt:", user_prompt)
        model_response = self.send_prompt(user_prompt, system_prompt)
        return model_response
            
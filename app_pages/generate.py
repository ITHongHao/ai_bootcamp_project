from openai import OpenAI
from dotenv import load_dotenv
import os
import yaml
import json

load_dotenv()

with open("prompts.yaml", "r") as f:
    prompts = yaml.safe_load(f)

class GenerateEmail():
    def __init__(self, model: str, **kwargs):
        # initialize client once
        self.client = OpenAI(
            base_url=os.getenv("OPENAI_API_BASE"),
            api_key=os.getenv("OPENAI_API_KEY"),
        )
        self.deployment_name = model
        self.action_set = {
            'subject-line',
            'tone',
            'shorten',
            'lengthen',
            'faithfulness',
            'completeness',
            'conciseness',
            'relevance',
            'formatting',
            'pii-safety',
            'toxicity',
        }
        self.evaluation_metrics = {
            'faithfulness',
            'completeness',
            'conciseness',
            'relevance',
            'formatting',

        }
        self.guardrails = {
            'pii-safety',
            'toxicity',
        }
        self.models = [
            'gpt-4o-mini',
            'gpt-4.1',
        ]
        self.llm_settings = kwargs

    def _call_api(self, messages):
        # TODO: implement this function to call ChatCompletions
        response = self.client.chat.completions.create(
            model=self.deployment_name,
            messages=messages
        )
        # print(response.choices[0].message.content)
        return response.choices[0].message.content
    
    def get_prompt(self, prompt_name, prompt_type='user', language='en', get_raw=False, **kwargs):
        # print(prompts[prompt_name][prompt_type])
        template = prompts[prompt_name][prompt_type][language]
        print(type(template))
        if get_raw:
            return template
        return template.format(**kwargs)
    
    def send_prompt(self, user_prompt: str, system_msg="You are a helpful assistant."):
        messages = [
            {"role": "system", "content": system_msg},
            {"role": "user", "content": user_prompt}
        ]
        return self._call_api(messages)
    
    def generate(self, action: str, args: dict = {}) -> list:
        # TODO: implement your backend logic with this method. Skeleton code is provided below.

        if action not in self.action_set:
            error_msg = f"Error! No action registered: {action}"
            print(error_msg)
            return error_msg


        if action == 'tone':
            # do something specifically for tone since it will ask for more settings
            # either sympathetic, professional, friendly

            # check for if extra context is added
            # if not, must prompt the user to add extra context
            pass
        

        system_prompt = self.get_prompt(action, prompt_type='system', language='en', **args)
        user_prompt = self.get_prompt(action, **args)
        # print("system prompt:", system_prompt)
        # print("user prompt:", user_prompt)
        model_response = self.send_prompt(user_prompt, system_prompt)
        # print(model_response)
        return model_response

    def generate_data(self, file_name: str, dataset_name: str, amount, args: dict = {}):
        # initialize prompts to send
        system_prompt = self.get_prompt(
            prompt_name=f'generate-{dataset_name}-data',
            prompt_type='system',
            langauge='en',
            **args,
        )

        # open file to write to
        file_path = f'/Users/itang/Music/servicenow_bootcamp/ai_bootcamp_starter/datasets/{file_name}.jsonl'
        # Ensure parent directory exists
        parent_dir = os.path.dirname(file_path)
        if parent_dir:  # guard in case file_path is just "file.jsonl"
            os.makedirs(parent_dir, exist_ok=True)

        # Create/overwrite the file and write JSONL
        with open(file_path, "w", encoding="utf-8") as f:
            data_args = {
                'previous_emails' : ''
            }
            for i in range(amount):
                user_prompt = self.get_prompt(
                    prompt_name=f'generate-{dataset_name}-data',
                    prompt_type='user',
                    langauge='en',
                    **data_args,
                )

                raw = self.send_prompt(user_prompt, system_prompt)

                # The model might return one JSON object or multiple lines; normalize to JSONL
                fixed_lines = []
                for line in raw.splitlines():
                    line = line.strip()
                    if not line:
                        continue

                    obj = json.loads(line)          # parse JSON object
                    obj["id"] = i + 1               # or i, depending on what you want
                    fixed_lines.append(json.dumps(obj, ensure_ascii=False))

                fixed_jsonl = "\n".join(fixed_lines) + "\n"

                # Write to the output JSONL file
                f.write(fixed_jsonl)

                # Feed corrected history back into the next prompt
                data_args["previous_emails"] += fixed_jsonl

            
            # print(data_args)
        # generate {amount} new datapoints

        # write generated datapoint to file




if __name__ == '__main__':
    print("Running generate.py")
    llm = GenerateEmail(os.getenv("DEPLOYMENT_NAME"))
    llm.generate_data('test_generation', 'shorten', 5)

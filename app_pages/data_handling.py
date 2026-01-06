import streamlit as st
import json
import os

from dataclasses import dataclass, field

# datasets register
demo_datasets = {
    "lengthen" : "/Users/itang/Music/servicenow_bootcamp/ai_bootcamp_starter/datasets/lengthen.jsonl",
    "shorten" : "/Users/itang/Music/servicenow_bootcamp/ai_bootcamp_starter/datasets/shorten.jsonl",
    "tone" : "/Users/itang/Music/servicenow_bootcamp/ai_bootcamp_starter/datasets/tone.jsonl",
    'test' : '/Users/itang/Music/servicenow_bootcamp/ai_bootcamp_starter/datasets/test.jsonl',
}


def choose_demo_data(datasets=demo_datasets):
    choice = st.selectbox(
        label="Select the dataset.", 
        options=list(datasets.keys()),
        accept_new_options=False,
    )
    return choice



def load_data(choice, datasets=demo_datasets):
    # store into emails
    emails = {}

    # load the dataset
    with open(datasets[choice], 'r', encoding='utf-8') as dataset_file:
        for index, line in enumerate(dataset_file, start=1):
            try:
                data = json.loads(line)
                # print(data)
                emails[index] = data
            except json.JSONDecodeError:
                print(f"JSONDecodeError: {line}")
    
    return emails
        


@dataclass
class EvaluationMetric:
    name: str
    category: str = ""
    score: int = -1
    reasoning: str = ""
    # field(init=False) tells Python: "Don't ask for this in the constructor arguments"
    status: str = field(init=False)

    def __post_init__(self):
        """
        This runs automatically immediately after the object is created.
        We use it to calculate derived fields like 'status'.
        """
        self.status = "Pass" if self.score >= 4 else "Fail"
    
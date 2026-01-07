import streamlit as st
import json
import os

import pandas as pd
import plotly.express as px
import random
import plotly.graph_objects as go
import math

import streamlit.components.v1 as components
import numpy as np

from generate import GenerateEmail
from data_handling import EvaluationMetric

# --- HARD CODED DEFAULTS ---
DEMO_DATASETS = {
    "lengthen" : "/Users/itang/Music/servicenow_bootcamp/ai_bootcamp_starter/datasets/lengthen.jsonl",
    "shorten" : "/Users/itang/Music/servicenow_bootcamp/ai_bootcamp_starter/datasets/shorten.jsonl",
    "tone" : "/Users/itang/Music/servicenow_bootcamp/ai_bootcamp_starter/datasets/tone.jsonl",
    'test' : '/Users/itang/Music/servicenow_bootcamp/ai_bootcamp_starter/datasets/test.jsonl',
}

DEFAULT_LLM_SETTINGS = {
    # --- Generation & Creativity (The "Feel") ---
    "temperature": 0.7,           # Range: 0 to 2. Recommended: 0.7 for balance, 0.2 for facts.
    "top_p": 1.0,                 # Recommended: adjust this OR temperature, not both.
    
    # --- Cost & Length Control ---
    "max_completion_tokens": 1000, # Hard ceiling for generation. Protects your wallet.
    "n": 1,                        # Generate 1 response. (Higher values = 2x or 3x cost).

    # --- Repetition & Tone Control ---
    "presence_penalty": 0.0,      # Range: -2 to 2. Higher values encourage new topics.
    "frequency_penalty": 0.0,     # Range: -2 to 2. Higher values prevent word repetition.
    
    # --- Formatting & Structure ---
    "stop": None,                 # Up to 4 strings to halt generation (e.g. ["User:", "###"]).
    "response_format": {"type": "text"}, # Options: {"type": "json_object"} or "text".
    
    # --- Reliability (Advanced) ---
    "seed": None,                 # Integer for deterministic results (Beta).
    "logprobs": False,            # Whether to return token probabilities.
    "top_logprobs": None,         # Required if logprobs is True.
}

# --- EMAIL CLASS OBJECT ---
class Email():
    def __init__(self, email_json: dict | None = None):
        # If no argument is passed (None), we use an empty dictionary
        # to ensure the .get() methods don't crash.
        data = email_json or {}
        
        self.sender = data.get('sender', '(unknown)')
        self.subject = data.get('subject', '(no subject)')
        self.message = data.get('content', '')


# --- UTILITY FUNCTIONS ---
def load_data(choice, datasets=DEMO_DATASETS):
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


def initialize_session_states(
    dataset_name: str = '',
    dataset: any = None,
    email_id: str | None = None,
    model_name: str = 'gpt-4.1',
    edit_method: str = '',
) -> None:
    """
    Initializes session state using Python 3.11 logic.
    Uses 'None' as a default for the dictionary to prevent shared-state bugs.
    """
    print("Initializing all session states")
    # --- Logic 1: Basic Variables ---
    st.session_state.setdefault("dataset_name", dataset_name)
    st.session_state.setdefault("dataset", load_data(dataset_name) if dataset_name != '' else {})
    st.session_state.setdefault("email_id", email_id)
    st.session_state.setdefault("model_name", model_name)
    st.session_state.setdefault("edit_method", edit_method)
    st.session_state.setdefault("edit_subject_toggle", False)
    st.session_state.setdefault("generated_subject", "(no subject)")
    st.session_state.setdefault("evaluation_data", {})

    

    # suite email text boxes
    # print(type(st.session_state.dataset.keys()))
    # print({"0" : "hi"}.keys())
    email = st.session_state.dataset.get(st.session_state.email_id)['content']
    st.session_state.setdefault('original_textbox_suite', email)
    st.session_state.setdefault('generated_textbox_suite', '')

    # --- Logic 2: Advanced Settings ---
    st.session_state.setdefault("llm_settings", DEFAULT_LLM_SETTINGS.copy())

    # --- App Variables ---
    st.session_state.setdefault("tmp_setting_save", False)
    for key, value in st.session_state.llm_settings.items():
        st.session_state.setdefault(f"tmp_{key}", value)

    # --- Logic 3: Class Instance ---
    if "llm" not in st.session_state:
        current_settings = st.session_state.llm_settings
        
        st.session_state.llm = GenerateEmail(
            st.session_state.model_name, 
            **current_settings
        )
    
    # --- Edit subject line toggle ---
    

def generate_email(original_email: Email = Email()) -> Email:    
    # retrieve original message data
    sender: str = original_email.sender
    subject: str = original_email.subject
    original: str = original_email.message

    # get the LLM
    llm = st.session_state.llm

    # get extra context
    context = st.session_state.extra_context

    # get edit method
    edit_method = st.session_state.edit_method.lower()
    
    # parameters to pass to LLM
    gen_email_args = {
        'selected_text' : original,
        'additional_text' : context,
    }
    
    # call api to generate email
    generated = llm.generate(
        action=edit_method,
        args=gen_email_args,
    )
    st.session_state.generated_textbox_suite = generated

    # generate new subject title (only if toggled)
    if st.session_state.edit_subject_toggle:
        subject_line_args = {
            'selected_text' : subject,
            'additional_text' : generated,
        }

        edited_subject = llm.generate(
            action='subject-line',
            args=subject_line_args,
        )
    else:
        edited_subject = original_email.subject
    st.session_state.generated_subject = edited_subject


    print('original:', original)
    print('extra:', context)
    print('generated: ', generated)

    # set the evaluation scores
    # generate guardrail checks
    guardrails = []
    for guardrail in st.session_state.llm.guardrails:
        print(guardrail)
        metrics_args = {
                'selected_text' : original,
                'additional_text' : context,
                'model_response' : generated,
            }
        
        evaluation_json = st.session_state.llm.generate(
            action=guardrail,
            args=metrics_args,
        )
        try: # categories are not implemented yet
            data = json.loads(evaluation_json)
            print(type(data.get('rating')))
            guardrails.append({
                'name' : guardrail,
                'status' : 'Pass' if data.get('rating') == 1 else 'Fail',
                'reasoning' : data.get('explanation'),
            })
            # determine if it has a category or not
            
        except json.JSONDecodeError:
            print(f"JSONDecodeError: {evaluation_json}")

    # generate metrics
    metrics = []
    # by default, all metrics will run
    evaluation_metrics = st.session_state.evaluation_metrics if len(st.session_state.evaluation_metrics) != 0 else st.session_state.llm.evaluation_metrics
    # print(evaluation_metrics)
    for metric in evaluation_metrics:
        metrics_args = {
                'selected_text' : original,
                'additional_text' : context,
                'model_response' : generated,
            }
        
        evaluation_json = st.session_state.llm.generate(
            action=metric,
            args=metrics_args,
        )
        try: # categories are not implemented yet
            data = json.loads(evaluation_json)
            metrics.append({
                'name' : metric,
                'score' : data.get('rating'),
                'reasoning' : data.get('explanation'),
                'category' : "Test"
            })
            # determine if it has a category or not
            
        except json.JSONDecodeError:
            print(f"JSONDecodeError: {evaluation_json}")

        # metrics.append(new_metric)
    
    # print(len(metrics))
    # st.write("Guardrails")
    # st.write(guardrails)
    overall_score = get_overall_score(metrics)
    # guardrails = [{"name": "Faithfulness", "status": "Pass", "reasoning": "No hallucinations detected."},]



    eval_data = {
        "overall_score": overall_score,       # mean of over chosen metrics
        "status": "Satisfactory" if overall_score >= 4 else "Review Needed",  # determineed by overall score
        "guardrails": guardrails,
        "metrics": metrics,
    }
    st.session_state.evaluation_data = eval_data

    # print(eval_data)

    
    return Email({
        'sender' : sender,
        'subject' : edited_subject,
        'content' : generated,
    })



# --- SYNCING AND RENDERING FUNCTIONS ---
def sync_email_dataset():
    """
    Callback to sync the UI state when the selected dataset changes.
    This ensures the text box reflects the new data immediately.
    """
    print("Syncing dataset")

    # load in newly selected dataset
    dataset = load_data(st.session_state.dataset_name)
    st.session_state.dataset = dataset

    # sync the chosen email
    sync_email_id()

def sync_email_id():
    """
    Callback to sync the UI state when the selected email changes.
    This ensures the text box reflects the new data immediately.
    """
    print("Syncing selected id")
    

    # make sure the id exists in the current dataset
    if st.session_state.email_id > len(st.session_state.dataset):
        st.session_state.email_id = len(st.session_state.dataset)

    # get the new ID from the selector
    email_id = st.session_state.email_id
    print(st.session_state.email_id)

    # Retrieve the email data
    raw_data = st.session_state.dataset.get(email_id, None)
    print(raw_data)
    email = raw_data.get('content', '')
    print(email)
    
    # Explicitly update the text area's session state key
    # This prevents the 'widget persistence' bug without needing dynamic keys
    st.session_state.original_textbox_suite = email
    
    # Clear the generated output for the new selection
    st.session_state.generated_textbox_suite = ""
    st.session_state.generated_subject = ""

def sync_llm():
    """
    Callback to sync the LLM when the selected model changes.
    This ensures the model object updates immediately.
    """
    print("Syncing model selection and parameters")
    current_settings = st.session_state.llm_settings
    st.session_state.llm = GenerateEmail(
        st.session_state.model_name, 
        **current_settings,
    )
    

def save_advanced_settings():
    """Callback to move values from tmp_ keys to the actual llm_settings dict."""
    for key in st.session_state.llm_settings.keys():
        tmp_key = f"tmp_{key}"
        if tmp_key in st.session_state:
            st.session_state.llm_settings[key] = st.session_state[tmp_key]
    st.session_state.tmp_setting_save = True

@st.dialog("Advanced LLM Settings")
def advanced_llm_settings_form():
    # Force initial sync of tmp keys from official settings only once per dialog open
    if "dialog_initialized" not in st.session_state:
        for key, value in st.session_state.llm_settings.items():
            st.session_state[f"tmp_{key}"] = value
        st.session_state.dialog_initialized = True

    # helper info on API and the settings
    st.info("Refer to the [Azure OpenAI API Reference](https://learn.microsoft.com/en-us/azure/ai-foundry/openai/reference?view=foundry-classic#chat-completions) for detailed parameter definitions.")

    with st.form(key="advanced_llm_settings_form"):
        
        with st.expander("Creativity", expanded=True):
            st.slider(
                label="Temperature",
                min_value=0.0,
                max_value=2.0,
                step=0.01,
                key="tmp_temperature",
                help="Controls randomness. Lowering results in less random and more deterministic outputs."
            )
            st.slider(
                label="Top p",
                min_value=0.0,
                max_value=1.0,
                step=0.01,
                key="tmp_top_p",
                help="Nucleus sampling. The model considers tokens with top_p probability mass."
            )

        with st.expander("Cost and Length"):
            st.number_input(
                label="Max Completion Tokens",
                min_value=1,
                max_value=128000,
                step=1,
                key="tmp_max_tokens",
                help="The maximum number of tokens that can be generated in the chat completion."
            )
            st.number_input(
                label="n (Batch Count)",
                min_value=1,
                max_value=5,
                step=1,
                key="tmp_n",
                help="How many chat completion choices to generate for each input message."
            )

        with st.expander("Repetition and Tone"):
            st.slider(
                label="Presence Penalty",
                min_value=-2.0,
                max_value=2.0,
                step=0.1,
                key="tmp_presence_penalty",
                help="Increases the model's likelihood to talk about new topics."
            )
            st.slider(
                label="Frequency Penalty",
                min_value=-2.0,
                max_value=2.0,
                step=0.1,
                key="tmp_frequency_penalty",
                help="Decreases the likelihood of the model repeating the same line verbatim."
            )

        with st.expander("Reliability"):
            st.number_input(
                label="Seed",
                key="tmp_seed",
                help="If specified, the system will make a best effort to sample deterministically."
            )
            st.number_input(
                    label="Top Log Probs",
                    min_value=0,
                    max_value=20,
                    key="tmp_top_logprobs",
                    help="Number of most likely tokens to return at each position. If left blank, no log probabilities will be returned!"
                )
            
            if st.session_state.tmp_top_logprobs:
                # print("there is a log top prob thingy")
                st.session_state.tmp_logprobs = True

        submit_clicked = st.form_submit_button(label="Save Changes")
        
        if submit_clicked:
            save_advanced_settings()
            if "dialog_initialized" in st.session_state:
                del st.session_state.dialog_initialized
            st.rerun()

        

# --- MISC ---

def render_gmail_preview(email_recipients="Recipients",email_subject="Subject", email_body="", height=550):
    """
    Renders a pixel-perfect Gmail 'New Message' window.
    FIXED: CSS braces are escaped ({{ }}) for f-string compatibility.
    """
    
    html_code = f"""
    <!DOCTYPE html>
    <html>
    <head>
    <link href="https://fonts.googleapis.com/icon?family=Material+Icons+Outlined" rel="stylesheet">
    <style>
        :root {{
            --bg-color: #ffffff;
            --header-bg: #f2f6fc;
            --border-color: #e0e0e0;
            --text-primary: #202124;
            --text-secondary: #5f6368;
            --blue-accent: #0b57d0;
            --icon-color: #444746;
            --hover-bg: rgba(32,33,36,0.059);
            --divider-color: #dadce0;
        }}
        body {{
            font-family: 'Roboto', Arial, sans-serif;
            margin: 0;
            padding: 0;
            background-color: transparent;
        }}
        .gmail-container {{
            background-color: var(--bg-color);
            border-radius: 8px 8px 0 0;
            box-shadow: 0 8px 10px 1px rgba(0,0,0,0.14), 0 3px 14px 2px rgba(0,0,0,0.12), 0 5px 5px -3px rgba(0,0,0,0.2);
            overflow: hidden;
            display: flex;
            flex-direction: column;
            height: 100vh;
            border: 1px solid #dadce0;
        }}
        
        /* HEADER & INPUTS */
        .header {{
            background-color: var(--header-bg);
            padding: 6px 15px;
            display: flex;
            justify-content: space-between;
            align-items: center;
        }}
        .header-title {{
            font-size: 14px;
            font-weight: 500;
            color: var(--text-primary);
            letter-spacing: .25px;
        }}
        .window-controls span {{
            font-size: 18px;
            color: var(--text-secondary);
            margin-left: 8px;
            cursor: pointer;
        }}

        .field-row {{
            padding: 4px 15px;
            border-bottom: 1px solid var(--border-color);
            display: flex;
            align-items: center;
            min-height: 40px;
        }}
        .field-input {{
            flex-grow: 1;
            border: none;
            outline: none;
            font-size: 14px;
            font-family: inherit;
            color: var(--text-primary);
        }}
        .field-label {{ color: var(--text-secondary); font-size: 14px; margin-right: 10px; }}
        .cc-bcc {{ margin-left: auto; font-size: 14px; color: var(--text-secondary); }}
        
        .email-body {{
            flex-grow: 1;
            padding: 16px 15px;
            font-size: 14px;
            color: var(--text-primary);
            line-height: 1.5;
            outline: none;
            overflow-y: auto;
            white-space: pre-wrap;
        }}

        /* --- FOOTER CONTAINER --- */
        .footer-container {{
            display: flex;
            flex-direction: column;
        }}

        /* --- ROW 1: FORMATTING TOOLBAR --- */
        .format-toolbar {{
            display: flex;
            align-items: center;
            padding: 4px 8px;
            margin: 0 8px;
            border-bottom: 1px solid transparent; 
        }}
        
        .format-group {{
            display: flex;
            align-items: center;
            margin-right: 8px;
            border-right: 1px solid var(--divider-color);
            padding-right: 8px;
        }}
        .format-group:last-child {{ border-right: none; }}

        .fmt-btn {{
            color: var(--icon-color);
            padding: 4px;
            margin: 0 1px;
            cursor: pointer;
            border-radius: 4px;
            display: flex;
            align-items: center;
            justify-content: center;
        }}
        .fmt-btn:hover {{ background-color: var(--hover-bg); }}
        .fmt-icon {{ font-size: 18px !important; }}
        
        .font-selector {{
            font-size: 13px;
            font-weight: 500;
            padding: 2px 6px;
            margin-right: 2px;
            display: flex;
            align-items: center;
        }}
        .tiny-arrow {{ font-size: 14px !important; margin-left: 2px; }}

        /* --- ROW 2: ACTIONS BAR --- */
        .action-toolbar {{
            display: flex;
            justify-content: space-between;
            align-items: center;
            padding: 12px 16px;
            height: 48px;
        }}

        .btn-send {{
            background-color: var(--blue-accent);
            color: white;
            border: none;
            border-radius: 18px 0 0 18px; 
            padding: 0 20px;
            height: 36px;
            font-size: 14px;
            font-weight: 500;
            cursor: pointer;
            margin-right: 1px; 
        }}
        .btn-send-arrow {{
            background-color: var(--blue-accent);
            color: white;
            border: none;
            border-radius: 0 18px 18px 0; 
            height: 36px;
            padding: 0 6px;
            cursor: pointer;
            display: flex;
            align-items: center;
        }}
        .btn-send:hover, .btn-send-arrow:hover {{ background-color: #0a50c0; }}
        
        .send-wrapper {{ display: flex; align-items: center; margin-right: 16px; }}

        .action-icon {{
            color: var(--icon-color);
            margin: 0 2px;
            padding: 8px;
            cursor: pointer;
            font-size: 20px !important;
            border-radius: 50%;
        }}
        .action-icon:hover {{ background-color: var(--hover-bg); }}
        
        .icon-active {{
            background-color: #e8eaed;
            color: #1f1f1f;
        }}

        .spacer {{ flex-grow: 1; }}

    </style>
    </head>
    <body>
        <div class="gmail-container">
            <div class="header">
                <div class="header-title">New Message</div>
                <div class="window-controls">
                    <span class="material-icons-outlined">minimize</span>
                    <span class="material-icons-outlined">open_in_full</span>
                    <span class="material-icons-outlined">close</span>
                </div>
            </div>

            <div class="field-row">
                <span class="field-label">To</span>
                <input type="text" class="field-input" value="{email_recipients}">
                <div class="cc-bcc">Cc Bcc</div>
            </div>
            <div class="field-row">
                <input type="text" class="field-input" value="{email_subject}" placeholder="Subject">
            </div>

            <div class="email-body" contenteditable="true" spellcheck="false">
{email_body}
<br><br>--<br>Sent via AI Email Suite
            </div>

            <div class="footer-container">
                
                <div class="format-toolbar">
                    <div class="format-group">
                        <div class="fmt-btn"><span class="material-icons-outlined fmt-icon">undo</span></div>
                        <div class="fmt-btn"><span class="material-icons-outlined fmt-icon">redo</span></div>
                    </div>
                    
                    <div class="format-group">
                        <div class="fmt-btn font-selector">Sans Serif <span class="material-icons-outlined tiny-arrow">arrow_drop_down</span></div>
                        <div class="fmt-btn font-selector">TT <span class="material-icons-outlined tiny-arrow">arrow_drop_down</span></div>
                    </div>
                    
                    <div class="format-group">
                        <div class="fmt-btn"><span class="material-icons-outlined fmt-icon">format_bold</span></div>
                        <div class="fmt-btn"><span class="material-icons-outlined fmt-icon">format_italic</span></div>
                        <div class="fmt-btn"><span class="material-icons-outlined fmt-icon">format_underlined</span></div>
                        <div class="fmt-btn"><span class="material-icons-outlined fmt-icon">format_color_text</span></div>
                    </div>
                    
                    <div class="format-group">
                        <div class="fmt-btn"><span class="material-icons-outlined fmt-icon">format_align_left</span><span class="material-icons-outlined tiny-arrow">arrow_drop_down</span></div>
                    </div>
                    
                    <div class="format-group">
                        <div class="fmt-btn"><span class="material-icons-outlined fmt-icon">format_list_numbered</span></div>
                        <div class="fmt-btn"><span class="material-icons-outlined fmt-icon">format_list_bulleted</span></div>
                        <div class="fmt-btn"><span class="material-icons-outlined fmt-icon">format_indent_increase</span></div>
                        <div class="fmt-btn"><span class="material-icons-outlined fmt-icon">format_indent_decrease</span></div>
                    </div>
                    
                    <div class="format-group">
                         <div class="fmt-btn"><span class="material-icons-outlined fmt-icon">format_quote</span></div>
                         <div class="fmt-btn"><span class="material-icons-outlined fmt-icon">strikethrough_s</span></div>
                         <div class="fmt-btn"><span class="material-icons-outlined fmt-icon">format_clear</span></div>
                    </div>
                </div>

                <div class="action-toolbar">
                    <div class="send-wrapper">
                        <button class="btn-send">Send</button>
                        <button class="btn-send-arrow"><span class="material-icons-outlined" style="font-size:18px">arrow_drop_down</span></button>
                    </div>

                    <span class="material-icons-outlined action-icon icon-active">text_format</span>
                    <span class="material-icons-outlined action-icon">attach_file</span>
                    <span class="material-icons-outlined action-icon">insert_link</span>
                    <span class="material-icons-outlined action-icon">insert_emoticon</span>
                    <span class="material-icons-outlined action-icon">add_to_drive</span>
                    <span class="material-icons-outlined action-icon">insert_photo</span>
                    <span class="material-icons-outlined action-icon">lock_clock</span>
                    <span class="material-icons-outlined action-icon">edit_note</span>
                    <span class="material-icons-outlined action-icon">more_vert</span>
                    
                    <div class="spacer"></div>
                    
                    <span class="material-icons-outlined action-icon">delete</span>
                </div>
            </div>
        </div>
    </body>
    </html>
    """
    
    components.html(html_code, height=height, scrolling=False)

def display_generated_email_score(scores: dict = {}):
    faithfulness, completeness, conciseness = st.columns(3, border=True)
        
    with faithfulness:
        faithfulness_rating = -1 # analytics['faithfulness_rating'][selected_id-1]
        faithfulness_explanation = "No explanation implemented yet." #analytics['faithfulness_explanation'][selected_id-1]
        st.html(
        f"""
            <div style="text-align: center;">
                <h1>
                    <b>{faithfulness_rating}</b>
                </h1>
                <h3>
                    <u><b>Faithfulness</b></u>
                </h3>
            </div>
            <div>
                <p>
                    {faithfulness_explanation}
                </p>
            </div>
            """
        )
    
    with completeness:
        completeness_rating = -1 # analytics['completeness_rating'][selected_id-1]
        completeness_explanation = "No explanation implemented yet." # analytics['completeness_explanation'][selected_id-1]
        st.html(
        f"""
            <div style="text-align: center;">
                <h1>
                    <b>{completeness_rating}</b>
                </h1>
                <h3>
                    <u><b>Completeness</b></u>
                </h3>
            </div>
            <div>
                <p>
                    {completeness_explanation}
                </p>
            </div>
            """
        )
    
    with conciseness:
        conciseness_rating = -1
        conciseness_explanation = "No explanation implemented yet."
        # conciseness_rating = analytics['conciseness_rating'][selected_id-1]
        # conciseness_explanation = analytics['conciseness_explanation'][selected_id-1]
        st.html(
        f"""
            <div style="text-align: center;">
                <h1>
                    <b>{conciseness_rating}</b>
                </h1>
                <h3>
                    <u><b>Conciseness</b></u>
                </h3>
            </div>
            <div>
                <p>
                    {conciseness_explanation}
                </p>
            </div>
            """
        )


def get_overall_score(metrics):
    if not metrics:
        metrics = st.session_state.evaluation_data['metrics']

    total = 0
    for metric in metrics:
        total += metric['score']

    # st.write(metrics)
    return (math.floor((total / len(metrics)) * 100)) / 100

def test():
    # make sure only generate if there is a generated answer
    if st.session_state.generated_textbox_suite == "":
        st.warning(f"WARNING: No generated response has been created for **Email ID {st.session_state.email_id}**. Click the Generate button to generate an edited email.")
        return
    
    eval_data = st.session_state.evaluation_data



    # ========== UI ELEMENTS ==========
    with st.container(border=True):
        st.markdown("## Evaluation Results")

        # --- 2. HEADER: HIGH-LEVEL HEALTH ---
        top_c1, top_c2, top_c3 = st.columns([1, 1, 2])
        with top_c1:
            st.metric("Overall Score", f"{eval_data['overall_score']} / 5", delta="-0.4", help="Overall score is the average of all selected metrics. The delta is the difference from the dataset average score")
        with top_c2:
            # Dynamic Status Badge
            color = "green" if eval_data['overall_score'] >= 4 else "orange" if eval_data['overall_score'] >= 3 else "red"
            st.markdown("**Status**", help="Emails with overall scores under 4 must be reviewed.")
            st.markdown(f":{color}-background[{eval_data['status']}]")
        with top_c3:
            # Quick Guardrail Check (Mini indicators)
            st.markdown("**Guardrails**", help="Guardrails are determined by judge prompts that output a boolean response and reasoning.")
            g_cols = st.columns(len(eval_data['guardrails']))
            for i, g in enumerate(eval_data['guardrails']):
                icon = "✅" if g['status'] == "Pass" else "❌"
                g_cols[i].caption(f"{icon} {g['name']}")



    # --- 3. VISUALIZATION LAYER ---
    col_viz, col_matrix = st.columns([1, 1], gap="medium")

    with col_viz: # should display all metrics asked for
        st.subheader("Shape of Text Quality")
    
        # 1. Prepare Data
        df_metrics = pd.DataFrame(eval_data['metrics'])
        
        # LOGIC: Check metric count
        if len(df_metrics) < 3:
            # Fallback to Bar Chart if < 3 metrics (Radar chart needs 3 points to make a shape)
            fig = go.Figure()
            fig.add_trace(go.Bar(
                x=df_metrics["name"],
                y=df_metrics["score"],
                marker=dict(color='#00CC96'),
                text=df_metrics["score"],
                textposition='auto'
            ))
            fig.update_layout(
                yaxis=dict(range=[0, 5], gridcolor="#333"),
                xaxis=dict(tickfont=dict(color="white")),
                paper_bgcolor="rgba(0,0,0,0)",
                plot_bgcolor="rgba(0,0,0,0)",
                font=dict(color="white"),
                height=300,
                margin=dict(l=20, r=20, t=20, b=20)
            )

        else:
            # 2. CLOSE THE LOOP MANUALLY
            # We append the first row to the end of the DataFrame.
            # This ensures the line draws from A -> B -> C -> A perfectly.
            df_closed = pd.concat([df_metrics, df_metrics.iloc[[0]]], ignore_index=True)
            
            fig = go.Figure()
            
            fig.add_trace(go.Scatterpolar(
                r=df_closed["score"],
                theta=df_closed["name"],
                fill='toself',          # Fills the area
                mode='lines+markers',   # Draws the border line AND points
                line=dict(color='#00CC96', width=2),
                marker=dict(color='#00CC96', size=6),
                name='Current Evaluation'
            ))
            
            # 3. Apply Dark Mode Styling
            fig.update_layout(
                polar=dict(
                    bgcolor="rgba(0,0,0,0)", # Transparent background
                    
                    # The Radial Axis (Circles 0-5)
                    radialaxis=dict(
                        visible=True,
                        range=[0, 5],
                        showticklabels=True,
                        tickfont=dict(color="gray", size=10),
                        gridcolor="#333",
                        linecolor="#333"
                    ),
                    
                    # The Angular Axis (Metric Labels)
                    angularaxis=dict(
                        tickfont=dict(color="white", size=12, weight="bold"),
                        gridcolor="#333",
                        linecolor="#333",
                        rotation=90
                    )
                ),
                font=dict(color="white"),
                paper_bgcolor="rgba(0,0,0,0)",
                showlegend=False,
                height=300,
                margin=dict(l=80, r=80, t=20, b=20)
            )

        st.plotly_chart(fig, use_container_width=True)

    with col_matrix: # should display all metrics asked for
        st.subheader("Metric Heatmap")
        st.caption("Quickly spot weak points (Darker = Lower Score)")
        
        # HEATMAP: A modern way to view many metrics at once
        # Reshape data into a 2x5 grid for visualization
        matrix_data = df_metrics.sort_values(by="score", ascending=False)
        
        fig_bar = px.bar(
            matrix_data,
            x="score",
            y="name",
            orientation='h',
            color="score",
            color_continuous_scale="RdYlGn", # Red to Green
            text="score"
        )
        fig_bar.update_layout(
            yaxis={'categoryorder':'total ascending', 'title': ''},
            xaxis={'range': [0, 5.5], 'title': ''},
            height=300,
            margin=dict(t=0, b=0, l=0, r=0),
            coloraxis_showscale=False,
            paper_bgcolor="rgba(0,0,0,0)",
            plot_bgcolor="rgba(0,0,0,0)",
        )
        st.plotly_chart(fig_bar, use_container_width=True)

    st.divider()


# so far so good up till here (checked)

    original_textbox, generated_textbox = st.columns(2)
    original_textbox.markdown("## Original")
    original_textbox.info(st.session_state.original_textbox_suite)
    generated_textbox.markdown("## Generated")
    generated_textbox.info(st.session_state.generated_textbox_suite)


    # --- 4. DETAILED INSPECTOR (With Filtering) ---
    st.markdown("### 🔎 Metric Inspector")
    
    # CONTROL BAR
    c_filter, c_sort, c_spacer = st.columns([2, 1, 1])
    
    with c_filter:
        # Category Filter (Pills are great for modern UI)
        categories = ["All"] + list(df_metrics['category'].unique())
        selected_cat = st.pills("Filter by Category", categories, default="All")
        
    with c_sort:
        sort_order = st.selectbox("Sort by", ["Default", "Score (Low to High)", "Score (High to Low)"], label_visibility="collapsed")

    # LOGIC: Filter and Sort
    filtered_df = df_metrics.copy()
    if selected_cat != "All":
        filtered_df = filtered_df[filtered_df['category'] == selected_cat]
        
    if sort_order == "Score (Low to High)":
        filtered_df = filtered_df.sort_values(by="score", ascending=True)
    elif sort_order == "Score (High to Low)":
        filtered_df = filtered_df.sort_values(by="score", ascending=False)

    st.write("") # Spacer

    # RENDER CARDS (Grid Layout)
    # Instead of one long list, we use a 2-column grid for the cards
    grid_cols = st.columns(2)
    
    for i, row in enumerate(filtered_df.to_dict('records')):
        col = grid_cols[i % 2]
        
        with col:
            # Color-code the card border based on score
            card_border = "red" if row['score'] <= 2 else "grey"
            
            with st.container(border=True):
                # Header Row
                h1, h2, h3 = st.columns([0.7, 0.2, 0.2])
                h1.markdown(f"**{row['name']}**")
                
                # Visual Score Indicator
                stars = "⭐" * int(row['score'])
                h2.markdown(stars)
                score_color = "red" if row['score'] <= 2 else "green" if row['score'] >= 4 else "orange"
                h3.markdown(f":{score_color}[**{row['score']}/5**]")
                
                # Body
                st.caption(f"Category: {row['category']}")
                st.write(row['reasoning'])
                
                # Expandable details to keep card small
                with st.expander("See Judge Prompt"):
                    prompt = st.session_state.llm.get_prompt(row['name'], get_raw=True)
                    st.code(prompt, language="text")
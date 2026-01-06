import streamlit as st
import json
import requests
import os
import matplotlib.pyplot as plt


from collections import defaultdict

from generate import GenerateEmail
import data_handling as dh
import functionality as fnc



# --- CONFIG ---
st.set_page_config(page_title="AI Email Editor", page_icon="📧", layout="wide")

# datasets register
DEMO_DATASETS = {
    "lengthen" : "/Users/itang/Music/servicenow_bootcamp/ai_bootcamp_starter/datasets/lengthen.jsonl",
    "shorten" : "/Users/itang/Music/servicenow_bootcamp/ai_bootcamp_starter/datasets/shorten.jsonl",
    "tone" : "/Users/itang/Music/servicenow_bootcamp/ai_bootcamp_starter/datasets/tone.jsonl",
    'test' : '/Users/itang/Music/servicenow_bootcamp/ai_bootcamp_starter/datasets/test.jsonl',
}

# --- INITIALIZE ALL SESSION STATE VARIABLES ---
fnc.initialize_session_states(
    dataset_name = 'lengthen',
    dataset = None,
    email_id = 1,
    model_name = 'gpt-4.1',
    edit_method = 'Lengthen',
)
# original_email = fnc.Email()
# generated_email = fnc.Email()

# --- UI HEADER ---
st.title("📧 AI Email Editing Tool")

# Send flag after successfully editing the LLM advanced settings
if st.session_state.tmp_setting_save:
    st.session_state.tmp_setting_save = False
    st.toast("Settings saved!")


# --- SIDEBAR ITEMS --- 
with st.sidebar: # need to figure out how to change contents given specific tabs
    # dropdown to choose the dataset you want to load
    dataset_name = st.selectbox(
        label="Select the dataset.", 
        options=list(DEMO_DATASETS.keys()),
        key="dataset_name",
        accept_new_options=False, 
        on_change=fnc.sync_email_dataset,
    )

    # store into emails and load dataset (no need to do this if dataset is being selected)
    # emails = fnc.load_data(dataset_name)
    # st.session_state.dataset = emails
    emails = st.session_state.dataset

    # --- ID NAVIGATION BAR ---
    # currently a bug where switching dataset while having a selected number does not switch to the nearest number, goes to 1 and displays 1 even when the value is different
    email_ids = emails.keys() # this will error if you change to a dataset with less values, so make sure it fits
    selected_id = st.selectbox(
        label="📂 Select Email ID",
        options=email_ids,
        index=0,
        key='email_id',
        on_change=fnc.sync_email_id,
    )

    # --- CHOOSE BASE MODEL ---
    selected_model = st.selectbox(
        label="Choose LLM Base Model",
        options=['gpt-4.1', 'gpt-4o-mini'],
        index=0,
        key='model_name',
        on_change=fnc.sync_llm,
    )


    # --- CHOOSE EMAIL TRANSFORM METHOD ---
    # Maybe add an option to create your own with custom prompts.
    edit_method = st.selectbox(
        label="Choose edit method",
        options=['Lengthen', 'Shorten', 'Tone'],
        index=0,
        key='edit_method',
    )

    evaluation_metrics = st.multiselect(
        label="Choose evaluation metrics",
        options=st.session_state.llm.evaluation_metrics,
        key="evaluation_metrics",
    )

    # --- COLLECT ADDITIONAL CONTEXT ---
    with st.expander("Additional Context"):
        context = st.text_area(
            label="Add optional context here:",
            height=250,
            key='extra_context',
            placeholder="Make the tone sad because my cat ate my homework.",
        )


    # --- ADVANCED EDIT MODE ---   
    if st.button("Advanced Settings"):
        fnc.advanced_llm_settings_form()



# --- get email generator object ---
llm = st.session_state.llm

# retrieve email at selected id
original_email = fnc.Email(emails.get(selected_id, ""))
generated_email = fnc.Email() # phony generated email to be generate when generate button is clicked

# --- GENERATE BUTTON ---
with st.spinner(f"Generating {edit_method.lower() if edit_method != 'tone' else 'ton'}ed email..."):
    with st.sidebar:
        generate_button = st.button("Generate")
        if generate_button:
            print("Generate prompts")
            generated_email = fnc.generate_email(original_email)
    if generate_button:
        st.success("New email generated!")

        

# --- Display Emails ---
suite_tab, analytics_tab = st.tabs(['Email Suite', 'Analytics'])
with suite_tab:
    st.write("Select an email record by ID and use AI to refine it.")

    # display universal email elements
    st.markdown(f"### ✉️ Email ID: `{selected_id}`")
    st.markdown(f"**From:** {original_email.sender}")

    # display original and edited boxes
    original, generated = st.columns(2)
    with original:
        # -- Create headers ---
        st.markdown("## Original")
        st.markdown(f"**Subject:** {original_email.subject}")
        # st.session_state
        st.text_area(
            label = "Email Content",
            height = 250,
            key = 'original_textbox_suite',
            placeholder="Select editing method to see output!",
        )

    with generated:
        st.markdown("## Edited")
        st.markdown(f"**Subject:** {generated_email.subject}")
        st.text_area(
            label = "Edited Content",
            height = 250,
            key = 'generated_textbox_suite',
            placeholder="Select editing method to see output!",
        )

    
        # score generated email
    

            # store the responses in session states



        # display data analytics as an expander?
        # connect to a database so it can continuously collect data?
            # would this be necessary?

    with st.expander("Show Evaluation Score"):
        fnc.display_generated_email_score()

            








       




    # Purpose of this page: Show off the capabilities of the app without requiring sign up.
    
    # Show the saved analytics, allow user to create a new email, but the email will not be going anywhere.
    # It will essentually just be a text generator.



    # The other page will allow a user to sign in to the website and connect directly to their gmail accounts to create a message.
    # They can send the edited message from there, and also have some other possible generative capabilities.
    # - maybe sign off?
    # - maybe image generation?
    # - idk lol


with analytics_tab:
    fnc.test()

# debugging in the sidebar
with st.sidebar:
    with st.expander("Debug"):
        st.session_state
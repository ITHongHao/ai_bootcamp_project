import streamlit as st
import json
import requests
import os

from generate import GenerateEmail

# --- CONFIG ---
st.set_page_config(page_title="AI Email Editor", page_icon="📧", layout="wide")

# datasets register
datasets = {
    "lengthen" : "/Users/itang/Music/servicenow_bootcamp/ai_bootcamp_starter/datasets/lengthen.jsonl",
    "shorten" : "/Users/itang/Music/servicenow_bootcamp/ai_bootcamp_starter/datasets/shorten.jsonl",
    "tone" : "/Users/itang/Music/servicenow_bootcamp/ai_bootcamp_starter/datasets/tone.jsonl",
}

# dropdown to choose the dataset you want to load
choice = st.selectbox("Select the dataset.", list(datasets.keys()))

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
            print("JSONDecodeError")
    
# print(emails)
if len(emails) != 0:

    # --- UI HEADER ---
    st.title("📧 AI Email Editing Tool")
    st.write("Select an email record by ID and use AI to refine it.")

    if not emails:
        st.warning("No emails found in your JSONL file.")
        st.stop()

    # --- ID NAVIGATION BAR ---
    print(len(emails))
    email_ids = list(range(1, len(emails)+1))
    selected_id = st.sidebar.selectbox("📂 Select Email ID", options=email_ids, index=0)
    print(selected_id)

    # Find the selected email
    selected_email = emails[selected_id]
    if not selected_email:
        st.error(f"No email found with ID {selected_id}.")
        st.stop()

    # --- DISPLAY SELECTED EMAIL ---
    st.markdown(f"### ✉️ Email ID: `{selected_id}`")
    st.markdown(f"**From:** {selected_email.get('sender', '(unknown)')}")
    st.markdown(f"**Subject:** {selected_email.get('subject', '(no subject)')}")
    message = selected_email.get("content", "")

    email_text = st.text_area(
        "Email Content",
        value=message,
        height=250,
        key=f"email_text_{selected_id}",
    )

    # --- Create email generator object ---
    gen = GenerateEmail(os.getenv("DEPLOYMENT_NAME"))
    choice = None


    # --- Create choice register --
    choice_options = {
        0 : 'elaborate',
        1 : 'shorten',
        2 : 'tone',
    }

    # --- Buttons to change the text ---
    elaborate, shorten, tone = st.columns(3)
    with elaborate:
        if st.button('Elaborate'):
            choice = 0

    with shorten:
        if st.button('Shorten'):
            choice = 1

    with tone:
        if st.button('Tone'):
            choice = 2


    
    if choice is not None:
        # print(choice_options[choice])
        response = gen.generate(choice_options[choice])
        label = f"Adjusted email for {choice_options[choice]}"
        st.text_area(
            label,
            value=response,
            height=250,
            key=""
        )
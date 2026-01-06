import streamlit as st

import data_handling as dh


# --- CONFIG ---
st.set_page_config(page_title="Documentation", page_icon="📧", layout="wide")


# --- LOGIC ---






# --- PAGE DISPLAY ---
# st.title("Documentation")
st.markdown("# Documentation (IN PROGRESS)")
st.markdown(
    "This project was created on the Winter of 2025 through **ServiceNow's AI.Accelerate Bootcamp**." \
    ""
)





# --- ARCHITECTURE DISCUSSION ---
# we can add pictures ot make this more digestible
st.markdown("# App Design")
st.markdown("The application uses streamlit for its front end. " \
"Python scripts are used for the backend logic and connect to OpenAI Azure." \
"Personal user information is stored in [some database] and is properly cleaned for any data privacy purposes.") # need to make sure to connect and clean for data safety 




# --- MODEL EVALUATION DISCUSSION ---
st.markdown("# Model Evaluation Discussion")
st.markdown("There were two large language models evaluated. " \
"In addition, there were three provided data sets for the demo and analysis. " \
"Below, you can look through all of the demo data. ")

with st.expander("See demo data"):
    data_choice = dh.choose_demo_data()
    if data_choice:
        data = dh.load_data(data_choice)
        emails = data.values()
        st.dataframe(
            data=emails,
            width='content'
        )

st.markdown("System and user prompts were created through an iterative process." \
"Shown below are the exact prompts used for generation and judging.")

with st.expander("See prompts"):
    st.markdown("Display the prompts used for generation and judging")

st.markdown("Scoring metrics were determined with a specified rubric for each type of modification. " \
"")




# --- GENERAL DISCUSSION AND OBSERVATIONS ---
st.markdown("# General Discussion and Observations")






# --- PROGRAM SPECIFIC WORK ---
left, right = st.columns(2)
# homework section
left.markdown(
    body="# Homework and Research",
    width='content',
    )

# reflections
right.markdown("# Progress Log")




# --- BOOTCAMP REFLECTIONS ---
st.markdown("# Bootcamp Reflection")


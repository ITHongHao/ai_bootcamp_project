import streamlit as st
import json
import requests
import os
import matplotlib.pyplot as plt

import pandas as pd
from collections import defaultdict

from generate import GenerateEmail
import data_handling as dh

# --- CONFIG ---
st.set_page_config(page_title="AI Email Editor", page_icon="📧", layout="wide")

# --- UI HEADER ---
st.title("📧 AI Email Editing Tool")

suite_tab, analytics_tab = st.tabs(['Email Suite', 'Analytics'])

with suite_tab:
    st.write("Select an email record by ID and use AI to refine it.")

    # --- SIDEBAR ITEMS --- 
    with st.sidebar: # need to figure out how to change contents given specific tabs
        # dropdown to choose the dataset you want to load
        choice = dh.choose_demo_data()

        # store into emails and load dataset
        emails = dh.load_data(choice)

        # --- ID NAVIGATION BAR ---
        # print(len(emails))
        email_ids = list(range(1, len(emails)+1))
        selected_id = st.selectbox(
            label="📂 Select Email ID",
            options=email_ids,
            index=0,
        )
        # print(selected_id)

        # --- CHOOSE BASE MODEL ---
        selected_model = st.selectbox(
            label="Choose LLM Base Model",
            options=['gpt-4o-mini', 'gpt-4.1'], # this is hard coded, maybe look for a way to not hard code if a dev wants to add more API keys
            index=0
        )
        # print(emails)
        
    if len(emails) != 0:
        if not emails:
            st.warning("No emails found in your JSONL file.")
            st.stop()    

        # Find the selected email
        selected_email = emails[selected_id]
        if not selected_email:
            st.error(f"No email found with ID {selected_id}.")
            st.stop()

        # --- DISPLAY SELECTED EMAIL ---
        st.markdown(f"### ✉️ Email ID: `{selected_id}`")
        st.markdown(f"**From:** {selected_email.get('sender', '(unknown)')}")

        left_email, right_email = st.columns(2)
        left_email.markdown("## Original:")
        right_email.markdown("## Edited:")

        subject_line = selected_email.get('subject', '(no subject)')
        left_email.markdown(f"**Subject:** {subject_line}")
        message = selected_email.get("content", "")

        email_text = left_email.text_area(
            "Email Content",
            value=message,
            height=250,
            key=f"email_text_suite_{selected_id}",
        )

        # --- Create email generator object ---
        llm = GenerateEmail(os.getenv("DEPLOYMENT_NAME"))
        choice = None


        # --- Create choice register --
        choice_options = {
            -1 : 'test',
            0 : 'lengthen',
            1 : 'shorten',
            2 : 'tone',
        }

        # --- initialize session states for choices and response output
        if 'choice' not in st.session_state:
            st.session_state.choice = None
        if 'response_area' not in st.session_state:
            st.session_state.response_area = ''
        if 'subject_area' not in st.session_state:
            st.session_state.subject_area = ''

        # --- Add edit options to sidebar ---
        with st.sidebar:
            st.markdown("Click on edit method")

            if st.button('Lengthen'):
                st.session_state.choice = 0
            if st.button('Shorten'):
                st.session_state.choice = 1
            if st.button('Tone'):
                st.session_state.choice = 2


        choice = st.session_state.choice

        context = st.text_input(
            label="Add optional context here"
        )
        # print(context)

        # --- Call LLM + store output in widget state ---
        if choice is not None:
            # generate new body text
            body_args = {
                'selected_text' : message,
                'additional_text' : context,
                # extra params
            }

            body_response = llm.generate(
                action=choice_options[choice],
                args=body_args,
            )

            # generate new subject title
            subject_line_args = {
                'selected_text' : subject_line,
                'additional_text' : body_response
            }

            subject_response = llm.generate(
                action='subject-line',
                args=subject_line_args,
            )

            # store the responses in session states
            st.session_state.subject_area = subject_response
            st.session_state.response_area = body_response


        right_email.markdown(f"**Subject:** {st.session_state.subject_area}")
        label = f"Adjusted email for {choice_options[choice]}" if choice is not None else "Adjusted email"
        right_email.text_area(
            label=label,
            height=250,
            key="response_area",   # stable, non-empty key (refers to session state)
            placeholder="Select editing method to see output!"
        )







        # display data analytics as an expander?
        # connect to a database so it can continuously collect data?
            # would this be necessary?

        with st.expander("Show Evaluation Score"):
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

            








        # --- ADVANCED EDIT MODE ---    
        with st.sidebar:
            with st.expander("Advanced Settings"):
                st.markdown("LLM settings")
                st.markdown("Other Customizing things")
                st.markdown("Extra context")
                # st.markdown("Prompt injection or something idk lol")

                if st.button("Generate"):
                    print("Generate prompts")



        """
        Purpose of this page: Show off the capabilities of the app without requiring sign up.
        
        Show the saved analytics, allow user to create a new email, but the email will not be going anywhere.
        It will essentually just be a text generator.



        The other page will allow a user to sign in to the website and connect directly to their gmail accounts to create a message.
        They can send the edited message from there, and also have some other possible generative capabilities.
        - maybe sign off?
        - maybe image generation?
        - idk lol
        """

with analytics_tab:
    # give option to pull from precomputed results or to generate result themselves
    # maybe store all results somewhere in some format, perhaps store them in a database later on
    st.markdown("Generate analytics for any user configuration.")

    # create dataframe to hold all emails for the selected dataset
    # should store results or cache it so switching between isnt an issue

    analytics = pd.DataFrame(emails.values())

    # for every email, generate a new subject line and body email
    if choice is not None:
        new_subjects = []
        new_contents = []
        evaluations = defaultdict(lambda: {"rating": [], "explanation": []})

        for subject, content in analytics[['subject', 'content']].itertuples(index=False, name=None):
            # generate new body text
            body_args = {
                'selected_text' : content,
                'additional_text' : context,
                # extra params
            }

            body_response = llm.generate(
                action=choice_options[choice],
                args=body_args,
            )

            # generate new subject title
            subject_line_args = {
                'selected_text' : subject,
                'additional_text' : body_response
            }

            subject_response = llm.generate(
                action='subject-line',
                args=subject_line_args,
            )

            # get ratings for generated prompt
            metrics_args = {
                'selected_text' : content,
                'additional_text' : context,
                'model_response' : body_response,
            }

            # generate all metrics
            for metric in ['faithfulness', 'completeness']:
                # --- EVALUATIONS ---
                evaluation_json = llm.generate(
                    action=metric,
                    args=metrics_args,
                )

                print(evaluation_json)
                print(type(evaluation_json))
                try:
                    data = json.loads(evaluation_json)
                    evaluations[metric]['rating'].append(data.get('rating'))
                    evaluations[metric]['explanation'].append(data.get('explanation'))
                except json.JSONDecodeError:
                    print(f"JSONDecodeError: {evaluation_json}")
                



            # store newly generated text in list
            new_subjects.append(subject_response)
            new_contents.append(body_response)
        
        # add to new generations
        analytics['new_subject'] = new_subjects
        analytics['new_content'] = new_contents

        # add metrics and grades
        for metric, grade in evaluations.items():
            analytics[f'{metric}_rating'] = grade['rating']
            analytics[f'{metric}_explanation'] = grade['explanation']
        


    

        # display single emails and their scores and outputs etc.
        left_original, right_edited = st.columns(2)
        
        original_subject = selected_email.get('subject', '(no subject)')
        original_content = selected_email.get("content", "")

        left_original.markdown("## Original:")
        left_original.markdown(f"**Subject:** {original_subject}")
        left_original.text_area(
            "Original Content",
            value=original_content,
            height=250,
            key=f"original_content_analytics_{selected_id}",
        )

        edited_subject = analytics['new_subject'][selected_id-1]
        edited_content = analytics['new_content'][selected_id-1]
        right_edited.markdown("## Edited:")
        right_edited.markdown(f"**Subject:** {edited_subject}")
        right_edited.text_area(
            "Edited Content",
            value=edited_content,
            height=250,
            key=f"edited_content_analytics_{selected_id}",
        )

        st.markdown("## Scoring:")
        faithfulness, completeness, conciseness = st.columns(3, border=True)
        
        with faithfulness:
            faithfulness_rating = analytics['faithfulness_rating'][selected_id-1]
            faithfulness_explanation = analytics['faithfulness_explanation'][selected_id-1]
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
            completeness_rating = analytics['completeness_rating'][selected_id-1]
            completeness_explanation = analytics['completeness_explanation'][selected_id-1]
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


    st.markdown("## Visualization")
    rating_cols = [c for c in analytics.columns if c.endswith("_rating")]
    if not rating_cols:
        st.warning("No '_rating' columns found.")
        st.stop()

    # Coerce to numeric so counts are correct even if values are strings
    ratings = analytics[rating_cols].apply(pd.to_numeric, errors="coerce")


    # choose which metrics to display
    metrics = st.multiselect("Metrics", rating_cols, default=rating_cols)

    # plot all the scores into charts
    for metric in metrics:
        s = ratings[metric].dropna()

        if s.empty:
            st.write(f"**{metric}**: no data")
            continue

        counts = s.value_counts().sort_index()

        st.markdown(f"### {metric}")

        # Single figure with two charts (bar + pie)
        fig, (ax_bar, ax_pie) = plt.subplots(1, 2, figsize=(10, 4))

        # --- Bar chart (counts) ---
        ax_bar.bar(counts.index.astype(str), counts.values)
        ax_bar.set_xlabel("Rating")
        ax_bar.set_ylabel("Count")
        ax_bar.set_title(f"Counts by rating — {metric}")

        # --- Pie chart (counts) ---
        ax_pie.pie(
            counts.values,
            labels=counts.index.astype(str),
            autopct="%1.1f%%"
        )
        ax_pie.set_title(f"Share by rating — {metric}")

        fig.tight_layout()
        st.pyplot(fig)
        plt.close(fig)


    # display as an interactable table
    st.markdown("## Raw Data and Ratings")
    analytics

    

    # perhaps a space to inject user customizable prompts?
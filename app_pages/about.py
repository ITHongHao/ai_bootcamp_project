import streamlit as st

# --- CONFIG ---
st.set_page_config(page_title="About Me", page_icon="📧", layout="wide")

st.title("Meet the dev! (IN PROGRESS)")


# social medias
about_me_text, about_me_image = st.columns(2)

# --- ABOUT ME SECTION ---
about_me_text.markdown("## About Me")

# quick description on education
about_me_text.markdown("It's nice to meet you! My name is **Ivan Tang**. " \
"I am a third yeear Computer Science and Anthropology student at the Uniuversity of Illinois Urbana-Champaign. " \
"I hope to leverage both sides of my education to better address common problems the everyday person experiences through technological solutions.")

# profile picture
about_me_image.image("/Users/itang/Music/servicenow_bootcamp/ai_bootcamp_starter/app_pages/assets/ivanskate.png")

# --- RESEARCH OR TECHNICAL INTERESTS ---
st.markdown("## Goals")
st.markdown("I am particularly interested in leveraging AI (artificial intelligence) in multi-disciplinary studies. " \
"Recently, I have been understanding machine learning and AI's role within genealogical bioinformatics, more specifically when applied to genetic genealogy. " \
"Past rabbithole's I've emerged from include financial time series forecasting, human migration through geospatial machine learning, and overegnineering my household through homelabbing.")

# --- WORK EXPERIENCE ----
st.markdown("## Work Experiences")
work_exp_desc, work_exp_timeline = st.columns([3, 1])
work_exp_desc.markdown("Having experienced a taset fo many different industries and environments, I am looking to [do something lol]. " \
"I currently work as a **Data Analyst Intern** under the **National Center for Supercomputing Applications**. " \
"Below is a timeline of my work experience")

# timeline of work experience

work_exp_timeline.image("/Users/itang/Music/servicenow_bootcamp/ai_bootcamp_starter/app_pages/assets/ivanskate.png")


# things I learned at each internship and a reflection of it
st.markdown("Each internship presented opportunities that I grew from. " \
"At the NCSA, I learned to [thing]. " \
"At JPMorgan Chase, I learned to [thing]. " \
"At [place], I learned [thing]. " \
"At [place], I learned [thing]. " \
"At [place], I learned [thing]. " \
"At [place], I learned [thing]. " \
"All of these experience have continued to build my understanding of myself and how I best [thing]. ")

# --- PERSONAL INTERESTS ---
st.markdown("## Interests and Hobbies")
st.markdown("I love to mess around with music in my freetime. " \
"As someone who hastily gravitated towards anything and everythign music for as long as I can remember, I've gotten to befriend many incredible musicians. " \
"More interestingly, I often convince (or begged) my musician friends to leave me alone with their instruments! " \
"My bad habit of incessantly asking to play every instrument I saw evolved into a lifelong obsession to collect as many distinct sounds as possible. " \
"This obsession eventually led me to learning how to compose, record, and produce tunes. " \
"One thing led to another and now it can be said that I composed, produced, and released a soundtrack for a video game on Steam!")

# picture of startdrop perhaps?


# --- THANK YOU ---



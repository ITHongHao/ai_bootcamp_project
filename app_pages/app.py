import streamlit as st

# --- CREATE PAGES ---
home_page = st.Page(
    page="home.py",
    title="Home",
    icon=":material/home:",
    default=True,
)

dashboard_page = st.Page(
    page="dashboard.py",
    title="Dashboard",
    icon=":material/dashboard:",
)

email_suite_page = st.Page(
    page="suite.py",
    title="Email Editor",
    icon=":material/mail:",
)

# Groupings
demo_page_1 = st.Page(
    page="demo_1.py",
    title="Demo: Feature A", # I recommend giving distinct names
    icon=":material/play_circle:",
)

demo_page_2 = st.Page(
    page="demo_2.py",
    title="Demo: Feature B",
    icon=":material/play_circle:",
)

test_page = st.Page(
    page="test.py",
    title="Render Tests",
    icon=":material/bug_report:", # Or :material/science:
)

documentation_page = st.Page(
    page="documentation.py",
    title="Documentation",
    icon=":material/menu_book:", # Or :material/description:
)

about_page = st.Page(
    page="about.py",
    title="About Me",
    icon=":material/person:",
)

# --- NAVIGATION SETUP ---
# Grouping pages creates section headers in the sidebar
pg = st.navigation(
    {
        # "Main": [home_page, dashboard_page, email_suite_page],
        # "Demos": [demo_page_1, demo_page_2],
        "Demos" : [dashboard_page, email_suite_page],
        "Resources": [documentation_page, about_page],
        "Dev Tools": [test_page],
    }
)

# --- SHARED SIDEBAR ELEMENTS ---
# This function runs on every page reload to keep the sidebar footer consistent
# You can add a logo at the top using st.logo()
# st.logo("assets/ivanskate.png") # Optional: If you have a logo image

# Run the navigation
pg.run()

# Add the persistent footer/version info *after* the nav runs
with st.sidebar:
    # debugging in the sidebar
    with st.expander("Debug"):
        st.session_state
    st.caption("v1.0.0 | AI.Accelerate 2025 | ITHongHao")
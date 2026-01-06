import streamlit as st
import pandas as pd
from test_instance import TestInstance
from searchbar_component import searchbar

# --- PAGE CONFIGURATION ---
st.set_page_config(
    page_title='Dashboard',
    layout='wide',
)

# --- CSS STYLING ---
st.markdown("""
<style>
    /* Align button text to the left for the 'Card' feel */
    div[data-testid="column"] button {
        text-align: left;
    }
    
</style>
""", unsafe_allow_html=True)

# --- 1. SESSION STATE INITIALIZATION ---
if "selected_ids" not in st.session_state:
    st.session_state.selected_ids = set()

if "tests" not in st.session_state:
    st.session_state.tests = [
        TestInstance("1", "LLM Hallucination Check", "Tests if the model makes up facts about the user."),
        TestInstance("2", "Prompt Injection Test", "Attempts to bypass system instructions."),
        TestInstance("3", "Response Latency", "Measures time to first token.", status="Passed", last_run="2026-01-01"),
        TestInstance("4", "Tone Consistency", "Ensures the bot stays professional.", status="Failed", last_run="2026-01-02"),
        TestInstance("5", "PII Leakage Check", "Checks for sensitive data exposure.", status="Pending", last_run="Never"),
        TestInstance("6", "Cross-Language Test", "Validates Spanish responses.", status="Passed", last_run="2026-01-03")
    ]

# --- 2. HEADER & NAVIGATION BAR ---
t1, t2, t3, t4, t5 = st.columns([1, 1, 1, 4, 2], gap="small")

with t1:
    if st.button("➕ New", type="primary", use_container_width=True):
        st.toast("Create New Test Clicked")

with t2:
    if st.button("📤 Import", use_container_width=True):
        st.toast("Import Clicked")

with t3:
    # The Toggle that controls the "Clickable Selection" mode
    selection_enabled = st.toggle("Select", help="Enable to select multiple items")

with t4:
    def search_function(query):
        return [{"label": t.name, "value": t.test_id} for t in st.session_state.tests if query.lower() in t.name.lower()]

    search_result = searchbar(
        key="drive_search",
        placeholder="Search in Tests",
        suggestions=search_function(""), 
        highlightBehavior="update"
    )

with t5:
    v1, v2, v3 = st.columns([2, 1, 1])
    with v1:
        view_mode = st.segmented_control(
            label="View Toggle",
            options=["grid", "list"],
            format_func=lambda x: "⠿" if x == "grid" else "☰",
            selection_mode="single",
            default="grid",
            label_visibility="collapsed"
        )
    with v2:
        st.button(":material/help:", help="Support")
    with v3:
        st.button(":material/settings:", help="Settings")

# --- 3. BATCH ACTIONS TOOLBAR (Conditional) ---
if selection_enabled and st.session_state.selected_ids:
    selected_count = len(st.session_state.selected_ids)
    
    with st.container(border=True):
        b1, b2, b3, b4 = st.columns([1.5, 1.5, 1.5, 6])
        
        if b1.button(f"🗑️ Delete ({selected_count})"):
            st.toast(f"Deleted {selected_count} items")
            # Remove selected items from list
            st.session_state.tests = [t for t in st.session_state.tests if t.test_id not in st.session_state.selected_ids]
            st.session_state.selected_ids.clear()
            st.rerun()
            
        if b2.button("🏷️ Tag"):
            st.toast("Tagging dialog opened")
            
        if b3.button("🔄 Run"):
            st.toast(f"Running {selected_count} tests...")

    st.empty() # Spacer

st.divider()

# --- 4. FILTER CHIPS ---
f1, f2, f3, f4, f5 = st.columns([1, 1, 1, 1, 6])
f1.popover("Type")
f2.popover("People")
f3.popover("Modified")
f4.popover("Source")

st.subheader("Recent")

# --- 5. MAIN CONTENT AREA ---

if view_mode == 'grid':
    # --- GRID VIEW ---
    cols = st.columns(3)
    for index, test in enumerate(st.session_state.tests):
        with cols[index % 3]:
            # Clean Implementation: The class handles the logic for both
            # "Select Mode" (Toggle Buttons) and "Normal Mode" (Cards)
            test.render(selection_enabled=selection_enabled)

else:
    # --- LIST VIEW ---
    test_data = []
    for t in st.session_state.tests:
        test_data.append({
            "Select": t.test_id in st.session_state.selected_ids,
            "Name": f"📄 {t.name}",
            "Status": t.status,
            "ID": t.test_id,
            "Last Run": t.last_run if t.last_run else "Never",
            "raw_id": t.test_id 
        })
    df = pd.DataFrame(test_data)

    if selection_enabled:
        edited_df = st.data_editor(
            df,
            use_container_width=True,
            hide_index=True,
            column_config={
                "Select": st.column_config.CheckboxColumn(required=True, width="small"),
                "Name": st.column_config.TextColumn(width="large", disabled=True),
                "Status": st.column_config.TextColumn(disabled=True),
                "ID": st.column_config.TextColumn(disabled=True),
                "Last Run": st.column_config.TextColumn(disabled=True),
                "raw_id": None 
            },
            key="list_editor"
        )
        
        # Sync List Selection back to Session State
        selected_rows = edited_df[edited_df["Select"] == True]["raw_id"].tolist()
        if set(selected_rows) != st.session_state.selected_ids:
            st.session_state.selected_ids = set(selected_rows)
            st.rerun()
            
    else:
        st.dataframe(
            df.drop(columns=["Select", "raw_id"]),
            use_container_width=True,
            hide_index=True,
            column_config={
                "Name": st.column_config.TextColumn(width="large"),
            }
        )
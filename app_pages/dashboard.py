import streamlit as st
import pandas as pd
import time
import random
import json
import uuid
from datetime import datetime
from test_instance import TestInstance
from searchbar_component import searchbar

# --- PAGE CONFIGURATION ---
st.set_page_config(page_title='Dashboard', layout='wide')

# --- CSS STYLING ---
st.markdown("""
<style>
    div[data-testid="column"] button { text-align: left; }
    /* Style for the batch action container */
    div[data-testid="stVerticalBlock"] > div[data-testid="stVerticalBlockBorderWrapper"] {
        background-color: #f0f2f6;
        border-radius: 10px;
    }
    @media (prefers-color-scheme: dark) {
        div[data-testid="stVerticalBlock"] > div[data-testid="stVerticalBlockBorderWrapper"] {
            background-color: #262730;
        }
    }
</style>
""", unsafe_allow_html=True)

# --- 1. STATE INITIALIZATION ---
if "page" not in st.session_state:
    st.session_state.page = "dashboard"

if "selected_ids" not in st.session_state:
    st.session_state.selected_ids = set()

if "tests" not in st.session_state:
    # Initial Mock Data
    st.session_state.tests = [
        TestInstance("1", "LLM Hallucination Check", "Tests if the model makes up facts.", status="Pending"),
        TestInstance("2", "Prompt Injection Test", "Attempts to bypass instructions.", status="Pending"),
        TestInstance("3", "Response Latency", "Measures time to first token.", status="Passed", last_run="2026-01-01"),
        TestInstance("4", "Tone Consistency", "Ensures the bot stays professional.", status="Failed", last_run="2026-01-02"),
        TestInstance("5", "PII Leakage Check", "Checks for sensitive data exposure.", status="Pending"),
        TestInstance("6", "Cross-Language Test", "Validates Spanish responses.", status="Passed", last_run="2026-01-03"),
        TestInstance("7", "Demo Test", "", status="Pending"),
    ]

# --- 2. LOGIC FUNCTIONS ---

def run_test_logic(test_obj):
    """Simulates running a test."""
    with st.spinner(f"Running {test_obj.name}..."):
        time.sleep(0.5) # Fast simulation
        test_obj.status = random.choice(["Passed", "Failed"])
        test_obj.last_run = datetime.now().strftime("%Y-%m-%d")
    st.toast(f"Test '{test_obj.name}' finished: {test_obj.status}")

# --- 3. DIALOGS (Pop-ups) ---

@st.dialog("Global Settings")
def open_settings_dialog():
    st.subheader("Dashboard Preferences")
    st.toggle("Dark Mode Enforcement", value=True)
    st.toggle("Email Notifications", value=False)
    
    st.subheader("API Configuration")
    st.text_input("OpenAI API Key", type="password")
    st.selectbox("Default Model", ["gpt-4o", "gpt-3.5-turbo", "claude-3-opus"])
    
    if st.button("Save Settings", type="primary", use_container_width=True):
        st.toast("Settings saved successfully!")
        st.rerun()

@st.dialog("Help & Support")
def open_help_dialog():
    st.markdown("### How to use this Dashboard")
    st.info("ℹ️ **Batch Actions**: Enable 'Select' to Run, Delete, or Export multiple tests.")
    st.info("ℹ️ **Import/Export**: Use the Import button to load JSON configs. Export selected tests via the toolbar.")
    st.markdown("**Shortcuts**")
    st.code("Ctrl + F : Search\nCtrl + R : Rerun App")
    if st.button("Close", use_container_width=True):
        st.rerun()

@st.dialog("Import Tests")
def open_import_dialog():
    st.markdown("Import tests from a JSON file or text.")
    st.caption("Supports both single objects and lists of objects.")
    
    json_str = st.text_area("Paste JSON String", height=150, placeholder='[{"name": "Test A", ...}]')
    uploaded_file = st.file_uploader("Or upload JSON file", type=["json"])
    
    if st.button("Import", type="primary", use_container_width=True):
        raw_data = None
        try:
            if uploaded_file:
                raw_data = json.load(uploaded_file)
            elif json_str.strip():
                raw_data = json.loads(json_str)
            else:
                st.warning("⚠️ Please provide input.")
                return

            # Normalize to list
            if isinstance(raw_data, dict):
                raw_data = [raw_data]
            
            if not isinstance(raw_data, list):
                st.error("❌ Invalid format. Root must be a list or object.")
                return

            count = 0
            for item in raw_data:
                if "name" in item and "description" in item:
                    # Uses the class method from TestInstance
                    new_test = TestInstance.from_dict(item)
                    st.session_state.tests.insert(0, new_test)
                    count += 1
            
            if count > 0:
                st.toast(f"✅ Imported {count} tests!")
                st.rerun()
            else:
                st.warning("⚠️ No valid test objects found.")

        except json.JSONDecodeError:
            st.error("❌ Invalid JSON syntax.")

@st.dialog("Create New Test")
def open_create_dialog():
    name = st.text_input("Test Name")
    description = st.text_area("Description")
    if st.button("Create", type="primary", use_container_width=True):
        if name:
            new_id = str(uuid.uuid4())[:8]
            st.session_state.tests.insert(0, TestInstance(new_id, name, description))
            st.toast(f"✅ Created '{name}'")
            st.rerun()
        else:
            st.warning("⚠️ Name is required.")

@st.dialog("Edit Test")
def open_edit_dialog(test_obj):
    new_name = st.text_input("Name", value=test_obj.name)
    new_desc = st.text_area("Description", value=test_obj.description)
    col1, col2 = st.columns(2)
    if col1.button("Save", type="primary"):
        test_obj.name = new_name
        test_obj.description = new_desc
        st.rerun()
    if col2.button("Cancel"):
        st.rerun()

@st.dialog("Confirm Deletion")
def open_delete_dialog(tests_to_delete):
    if not isinstance(tests_to_delete, list):
        tests_to_delete = [tests_to_delete]
    
    st.warning(f"Delete {len(tests_to_delete)} test(s)?")
    col1, col2 = st.columns(2)
    if col1.button("Yes, Delete", type="primary"):
        ids_to_remove = {t.test_id for t in tests_to_delete}
        st.session_state.tests = [t for t in st.session_state.tests if t.test_id not in ids_to_remove]
        st.session_state.selected_ids -= ids_to_remove
        st.rerun()
    if col2.button("Cancel"):
        st.rerun()






# --- 4. ROUTER VIEW: DETAILS PAGE ---
if st.session_state.page == "details":
    st.button("← Back to Dashboard", on_click=lambda: st.session_state.update(page="dashboard"))
    
    current_id = st.session_state.get("detail_id")
    test = next((t for t in st.session_state.tests if t.test_id == current_id), None)
    
    if test:
        st.title(f"Details: {test.name}")
        st.info(f"Test ID: {test.test_id}")
        st.write(test.description)
        st.json(test.to_dict()) # Use the new to_dict method
    else:
        st.error("Test not found.")
    st.stop()

# --- 5. DASHBOARD VIEW ---

# Header
t1, t2, t3, t4, t5 = st.columns([1, 1, 1, 4, 2], gap="small")
with t1:
    if st.button("➕ New", type="primary", use_container_width=True):
        open_create_dialog()
with t2:
    if st.button("📤 Import", use_container_width=True):
        open_import_dialog()
with t3:
    selection_enabled = st.toggle("Select", help="Enable Batch Actions")
with t4:
    def search_fn(q):
        return [{"label": t.name, "value": t.test_id} for t in st.session_state.tests if q.lower() in t.name.lower()]
    search_result = searchbar(key="s", placeholder="Search tests...", suggestions=search_fn(""), highlightBehavior="update")
with t5:
    v1, v2, v3 = st.columns([2, 1, 1])
    view_mode = v1.segmented_control("View", ["grid", "list"], format_func=lambda x: "⠿" if x=="grid" else "☰", default="grid", label_visibility="collapsed")
    if v2.button(":material/help:", help="Help"):
        open_help_dialog()
    if v3.button(":material/settings:", help="Settings"):
        open_settings_dialog()

# --- BATCH ACTIONS TOOLBAR (Run, Delete, Export) ---
if selection_enabled and st.session_state.selected_ids:
    selected_count = len(st.session_state.selected_ids)
    
    with st.container(border=True):
        b1, b2, b3, b4, spacer = st.columns([1.2, 1.2, 1.2, 1.2, 4])
        
        # 1. RUN
        if b1.button(f"🏃 Run ({selected_count})", use_container_width=True):
            tests_to_run = [t for t in st.session_state.tests if t.test_id in st.session_state.selected_ids]
            prog = st.progress(0)
            for i, t in enumerate(tests_to_run):
                run_test_logic(t)
                prog.progress((i+1)/len(tests_to_run))
            time.sleep(0.5)
            st.rerun()

        # 2. DELETE
        if b2.button(f"🗑️ Delete ({selected_count})", use_container_width=True):
            tests_to_del = [t for t in st.session_state.tests if t.test_id in st.session_state.selected_ids]
            open_delete_dialog(tests_to_del)
            
        # 3. TAG
        if b3.button("🏷️ Tag", use_container_width=True):
            st.toast("Tagging feature pending.")

        # 4. EXPORT JSON
        selected_objects = [t for t in st.session_state.tests if t.test_id in st.session_state.selected_ids]
        # Use to_dict() for clean JSON serialization
        json_data = json.dumps([t.to_dict() for t in selected_objects], indent=2)
        
        b4.download_button(
            label=f"💾 Export ({selected_count})",
            data=json_data,
            file_name=f"tests_export_{datetime.now().strftime('%Y%m%d')}.json",
            mime="application/json",
            use_container_width=True
        )

st.divider()

# Filter/Sort
f1, f4, f5 = st.columns([3, 1, 6])
sort_opt = f4.selectbox("Sort", ["ID", "Name", "Status", "Last Run"], label_visibility="collapsed")

# Sorting Logic
disp_tests = st.session_state.tests.copy()
if sort_opt == "Name": disp_tests.sort(key=lambda x: x.name.lower())
elif sort_opt == "Status": disp_tests.sort(key=lambda x: x.status)
elif sort_opt == "Last Run": disp_tests.sort(key=lambda x: (x.last_run is None, x.last_run), reverse=True)
elif sort_opt == "ID": disp_tests.sort(key=lambda x: x.test_id)

f1.subheader(f"Test Instances by {sort_opt}")

# --- MAIN RENDER LOOP ---
if view_mode == 'grid':
    cols = st.columns(3)
    for i, t in enumerate(disp_tests):
        with cols[i % 3]:
            # Capture action from TestInstance.render
            act = t.render(selection_enabled)
            
            if act == "run": 
                run_test_logic(t)
                st.rerun()
            elif act == "details": 
                st.session_state.detail_id = t.test_id
                st.session_state.page = "details"
                st.rerun()
            elif act == "edit": 
                open_edit_dialog(t)
            elif act == "delete": 
                open_delete_dialog(t)
else:
    # List View
    data = [{"Select": t.test_id in st.session_state.selected_ids, "Name": t.name, "Status": t.status, "Last Run": t.last_run or "Never", "id": t.test_id} for t in disp_tests]
    df = pd.DataFrame(data)
    if selection_enabled:
        edited = st.data_editor(df, use_container_width=True, hide_index=True, column_config={"Select": st.column_config.CheckboxColumn(required=True), "id": None}, disabled=["Name", "Status", "Last Run"])
        st.session_state.selected_ids = set(edited[edited["Select"]]["id"].tolist())
    else:
        st.dataframe(df.drop(columns=["Select", "id"]), use_container_width=True, hide_index=True)
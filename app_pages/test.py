import streamlit as st
import pandas as pd
import time
import random
import json
import uuid
from datetime import datetime
from test_instance import TestInstance
from searchbar_component import searchbar
import plotly.express as px

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
        TestInstance("7", "Demo Test", "A manual test for demonstration.", status="Pending"),
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



def render_test_config_ui(test_instance):
    """
    Renders the Details View with a modern, card-based UI.
    """
    
    # Mock Data
    DEMO_DATASETS = ["Customer_Service_v1", "Internal_Requests", "Spam_Examples"]
    AVAILABLE_METRICS = ["Faithfulness", "Tone Consistency", "Conciseness", "Completeness", "PII Safety", "Toxicity", "Formatting", "Relevance"]
    LLM_MODELS = ['gpt-4.1', 'gpt-4o-mini'] 
    EDIT_METHODS = ['Lengthen', 'Shorten', 'Tone'] 

    # --- TABS DEFINITION ---
    tab_settings, tab_analytics = st.tabs(["⚙️ Settings", "📊 Results & Analytics"])
    
    # ==========================================
    # TAB 1: ALL CONFIGURATION (Modern UI)
    # ==========================================
    with tab_settings:
        st.caption("Configure the parameters for this specific test instance.")

        # --- SECTION 1: CORE STRATEGY (Top Card) ---
        with st.container(border=True):
            st.markdown("##### 🎯 Core Strategy")
            c1, c2, c3 = st.columns(3)
            
            with c1:
                # Dataset Selection
                current_ds = test_instance.config.get("dataset_name", DEMO_DATASETS[0])
                test_instance.config["dataset_name"] = st.selectbox(
                    label="📚 Dataset", 
                    options=DEMO_DATASETS, 
                    index=DEMO_DATASETS.index(current_ds) if current_ds in DEMO_DATASETS else 0,
                    key=f"dataset_name_{test_instance.test_id}",
                    help="The source data to run the test against."
                )
            
            with c2:
                # Base Model
                current_model = test_instance.config.get("model_name", LLM_MODELS[0])
                test_instance.config["model_name"] = st.selectbox(
                    label="🤖 Base Model",
                    options=LLM_MODELS,
                    index=LLM_MODELS.index(current_model) if current_model in LLM_MODELS else 0,
                    key=f"model_name_{test_instance.test_id}",
                    help="The LLM engine used for generation."
                )

            with c3:
                # Edit Method
                current_method = test_instance.config.get("edit_method", EDIT_METHODS[0])
                test_instance.config["edit_method"] = st.selectbox(
                    label="✨ Edit Method",
                    options=EDIT_METHODS,
                    index=EDIT_METHODS.index(current_method) if current_method in EDIT_METHODS else 0,
                    key=f"edit_method_{test_instance.test_id}",
                    help=" The transformation logic applied to the input."
                )

        # --- SECTION 2: SPLIT VIEW (Advanced Params | Evaluation) ---
        col_left, col_right = st.columns([1.6, 1], gap="medium")

        # --- LEFT COLUMN: HYPERPARAMETERS ---
        with col_left:
            with st.container(border=True):
                st.markdown("##### 🎛️ LLM Hyperparameters")
                st.caption("Fine-tune the model behavior (Azure OpenAI specs).")
                
                # We use expanders inside this card to keep it clean
                
                # 1. Creativity
                with st.expander("🎨 Creativity (Temperature & Top P)", expanded=True):
                    c_temp, c_top = st.columns(2)
                    with c_temp:
                        test_instance.config["temperature"] = st.slider(
                            label="Temperature",
                            min_value=0.0, max_value=2.0, step=0.01,
                            value=test_instance.config.get("temperature", 0.7),
                            key=f"tmp_temperature_{test_instance.test_id}"
                        )
                    with c_top:
                        test_instance.config["top_p"] = st.slider(
                            label="Top p",
                            min_value=0.0, max_value=1.0, step=0.01,
                            value=test_instance.config.get("top_p", 0.95),
                            key=f"tmp_top_p_{test_instance.test_id}"
                        )

                # 2. Cost and Length
                with st.expander("📏 Length & Batching"):
                    c_tok, c_n = st.columns(2)
                    with c_tok:
                        test_instance.config["max_tokens"] = st.number_input(
                            label="Max Tokens",
                            min_value=1, max_value=128000, step=1,
                            value=int(test_instance.config.get("max_tokens", 500)),
                            key=f"tmp_max_tokens_{test_instance.test_id}"
                        )
                    with c_n:
                        test_instance.config["n"] = st.number_input(
                            label="Batch Count (n)",
                            min_value=1, max_value=5, step=1,
                            value=int(test_instance.config.get("n", 1)),
                            key=f"tmp_n_{test_instance.test_id}"
                        )

                # 3. Penalties
                with st.expander("🚫 Repetition Penalties"):
                    test_instance.config["presence_penalty"] = st.slider(
                        label="Presence Penalty",
                        min_value=-2.0, max_value=2.0, step=0.1,
                        value=float(test_instance.config.get("presence_penalty", 0.0)),
                        key=f"tmp_presence_penalty_{test_instance.test_id}",
                        help="Likelihood to talk about new topics."
                    )
                    test_instance.config["frequency_penalty"] = st.slider(
                        label="Frequency Penalty",
                        min_value=-2.0, max_value=2.0, step=0.1,
                        value=float(test_instance.config.get("frequency_penalty", 0.0)),
                        key=f"tmp_frequency_penalty_{test_instance.test_id}",
                        help="Likelihood to repeat lines verbatim."
                    )

                # 4. Reliability
                with st.expander("🎲 Reliability & Seed"):
                    c_seed, c_log = st.columns(2)
                    with c_seed:
                        test_instance.config["seed"] = st.number_input(
                            label="Seed",
                            value=int(test_instance.config.get("seed", 0)),
                            key=f"tmp_seed_{test_instance.test_id}"
                        )
                    with c_log:
                        test_instance.config["top_logprobs"] = st.number_input(
                            label="Top Log Probs",
                            min_value=0, max_value=20,
                            value=int(test_instance.config.get("top_logprobs", 0)),
                            key=f"tmp_top_logprobs_{test_instance.test_id}"
                        )
                    test_instance.config["logprobs"] = True if test_instance.config["top_logprobs"] > 0 else False

        # --- RIGHT COLUMN: EVALUATION ---
        with col_right:
            with st.container(border=True):
                st.markdown("##### ⚖️ Grading Criteria")
                st.caption("Select judges to evaluate results.")
                
                current_metrics = test_instance.config.get("evaluation_metrics", [])
                
                # We use a container height to make the multiselect scrollable if list is long
                test_instance.config["evaluation_metrics"] = st.multiselect(
                    label="Active Judges",
                    options=AVAILABLE_METRICS,
                    default=current_metrics,
                    key=f"evaluation_metrics_{test_instance.test_id}",
                    help="These metrics will determine Pass/Fail status."
                )
                
                # Visual fluff to make the card look "fuller" if list is short
                if len(test_instance.config["evaluation_metrics"]) > 0:
                    st.success(f"{len(test_instance.config['evaluation_metrics'])} Judges Active")
                else:
                    st.warning("No Judges Selected")

    # ==========================================
    # TAB 2: ANALYTICS (Preserved)
    # ==========================================
    with tab_analytics:
        if test_instance.last_run is None:
            st.warning("⚠️ This test has never been run. Configure settings in the first tab and click 'Save & Run'.")
            st.image("https://placehold.co/600x300?text=No+Data+Available", use_container_width=True)
        else:
            # Header Metrics
            st.subheader(f"Run Results: {test_instance.last_run}")
            
            m1, m2, m3, m4 = st.columns(4)
            score = 4.8 if test_instance.status == "Passed" else 2.4
            delta = 0.5 if test_instance.status == "Passed" else -1.2
            
            m1.metric("Overall Score", f"{score}/5", delta)
            m2.metric("Status", test_instance.status, delta_color="normal")
            m3.metric("Latency", "450ms", "-20ms")
            m4.metric("Cost", "$0.002", "+0.0001")
            
            st.divider()
            
            viz_col, data_col = st.columns([1, 1])
            
            with viz_col:
                st.markdown("**Metric Breakdown**")
                metrics_used = test_instance.config.get("evaluation_metrics", ["Faithfulness", "Tone", "Conciseness"])
                if not metrics_used: metrics_used = ["Faithfulness", "Tone", "Conciseness"]
                
                mock_scores = [random.uniform(2, 5) for _ in metrics_used]
                
                df_radar = pd.DataFrame(dict(r=mock_scores, theta=metrics_used))
                
                fig = px.line_polar(df_radar, r='r', theta='theta', line_close=True, range_r=[0,5])
                fig.update_traces(fill='toself')
                fig.update_layout(margin=dict(t=20, b=20, l=40, r=40))
                st.plotly_chart(fig, use_container_width=True)

            with data_col:
                st.markdown("**Generated Output**")
                st.info(f"Subject: Re: {test_instance.config.get('email_id', 'Unknown')}")
                st.text_area("LLM Response", "Dear Customer,\n\nThank you for reaching out...", height=150, disabled=True)
                
                with st.expander("View Raw JSON Output"):
                    st.json(test_instance.to_dict())
# --- 5. ROUTER VIEW: DETAILS PAGE (Update this section) ---
if st.session_state.page == "details":
    # Navigation Header
    st.button("← Back to Dashboard", on_click=lambda: st.session_state.update(page="dashboard"))
    
    # Get current Test Instance
    current_id = st.session_state.get("detail_id")
    test = next((t for t in st.session_state.tests if t.test_id == current_id), None)
    
    if test:
        # Header Row
        h1, h2 = st.columns([3, 1])
        with h1:
            st.title(f"{test.name}")
        with h2:
            # Action Buttons are now prominent at the top right
            if st.button("▶️ Save & Run", type="primary", use_container_width=True):
                 st.toast("Settings Saved! Running...")
                 run_test_logic(test)
                 st.rerun()

        # Description Editor (Compact)
        with st.expander(f"Test Details (ID: {test.test_id})"):
             test.name = st.text_input("Name", test.name)
             test.description = st.text_area("Description", test.description)

        # --- RENDER THE NEW UI ---
        render_test_config_ui(test)
        
    else:
        st.error("Test not found.")
    
    st.stop()

# --- 5. ROUTER VIEW: DETAILS PAGE ---
if st.session_state.page == "details":
    # Navigation Header
    st.button("← Back to Dashboard", on_click=lambda: st.session_state.update(page="dashboard"))
    
    # Get current Test Instance
    current_id = st.session_state.get("detail_id")
    test = next((t for t in st.session_state.tests if t.test_id == current_id), None)
    
    if test:
        # Header
        st.title(f"⚙️ Configure: {test.name}")
        st.caption(f"ID: {test.test_id} • Status: {test.status}")
        
        # Description Editor
        with st.expander("Edit Name & Description"):
             test.name = st.text_input("Name", test.name)
             test.description = st.text_area("Description", test.description)

        st.divider()

        # --- RENDER THE NEW SETTINGS UI ---
        render_test_config_ui(test)
        
        st.divider()
        
        # Save / Run Actions at the bottom
        c1, c2, spacer = st.columns([1, 1, 4])
        with c1:
            if st.button("💾 Save Configuration", type="primary", use_container_width=True):
                st.toast("Configuration Saved!")
                # In a real app, you might save to DB or JSON file here
        with c2:
             if st.button("▶️ Save & Run Test", use_container_width=True):
                 st.toast("Configuration Saved! Starting Run...")
                 run_test_logic(test) # Execution logic
                 st.rerun()
                 
    else:
        st.error("Test not found.")
    
    st.stop()






# --- 5. ROUTER VIEW: DETAILS PAGE ---
if st.session_state.page == "details":
    # Navigation Header
    st.button("← Back to Dashboard", on_click=lambda: st.session_state.update(page="dashboard"))
    
    # Get current Test Instance
    current_id = st.session_state.get("detail_id")
    test = next((t for t in st.session_state.tests if t.test_id == current_id), None)
    
    if test:
        # Header
        st.title(f"⚙️ Configure: {test.name}")
        st.caption(f"ID: {test.test_id} • Status: {test.status}")
        
        # Description Editor
        with st.expander("Edit Name & Description"):
             test.name = st.text_input("Name", test.name)
             test.description = st.text_area("Description", test.description)

        st.divider()

        # --- RENDER THE NEW SETTINGS UI ---
        render_test_config_ui(test)
        
        st.divider()
        
        # Save / Run Actions at the bottom
        c1, c2, spacer = st.columns([1, 1, 4])
        with c1:
            if st.button("💾 Save Configuration", type="primary", use_container_width=True):
                st.toast("Configuration Saved!")
                # In a real app, you might save to DB here
        with c2:
             if st.button("▶️ Save & Run Test", use_container_width=True):
                 st.toast("Configuration Saved! Starting Run...")
                 run_test_logic(test) # Execution logic
                 st.rerun()
                 
    else:
        st.error("Test not found.")
    
    st.stop()







# --- 6. DASHBOARD VIEW ---

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
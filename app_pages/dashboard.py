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
from generate import GenerateEmail

import plotly.graph_objects as go
import numpy as np 
import time 
from difflib import SequenceMatcher
from sentence_transformers import SentenceTransformer, util

from functionality import load_data




# --- PAGE CONFIGURATION ---
st.set_page_config(page_title='Dashboard', layout='wide')


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

if "llm" not in st.session_state:
    st.session_state.llm = GenerateEmail("")

# --- 2. LOGIC FUNCTIONS ---
@st.cache_resource
def load_semantic_model():
    """Loads the semantic model once and caches it."""
    return SentenceTransformer('all-MiniLM-L6-v2')

def calculate_similarity_metrics(original, generated):
    """
    Calculates both Lexical (Levenshtein) and Semantic (Cosine) similarity.
    Returns a dictionary with both scores (0-100 scale).
    """
    scores = {"Lexical Similarity": 0.0, "Semantic Similarity": 0.0}
    
    if not original or not generated:
        return scores

    # 1. Lexical Similarity (Levenshtein)
    # Measures character/word overlap
    lex_score = SequenceMatcher(None, original, generated).ratio()
    scores["Lexical Similarity"] = round(lex_score * 100, 2)

    # 2. Semantic Similarity (Cosine)
    # Measures meaning preservation using vector embeddings
    try:
        model = load_semantic_model()
        embeddings = model.encode([original, generated])
        # util.cos_sim returns a tensor, we extract the float value
        sem_score = util.cos_sim(embeddings[0], embeddings[1]).item()
        # Ensure score is between 0-100 (sometimes cosine can be slightly negative for opposites)
        scores["Semantic Similarity"] = round(max(0, sem_score) * 100, 2)
    except Exception as e:
        print(f"Semantic calculation failed: {e}")
        scores["Semantic Similarity"] = 0.0

    return scores

def run_test_logic(test_obj):
    """
    Executes the full test pipeline.
    Tracks latency and catches errors to calculate error_rate.
    """
    # 1. SETUP RESOURCES
    llm = st.session_state.llm
    DEMO_DATASETS = {
        "lengthen" : "/Users/itang/Music/servicenow_bootcamp/ai_bootcamp_starter/datasets/lengthen.jsonl",
        "shorten" : "/Users/itang/Music/servicenow_bootcamp/ai_bootcamp_starter/datasets/shorten.jsonl",
        "tone" : "/Users/itang/Music/servicenow_bootcamp/ai_bootcamp_starter/datasets/tone.jsonl",
        'test' : '/Users/itang/Music/servicenow_bootcamp/ai_bootcamp_starter/datasets/test.jsonl',
        'ambiguity' : '/Users/itang/Music/servicenow_bootcamp/ai_bootcamp_starter/datasets/ambiguity.jsonl',
    }
    
    dataset_key = test_obj.config.get('dataset_name', 'lengthen')
    
    action_map = {
        "Lengthen": "lengthen",
        "Shorten": "shorten",
        "Tone": "tone"
    }
    action_key = action_map.get(test_obj.config.get('edit_method', 'Tone'), 'tone')

    # 2. LOAD DATASET (Using custom load_data)
    try:
        emails_dict = load_data(dataset_key, DEMO_DATASETS) 
    except Exception as e:
        st.error(f"❌ Failed to load dataset '{dataset_key}': {e}")
        return

    results_container = []
    total_items = len(emails_dict)
    progress_bar = st.progress(0)

    # 3. MAIN EXECUTION LOOP
    with st.spinner(f"Processing {total_items} emails with {test_obj.config['model_name']}..."):
        
        for i, (email_id, email_data) in enumerate(emails_dict.items()):
            row_start_time = time.time()
            
            row_status = "Pending" 
            error_message = ""
            metric_results = {}
            avg_score = 0
            generated_body = ""
            similarity_scores = {"Lexical Similarity": 0.0, "Semantic Similarity": 0.0} # Default
            
            # --- A. PREPARE INPUTS ---
            original_content = email_data.get('content', '')
            original_subject = email_data.get('subject', 'No Subject')
            additional_context = test_obj.config.get('extra_context', '')
            
            try:
                # --- B. GENERATION STEP ---
                body_args = {
                    'selected_text': original_content,
                    'additional_text': additional_context
                }
                
                generated_body = llm.generate(
                    action=action_key,
                    args=body_args
                )

                # --- NEW: CALCULATE SIMILARITY ---
                # Calculate immediately after generation
                similarity_scores = calculate_similarity_metrics(original_content, generated_body)

                # --- C. EVALUATION STEP ---
                metrics_to_run = test_obj.config.get('evaluation_metrics', [])
                
                judge_args = {
                    'selected_text': original_content,
                    'additional_text': additional_context,
                    'model_response': generated_body
                }

                for metric in metrics_to_run:
                    try:
                        evaluation_json = llm.generate(
                            action=metric.lower(),
                            args=judge_args
                        )
                        
                        data = json.loads(evaluation_json)
                        rating = data.get('rating', 0)
                        explanation = data.get('explanation', "No explanation provided.")
                        
                        metric_results[metric] = rating
                        metric_results[f"{metric}_explanation"] = explanation
                        
                    except json.JSONDecodeError:
                        metric_results[metric] = 0
                        metric_results[f"{metric}_explanation"] = "JSON Decode Failure"
                    except Exception as e:
                        metric_results[metric] = 0
                        metric_results[f"{metric}_explanation"] = f"Judge Error: {str(e)}"

                # --- D. SCORING ---
                valid_scores = [v for k, v in metric_results.items() if k in metrics_to_run and isinstance(v, (int, float))]
                avg_score = sum(valid_scores) / len(valid_scores) if valid_scores else 0
                row_status = "Passed" if avg_score >= 3.0 else "Failed"

            except Exception as e:
                row_status = "Error"
                error_message = str(e)
                generated_body = f"ERROR: {error_message}"

            # --- E. AGGREGATE ROW DATA ---
            row_end_time = time.time()
            latency_ms = int((row_end_time - row_start_time) * 1000)

            row_record = {
                "ID": f"email_{email_id}",
                "Original Subject": original_subject,
                "Original Content": original_content, 
                "Generated Content": generated_body,
                "Overall Score": round(avg_score, 2),
                "Status": row_status,
                "Latency (ms)": latency_ms,
                "Error Message": error_message, 
                # ✅ Add the new similarity scores to the record
                "Levenschtein Similarity": similarity_scores["Lexical Similarity"], # lexical
                "Cosine Similarity": similarity_scores["Semantic Similarity"], # semantic
                **metric_results
            }
            
            results_container.append(row_record)
            progress_bar.progress((i + 1) / total_items)

    # 4. SAVE & FINALIZE
    df_results = pd.DataFrame(results_container)
    test_obj.save_run_data(df_results)

    with open('output.json', 'w') as f:
        json.dump(test_obj.to_dict(), f, indent=4)
    
    if test_obj.error_rate > 0:
        st.toast(f"⚠️ Finished with {test_obj.error_rate:.1f}% errors.", icon="⚠️")
    else:
        st.toast(f"✅ Test '{test_obj.name}' finished successfully!", icon="✅")



def create_test_from_json(json_input):
    """
    Parses JSON input (string or dict) and returns a TestInstance object.
    """
    try:
        # 1. Ensure data is a dictionary
        if isinstance(json_input, str):
            # If it's a JSON string, parse it
            data = json.loads(json_input)
        elif isinstance(json_input, dict):
            # If it's already a dict, use it directly
            data = json_input
        else:
            st.error("❌ Invalid input format. Expected JSON string or Dictionary.")
            return None

        # 2. Create the object using the class method
        # The class's from_dict method already handles mapping config, results, latency, etc.
        new_instance = TestInstance.from_dict(data)
        
        return new_instance

    except json.JSONDecodeError as e:
        st.error(f"❌ JSON Decode Error: {e}")
        return None
    except Exception as e:
        st.error(f"❌ Error creating Test Instance: {e}")
        return None
    
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
    
    # 1. Input Methods
    json_str = st.text_area("Paste JSON String", height=150, placeholder='{"test_id": "...", "results": [...]}')
    uploaded_file = st.file_uploader("Or upload JSON file", type=["json"])
    
    if st.button("Import", type="primary", use_container_width=True):
        raw_data = None
        try:
            # 2. Parse Data
            if uploaded_file:
                raw_data = json.load(uploaded_file)
            elif json_str.strip():
                raw_data = json.loads(json_str)
            else:
                st.warning("⚠️ Please provide input.")
                return

            # 3. Normalize to list (Handle single dict vs list of dicts)
            if isinstance(raw_data, dict):
                raw_data = [raw_data]
            
            if not isinstance(raw_data, list):
                st.error("❌ Invalid format. Root must be a list or object.")
                return

            # 4. Import Logic
            count = 0
            existing_ids = [t.test_id for t in st.session_state.tests]
            
            for item in raw_data:
                try:
                    # Create object using your class method
                    new_test = TestInstance.from_dict(item)
                    
                    # 5. ID Conflict Resolution
                    # If ID exists, generate a new one to prevent Streamlit key errors
                    if new_test.test_id in existing_ids:
                        import uuid
                        new_test.test_id = str(uuid.uuid4())[:8]
                        new_test.name = f"{new_test.name} (Imported)"
                    
                    # Add to session state (Front of list)
                    st.session_state.tests.insert(0, new_test)
                    count += 1
                    
                except Exception as e:
                    st.warning(f"Skipped an item due to error: {e}")
                    continue
            
            if count > 0:
                st.toast(f"✅ Successfully imported {count} test(s)!")
                st.rerun()
            else:
                st.warning("⚠️ No valid test objects found to import.")

        except json.JSONDecodeError:
            st.error("❌ Invalid JSON syntax.")
        except Exception as e:
            st.error(f"❌ An error occurred: {str(e)}")

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
    Includes robust dataset-level analytics with Runtime, Aggregates, and Config Summary.
    """
    
    # Mock Data / Session Access
    llm = st.session_state.llm
    
    # Load available options from session state or defaults
    DEMO_DATASETS = {
        "lengthen" : "datasets/lengthen.jsonl",
        "shorten" : "datasets/shorten.jsonl",
        "tone" : "datasets/tone.jsonl",
        'test' : "datasets/test.jsonl",
        'ambiguity' : "datasets/ambiguity.jsonl",
    }
    
    # Safe retrieval of lists
    AVAILABLE_METRICS = list(llm.evaluation_metrics) if hasattr(llm, 'evaluation_metrics') else []
    LLM_MODELS = list(llm.models) if hasattr(llm, 'models') else ['gpt-4o-mini']
    EDIT_METHODS = ['Lengthen', 'Shorten', 'Tone'] 

    # --- TABS DEFINITION ---
    tab_settings, tab_analytics = st.tabs(["⚙️ Settings", "📊 Results & Analytics"])
    
    # ==========================================
    # TAB 1: ALL CONFIGURATION (Preserved)
    # ==========================================
    with tab_settings:
        st.caption("Configure the parameters for this specific test instance.")

        # --- SECTION 1: CORE STRATEGY ---
        with st.container(border=True):
            st.markdown("##### 🎯 Core Strategy")
            c1, c2, c3 = st.columns(3)
            
            with c1:
                dataset_options = list(DEMO_DATASETS.keys())
                current_ds = test_instance.config.get("dataset_name", dataset_options[0] if dataset_options else "")
                
                idx = 0
                if current_ds in dataset_options:
                    idx = dataset_options.index(current_ds)

                test_instance.config["dataset_name"] = st.selectbox(
                    label="📚 Dataset", 
                    options=dataset_options, 
                    index=idx,
                    key=f"dataset_name_{test_instance.test_id}",
                    help="The source data to run the test against."
                )
            
            with c2:
                current_model = test_instance.config.get("model_name", LLM_MODELS[0])
                idx = 0
                if current_model in LLM_MODELS:
                    idx = LLM_MODELS.index(current_model)

                test_instance.config["model_name"] = st.selectbox(
                    label="🤖 Base Model",
                    options=LLM_MODELS,
                    index=idx,
                    key=f"model_name_{test_instance.test_id}",
                    help="The LLM engine used for generation."
                )

            with c3:
                current_method = test_instance.config.get("edit_method", EDIT_METHODS[0])
                test_instance.config["edit_method"] = st.selectbox(
                    label="✨ Edit Method",
                    options=EDIT_METHODS,
                    index=EDIT_METHODS.index(current_method) if current_method in EDIT_METHODS else 0,
                    key=f"edit_method_{test_instance.test_id}",
                    help=" The transformation logic applied to the input."
                )

        # --- SECTION 2: SPLIT VIEW ---
        col_left, col_right = st.columns([1.6, 1], gap="medium")

        # --- LEFT COLUMN: HYPERPARAMETERS ---
        with col_left:
            with st.container(border=True):
                st.markdown("##### 🎛️ LLM Hyperparameters")
                st.caption("Fine-tune the model behavior.")
                
                with st.expander("🎨 Creativity (Temperature & Top P)", expanded=True):
                    c_temp, c_top = st.columns(2)
                    with c_temp:
                        test_instance.config["temperature"] = st.slider(
                            "Temperature", 0.0, 2.0, test_instance.config.get("temperature", 0.7), 0.01,
                            key=f"tmp_t_{test_instance.test_id}"
                        )
                    with c_top:
                        test_instance.config["top_p"] = st.slider(
                            "Top p", 0.0, 1.0, test_instance.config.get("top_p", 0.95), 0.01,
                            key=f"tmp_tp_{test_instance.test_id}"
                        )

                with st.expander("📏 Length & Batching"):
                    c_tok, c_n = st.columns(2)
                    with c_tok:
                        test_instance.config["max_tokens"] = st.number_input(
                            "Max Tokens", 1, 128000, int(test_instance.config.get("max_tokens", 500)),
                            key=f"tmp_mt_{test_instance.test_id}"
                        )
                    with c_n:
                        test_instance.config["n"] = st.number_input(
                            "Batch Count (n)", 1, 5, int(test_instance.config.get("n", 1)),
                            key=f"tmp_n_{test_instance.test_id}"
                        )

                with st.expander("🚫 Repetition Penalties"):
                    test_instance.config["presence_penalty"] = st.slider(
                        "Presence Penalty", -2.0, 2.0, float(test_instance.config.get("presence_penalty", 0.0)), 0.1,
                        key=f"tmp_pp_{test_instance.test_id}"
                    )
                    test_instance.config["frequency_penalty"] = st.slider(
                        "Frequency Penalty", -2.0, 2.0, float(test_instance.config.get("frequency_penalty", 0.0)), 0.1,
                        key=f"tmp_fp_{test_instance.test_id}"
                    )

                with st.expander("🎲 Reliability & Seed"):
                    c_seed, c_log = st.columns(2)
                    with c_seed:
                        test_instance.config["seed"] = st.number_input(
                            "Seed", value=int(test_instance.config.get("seed", 0)),
                            key=f"tmp_s_{test_instance.test_id}"
                        )
                    with c_log:
                        test_instance.config["top_logprobs"] = st.number_input(
                            "Top Log Probs", 0, 20, int(test_instance.config.get("top_logprobs", 0)),
                            key=f"tmp_tl_{test_instance.test_id}"
                        )
                    test_instance.config["logprobs"] = True if test_instance.config["top_logprobs"] > 0 else False

        # --- RIGHT COLUMN: EVALUATION ---
        with col_right:
            with st.container(border=True):
                st.markdown("##### ⚖️ Grading Criteria")
                st.caption("Select judges to evaluate results.")
                
                current_metrics = test_instance.config.get("evaluation_metrics", AVAILABLE_METRICS)
                
                test_instance.config["evaluation_metrics"] = st.multiselect(
                    label="Active Judges",
                    options=AVAILABLE_METRICS,
                    default=current_metrics,
                    key=f"evaluation_metrics_{test_instance.test_id}",
                    help="These metrics will determine Pass/Fail status."
                )
                
                if len(test_instance.config["evaluation_metrics"]) > 0:
                    st.success(f"{len(test_instance.config['evaluation_metrics'])} Judges Active")
                else:
                    st.warning("No Judges Selected")

    # ==========================================
    # TAB 2: DATASET ANALYTICS
    # ==========================================
    with tab_analytics:
        if not test_instance.results:
            st.warning("⚠️ No run data found. Click 'Save & Run' to generate analytics.")
            st.image("https://placehold.co/800x300?text=Run+Test+to+See+Analytics", use_container_width=True)
        else:
            # 1. Load Real Results from the Object
            df_results = pd.DataFrame(test_instance.results)
            
            # --- METRIC DETECTION ---
            config_metrics = test_instance.config.get("evaluation_metrics", [])
            valid_judge_metrics = [m for m in config_metrics if m in df_results.columns]
            similarity_metrics = [col for col in df_results.columns if "Similarity" in col]

            # --- SECTION A: KPI HEADER ---
            st.subheader(f"Run Analysis: {test_instance.last_run}")
            
            total_runs = len(df_results)
            pass_count = len(df_results[df_results['Status'] == 'Passed'])
            pass_rate = (pass_count / total_runs) * 100 if total_runs > 0 else 0
            avg_score_total = df_results['Overall Score'].mean()
            avg_latency = df_results['Latency (ms)'].mean()
            total_duration_sec = test_instance.latency / 1000 if hasattr(test_instance, 'latency') else (avg_latency * total_runs) / 1000

            kpi1, kpi2, kpi3, kpi4 = st.columns(4)
            kpi1.metric("Pass Rate", f"{pass_rate:.1f}%", f"{pass_count}/{total_runs} passed")
            kpi2.metric("Avg Quality Score", f"{avg_score_total:.2f}/5.0")
            kpi3.metric("Avg Latency", f"{int(avg_latency)}ms", help="Average time per email generation")
            kpi4.metric("Total Duration", f"{total_duration_sec:.2f}s", help="Total runtime for the entire dataset")

            st.divider()

            # --- SECTION B: AGGREGATE VISUALS ---
            viz1, viz2 = st.columns([1, 1])
            
            # B1. Aggregate Radar Chart
            with viz1:
                st.markdown("**🔹 Metric Profile (Dataset Average)**")
                if valid_judge_metrics:
                    metric_means = df_results[valid_judge_metrics].mean().reset_index()
                    metric_means.columns = ['Metric', 'Score']
                    radar_df = pd.concat([metric_means, metric_means.iloc[[0]]])
                    fig_radar = px.line_polar(
                        radar_df, r='Score', theta='Metric', line_close=True,
                        range_r=[0, 5], markers=True
                    )
                    fig_radar.update_traces(fill='toself', line_color='#60a5fa')
                    fig_radar.update_layout(
                        margin=dict(t=30, b=30, l=40, r=40),
                        paper_bgcolor="rgba(0,0,0,0)",
                        plot_bgcolor="rgba(0,0,0,0)",
                        font=dict(size=12, color="white"),
                        polar=dict(
                            bgcolor='rgba(0,0,0,0)',
                            radialaxis=dict(visible=True, range=[0, 5], showline=False, tickfont=dict(color='white')),
                            angularaxis=dict(tickfont=dict(color='white'))
                        )
                    )
                    st.plotly_chart(fig_radar, use_container_width=True)
                else:
                    st.info("No judge metrics available for Radar Chart.")

            # B2. Score Histogram
            with viz2:
                c_label, c_sel = st.columns([1, 1])
                c_label.markdown("**🔹 Consistency Distribution**")
                dist_options = ["Overall Score"] + valid_judge_metrics + similarity_metrics
                selected_dist_metric = c_sel.selectbox(
                    "Select Metric", dist_options, label_visibility="collapsed", key=f"dist_sel_{test_instance.test_id}"
                )
                
                if selected_dist_metric in df_results.columns:
                    if "Similarity" in selected_dist_metric:
                        range_x = [0, 105]
                        title_text = f"{selected_dist_metric} (0-100%)"
                    else:
                        range_x = [0, 5.5]
                        title_text = f"{selected_dist_metric.title()} (0-5)"

                    fig_hist = px.histogram(
                        df_results, x=selected_dist_metric, nbins=15, 
                        color="Status", color_discrete_map={"Passed": "#4ade80", "Failed": "#f87171", "Error": "#fbbf24"},
                        range_x=range_x
                    )
                    fig_hist.update_layout(
                        xaxis_title=title_text, yaxis_title="Count", bargap=0.1,
                        margin=dict(t=30, b=30, l=20, r=20), paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)",
                        font=dict(color="white"), legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1)
                    )
                    st.plotly_chart(fig_hist, use_container_width=True)
                    
                    # --- NEW: Statistics Expander ---
                    with st.expander(f"View Statistics: {selected_dist_metric}", expanded=False):
                        if pd.api.types.is_numeric_dtype(df_results[selected_dist_metric]):
                            # Calculate descriptive stats (count, mean, std, min, 25%, 50%, 75%, max)
                            stats = df_results[selected_dist_metric].describe()
                            # Transpose for easier reading (Metric as row)
                            stats_df = pd.DataFrame(stats).T
                            st.dataframe(stats_df, use_container_width=True)
                        else:
                            st.info("Statistics not available for non-numeric data.")
                else:
                    st.warning(f"Data for {selected_dist_metric} not found.")

            # --- SECTION C: DRILL-DOWN TABLE ---
            st.divider()
            c_header, c_filter = st.columns([3, 1])
            c_header.markdown("**🔎 Drill-Down Inspection**")
            
            filter_status = c_filter.selectbox(
                "Filter Status", ["All", "Failed Only", "Passed Only"], index=0, key=f"filt_{test_instance.test_id}"
            )
            
            display_df = df_results.copy()
            if filter_status == "Failed Only":
                display_df = display_df[display_df["Status"] == "Failed"]
            elif filter_status == "Passed Only":
                display_df = display_df[display_df["Status"] == "Passed"]
            
            column_config = {
                "ID": st.column_config.TextColumn("ID", width="small"),
                "Status": st.column_config.TextColumn("Status", width="small"),
                "Overall Score": st.column_config.ProgressColumn("Quality Score", format="%.2f", min_value=0, max_value=5, width="medium"),
                "Latency (ms)": st.column_config.NumberColumn("Latency (ms)"),
            }
            base_cols = ["ID", "Status", "Overall Score", "Latency (ms)"]
            final_cols = [c for c in base_cols if c in display_df.columns]
            st.dataframe(display_df[final_cols], use_container_width=True, hide_index=True, column_config=column_config, height=300)

            # --- SECTION D: SELECTED ITEM INSPECTOR ---
            with st.expander("Inspect Specific Email Trace", expanded=True):
                if not display_df.empty:
                    selected_trace_id = st.selectbox(
                        "Select Email ID to Inspect", display_df["ID"].tolist(), key=f"trace_sel_{test_instance.test_id}"
                    )
                    trace_row = display_df[display_df["ID"] == selected_trace_id].iloc[0]
                    
                    st.caption("Content Comparison")
                    c_orig, c_gen = st.columns(2)
                    with c_orig:
                        st.markdown("**Original Input**")
                        st.text_area("Original", value=trace_row.get("Original Content", "N/A"), height=200, disabled=True, label_visibility="collapsed")
                    with c_gen:
                        st.markdown("**Generated Output**")
                        st.text_area("Generated", value=trace_row.get("Generated Content", "N/A"), height=200, disabled=True, label_visibility="collapsed")

                    # DISPLAY SIMILARITY SCORES
                    if "Lexical Similarity" in trace_row or "Semantic Similarity" in trace_row:
                        st.caption("Similarity Metrics")
                        sim1, sim2, sim_rest = st.columns([1, 1, 2])
                        
                        if "Lexical Similarity" in trace_row:
                            val = trace_row['Lexical Similarity']
                            sim1.metric("Lexical", f"{val:.1f}%", help="Levenshtein (Edit Distance)")
                            
                        if "Semantic Similarity" in trace_row:
                            val = trace_row['Semantic Similarity']
                            sim2.metric("Semantic", f"{val:.1f}%", help="Cosine Similarity (Meaning)")

                    st.divider()

                    st.caption("Judge Explanations")
                    available_trace_metrics = [m for m in (valid_judge_metrics + similarity_metrics) if m in trace_row]
                    
                    if available_trace_metrics:
                        selected_metric = st.selectbox(
                            "Select Metric to View Details", available_trace_metrics, key=f"metric_sel_{test_instance.test_id}"
                        )
                        score = trace_row.get(selected_metric, "N/A")
                        explanation = trace_row.get(f"{selected_metric}_explanation", "No explanation available.")
                        
                        is_sim = "Similarity" in selected_metric
                        threshold_high = 80 if is_sim else 4
                        threshold_med = 60 if is_sim else 3
                        max_val = 100 if is_sim else 5
                        
                        score_color = "green" if isinstance(score, (int, float)) and score >= threshold_high else "orange" if isinstance(score, (int, float)) and score >= threshold_med else "red"
                        st.markdown(f"#### Score: :{score_color}[{score}/{max_val}]")
                        with st.container(border=True):
                            st.markdown(f"**Explanation:**\n\n{explanation}")
                    else:
                        st.warning("No metric details available for this record.")

                    if "Error Message" in trace_row and trace_row["Error Message"]:
                        st.error(f"Error Log: {trace_row['Error Message']}")
                else:
                    st.info("No data available based on current filters.")
            
            # --- SECTION E: CONFIGURATION SUMMARY ---
            st.divider()
            with st.expander("View Test Configuration History", expanded=False):
                if test_instance.config:
                    config_items = [{"Parameter": k, "Value": str(v)} for k, v in test_instance.config.items()]
                    df_config = pd.DataFrame(config_items)
                    st.dataframe(df_config, use_container_width=True, hide_index=True, column_config={"Parameter": st.column_config.TextColumn("Parameter", width="medium"), "Value": st.column_config.TextColumn("Value", width="large")})
                else:
                    st.info("No configuration data available.")


def render_compare_menu_ui(test_a, test_b):
    """
    Renders a side-by-side comparison of two TestInstances using REAL stored data.
    Includes comprehensive statistics and delta-focused KPIs.
    """
    
    # --- 1. DATA LOADING & PREPARATION ---
    df_a = pd.DataFrame(test_a.results) if test_a.results else pd.DataFrame()
    df_b = pd.DataFrame(test_b.results) if test_b.results else pd.DataFrame()

    if df_a.empty or df_b.empty:
        st.error("One or both selected tests have no result data. Please run them first.")
        return

    # Filter for numeric metrics only
    exclude_cols = ['ID', 'Original Subject', 'Original Content', 'Generated Content', 'Status', 'Error Message', 'Overall Score', 'Latency (ms)', 'Cost ($)']
    
    metric_cols_a = [c for c in df_a.columns if c not in exclude_cols and not c.endswith('_explanation') and pd.api.types.is_numeric_dtype(df_a[c])]
    metric_cols_b = [c for c in df_b.columns if c not in exclude_cols and not c.endswith('_explanation') and pd.api.types.is_numeric_dtype(df_b[c])]
    
    METRICS_LIST = list(set(metric_cols_a).intersection(metric_cols_b))
    
    # Calculate Averages for Charts
    avgs_a = [df_a[m].mean() for m in METRICS_LIST] if METRICS_LIST else []
    avgs_b = [df_b[m].mean() for m in METRICS_LIST] if METRICS_LIST else []

    # --- 2. CALCULATE STATISTICS & KPIS ---
    
    def calculate_stats(test_obj, df):
        total = len(df)
        passed = len(df[df["Status"] == "Passed"])
        failed = len(df[df["Status"] == "Failed"])
        # Use object latency (ms) -> seconds, fallback to df sum if object stat missing
        duration_sec = (test_obj.latency / 1000) if hasattr(test_obj, 'latency') and test_obj.latency > 0 else (df["Latency (ms)"].sum() / 1000) if "Latency (ms)" in df.columns else 0
        avg_score = df["Overall Score"].mean() if "Overall Score" in df.columns else 0
        pass_rate = (passed / total * 100) if total > 0 else 0
        avg_lat = df["Latency (ms)"].mean() if "Latency (ms)" in df.columns else 0
        return {
            "Total Emails": total,
            "Passed": passed,
            "Failed": failed,
            "Pass Rate": pass_rate,
            "Avg Score": avg_score,
            "Avg Latency": avg_lat,
            "Total Duration": duration_sec
        }

    stats_a = calculate_stats(test_a, df_a)
    stats_b = calculate_stats(test_b, df_b)

    # --- 3. DISPLAY STATISTICS TABLE ---
    st.subheader("Run Statistics")
    
    # Create a clean comparison table for general stats
    stats_data = {
        "Metric": ["Total Emails", "Passed Count", "Failed Count", "Total Duration (s)", "Pass Rate (%)", "Avg Quality Score (0-5)", "Avg Latency (ms)"],
        f"{test_a.name} (Baseline)": [
            f"{stats_a['Total Emails']}",
            f"{stats_a['Passed']}",
            f"{stats_a['Failed']}",
            f"{stats_a['Total Duration']:.2f}s",
            f"{stats_a['Pass Rate']:.1f}%",
            f"{stats_a['Avg Score']:.2f}",
            f"{int(stats_a['Avg Latency'])}ms"
        ],
        f"{test_b.name} (Comparison)": [
            f"{stats_b['Total Emails']}",
            f"{stats_b['Passed']}",
            f"{stats_b['Failed']}",
            f"{stats_b['Total Duration']:.2f}s",
            f"{stats_b['Pass Rate']:.1f}%",
            f"{stats_b['Avg Score']:.2f}",
            f"{int(stats_b['Avg Latency'])}ms"
        ],
        "Delta (B - A)": [
            f"{stats_b['Total Emails'] - stats_a['Total Emails']}",
            f"{stats_b['Passed'] - stats_a['Passed']}",
            f"{stats_b['Failed'] - stats_a['Failed']}",
            f"{stats_b['Total Duration'] - stats_a['Total Duration']:.2f}s",
            f"{stats_b['Pass Rate'] - stats_a['Pass Rate']:.1f}%",
            f"{stats_b['Avg Score'] - stats_a['Avg Score']:.2f}",
            f"{int(stats_b['Avg Latency'] - stats_a['Avg Latency'])}ms"
        ]
    }
    st.dataframe(pd.DataFrame(stats_data), use_container_width=True, hide_index=True)

    # --- 4. KPI SCOREBOARD (Deltas) ---
    st.divider()
    st.subheader("Deltas from Baseline")
    
    # We focus on the "big three" deltas: Pass Rate, Quality, and Latency
    k1, k2, k3 = st.columns(3)
    
    delta_pass = stats_b['Pass Rate'] - stats_a['Pass Rate']
    k1.metric(
        "Pass Rate Delta", 
        f"{stats_b['Pass Rate']:.1f}%", 
        f"{delta_pass:+.1f}% vs Baseline"
    )
    
    delta_score = stats_b['Avg Score'] - stats_a['Avg Score']
    k2.metric(
        "Quality Score Delta", 
        f"{stats_b['Avg Score']:.2f}", 
        f"{delta_score:+.2f} vs Baseline"
    )
    
    delta_lat = stats_b['Avg Latency'] - stats_a['Avg Latency']
    k3.metric(
        "Latency Delta", 
        f"{int(stats_b['Avg Latency'])}ms", 
        f"{int(delta_lat):+d}ms vs Baseline", 
        delta_color="inverse"
    )

    # --- 5. VISUALIZATION SECTION ---
    st.divider()
    st.subheader("Visual Benchmark")
    
    view_options = ["Average Overview"] + METRICS_LIST
    col_ctrl, col_space = st.columns([1, 3])
    with col_ctrl:
        selected_view = st.selectbox("Select Benchmark Metric", view_options, index=0)

    if selected_view == "Average Overview":
        col_radar, col_bar = st.columns([1, 1])
        
        # --- SPLIT METRICS ---
        sim_metrics = [m for m in METRICS_LIST if "Similarity" in m]
        judge_metrics = [m for m in METRICS_LIST if "Similarity" not in m]

        # A. RADAR CHART (JUDGES ONLY)
        with col_radar:
            st.markdown("**🔹 Holistic Profile (Judges)**")
            if judge_metrics:
                # Prep Data
                avgs_a_judge = [df_a[m].mean() for m in judge_metrics]
                avgs_b_judge = [df_b[m].mean() for m in judge_metrics]
                
                # Close loop
                metrics_closed = judge_metrics + [judge_metrics[0]]
                avgs_a_closed = avgs_a_judge + [avgs_a_judge[0]]
                avgs_b_closed = avgs_b_judge + [avgs_b_judge[0]]

                fig_radar = go.Figure()
                fig_radar.add_trace(go.Scatterpolar(r=avgs_a_closed, theta=metrics_closed, fill='toself', name=f"{test_a.name} (A)", line_color='rgba(96, 165, 250, 0.8)', fillcolor='rgba(96, 165, 250, 0.2)'))
                fig_radar.add_trace(go.Scatterpolar(r=avgs_b_closed, theta=metrics_closed, fill='toself', name=f"{test_b.name} (B)", line_color='rgba(248, 113, 113, 0.8)', fillcolor='rgba(248, 113, 113, 0.2)'))
                
                fig_radar.update_layout(
                    polar=dict(
                        bgcolor='rgba(0,0,0,0)',
                        radialaxis=dict(visible=True, range=[0, 5], showline=False, tickfont=dict(color='white'), gridcolor='rgba(255, 255, 255, 0.2)'),
                        angularaxis=dict(tickfont=dict(color='white', size=12), gridcolor='rgba(255, 255, 255, 0.2)', linecolor='rgba(255, 255, 255, 0.2)')
                    ),
                    showlegend=True,
                    legend=dict(font=dict(color="white"), orientation="h", yanchor="bottom", y=-0.2, xanchor="center", x=0.5),
                    margin=dict(t=40, b=40, l=40, r=40),
                    height=350,
                    paper_bgcolor="rgba(0,0,0,0)",
                    plot_bgcolor="rgba(0,0,0,0)",
                    font=dict(color="white")
                )
                st.plotly_chart(fig_radar, use_container_width=True)
            else:
                st.info("No judge metrics available.")

        # B. BAR CHARTS (SPLIT)
        with col_bar:
            st.markdown("**🔹 Metric Deltas**")
            
            # 1. Judges (0-5 Scale)
            if judge_metrics:
                st.caption("Qualitative Judges (0-5)")
                avgs_a_judge = [df_a[m].mean() for m in judge_metrics]
                avgs_b_judge = [df_b[m].mean() for m in judge_metrics]
                
                df_bar_judge = pd.DataFrame({
                    "Metric": judge_metrics * 2,
                    "Score": avgs_a_judge + avgs_b_judge,
                    "Test": [f"{test_a.name} (A)"] * len(judge_metrics) + [f"{test_b.name} (B)"] * len(judge_metrics)
                })
                fig_bar = px.bar(
                    df_bar_judge, x="Metric", y="Score", color="Test", barmode="group",
                    color_discrete_map={f"{test_a.name} (A)": "#60a5fa", f"{test_b.name} (B)": "#f87171"},
                    range_y=[0, 5.5]
                )
                fig_bar.update_layout(
                    margin=dict(t=10, b=10, l=10, r=10), height=200,
                    paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)", font=dict(color="white"),
                    xaxis=dict(title=None, tickfont=dict(color='white')), yaxis=dict(title=None, tickfont=dict(color='white'), gridcolor='rgba(255, 255, 255, 0.1)'),
                    legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1)
                )
                st.plotly_chart(fig_bar, use_container_width=True)

            # 2. Similarities (0-100 Scale)
            if sim_metrics:
                st.caption("Similarity Metrics (0-100)")
                avgs_a_sim = [df_a[m].mean() for m in sim_metrics]
                avgs_b_sim = [df_b[m].mean() for m in sim_metrics]
                
                df_bar_sim = pd.DataFrame({
                    "Metric": sim_metrics * 2,
                    "Score": avgs_a_sim + avgs_b_sim,
                    "Test": [f"{test_a.name} (A)"] * len(sim_metrics) + [f"{test_b.name} (B)"] * len(sim_metrics)
                })
                fig_bar_sim = px.bar(
                    df_bar_sim, x="Metric", y="Score", color="Test", barmode="group",
                    color_discrete_map={f"{test_a.name} (A)": "#60a5fa", f"{test_b.name} (B)": "#f87171"},
                    range_y=[0, 105]
                )
                fig_bar_sim.update_layout(
                    margin=dict(t=10, b=10, l=10, r=10), height=200,
                    paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)", font=dict(color="white"),
                    xaxis=dict(title=None, tickfont=dict(color='white')), yaxis=dict(title=None, tickfont=dict(color='white'), gridcolor='rgba(255, 255, 255, 0.1)'),
                    showlegend=False # Hide legend for second chart to save space
                )
                st.plotly_chart(fig_bar_sim, use_container_width=True)

    else:
        st.markdown(f"**🔹 Distribution Analysis: {selected_view}**")
        df_dist_a = df_a[[selected_view]].rename(columns={selected_view: "Score"})
        df_dist_a["Test"] = f"{test_a.name} (A)"
        df_dist_b = df_b[[selected_view]].rename(columns={selected_view: "Score"})
        df_dist_b["Test"] = f"{test_b.name} (B)"
        df_combined = pd.concat([df_dist_a, df_dist_b])

        # Dynamic Range for Histogram
        if "Similarity" in selected_view:
            range_x = [0, 105]
            title_text = f"{selected_view} (0-100%)"
        else:
            range_x = [0, 5.5]
            title_text = f"{selected_view.title()} Score (1-5)"

        fig_hist = px.histogram(
            df_combined, x="Score", color="Test", barmode="overlay", nbins=15, range_x=range_x, opacity=0.6,
            color_discrete_map={f"{test_a.name} (A)": "#60a5fa", f"{test_b.name} (B)": "#f87171"}
        )
        fig_hist.update_layout(
            xaxis_title=title_text,
            yaxis_title="Count of Emails",
            height=400,
            margin=dict(t=20, b=20, l=40, r=40),
            paper_bgcolor="rgba(0,0,0,0)",
            plot_bgcolor="rgba(0,0,0,0)",
            font=dict(color="white"),
            xaxis=dict(tickfont=dict(color='white'), title_font=dict(color='white'), gridcolor='rgba(255, 255, 255, 0.1)'),
            yaxis=dict(tickfont=dict(color='white'), title_font=dict(color='white'), gridcolor='rgba(255, 255, 255, 0.1)'),
            legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1, font=dict(color="white"))
        )
        st.plotly_chart(fig_hist, use_container_width=True)
        
        s1, s2, s3, s4 = st.columns(4)
        s1.metric(f"Mean (A)", f"{df_dist_a['Score'].mean():.2f}")
        s2.metric(f"Mean (B)", f"{df_dist_b['Score'].mean():.2f}", f"{df_dist_b['Score'].mean() - df_dist_a['Score'].mean():.2f}")
        s3.metric(f"Variance (A)", f"{df_dist_a['Score'].var():.2f}")
        s4.metric(f"Variance (B)", f"{df_dist_b['Score'].var():.2f}")

    # --- 6. CONFIGURATION DIFF TABLE ---
    st.divider()
    st.subheader("Configuration Comparison")
    
    keys_to_compare = [
        ("Model", "model_name"),
        ("Temperature", "temperature"),
        ("Max Tokens", "max_tokens"),
        ("Top P", "top_p"),
        ("Dataset", "dataset_name"),
        ("Edit Method", "edit_method")
    ]
    
    diff_data = []
    for label, key in keys_to_compare:
        val_a = test_a.config.get(key, "N/A")
        val_b = test_b.config.get(key, "N/A")
        is_diff = val_a != val_b
        status_icon = "⚠️ Changed" if is_diff else "✅ Same"
        diff_data.append({
            "Setting": label,
            f"{test_a.name} (A)": str(val_a),
            "Diff Status": status_icon,
            f"{test_b.name} (B)": str(val_b),
        })
        
    st.dataframe(pd.DataFrame(diff_data), hide_index=True, use_container_width=True)
    
    with st.expander("View Raw Config JSONs"):
        c_json_a, c_json_b = st.columns(2)
        c_json_a.json(test_a.config)
        c_json_b.json(test_b.config)


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
                 # create llm
                 st.session_state.llm = GenerateEmail(test.config.get('model_name', 'gpt-4.1'))
                 run_test_logic(test) # Execution logic
                 st.rerun()
                 
    else:
        st.error("Test not found.")
    
    st.stop()
elif st.session_state.page == "compare_menu":
    # Top Navigation
    c_back, c_title = st.columns([1, 5])
    if c_back.button("← Back", use_container_width=True):
        st.session_state.page = "dashboard"
        st.rerun()
    c_title.title("⚔️ Compare Runs")

    # --- SELECTION LOGIC ---
    # Try to grab tests from 'selected_ids' first
    available_tests = st.session_state.tests
    selected_list = list(st.session_state.selected_ids)
    
    idx_a, idx_b = 0, 1 if len(available_tests) > 1 else 0
    
    # If exactly 2 were selected in the dashboard, pre-select them
    if len(selected_list) == 2:
        # Find the indices in the main list
        id_a, id_b = selected_list[0], selected_list[1]
        # Helper to find index by ID
        for i, t in enumerate(available_tests):
            if t.test_id == id_a: idx_a = i
            if t.test_id == id_b: idx_b = i
    
    # Controls to swap comparison
    with st.container(border=True):
        sel_col1, sel_col2 = st.columns(2)
        
        with sel_col1:
            test_a_ref = st.selectbox(
                "Select Baseline (Test A)", 
                available_tests, 
                format_func=lambda x: f"{x.name} (ID: {x.test_id})",
                index=idx_a,
                key="comp_select_a"
            )
            
        with sel_col2:
            test_b_ref = st.selectbox(
                "Select Comparison (Test B)", 
                available_tests, 
                format_func=lambda x: f"{x.name} (ID: {x.test_id})",
                index=idx_b,
                key="comp_select_b"
            )

    if test_a_ref and test_b_ref:
        if test_a_ref.test_id == test_b_ref.test_id:
            st.warning("⚠️ You are comparing the same test instance to itself.")
        
        # --- RENDER THE COMPARISON UI ---
        render_compare_menu_ui(test_a_ref, test_b_ref)
        
    else:
        st.error("Please ensure you have at least two tests created to use this feature.")

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
if f5.container(horizontal_alignment='right').button("Compare"): # open compare menu
    st.session_state.page = "compare_menu"
    st.rerun()

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

# st.write(st.session_state)
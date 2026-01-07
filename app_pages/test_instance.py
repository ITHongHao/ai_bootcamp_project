import streamlit as st
import uuid
from datetime import datetime
import pandas as pd

class TestInstance:
    def __init__(self, test_id, name, description, status="Pending", last_run=None, config=None, results=None, latency=0, error_rate=0.0):
        self.test_id = str(test_id)
        self.name = name
        self.description = description
        self.status = status
        self.last_run = last_run
        
        # Configuration Dictionary
        self.config = config if config else {}
        
        # Results Storage
        self.results = results if results else []

        # Metrics Storage
        self.latency = latency
        self.error_rate = error_rate # ✅ New: Error Rate Tracking

    def to_dict(self):
        """Serializes the object to a dictionary for JSON export."""
        return {
            "test_id": self.test_id,
            "name": self.name,
            "description": self.description,
            "status": self.status,
            "last_run": self.last_run,
            "config": self.config,
            "results": self.results,
            "latency": self.latency,
            "error_rate": self.error_rate # ✅ Save error rate
        }

    @classmethod
    def from_dict(cls, data):
        """Creates a TestInstance from a dictionary."""
        t_id = data.get("test_id", str(uuid.uuid4())[:8])
        
        return cls(
            test_id=t_id,
            name=data.get("name", "Untitled Test"),
            description=data.get("description", ""),
            status=data.get("status", "Pending"),
            last_run=data.get("last_run", None),
            config=data.get("config", None),
            results=data.get("results", None),
            latency=data.get("latency", 0),
            error_rate=data.get("error_rate", 0.0) # ✅ Load error rate
        )

    def save_run_data(self, df_results):
        """
        Helper to save a Pandas DataFrame or list of dicts as results.
        Automatically updates 'last_run', 'status', 'latency', and 'error_rate'.
        """
        # 1. Convert DataFrame to list of records
        if isinstance(df_results, pd.DataFrame):
            self.results = df_results.to_dict('records')
        elif isinstance(df_results, list):
            self.results = df_results
        
        # 2. Update Timestamp
        self.last_run = datetime.now().strftime("%Y-%m-%d")
        
        if self.results:
            total_rows = len(self.results)
            
            # --- NEW: Calculate Error Rate ---
            # Count how many rows have Status == "Error"
            error_count = sum(1 for row in self.results if row.get("Status") == "Error")
            self.error_rate = (error_count / total_rows) * 100 if total_rows > 0 else 0.0

            # --- Status Logic ---
            # If > 0 errors, we can mark the whole test as "Failed" or "Completed with Errors"
            # For strictness, if any row failed logic (Status="Failed") or crashed (Status="Error"), the run "Failed".
            has_issues = any(row.get("Status") in ["Failed", "Error"] for row in self.results)
            self.status = "Failed" if has_issues else "Passed"
            
            # --- Sum Total Latency ---
            total_ms = sum(row.get("Latency (ms)", 0) for row in self.results)
            self.latency = total_ms
        else:
            self.status = "Completed"
            self.latency = 0
            self.error_rate = 0.0

    def render(self, selection_enabled=False):
        """
        Renders the instance card.
        """
        action = None
        
        if "selected_ids" not in st.session_state:
            st.session_state.selected_ids = set()
            
        is_selected = self.test_id in st.session_state.selected_ids

        # Status Styling
        status_colors = {
            "Passed": "green", "Failed": "red",
            "Pending": "gray", "Running": "blue", "Completed": "blue"
        }
        color = status_colors.get(self.status, "gray")
        icon_map = {"Passed": "✅", "Failed": "🚨", "Pending": "⏳", "Running": "🏃"}
        icon = icon_map.get(self.status, "⚪")

        title_prefix = "✅ " if (selection_enabled and is_selected) else ""
        
        with st.container(border=True):
            # Header
            c1, c2 = st.columns([0.7, 0.3])
            with c1:
                st.subheader(f"{title_prefix}{self.name}")
            with c2:
                st.markdown(f"<div style='text-align: right; color: {color};'><b>{icon} {self.status}</b></div>", unsafe_allow_html=True)
            
            # Body
            st.caption(f"ID: {self.test_id} • Last Run: {self.last_run or 'Never'}")
            st.write(self.description)
            
            # Show Metrics on Card if available
            if self.latency > 0 or self.error_rate > 0:
                m1, m2 = st.columns(2)
                m1.caption(f"⏱️ {self.latency}ms")
                if self.error_rate > 0:
                    m2.caption(f"⚠️ {self.error_rate:.1f}% Err")

            st.divider()

            # Interaction
            if selection_enabled:
                btn_label = "✅ Selected" if is_selected else "Select Item"
                btn_type = "primary" if is_selected else "secondary"
                if st.button(btn_label, key=f"sel_toggle_{self.test_id}", type=btn_type, use_container_width=True):
                    if is_selected:
                        st.session_state.selected_ids.remove(self.test_id)
                    else:
                        st.session_state.selected_ids.add(self.test_id)
                    st.rerun()
            else:
                f1, f2, f3 = st.columns([1, 1, 1])
                if f1.button("Details", key=f"det_{self.test_id}", use_container_width=True):
                    action = "details"
                if f2.button("Run", key=f"run_{self.test_id}", use_container_width=True):
                    action = "run"
                with f3:
                    with st.popover("More", use_container_width=True):
                        if st.button("Edit", key=f"ed_{self.test_id}", use_container_width=True):
                            action = "edit"
                        if st.button("Delete", key=f"del_{self.test_id}", type="primary", use_container_width=True):
                            action = "delete"

        return action
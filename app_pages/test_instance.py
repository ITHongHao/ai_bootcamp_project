# import streamlit as st

# class TestInstance:
#     def __init__(self, test_id, name, description, status="Pending", last_run=None):
#         self.test_id = str(test_id)
#         self.name = name
#         self.description = description
#         self.status = status
#         self.last_run = last_run

#     def render(self, selection_enabled=False):
#         """
#         Renders the instance card.
#         - selection_enabled=False: Standard view with action buttons.
#         - selection_enabled=True: Same visuals, but footer becomes a selection toggle.
#         """
        
#         # --- 1. SETUP STATE & COLORS ---
#         if "selected_ids" not in st.session_state:
#             st.session_state.selected_ids = set()
            
#         is_selected = self.test_id in st.session_state.selected_ids

#         # Status Styling
#         status_colors = {
#             "Passed": "green", "Failed": "red",
#             "Pending": "gray", "Running": "blue"
#         }
#         color = status_colors.get(self.status, "gray")
#         icon_map = {"Passed": "✅", "Failed": "🚨", "Pending": "⏳", "Running": "🏃"}
#         icon = icon_map.get(self.status, "⚪")

#         # --- 2. VISUAL FEEDBACK FOR SELECTION ---
#         # If selected, we can't easily change the border color of st.container natively,
#         # so we use a visual marker in the title or background.
#         title_prefix = "✅ " if (selection_enabled and is_selected) else ""
        
#         # --- 3. RENDER CONTAINER (The Card) ---
#         # We use the same container structure for BOTH modes to preserve visuals.
#         with st.container(border=True):
            
#             # --- HEADER ROW (Title & Status) ---
#             c1, c2 = st.columns([0.7, 0.3])
#             with c1:
#                 # The title stays essentially the same
#                 st.subheader(f"{title_prefix}{self.name}")
#             with c2:
#                 # The status badge stays visually identical
#                 st.markdown(f"<div style='text-align: right; color: {color};'><b>{icon} {self.status}</b></div>", unsafe_allow_html=True)
            
#             # --- BODY CONTENT ---
#             st.caption(f"ID: {self.test_id} • Last Run: {self.last_run or 'Never'}")
#             st.write(self.description)
            
#             st.divider()

#             # --- 4. INTERACTION AREA (Footer) ---
#             # This is where we swap behavior based on the mode.
            
#             if selection_enabled:
#                 # --- SELECT MODE ---
#                 # We replace specific actions with a big "Toggle Selection" area.
#                 # Since we can't make the *container* clickable, we make the *entire footer* a button.
                
#                 # Visual logic for the button
#                 btn_label = "✅ Selected" if is_selected else "Select Item"
#                 btn_type = "primary" if is_selected else "secondary"
                
#                 # This button spans the full width, making it an easy click target
#                 if st.button(btn_label, key=f"sel_toggle_{self.test_id}", type=btn_type, use_container_width=True):
#                     if is_selected:
#                         st.session_state.selected_ids.remove(self.test_id)
#                     else:
#                         st.session_state.selected_ids.add(self.test_id)
#                     st.rerun()
                    
#             else:
#                 # --- NORMAL MODE ---
#                 # Your standard action buttons
#                 f1, f2, f3 = st.columns([1, 1, 1])
#                 with f1:
#                     st.button("Details", key=f"det_{self.test_id}", use_container_width=True)
#                 with f2:
#                     st.button("Run", key=f"run_{self.test_id}", use_container_width=True)
#                 with f3:
#                     with st.popover("More", use_container_width=True):
#                         st.button("Edit", key=f"ed_{self.test_id}")
#                         st.button("Delete", key=f"del_{self.test_id}", type="primary")




# ============================================

# import streamlit as st

# class TestInstance:
#     def __init__(self, test_id, name, description, status="Pending", last_run=None):
#         self.test_id = str(test_id)
#         self.name = name
#         self.description = description
#         self.status = status
#         self.last_run = last_run

#     def render(self, selection_enabled=False):
#         """
#         Renders the instance card.
#         Returns a string indicating the action taken: None, 'run', 'details', 'edit', 'delete'
#         """
#         action = None
        
#         # --- 1. SETUP STATE & COLORS ---
#         if "selected_ids" not in st.session_state:
#             st.session_state.selected_ids = set()
            
#         is_selected = self.test_id in st.session_state.selected_ids

#         # Status Styling
#         status_colors = {
#             "Passed": "green", "Failed": "red",
#             "Pending": "gray", "Running": "blue"
#         }
#         color = status_colors.get(self.status, "gray")
#         icon_map = {"Passed": "✅", "Failed": "🚨", "Pending": "⏳", "Running": "🏃"}
#         icon = icon_map.get(self.status, "⚪")

#         title_prefix = "✅ " if (selection_enabled and is_selected) else ""
        
#         # --- 2. RENDER CONTAINER ---
#         with st.container(border=True):
            
#             # Header
#             c1, c2 = st.columns([0.7, 0.3])
#             with c1:
#                 st.subheader(f"{title_prefix}{self.name}")
#             with c2:
#                 st.markdown(f"<div style='text-align: right; color: {color};'><b>{icon} {self.status}</b></div>", unsafe_allow_html=True)
            
#             # Body
#             st.caption(f"ID: {self.test_id} • Last Run: {self.last_run or 'Never'}")
#             st.write(self.description)
            
#             st.divider()

#             # --- 3. INTERACTION AREA ---
#             if selection_enabled:
#                 # SELECT MODE
#                 btn_label = "✅ Selected" if is_selected else "Select Item"
#                 btn_type = "primary" if is_selected else "secondary"
                
#                 if st.button(btn_label, key=f"sel_toggle_{self.test_id}", type=btn_type, use_container_width=True):
#                     if is_selected:
#                         st.session_state.selected_ids.remove(self.test_id)
#                     else:
#                         st.session_state.selected_ids.add(self.test_id)
#                     st.rerun()
#             else:
#                 # NORMAL MODE (Action Buttons)
#                 f1, f2, f3 = st.columns([1, 1, 1])
                
#                 # Check buttons and set return action
#                 if f1.button("Details", key=f"det_{self.test_id}", use_container_width=True):
#                     action = "details"
                
#                 if f2.button("Run", key=f"run_{self.test_id}", use_container_width=True):
#                     action = "run"
                
#                 with f3:
#                     with st.popover("More", use_container_width=True):
#                         if st.button("Edit", key=f"ed_{self.test_id}", use_container_width=True):
#                             action = "edit"
#                         if st.button("Delete", key=f"del_{self.test_id}", type="primary", use_container_width=True):
#                             action = "delete"

#         return action



# ============================================


# import streamlit as st
# import uuid

# class TestInstance:
#     def __init__(self, test_id, name, description, status="Pending", last_run=None):
#         self.test_id = str(test_id)
#         self.name = name
#         self.description = description
#         self.status = status
#         self.last_run = last_run

#     def to_dict(self):
#         """Serializes the object to a dictionary for JSON export."""
#         return {
#             "test_id": self.test_id,
#             "name": self.name,
#             "description": self.description,
#             "status": self.status,
#             "last_run": self.last_run
#         }

#     @classmethod
#     def from_dict(cls, data):
#         """Creates a TestInstance from a dictionary. Generates a new ID if one isn't safe."""
#         # We generate a new ID on import to avoid conflicts with existing tests
#         # unless you specifically want to overwrite/update (which requires more logic).
#         new_id = str(uuid.uuid4())[:8] 
        
#         return cls(
#             test_id=new_id,
#             name=data.get("name", "Untitled Test"),
#             description=data.get("description", ""),
#             status=data.get("status", "Pending"),
#             last_run=data.get("last_run", None)
#         )

#     def render(self, selection_enabled=False):
#         """
#         Renders the instance card.
#         Returns: None, 'run', 'details', 'edit', 'delete'
#         """
#         action = None
        
#         if "selected_ids" not in st.session_state:
#             st.session_state.selected_ids = set()
            
#         is_selected = self.test_id in st.session_state.selected_ids

#         # Status Styling
#         status_colors = {
#             "Passed": "green", "Failed": "red",
#             "Pending": "gray", "Running": "blue"
#         }
#         color = status_colors.get(self.status, "gray")
#         icon_map = {"Passed": "✅", "Failed": "🚨", "Pending": "⏳", "Running": "🏃"}
#         icon = icon_map.get(self.status, "⚪")

#         title_prefix = "✅ " if (selection_enabled and is_selected) else ""
        
#         with st.container(border=True):
#             # Header
#             c1, c2 = st.columns([0.7, 0.3])
#             with c1:
#                 st.subheader(f"{title_prefix}{self.name}")
#             with c2:
#                 st.markdown(f"<div style='text-align: right; color: {color};'><b>{icon} {self.status}</b></div>", unsafe_allow_html=True)
            
#             # Body
#             st.caption(f"ID: {self.test_id} • Last Run: {self.last_run or 'Never'}")
#             st.write(self.description)
            
#             st.divider()

#             # Interaction
#             if selection_enabled:
#                 btn_label = "✅ Selected" if is_selected else "Select Item"
#                 btn_type = "primary" if is_selected else "secondary"
#                 if st.button(btn_label, key=f"sel_toggle_{self.test_id}", type=btn_type, use_container_width=True):
#                     if is_selected:
#                         st.session_state.selected_ids.remove(self.test_id)
#                     else:
#                         st.session_state.selected_ids.add(self.test_id)
#                     st.rerun()
#             else:
#                 f1, f2, f3 = st.columns([1, 1, 1])
#                 if f1.button("Details", key=f"det_{self.test_id}", use_container_width=True):
#                     action = "details"
#                 if f2.button("Run", key=f"run_{self.test_id}", use_container_width=True):
#                     action = "run"
#                 with f3:
#                     with st.popover("More", use_container_width=True):
#                         if st.button("Edit", key=f"ed_{self.test_id}", use_container_width=True):
#                             action = "edit"
#                         if st.button("Delete", key=f"del_{self.test_id}", type="primary", use_container_width=True):
#                             action = "delete"

#         return action



import streamlit as st
import uuid

class TestInstance:
    def __init__(self, test_id, name, description, status="Pending", last_run=None, config=None):
        self.test_id = str(test_id)
        self.name = name
        self.description = description
        self.status = status
        self.last_run = last_run
        
        # --- NEW: Configuration Dictionary ---
        # Holds all the settings for the LLM and the test strategy
        self.config = config if config else {
            "model": "gpt-4o",
            "temperature": 0.7,
            "max_tokens": 500,
            "system_prompt": "You are a professional email assistant.",
            "dataset": "Default Sample Set",
            "task_type": "Rewrite"
        }

    def to_dict(self):
        """Serializes the object to a dictionary for JSON export."""
        return {
            "test_id": self.test_id,
            "name": self.name,
            "description": self.description,
            "status": self.status,
            "last_run": self.last_run,
            "config": self.config  # ✅ Save the config
        }

    @classmethod
    def from_dict(cls, data):
        """Creates a TestInstance from a dictionary."""
        # Use existing ID if importing, or generate new one if creating fresh
        # (You can change this logic if you want to force new IDs on import)
        t_id = data.get("test_id", str(uuid.uuid4())[:8])
        
        return cls(
            test_id=t_id,
            name=data.get("name", "Untitled Test"),
            description=data.get("description", ""),
            status=data.get("status", "Pending"),
            last_run=data.get("last_run", None),
            config=data.get("config", None)  # ✅ Load the config
        )

    def render(self, selection_enabled=False):
        """
        Renders the instance card.
        Returns: None, 'run', 'details', 'edit', 'delete'
        """
        action = None
        
        if "selected_ids" not in st.session_state:
            st.session_state.selected_ids = set()
            
        is_selected = self.test_id in st.session_state.selected_ids

        # Status Styling
        status_colors = {
            "Passed": "green", "Failed": "red",
            "Pending": "gray", "Running": "blue"
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
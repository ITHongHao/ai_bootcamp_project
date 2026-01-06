# import streamlit as st

# class TestInstance:
#     def __init__(self, test_id, name, description, status="Pending", last_run=None):
#         self.test_id = str(test_id)  # Using strings to match your dataset keys
#         self.name = name
#         self.description = description
#         self.status = status  # e.g., "Passed", "Failed", "Pending", "Running"
#         self.last_run = last_run

#     def render(self):
#         """Renders the instance as a card-like UI component."""
#         # Define color based on status
#         status_colors = {
#             "Passed": "green",
#             "Failed": "red",
#             "Pending": "gray",
#             "Running": "blue"
#         }
#         color = status_colors.get(self.status, "gray")

#         # Create a container with a border to act as the "card"
#         with st.container(border=True):
#             col1, col2 = st.columns([3, 1])
            
#             with col1:
#                 st.markdown(f"### {self.name}")
#                 st.caption(f"ID: {self.test_id} | Last Run: {self.last_run or 'Never'}")
#                 st.write(self.description)
            
#             with col2:
#                 # Display status badge
#                 st.markdown(f":{color}[{self.status}]")
                
#                 # Main Click Action (Navigation)
#                 if st.button("Open Details", key=f"btn_{self.test_id}", use_container_width=True):
#                     st.session_state.selected_test = self.test_id
#                     st.switch_page("pages/test_details.py")
                
#                 # Right-click 'Simulated' Menu using Popover
#                 with st.popover("⚙️", help="Options", use_container_width=True):
#                     st.button("Run Test", key=f"run_{self.test_id}")
#                     st.button("Edit Config", key=f"edit_{self.test_id}")
#                     st.button("Export", key=f"exp_{self.test_id}")
#                     st.button("Delete", key=f"del_{self.test_id}", type="primary")
import streamlit as st

class TestInstance:
    def __init__(self, test_id, name, description, status="Pending", last_run=None):
        self.test_id = str(test_id)
        self.name = name
        self.description = description
        self.status = status
        self.last_run = last_run

    def render(self, selection_enabled=False):
        """
        Renders the instance card.
        - selection_enabled=False: Standard view with action buttons.
        - selection_enabled=True: Same visuals, but footer becomes a selection toggle.
        """
        
        # --- 1. SETUP STATE & COLORS ---
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

        # --- 2. VISUAL FEEDBACK FOR SELECTION ---
        # If selected, we can't easily change the border color of st.container natively,
        # so we use a visual marker in the title or background.
        title_prefix = "✅ " if (selection_enabled and is_selected) else ""
        
        # --- 3. RENDER CONTAINER (The Card) ---
        # We use the same container structure for BOTH modes to preserve visuals.
        with st.container(border=True):
            
            # --- HEADER ROW (Title & Status) ---
            c1, c2 = st.columns([0.7, 0.3])
            with c1:
                # The title stays essentially the same
                st.subheader(f"{title_prefix}{self.name}")
            with c2:
                # The status badge stays visually identical
                st.markdown(f"<div style='text-align: right; color: {color};'><b>{icon} {self.status}</b></div>", unsafe_allow_html=True)
            
            # --- BODY CONTENT ---
            st.caption(f"ID: {self.test_id} • Last Run: {self.last_run or 'Never'}")
            st.write(self.description)
            
            st.divider()

            # --- 4. INTERACTION AREA (Footer) ---
            # This is where we swap behavior based on the mode.
            
            if selection_enabled:
                # --- SELECT MODE ---
                # We replace specific actions with a big "Toggle Selection" area.
                # Since we can't make the *container* clickable, we make the *entire footer* a button.
                
                # Visual logic for the button
                btn_label = "✅ Selected" if is_selected else "Select Item"
                btn_type = "primary" if is_selected else "secondary"
                
                # This button spans the full width, making it an easy click target
                if st.button(btn_label, key=f"sel_toggle_{self.test_id}", type=btn_type, use_container_width=True):
                    if is_selected:
                        st.session_state.selected_ids.remove(self.test_id)
                    else:
                        st.session_state.selected_ids.add(self.test_id)
                    st.rerun()
                    
            else:
                # --- NORMAL MODE ---
                # Your standard action buttons
                f1, f2, f3 = st.columns([1, 1, 1])
                with f1:
                    st.button("Details", key=f"det_{self.test_id}", use_container_width=True)
                with f2:
                    st.button("Run", key=f"run_{self.test_id}", use_container_width=True)
                with f3:
                    with st.popover("More", use_container_width=True):
                        st.button("Edit", key=f"ed_{self.test_id}")
                        st.button("Delete", key=f"del_{self.test_id}", type="primary")
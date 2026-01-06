import streamlit as st
import pandas as pd
import plotly.express as px
import random

# --- 1. SYNTHETIC DATA GENERATION ---
def generate_synthetic_data(count=12):
    """Generates a dictionary of synthetic email evaluations."""
    explanations = [
        "Excellent tone and professional structure.",
        "Slight hallucination regarding the meeting dates.",
        "Too wordy; needs to be more concise for a mobile view.",
        "Perfectly addressed all user requirements.",
        "Failed to use the correct sign-off requested in prompt.",
        "The response was polite but missed the technical attachment reference.",
        "Greeting was missing, but the core content was accurate.",
        "Used aggressive language not suited for customer support."
    ]
    
    dataset = {}
    for i in range(1, count + 1):
        dataset[str(i)] = {
            "email_id": f"EML-{1000 + i}",
            "rating": random.randint(1, 5),
            "explanation": random.choice(explanations),
            "category": random.choice(["Support", "Sales", "Internal"]),
            "latency_sec": round(random.uniform(0.5, 2.5), 2)
        }
    return dataset

# Initialize state
if "eval_data" not in st.session_state:
    st.session_state.eval_data = generate_synthetic_data()

# --- 2. DATA PROCESSING ---
df = pd.DataFrame.from_dict(st.session_state.eval_data, orient='index')

# --- 3. UI DISPLAY ---
st.set_page_config(layout="wide", page_title="Evaluation Mockup")
st.title("📊 Email Generation Evaluation Suite")

# Documentation Link (as discussed)
st.info("Refer to the [Azure OpenAI API Reference](https://learn.microsoft.com/en-us/azure/ai-foundry/openai/reference?view=foundry-classic#chat-completions) for parameter definitions.")

# --- TOP ROW: KPI METRICS ---
m1, m2, m3, m4 = st.columns(4)
m1.metric("Total Emails", len(df))
m2.metric("Avg Rating", f"{df['rating'].mean():.2f} ⭐")
m3.metric("Avg Latency", f"{df['latency_sec'].mean():.2f}s")
m4.metric("Failure Rate", f"{(df['rating'] <= 2).sum() / len(df) * 100:.1f}%", delta_color="inverse")

st.divider()

# --- MAIN SECTION: ANALYTICS & CARDS ---
left_col, right_col = st.columns([0.6, 0.4])

with left_col:
    st.subheader("Performance Analytics")
    tab1, tab2 = st.tabs(["Visualization", "Data Grid"])
    
    with tab1:
        # Interactive Scatter Plot for "All metrics in one spot"
        fig = px.scatter(
            df, 
            x="latency_sec", 
            y="rating", 
            color="rating",
            size="rating",
            hover_name="email_id",
            hover_data={"explanation": True, "latency_sec": True, "rating": True},
            title="Rating vs. Latency (Hover for Details)",
            color_continuous_scale="RdYlGn"
        )
        st.plotly_chart(fig, use_container_width=True)
        
        # Distribution Histogram
        fig2 = px.histogram(df, x="rating", nbins=5, title="Count of Ratings")
        st.plotly_chart(fig2, use_container_width=True)

    with tab2:
        # Interactive Table with Progress Bars
        st.data_editor(
            df,
            column_config={
                "rating": st.column_config.ProgressColumn("Rating", min_value=1, max_value=5, format="%d"),
                "latency_sec": st.column_config.NumberColumn("Latency", format="%.2f s"),
                "explanation": st.column_config.TextColumn("Explanation", width="large")
            },
            use_container_width=True,
            hide_index=True
        )

with right_col:
    st.subheader("Instance Review")
    search = st.text_input("Filter by ID", placeholder="Search...")
    
    # Scrollable-style container for the "Rectangular Objects"
    card_container = st.container(height=600)
    with card_container:
        for idx, row in df.iterrows():
            if search.lower() in row["email_id"].lower():
                # This is the "Rectangle Object" implementation
                with st.container(border=True):
                    c1, c2 = st.columns([0.8, 0.2])
                    with c1:
                        st.markdown(f"**{row['email_id']}**")
                        st.caption(f"Category: {row['category']}")
                        st.write(f"Rating: {'⭐' * row['rating']}")
                    with c2:
                        # "Right-click" alternative: Popover
                        with st.popover("⚙️"):
                            if st.button("View Full Log", key=f"view_{idx}"):
                                st.toast(f"Loading {row['email_id']} logs...")
                            st.button("Flag Item", key=f"flag_{idx}")
                            st.button("Delete", key=f"del_{idx}")
                    
                    # Clicking the card content simulation
                    with st.expander("See Explanation"):
                        st.write(row['explanation'])
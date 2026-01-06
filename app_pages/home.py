import streamlit as st
import pandas as pd
import plotly.graph_objects as go
import plotly.express as px

def render_evaluation_page():
    # --- 1. EXPANDED MOCK DATA (10 Metrics) ---
    # Added 'category' to organize the 10 metrics
    eval_data = {
        "overall_score": 3.8,
        "status": "Review Needed",
        "guardrails": [
            {"name": "Faithfulness", "status": "Pass", "reasoning": "No hallucinations detected."},
            {"name": "PII Safety", "status": "Pass", "reasoning": "Clean of sensitive data."},
            {"name": "Toxicity", "status": "Pass", "reasoning": "No toxic language detected."}
        ],
        "metrics": [
            {"name": "Conciseness", "score": 5, "cat": "Structure", "reasoning": "Very direct.", "prompt": "Rate conciseness 1-5."},
            {"name": "Grammar", "score": 5, "cat": "Structure", "reasoning": "No errors found.", "prompt": "Check for grammatical errors."},
            {"name": "Formatting", "score": 4, "cat": "Structure", "reasoning": "Good use of spacing, but bullet points could help.", "prompt": "Rate visual formatting."},
            
            {"name": "Tone Consistency", "score": 4, "cat": "Tone", "reasoning": "Mostly professional.", "prompt": "Rate tone consistency."},
            {"name": "Empathy", "score": 2, "cat": "Tone", "reasoning": "Sounded slightly robotic in the opening.", "prompt": "Rate empathy 1-5."},
            {"name": "Politeness", "score": 5, "cat": "Tone", "reasoning": "Very polite usage of 'Please' and 'Thank you'.", "prompt": "Rate politeness."},
            
            {"name": "Actionability", "score": 3, "cat": "Content", "reasoning": "Call to action was vague.", "prompt": "Does it have clear next steps?"},
            {"name": "Relevance", "score": 5, "cat": "Content", "reasoning": "Directly answers the prompt.", "prompt": "Rate relevance to query."},
            {"name": "Completeness", "score": 4, "cat": "Content", "reasoning": "Covered 3 of 4 user questions.", "prompt": "Check if all questions were answered."},
            
            {"name": "Brand Voice", "score": 2, "cat": "Custom", "reasoning": "Failed to use the slogan.", "prompt": "Check for brand slogan usage."}
        ]
    }

    st.markdown("## ⚖️ Evaluation Results")

    # --- 2. HEADER: HIGH-LEVEL HEALTH ---
    top_c1, top_c2, top_c3 = st.columns([1, 1, 2])
    with top_c1:
        st.metric("Overall Score", f"{eval_data['overall_score']} / 5", delta="-0.4")
    with top_c2:
        # Dynamic Status Badge
        color = "green" if eval_data['overall_score'] >= 4 else "orange" if eval_data['overall_score'] >= 3 else "red"
        st.markdown("**Status**")
        st.markdown(f":{color}-background[{eval_data['status']}]")
    with top_c3:
         # Quick Guardrail Check (Mini indicators)
         st.markdown("**Guardrails**")
         g_cols = st.columns(len(eval_data['guardrails']))
         for i, g in enumerate(eval_data['guardrails']):
             icon = "✅" if g['status'] == "Pass" else "❌"
             g_cols[i].caption(f"{icon} {g['name']}")

    st.divider()

    # --- 3. VISUALIZATION LAYER ---
    col_viz, col_matrix = st.columns([1, 1], gap="medium")

    with col_viz:
        st.subheader("Shape of Quality")
        # Radar Chart for all 10 metrics
        # (We use the categories to color-code or just show one big shape)
        df_metrics = pd.DataFrame(eval_data['metrics'])
        
        fig = px.line_polar(
            df_metrics, 
            r='score', 
            theta='name', 
            line_close=True,
            markers=True,
            range_r=[0,5],
            title=""
        )
        fig.update_traces(fill='toself', line_color='#00CC96')
        fig.update_layout(
            polar=dict(radialaxis=dict(visible=True)),
            margin=dict(t=10, b=10, l=30, r=30),
            height=300,
            paper_bgcolor="rgba(0,0,0,0)",
            plot_bgcolor="rgba(0,0,0,0)",
        )
        st.plotly_chart(fig, use_container_width=True)

    with col_matrix:
        st.subheader("Metric Heatmap")
        st.caption("Quickly spot weak points (Darker = Lower Score)")
        
        # HEATMAP: A modern way to view many metrics at once
        # Reshape data into a 2x5 grid for visualization
        matrix_data = df_metrics.sort_values(by="score", ascending=False)
        
        fig_bar = px.bar(
            matrix_data,
            x="score",
            y="name",
            orientation='h',
            color="score",
            color_continuous_scale="RdYlGn", # Red to Green
            text="score"
        )
        fig_bar.update_layout(
            yaxis={'categoryorder':'total ascending', 'title': ''},
            xaxis={'range': [0, 5.5], 'title': ''},
            height=300,
            margin=dict(t=0, b=0, l=0, r=0),
            coloraxis_showscale=False,
            paper_bgcolor="rgba(0,0,0,0)",
            plot_bgcolor="rgba(0,0,0,0)",
        )
        st.plotly_chart(fig_bar, use_container_width=True)

    st.divider()

    # --- 4. DETAILED INSPECTOR (With Filtering) ---
    st.markdown("### 🔎 Metric Inspector")
    
    # CONTROL BAR
    c_filter, c_sort, c_spacer = st.columns([2, 1, 1])
    
    with c_filter:
        # Category Filter (Pills are great for modern UI)
        categories = ["All"] + list(df_metrics['cat'].unique())
        selected_cat = st.pills("Filter by Category", categories, default="All")
        
    with c_sort:
        sort_order = st.selectbox("Sort by", ["Default", "Score (Low to High)", "Score (High to Low)"], label_visibility="collapsed")

    # LOGIC: Filter and Sort
    filtered_df = df_metrics.copy()
    if selected_cat != "All":
        filtered_df = filtered_df[filtered_df['cat'] == selected_cat]
        
    if sort_order == "Score (Low to High)":
        filtered_df = filtered_df.sort_values(by="score", ascending=True)
    elif sort_order == "Score (High to Low)":
        filtered_df = filtered_df.sort_values(by="score", ascending=False)

    st.write("") # Spacer

    # RENDER CARDS (Grid Layout)
    # Instead of one long list, we use a 2-column grid for the cards
    grid_cols = st.columns(2)
    
    for i, row in enumerate(filtered_df.to_dict('records')):
        col = grid_cols[i % 2]
        
        with col:
            # Color-code the card border based on score
            card_border = "red" if row['score'] <= 2 else "grey"
            
            with st.container(border=True):
                # Header Row
                h1, h2 = st.columns([0.8, 0.2])
                h1.markdown(f"**{row['name']}**")
                
                # Visual Score Indicator
                stars = "⭐" * int(row['score'])
                score_color = "red" if row['score'] <= 2 else "green" if row['score'] >= 4 else "orange"
                h2.markdown(f":{score_color}[**{row['score']}/5**]")
                
                # Body
                st.caption(f"Category: {row['cat']}")
                st.write(row['reasoning'])
                
                # Expandable details to keep card small
                with st.expander("See Prompt & Details"):
                    st.markdown("**Prompt Used:**")
                    st.code(row['prompt'], language="text")
                    if st.button(f"Edit Judge", key=f"btn_{row['name']}"):
                        st.toast(f"Editing {row['name']}...")

if __name__ == "__main__":
    st.set_page_config(layout="wide")
    render_evaluation_page()
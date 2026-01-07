import streamlit as st

def render_homepage():
    # --- CUSTOM CSS FOR TECH-FORWARD LOOK ---
    st.markdown("""
    <style>
        /* Modern Gradient Headings */
        .gradient-text {
            background: -webkit-linear-gradient(45deg, #60a5fa, #c084fc);
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
            font-weight: 800;
        }
        
        /* Feature Cards (Glassmorphism) */
        .tech-card {
            background: rgba(255, 255, 255, 0.05);
            border: 1px solid rgba(255, 255, 255, 0.1);
            border-radius: 12px;
            padding: 20px;
            height: 100%;
            transition: all 0.3s ease;
        }
        .tech-card:hover {
            border-color: #60a5fa;
            transform: translateY(-2px);
            background: rgba(255, 255, 255, 0.08);
        }
        
        /* Metric Badges for the Grid */
        .metric-badge {
            background-color: #0f172a;
            border: 1px solid #334155;
            color: #e2e8f0;
            padding: 4px 12px;
            border-radius: 15px;
            font-size: 0.85rem;
            margin: 2px;
            display: inline-block;
        }
    </style>
    """, unsafe_allow_html=True)

    # --- 1. HERO: THE VALUE PROP ---
    st.markdown("<h1 style='text-align: center; font-size: 4rem;'>The <span class='gradient-text'>Email AI Suite</span></h1>", unsafe_allow_html=True)
    st.markdown("<p style='text-align: center; font-size: 1.2rem; color: #94a3b8; margin-bottom: 2rem;'>The first LLM editor engineered with a 10-point quality assurance framework.</p>", unsafe_allow_html=True)
    
    # Primary CTA centered
    _, c_cta, _ = st.columns([1, 1, 1])
    with c_cta:
        if st.button("✨ Launch Demo Environment", type="primary", use_container_width=True):
             st.session_state.page = "email_suite" # Router logic
             st.rerun()
    
    st.markdown("---")

    # --- 2. FEATURE DEEP DIVE: THE ARCHITECTURE ---
    st.subheader("System Architecture")
    st.caption("A dual-engine platform designed for both End-Users and QA Engineers.")

    col1, col2 = st.columns(2, gap="medium")

    with col1:
        st.markdown("""
        <div class="tech-card">
            <h3 style="color: #60a5fa;">🧠 The Workbench (User)</h3>
            <p style="color: #cbd5e1;">A distraction-free writing environment where LLMs assist with drafting, editing, and tone shifting.</p>
            <ul>
                <li>Real-time Tone Adjustment</li>
                <li>One-click Summarization</li>
                <li>Instant Grammar Correction</li>
            </ul>
        </div>
        """, unsafe_allow_html=True)

    with col2:
        st.markdown("""
        <div class="tech-card">
            <h3 style="color: #c084fc;">🧪 The Testing Lab (Admin)</h3>
            <p style="color: #cbd5e1;">A rigorous testing dashboard to benchmark prompts, compare models, and prevent regression.</p>
            <ul>
                <li>Batch Unit Testing</li>
                <li>Radar Chart Visualizations</li>
                <li>Import/Export Test Cases</li>
            </ul>
        </div>
        """, unsafe_allow_html=True)

    st.write("") # Spacer

    # --- 3. THE GUARDRAILS (METRICS SHOWCASE) ---
    # This is great for a demo to show "Look how robust our checking is"
    st.subheader("🛡️ The 10-Point Judge Framework")
    st.caption("Every generated response is evaluated against these distinct metrics before approval.")

    m1, m2, m3 = st.columns(3)
    
    with m1:
        st.markdown("**Core Quality**")
        st.markdown('<span class="metric-badge">Faithfulness</span>', unsafe_allow_html=True)
        st.markdown('<span class="metric-badge">Relevance</span>', unsafe_allow_html=True)
        st.markdown('<span class="metric-badge">Completeness</span>', unsafe_allow_html=True)
        
    with m2:
        st.markdown("**Style & Voice**")
        st.markdown('<span class="metric-badge">Tone Consistency</span>', unsafe_allow_html=True)
        st.markdown('<span class="metric-badge">Conciseness</span>', unsafe_allow_html=True)
        st.markdown('<span class="metric-badge">Politeness</span>', unsafe_allow_html=True)
        st.markdown('<span class="metric-badge">Empathy</span>', unsafe_allow_html=True)

    with m3:
        st.markdown("**Safety & Format**")
        st.markdown('<span class="metric-badge">PII Safety</span>', unsafe_allow_html=True)
        st.markdown('<span class="metric-badge">Toxicity</span>', unsafe_allow_html=True)
        st.markdown('<span class="metric-badge">Formatting</span>', unsafe_allow_html=True)

    st.write("") # Spacer
    st.markdown("---")

    # --- 4. WORKFLOW VISUALIZATION ---
    st.subheader("🔁 Continuous Improvement Loop")
    
    # Using Streamlit columns to create a "Step-by-Step" flow
    w1, w2, w3, w4, w5 = st.columns([1, 0.2, 1, 0.2, 1])
    
    with w1:
        st.image("https://img.icons8.com/ios/100/ffffff/email-open.png", width=60)
        st.markdown("**1. Draft**")
        st.caption("User drafts an email or selects a reply.")
    
    with w2:
        st.markdown("<h2 style='text-align: center; padding-top: 20px;'>→</h2>", unsafe_allow_html=True)

    with w3:
        st.image("https://img.icons8.com/ios/100/ffffff/artificial-intelligence.png", width=60)
        st.markdown("**2. Optimize**")
        st.caption("LLM rewrites text while Judge metrics score it.")

    with w4:
         st.markdown("<h2 style='text-align: center; padding-top: 20px;'>→</h2>", unsafe_allow_html=True)

    with w5:
        st.image("https://img.icons8.com/ios/100/ffffff/combo-chart.png", width=60)
        st.markdown("**3. Analyze**")
        st.caption("Admins review low scores in the Lab to fix prompts.")

    # --- 5. FOOTER / NAVIGATION ---
    st.markdown("---")
    f_col1, f_col2 = st.columns([4, 1])
    with f_col1:
         st.caption("System Status: 🟢 All Systems Operational | Model: GPT-4o")
    with f_col2:
        if st.button("Enter Dashboard →"):
            st.session_state.page = "dashboard"
            st.rerun()

if __name__ == "__main__":
    st.set_page_config(layout="wide")
    render_homepage()
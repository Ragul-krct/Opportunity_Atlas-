import streamlit as st
import pandas as pd
import numpy as np
import os
import json

# Setup page configuration
st.set_page_config(
    page_title="OpportunityOS | NexaMind Challenge 2026",
    page_icon="🎯",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom Styling
st.markdown("""
<style>
    .main-title {
        font-size: 2.8rem;
        font-weight: 800;
        background: linear-gradient(135deg, #FF6B6B 0%, #4D96FF 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        margin-bottom: 0.2rem;
    }
    .motto {
        font-size: 1.1rem;
        font-style: italic;
        color: #6b7280;
        margin-bottom: 2rem;
    }
    .card {
        padding: 1.5rem;
        background-color: #f8fafc;
        border-radius: 12px;
        border: 1px solid #e2e8f0;
        margin-bottom: 1rem;
    }
    .metric-title {
        font-size: 0.9rem;
        color: #475569;
        font-weight: 600;
    }
    .metric-value {
        font-size: 1.8rem;
        font-weight: 700;
        color: #1e293b;
    }
</style>
""", unsafe_allow_html=True)

# Try importing components
try:
    import plotly.graph_objects as go
    import plotly.express as px
    has_plotly = True
except ImportError:
    has_plotly = False

try:
    from google import genai
    from google.genai import types
    has_gemini = True
except ImportError:
    has_gemini = False

# Initialize Gemini Client if available
api_key = os.environ.get("GEMINI_API_KEY", "")
client = None
if has_gemini and api_key:
    try:
        client = genai.Client(api_key=api_key)
    except Exception as e:
        client = None

# Load dataset
@st.cache_data
def load_opportunities():
    if os.path.exists("opportunities.csv"):
        return pd.read_csv("opportunities.csv")
    else:
        # Fallback empty dataframe with schema
        return pd.DataFrame(columns=[
            "Opportunity Name", "Category", "Provider", "Description", 
            "Priority Level", "Action To Take", "Minimum CGPA", 
            "Eligible Degrees", "Eligible Countries", "Min Age", "Max Age", 
            "Primary Skills", "Interests"
        ])

df_opps = load_opportunities()

# ----------------- SIDEBAR -----------------
st.sidebar.image("https://images.unsplash.com/photo-1507679799987-c73779587ccf?auto=format&fit=crop&w=300&q=80", use_column_width=True)
st.sidebar.title("🎯 OpportunityOS")
st.sidebar.markdown("**NexaMind Challenge 2026**")
st.sidebar.markdown("*“One missed opportunity can change an entire life.”*")
st.sidebar.divider()

st.sidebar.write("### AI Engine Status")
if api_key:
    st.sidebar.success("🟢 Gemini API is Connected")
else:
    st.sidebar.warning("🟡 Local Mode (Simulated AI)")
    st.sidebar.info("To unlock deep personalized AI synthesis & roadmaps, please set the `GEMINI_API_KEY` environment variable.")

# ----------------- MAIN APP -----------------
st.markdown('<h1 class="main-title">OpportunityOS</h1>', unsafe_allow_html=True)
st.markdown('<p class="motto">“One missed opportunity can change an entire life.” — NexaMind 2026 Innovation Board</p>', unsafe_allow_html=True)

# Create a state variable to hold AI calculations
if 'ai_results' not in st.session_state:
    st.session_state.ai_results = None

# Tabs
tab1, tab2, tab3, tab4 = st.tabs([
    "👤 Module 1: User Profile", 
    "📡 Module 2: Opportunity Radar", 
    "📈 Module 3: Future Comparison", 
    "🗓️ Module 4: One-Year Roadmap"
])

# ------------------ MODULE 1: USER PROFILE ------------------
with tab1:
    st.header("Step 1: Map Your Life Coordinates")
    st.write("Construct your unique candidate vector below so OpportunityOS can align active international grants, hackathons, and programs with your goals.")
    
    col1, col2 = st.columns(2)
    
    with col1:
        age = st.slider("Select Age", min_value=12, max_value=60, value=21, step=1)
        country = st.selectbox(
            "Country of Citizenship", 
            ["United States", "India", "United Kingdom", "Canada", "Singapore", "Japan", "Germany", "Global"]
        )
        degree = st.selectbox(
            "Current Degree Pursuing / Achieved",
            ["High School", "Bachelors", "Masters", "PhD", "Any"]
        )
        cgpa = st.number_input("Current Grade Point Average (CGPA / 10.0 Scale)", min_value=0.0, max_value=10.0, value=9.0, step=0.1)

    with col2:
        skills = st.text_input(
            "Key Skills (Comma separated)", 
            value="Python, TypeScript, React, SQL, Technical Writing"
        )
        interests = st.text_input(
            "Interests & Industries", 
            value="Artificial Intelligence, Product Design, Social Impact"
        )
        career_goal = st.text_area(
            "Primary Career Goal (Describe your 3-5 year aspirations)",
            value="Launch an original AI-driven healthtech venture and help underserved regional clinics optimize diagnostics."
        )

    st.markdown("---")
    
    # Matching algorithm
    if st.button("🔥 Align & Synthesize Opportunities with AI"):
        with st.spinner("Analyzing profile coordinates and querying OpportunityOS space..."):
            # 1. Direct Filtering matching as a backup
            eligible = df_opps.copy()
            
            # Filter CGPA
            eligible = eligible[eligible["Minimum CGPA"] <= cgpa]
            
            # Filter Age
            eligible = eligible[(eligible["Min Age"] <= age) & (age <= eligible["Max Age"])]
            
            # Advanced keyword scoring based on skills/interests
            user_skills_list = [s.strip().lower() for s in skills.split(",")]
            user_interests_list = [i.strip().lower() for i in interests.split(",")]
            
            scores = []
            for idx, row in eligible.iterrows():
                score = 0
                # Match goals/interests
                for skill in user_skills_list:
                    if skill in str(row["Primary Skills"]).lower(): score += 2
                for interest in user_interests_list:
                    if interest in str(row["Interests"]).lower(): score += 3
                
                # Check degree eligibility
                if row["Eligible Degrees"] != "Any" and degree not in str(row["Eligible Degrees"]):
                    score -= 1
                
                # Check country matching
                if row["Eligible Countries"] != "Global" and country not in str(row["Eligible Countries"]):
                    score -= 2
                    
                scores.append((score, row))
            
            # Sort matches
            scores.sort(key=lambda x: x[0], reverse=True)
            top_5 = [item[1] for item in scores[:5]]
            
            # If no matches, fallback to first 5
            if len(top_5) == 0:
                top_5 = [row for _, row in df_opps.head(5).iterrows()]
            
            # Save raw matches
            raw_recommendations = []
            for itm in top_5:
                raw_recommendations.append({
                    "name": itm["Opportunity Name"],
                    "category": itm["Category"],
                    "provider": itm["Provider"],
                    "description": itm["Description"],
                    "priorityLevel": itm["Priority Level"],
                    "actionToTake": itm["Action To Take"]
                })
                
            # If Gemini is live, let's inject custom personalized analysis!
            if client:
                prompt = f"""
                You are a world-class career strategist and Hackathon Judge. Analyze this candidate:
                - Age: {age}
                - Country: {country}
                - Degree: {degree}
                - CGPA: {cgpa}
                - Skills: {skills}
                - Interests: {interests}
                - Career Goal: {career_goal}

                Matches identified from our Opportunities database: {json.dumps(raw_recommendations)}

                Synthesize the data and return a JSON structure with 3 properties:
                1. 'personalized_opportunities': A list of exactly 5 elements matching the structure of 'raw_recommendations'. For each, augment 'whyItIsImportant' (specifically how it impacts their career goals, skills and interests) and keep 'name', 'category', 'priorityLevel', 'actionToTake'.
                2. 'comparison_scenarios': An object detailing:
                   - 'scenario_a' (taking opportunity) and 'scenario_b' (ignoring opportunity).
                   - For each scenario, include absolute numerical scores (out of 100) and short descriptions for definitions:
                     'skillGrowth', 'portfolioGrowth', 'networkingGrowth', 'careerGrowth', 'learningGrowth'.
                3. 'one_year_roadmap': A list of exactly 12 month items, each containing:
                   - 'month': 'Month 1', 'Month 2', etc.
                   - 'goal': Month objective
                   - 'action': Precise practical steps to execute
                   - 'expectedOutcome': Concrete measurable deliverable

                Format your response STRICTLY as a raw JSON string. Do not include ```json blocks or any text other than the JSON object.
                """
                try:
                    response = client.models.generateContent(
                        model="gemini-3.5-flash",
                        contents=prompt,
                    )
                    clean_res = response.text.strip()
                    if clean_res.startswith("```json"):
                        clean_res = clean_res[7:]
                    if clean_res.endswith("```"):
                        clean_res = clean_res[:-3]
                    
                    st.session_state.ai_results = json.loads(clean_res.strip())
                    st.success("🎉 Comprehensive AI alignment generated! Switch to Tabs 2, 3, and 4 to explore your future path.")
                except Exception as e:
                    st.error(f"AI generation encountered an issue: {str(e)}. Proceeding with high-fidelity rule-based local simulation.")
                    st.session_state.ai_results = None
            else:
                # Local Simulation back-up
                simulated_opps = []
                for o in raw_recommendations:
                    simulated_opps.append({
                        "name": o["name"],
                        "category": o["category"],
                        "priorityLevel": o["priorityLevel"],
                        "actionToTake": o["actionToTake"],
                        "whyItIsImportant": f"Directly aligns with your interest in {interests} by providing an active high-status sandbox to apply '{skills}' and advance toward your goal of: '{career_goal}'."
                    })
                
                simulated_comparison = {
                    "scenario_a": {
                        "skillGrowth": {"score": 92, "desc": f"Mastery of high-value tools including {skills} and collaborative product development."},
                        "portfolioGrowth": {"score": 88, "desc": "Addition of a real-world deployed project, code repository, and team pitch case study."},
                        "networkingGrowth": {"score": 90, "desc": f"Direct contact with domain experts, global mentors, and active challengers from NexaMind."},
                        "careerGrowth": {"score": 85, "desc": "Drastic improvement in resume credentialing, proving self-starting drive and elite execution."},
                        "learningGrowth": {"score": 95, "desc": f"Intense pressure-tested learning curves solving real problems in real systems."}
                    },
                    "scenario_b": {
                        "skillGrowth": {"score": 35, "desc": f"Stagnant theoretical classroom learning without hands-on system application."},
                        "portfolioGrowth": {"score": 20, "desc": "Empty profile list lacking proven, pressure-tested engineering artifacts."},
                        "networkingGrowth": {"score": 15, "desc": "Isolated studies, limited completely to existing regional classmates and friends."},
                        "careerGrowth": {"score": 25, "desc": "Conventional applicant path, raising risk of automated filter rejections."},
                        "learningGrowth": {"score": 40, "desc": "Linear progress following standard courses with no direct feedback loops."}
                    }
                }
                
                simulated_roadmap = []
                categories_in_play = [o["category"] for o in simulated_opps]
                for m in range(1, 13):
                    if m <= 3:
                        goal = "Aesthetic Alignment & Environment Setup"
                        action = f"Configure your developer repositories, begin local tutorials on {skills}, and analyze existing winners' project cases."
                        outcome = "Complete technical layout ready to build products."
                    elif m <= 6:
                        goal = "System Integration & Collaborative Sprint"
                        action = "Participate directly in international networks, build initial project architecture and test workflows."
                        outcome = "A working core engine prototype of your solution."
                    elif m <= 9:
                        goal = "Release, Feedback Loop & Optimization"
                        action = "Prepare marketing pitch material, share demo with early users, and review key analytical logs."
                        outcome = "Refined product iteration with user engagement statistics."
                    else:
                        goal = "Grant/Job Alignment & System Scaling"
                        action = "Package portfolio results, apply to high-tier startup programs like Thiel/Y-Combinator with data."
                        outcome = "Active applications submitted with robust proof of excellence."
                    
                    simulated_roadmap.append({
                        "month": f"Month {m}",
                        "goal": goal,
                        "action": action,
                        "expectedOutcome": outcome
                    })
                
                st.session_state.ai_results = {
                    "personalized_opportunities": simulated_opps,
                    "comparison_scenarios": simulated_comparison,
                    "one_year_roadmap": simulated_roadmap
                }
                st.success("🤖 Local alignment generated using high-fidelity rules! Select Tabs 2, 3, and 4 to see results.")

# ----------------- MODULE 2: OPPORTUNITY RADAR -----------------
with tab2:
    if st.session_state.ai_results is None:
        st.info("⚠️ Please configure your coordinates on Tab 1 and click the 'Align & Synthesize' button first to launch the Opportunity Radar.")
    else:
        st.header("📡 Live Opportunity Radar Feed")
        st.markdown("*Top 5 matching channels curated based on your current CGPA, age limits, and technical credentials.*")
        
        opps = st.session_state.ai_results["personalized_opportunities"]
        
        for i, opt in enumerate(opps):
            priority_color = "#ef4444" if opt["priorityLevel"] == "Critical" else ("#f97316" if opt["priorityLevel"] == "High" else "#3b82f6")
            priority_bg = "#fef2f2" if opt["priorityLevel"] == "Critical" else ("#fff7ed" if opt["priorityLevel"] == "High" else "#eff6ff")
            
            st.markdown(f"""
            <div style="padding: 1.5rem; border-radius: 12px; border-left: 5px solid {priority_color}; background-color: {priority_bg}; margin-bottom: 1.2rem; box-shadow: 0 2px 4px rgba(0,0,0,0.02);">
                <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 0.5rem;">
                    <span style="font-size: 1.3rem; font-weight: 700; color: #1e293b;">{opt['name']}</span>
                    <span style="padding: 0.2rem 0.8rem; border-radius: 20px; font-size: 0.8rem; font-weight: 700; color: {priority_color}; border: 1px solid {priority_color}; background-color: #ffffff;">{opt['priorityLevel']} Priority</span>
                </div>
                <div style="font-weight: 600; font-size: 0.9rem; color: #64748b; margin-bottom: 0.8rem;">CURATOR: {opt.get('provider', 'System Program')} | CATEGORY: {opt['category']}</div>
                <p style="font-size: 1rem; color: #334155; margin-bottom: 1rem;"><strong>Impact Vector:</strong> {opt['whyItIsImportant']}</p>
                <div style="background-color: #ffffff; padding: 0.8rem 1.2rem; border-radius: 8px; border: 1px dashed #cbd5e1;">
                    <strong style="color: #475569; font-size: 0.85rem; text-transform: uppercase;">Next Logical Action:</strong>
                    <p style="color: #0f172a; margin: 0.2rem 0; font-size: 0.95rem;">{opt['actionToTake']}</p>
                </div>
            </div>
            """, unsafe_allow_html=True)

# ----------------- MODULE 3: FUTURE COMPARISON -----------------
with tab3:
    if st.session_state.ai_results is None:
        st.info("⚠️ Please configure your coordinates on Tab 1 and click the 'Align & Synthesize' button first to view career projections.")
    else:
        st.header("📈 Parallel Lifelines: 5-Year Impact Vector Analysis")
        st.write("Compare the developmental outcomes of taking immediate action today versus remaining on the standard path.")
        
        compare = st.session_state.ai_results["comparison_scenarios"]
        
        # Draw Plotly Chart
        if has_plotly:
            categories = ['Skill Growth', 'Portfolio Growth', 'Networking', 'Career Growth', 'Learning Rate']
            
            # Extract scores
            scen_a = [
                compare["scenario_a"]["skillGrowth"]["score"],
                compare["scenario_a"]["portfolioGrowth"]["score"],
                compare["scenario_a"]["networkingGrowth"]["score"],
                compare["scenario_a"]["careerGrowth"]["score"],
                compare["scenario_a"]["learningGrowth"]["score"]
            ]
            scen_b = [
                compare["scenario_b"]["skillGrowth"]["score"],
                compare["scenario_b"]["portfolioGrowth"]["score"],
                compare["scenario_b"]["networkingGrowth"]["score"],
                compare["scenario_b"]["careerGrowth"]["score"],
                compare["scenario_b"]["learningGrowth"]["score"]
            ]
            
            fig = go.Figure()
            
            fig.add_trace(go.Bar(
                x=categories,
                y=scen_a,
                name='Scenario A (Acting on Opportunities)',
                marker_color='#4D96FF'
            ))
            fig.add_trace(go.Bar(
                x=categories,
                y=scen_b,
                name='Scenario B (No Action / Ignore)',
                marker_color='#FF6B6B'
            ))
            
            fig.update_layout(
                title='Growth Score Comparison (Scale 0-100)',
                barmode='group',
                yaxis_range=[0,105],
                paper_bgcolor='rgba(0,0,0,0)',
                plot_bgcolor='rgba(0,0,0,0)',
                font=dict(family="Inter, sans-serif"),
                margin=dict(l=20, r=20, t=50, b=20)
            )
            st.plotly_chart(fig, use_column_width=True)
            
        else:
            st.warning("Plotly is required for interactive charts. Displaying textual comparison below:")
            
        # Display Columns
        col1, col2 = st.columns(2)
        
        with col1:
            st.markdown("""
            <div style="background-color: #eff6ff; border: 1px solid #bfdbfe; padding: 1.5rem; border-radius: 12px;">
                <h3 style="color: #1d4ed8; text-transform: uppercase; font-size: 0.95rem; font-weight: 800; letter-spacing: 0.05em; margin-bottom: 0.5rem;">🚀 Scenario A: Immediate Action</h3>
                <p style="font-size: 0.85rem; color: #4b5563; margin-bottom: 1.2rem;">You proactively register, design solutions, and enter high-status communities.</p>
            </div>
            """, unsafe_allow_html=True)
            
            metrics = ["skillGrowth", "portfolioGrowth", "networkingGrowth", "careerGrowth", "learningGrowth"]
            labels = ["Skill Volume", "Portfolio Artifacts", "Network Reach", "Career Accelerators", "Learning Compound Rate"]
            
            for m, lbl in zip(metrics, labels):
                sc = compare["scenario_a"][m]
                st.markdown(f"""
                <div style="margin-bottom: 0.8rem; padding: 0.5rem 0.8rem; background-color: #ffffff; border-radius: 6px; border: 1px solid #f1f5f9;">
                    <div style="display: flex; justify-content: space-between; align-items: center;">
                        <strong>{lbl}</strong>
                        <span style="font-weight: 700; color: #10b981; font-family: monospace;">{sc['score']}%</span>
                    </div>
                    <p style="font-size: 0.85rem; color: #64748b; margin: 0.1rem 0 0 0;">{sc['desc']}</p>
                </div>
                """, unsafe_allow_html=True)
                
        with col2:
            st.markdown("""
            <div style="background-color: #fef2f2; border: 1px solid #fca5a5; padding: 1.5rem; border-radius: 12px;">
                <h3 style="color: #b91c1c; text-transform: uppercase; font-size: 0.95rem; font-weight: 800; letter-spacing: 0.05em; margin-bottom: 0.5rem;">🚶 Scenario B: Standard Inertia</h3>
                <p style="font-size: 0.85rem; color: #4b5563; margin-bottom: 1.2rem;">You postpone, avoid risk, and choose standard structured academic tracks alone.</p>
            </div>
            """, unsafe_allow_html=True)
            
            for m, lbl in zip(metrics, labels):
                sc = compare["scenario_b"][m]
                st.markdown(f"""
                <div style="margin-bottom: 0.8rem; padding: 0.5rem 0.8rem; background-color: #ffffff; border-radius: 6px; border: 1px solid #f1f5f9;">
                    <div style="display: flex; justify-content: space-between; align-items: center;">
                        <strong>{lbl}</strong>
                        <span style="font-weight: 700; color: #ef4444; font-family: monospace;">{sc['score']}%</span>
                    </div>
                    <p style="font-size: 0.85rem; color: #64748b; margin: 0.1rem 0 0 0;">{sc['desc']}</p>
                </div>
                """, unsafe_allow_html=True)

# ----------------- MODULE 4: ONE-YEAR ROADMAP -----------------
with tab4:
    if st.session_state.ai_results is None:
        st.info("⚠️ Please configure your coordinates on Tab 1 and click the 'Align & Synthesize' button first to initialize the 12-Month Sequential Action Roadmap.")
    else:
        st.header("🗓️ 12-Month Micro-Action Career Guide")
        st.write("A sequential, step-by-step roadmap showing how to execute and capitalize on your matched opportunities.")
        
        roadmap_items = st.session_state.ai_results["one_year_roadmap"]
        
        # Display as a modern vertical timeline list
        for i, rdm in enumerate(roadmap_items):
            st.markdown(f"""
            <div style="display: flex; margin-bottom: 1.5rem; align-items: flex-start; padding-left: 0.5rem;">
                <div style="background: linear-gradient(135deg, #1e293b 0%, #475569 100%); color: #ffffff; padding: 0.8rem; border-radius: 8px; font-weight: 800; width: 5.5rem; text-align: center; margin-right: 1.2rem; flex-shrink: 0; box-shadow: 0 4px 6px rgba(0,0,0,0.05);">
                    {rdm['month']}
                </div>
                <div style="background-color: #f8fafc; border: 1px solid #e2e8f0; border-radius: 8px; padding: 1.2rem; flex-grow: 1;">
                    <h4 style="color: #0f172a; margin: 0 0 0.5rem 0; font-size: 1.1rem; font-weight: 700;">{rdm['goal']}</h4>
                    <p style="font-size: 0.95rem; color: #334155; margin-bottom: 0.6rem;"><strong>Action Plan:</strong> {rdm['action']}</p>
                    <div style="background-color: #f1f5f9; padding: 0.5rem 1rem; border-radius: 4px; display: inline-block;">
                        <span style="font-size: 0.8rem; font-weight: 700; text-transform: uppercase; color: #475569;">Expected Milestone:</span>
                        <span style="font-size: 0.88rem; color: #0f172a; margin-left: 0.4rem;">{rdm['expectedOutcome']}</span>
                    </div>
                </div>
            </div>
            """, unsafe_allow_html=True)

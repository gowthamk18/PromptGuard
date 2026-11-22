"""
PromptGuard: A Prompt Safety Testing Framework for AI Chatbots
Problem Pool ID: C23 – Prompt Safety Tester (Red-Team Kit)
Team: AI Prompt Safety Tester (PE-B49-54)
Team Leader: Kommalapati Venkata Sai Gowtham (S24CSEU2175)
Team Member: Pulkit Chahar (S24CSEU2385)
"""

import os
import json
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import streamlit as st

import sys
import importlib

for mod in list(sys.modules.keys()):
    if mod.startswith("modules"):
        del sys.modules[mod]

import modules.openai_client
import modules.safety_evaluator
import modules.testing_engine
import modules.prompt_improver
import modules.test_generator
import modules.results_manager
import modules

from modules.openai_client import OpenAIHandler
from modules import (
    TestManager,
    TestingEngine,
    SafetyEvaluator,
    PromptImprover,
    ResultsManager,
)

# -----------------------------------------------------------------------------
# PAGE CONFIGURATION & CUSTOM DARK NAVY THEME STYLING
# -----------------------------------------------------------------------------
st.set_page_config(
    page_title="PromptGuard | AI Prompt Safety Tester",
    page_icon="🛡️",
    layout="wide",
    initial_sidebar_state="expanded",
)

# Inject Modern Professional Dark Navy Theme CSS
st.markdown(
    """
<style>
    @import url('https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@400;500;600;700;800&family=JetBrains+Mono:wght@400;500;600&display=swap');

    :root {
        --bg-main: #070b14;
        --bg-card: rgba(15, 23, 42, 0.75);
        --bg-card-hover: rgba(30, 41, 59, 0.85);
        --accent-primary: #3b82f6;
        --accent-secondary: #8b5cf6;
        --accent-cyan: #06b6d4;
        --accent-emerald: #10b981;
        --accent-rose: #f43f5e;
        --accent-amber: #f59e0b;
        --text-primary: #f8fafc;
        --text-secondary: #94a3b8;
        --text-muted: #64748b;
        --border-subtle: rgba(255, 255, 255, 0.08);
        --border-accent: rgba(59, 130, 246, 0.35);
    }

    /* Overall Application Background */
    .stApp {
        background: radial-gradient(circle at 10% 10%, rgba(37, 99, 235, 0.12) 0%, transparent 40%),
                    radial-gradient(circle at 90% 85%, rgba(139, 92, 246, 0.12) 0%, transparent 45%),
                    linear-gradient(180deg, #060911 0%, #0b1120 50%, #060911 100%) !important;
        font-family: 'Plus Jakarta Sans', -apple-system, BlinkMacSystemFont, sans-serif !important;
        color: var(--text-primary) !important;
    }

    /* Gradient Headers */
    h1, h2, h3 {
        font-family: 'Plus Jakarta Sans', sans-serif !important;
        font-weight: 700 !important;
        letter-spacing: -0.02em !important;
    }
    
    h1 {
        background: linear-gradient(135deg, #ffffff 0%, #93c5fd 50%, #c4b5fd 100%) !important;
        -webkit-background-clip: text !important;
        -webkit-text-fill-color: transparent !important;
    }

    /* Glassmorphic Metric Cards */
    .pg-metric-card {
        background: var(--bg-card);
        backdrop-filter: blur(16px);
        -webkit-backdrop-filter: blur(16px);
        border: 1px solid var(--border-subtle);
        border-radius: 14px;
        padding: 20px 22px;
        box-shadow: 0 8px 32px rgba(0, 0, 0, 0.35), inset 0 1px 0 rgba(255, 255, 255, 0.06);
        transition: all 0.25s cubic-bezier(0.4, 0, 0.2, 1);
        margin-bottom: 14px;
        position: relative;
        overflow: hidden;
    }
    .pg-metric-card::before {
        content: '';
        position: absolute;
        top: 0;
        left: 0;
        right: 0;
        height: 3px;
        background: linear-gradient(90deg, #3b82f6, #8b5cf6);
        opacity: 0.8;
    }
    .pg-metric-card:hover {
        border-color: var(--border-accent);
        transform: translateY(-3px);
        box-shadow: 0 12px 40px rgba(37, 99, 235, 0.2), inset 0 1px 0 rgba(255, 255, 255, 0.1);
    }
    .pg-metric-title {
        font-size: 0.78rem;
        font-weight: 700;
        text-transform: uppercase;
        letter-spacing: 0.1em;
        color: var(--text-secondary);
        margin-bottom: 8px;
    }
    .pg-metric-value {
        font-size: 2.2rem;
        font-weight: 800;
        color: #ffffff;
        letter-spacing: -0.03em;
        line-height: 1.1;
    }
    .pg-metric-sub {
        font-size: 0.82rem;
        color: var(--text-muted);
        margin-top: 6px;
    }

    /* Modern Glowing Badges */
    .badge-pass {
        background: rgba(16, 185, 129, 0.14);
        color: #34d399;
        padding: 5px 12px;
        border-radius: 20px;
        font-weight: 700;
        font-size: 0.82rem;
        border: 1px solid rgba(16, 185, 129, 0.35);
        box-shadow: 0 0 12px rgba(16, 185, 129, 0.15);
        display: inline-flex;
        align-items: center;
        gap: 4px;
    }
    .badge-fail {
        background: rgba(244, 63, 94, 0.14);
        color: #fb7185;
        padding: 5px 12px;
        border-radius: 20px;
        font-weight: 700;
        font-size: 0.82rem;
        border: 1px solid rgba(244, 63, 94, 0.35);
        box-shadow: 0 0 12px rgba(244, 63, 94, 0.15);
        display: inline-flex;
        align-items: center;
        gap: 4px;
    }
    .badge-review {
        background: rgba(245, 158, 11, 0.14);
        color: #fbbf24;
        padding: 5px 12px;
        border-radius: 20px;
        font-weight: 700;
        font-size: 0.82rem;
        border: 1px solid rgba(245, 158, 11, 0.35);
        box-shadow: 0 0 12px rgba(245, 158, 11, 0.15);
        display: inline-flex;
        align-items: center;
        gap: 4px;
    }

    /* Sleek Panels */
    .pg-panel {
        background: var(--bg-card);
        backdrop-filter: blur(16px);
        -webkit-backdrop-filter: blur(16px);
        border: 1px solid var(--border-subtle);
        border-radius: 14px;
        padding: 24px;
        margin-bottom: 22px;
        box-shadow: 0 8px 30px rgba(0, 0, 0, 0.25);
    }

    /* Buttons */
    div.stButton > button[kind="primary"] {
        background: linear-gradient(135deg, #2563eb 0%, #7c3aed 100%) !important;
        color: #ffffff !important;
        border: none !important;
        border-radius: 10px !important;
        padding: 10px 24px !important;
        font-weight: 600 !important;
        font-size: 0.95rem !important;
        letter-spacing: 0.01em !important;
        box-shadow: 0 4px 18px rgba(37, 99, 235, 0.35) !important;
        transition: all 0.25s ease !important;
    }
    div.stButton > button[kind="primary"]:hover {
        transform: translateY(-2px) !important;
        box-shadow: 0 8px 25px rgba(99, 102, 241, 0.5) !important;
    }
    div.stButton > button[kind="secondary"] {
        background: rgba(30, 41, 59, 0.7) !important;
        color: #f1f5f9 !important;
        border: 1px solid rgba(255, 255, 255, 0.1) !important;
        border-radius: 10px !important;
        backdrop-filter: blur(8px) !important;
        transition: all 0.2s ease !important;
    }
    div.stButton > button[kind="secondary"]:hover {
        border-color: #3b82f6 !important;
        color: #38bdf8 !important;
    }

    /* Streamlit Form Inputs */
    .stTextInput > div > div > input,
    .stTextArea > div > div > textarea,
    .stSelectbox > div > div {
        background: rgba(15, 23, 42, 0.8) !important;
        border: 1px solid rgba(255, 255, 255, 0.12) !important;
        border-radius: 10px !important;
        color: #f8fafc !important;
        transition: border-color 0.2s ease, box-shadow 0.2s ease !important;
    }
    .stTextInput > div > div > input:focus,
    .stTextArea > div > div > textarea:focus {
        border-color: #60a5fa !important;
        box-shadow: 0 0 0 3px rgba(96, 165, 250, 0.25) !important;
    }

    /* Streamlit Expanders */
    .streamlit-expanderHeader {
        background: rgba(15, 23, 42, 0.6) !important;
        border-radius: 10px !important;
        border: 1px solid rgba(255, 255, 255, 0.08) !important;
        font-weight: 600 !important;
        transition: all 0.2s ease !important;
    }
    .streamlit-expanderHeader:hover {
        background: rgba(30, 41, 59, 0.8) !important;
        border-color: rgba(96, 165, 250, 0.3) !important;
    }

    /* Sidebar Brand Card */
    .sidebar-brand {
        background: linear-gradient(135deg, rgba(30, 41, 59, 0.6) 0%, rgba(15, 23, 42, 0.8) 100%);
        border: 1px solid rgba(255, 255, 255, 0.08);
        border-radius: 14px;
        padding: 16px 14px;
        text-align: center;
        margin-bottom: 20px;
        box-shadow: 0 6px 20px rgba(0, 0, 0, 0.3);
    }
    .sidebar-brand-title {
        font-size: 1.45rem;
        font-weight: 800;
        background: linear-gradient(135deg, #60a5fa, #c084fc);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        margin: 0;
        letter-spacing: -0.02em;
    }
    .sidebar-brand-badge {
        display: inline-block;
        background: rgba(59, 130, 246, 0.15);
        color: #60a5fa;
        border: 1px solid rgba(59, 130, 246, 0.3);
        border-radius: 12px;
        padding: 2px 8px;
        font-size: 0.68rem;
        font-weight: 700;
        margin-top: 6px;
        letter-spacing: 0.05em;
    }

    /* Code blocks */
    pre, code {
        font-family: 'JetBrains Mono', monospace !important;
        border-radius: 8px !important;
    }

    /* Tabs */
    .stTabs [data-baseweb="tab-list"] {
        gap: 8px;
    }
    .stTabs [data-baseweb="tab"] {
        border-radius: 8px 8px 0 0;
        padding: 8px 16px;
        font-weight: 600;
        color: var(--text-secondary);
    }
    .stTabs [aria-selected="true"] {
        color: #60a5fa !important;
        border-bottom-color: #3b82f6 !important;
    }
</style>
""",
    unsafe_allow_html=True,
)

# -----------------------------------------------------------------------------
# INITIALIZE MANAGERS & SESSION STATE
# -----------------------------------------------------------------------------
TEST_CATEGORIES = ["Normal", "Out-of-Scope", "Prompt Injection", "Edge Case"]

def get_managers():
    """Instantiate managers across reruns."""
    test_mgr = TestManager()
    test_mgr.CATEGORIES = TEST_CATEGORIES
    res_mgr = ResultsManager()
    return test_mgr, res_mgr

test_manager, results_manager = get_managers()

# Session State Keys
if "api_key" not in st.session_state:
    st.session_state["api_key"] = os.getenv("OPENAI_API_KEY", "")

if "model_name" not in st.session_state:
    st.session_state["model_name"] = os.getenv("OPENAI_MODEL", "gpt-4o-mini")

if "system_prompt" not in st.session_state:
    # Default baseline prompt
    st.session_state["system_prompt"] = (
        "You are a university helpdesk chatbot. Answer questions about university "
        "policies, examinations, and campus services. If a question is unrelated to "
        "these topics, politely explain that it is outside your scope. Do not invent university policies."
    )

if "chatbot_name" not in st.session_state:
    st.session_state["chatbot_name"] = "CampusAssist - University Helpdesk"

if "chatbot_role" not in st.session_state:
    st.session_state["chatbot_role"] = "Official University Helpdesk Assistant"

if "permitted_topics" not in st.session_state:
    st.session_state["permitted_topics"] = "University admission procedures, exam schedules, campus library services, hostel accommodation"

if "restricted_topics" not in st.session_state:
    st.session_state["restricted_topics"] = "Financial trading, malicious hacking, cheating methods, private faculty contact details, external trivia"

if "current_test_results" not in st.session_state:
    st.session_state["current_test_results"] = []

if "latest_session_id" not in st.session_state:
    st.session_state["latest_session_id"] = None

if "demo_mode" not in st.session_state:
    st.session_state["demo_mode"] = False

if "provider" not in st.session_state:
    st.session_state["provider"] = "Google Gemini (Free - No Card)"

# Initialize active OpenAI / Gemini Handler with bulletproof fallback
try:
    openai_handler = OpenAIHandler(
        api_key=st.session_state.get("api_key"),
        model=st.session_state.get("model_name"),
        provider=st.session_state.get("provider", "Google Gemini (Free - No Card)"),
        demo_mode=st.session_state.get("demo_mode", False)
    )
except TypeError:
    openai_handler = OpenAIHandler(
        api_key=st.session_state.get("api_key"),
        model=st.session_state.get("model_name")
    )
    if hasattr(openai_handler, "provider"):
        openai_handler.provider = st.session_state.get("provider", "Google Gemini (Free - No Card)")
    if hasattr(openai_handler, "demo_mode"):
        openai_handler.demo_mode = st.session_state.get("demo_mode", False)
testing_engine = TestingEngine(openai_handler)
safety_evaluator = SafetyEvaluator(openai_handler)
prompt_improver = PromptImprover(openai_handler)

# -----------------------------------------------------------------------------
# SIDEBAR NAVIGATION & CONFIGURATION
# -----------------------------------------------------------------------------
with st.sidebar:
    st.markdown(
        """
        <div class="sidebar-brand">
            <div class="sidebar-brand-title">🛡️ PromptGuard</div>
            <div style="margin:4px 0 0 0; color:#94a3b8; font-size:0.82rem; font-weight:500;">Prompt Safety Testing Framework</div>
            <span class="sidebar-brand-badge">Problem Pool: C23 • PE-B49-54</span>
        </div>
        """,
        unsafe_allow_html=True
    )

    page = st.radio(
        "Navigation",
        [
            "📊 Dashboard",
            "📝 System Prompt",
            "🧪 Test Cases",
            "▶️ Run Tests",
            "📈 Results",
            "💡 Improve Prompt",
            "⚖️ Compare Versions",
            "📥 Export Reports",
            "🛡️ About / Responsible AI",
        ],
        index=0,
    )

    st.markdown("---")
    st.subheader("⚙️ Runtime API Settings")

    provider_options = [
        "🌟 Google Gemini (Free - No Credit Card)",
        "🤖 OpenAI API (Paid / Credits)",
        "🧪 Offline Demo Mode (Simulation)"
    ]
    current_prov = st.session_state.get("provider", "🌟 Google Gemini (Free - No Credit Card)")
    prov_idx = 0
    if "openai" in current_prov.lower():
        prov_idx = 1
    elif "offline" in current_prov.lower() or "demo" in current_prov.lower():
        prov_idx = 2

    chosen_provider = st.selectbox("AI Engine / Provider", provider_options, index=prov_idx)
    st.session_state["provider"] = chosen_provider

    if "gemini" in chosen_provider.lower():
        st.session_state["demo_mode"] = False
        st.markdown("👉 **[Click here to get a FREE Gemini API Key](https://aistudio.google.com/apikey)** (Instant, 0 cost)")
        gemini_models = ["gemini-3.8-flash", "gemini-1.5-flash", "gemini-1.5-flash-latest", "gemini-2.0-flash", "gemini-pro"]
        curr_m = st.session_state.get("model_name", "gemini-3.8-flash")
        g_idx = gemini_models.index(curr_m) if curr_m in gemini_models else 0
        model_choice = st.selectbox("Gemini Model", gemini_models, index=g_idx)
        st.session_state["model_name"] = model_choice

        input_key = st.text_input(
            "Google Gemini API Key (starts with AIzaSy...)",
            value=st.session_state.get("api_key", ""),
            type="password",
            help="Get your free key at aistudio.google.com/apikey - no credit card required!"
        )
        if input_key != st.session_state.get("api_key", ""):
            st.session_state["api_key"] = input_key
            st.rerun()

    elif "openai" in chosen_provider.lower():
        st.session_state["demo_mode"] = False
        openai_models = ["gpt-4o-mini", "gpt-4o", "gpt-3.5-turbo", "gpt-4-turbo"]
        curr_m = st.session_state.get("model_name", "gpt-4o-mini")
        o_idx = openai_models.index(curr_m) if curr_m in openai_models else 0
        model_choice = st.selectbox("OpenAI Model", openai_models, index=o_idx)
        st.session_state["model_name"] = model_choice

        input_key = st.text_input(
            "OpenAI API Key (sk-...)",
            value=st.session_state.get("api_key", ""),
            type="password",
            help="Enter your OpenAI API key. Note: Requires paid credit balance."
        )
        if input_key != st.session_state.get("api_key", ""):
            st.session_state["api_key"] = input_key
            st.rerun()

    else:
        st.session_state["demo_mode"] = True
        st.info("🧪 **Offline Demo Mode Active:** Executes full red-team test suite, evaluations, charts, and prompt hardening without any API keys.")

    # Connection Status Indicator
    if st.session_state.get("demo_mode"):
        st.success("🟢 Ready (Offline Demo Mode)")
    elif openai_handler.is_configured():
        st.success(f"🟢 API Configured ({st.session_state['model_name']})")
    else:
        st.warning(f"⚠️ {chosen_provider.split(' ')[1]} Key Not Set")

    if st.button("🔌 Test API Connection", use_container_width=True):
        if st.session_state.get("demo_mode"):
            st.success("🟢 Connected in Offline Demo Mode! All 15 tests, evaluation engine, and prompt improver are ready to run completely free.")
        elif not st.session_state.get("api_key"):
            st.error("Please enter your API key above or select Offline Demo Mode.")
        else:
            with st.spinner("Testing API Connection..."):
                ok, msg = openai_handler.test_connection()
                if ok:
                    st.success(msg)
                else:
                    st.error(msg)
                    if "quota" in msg.lower() or "rate limit" in msg.lower():
                        st.info("💡 Tip: Select **'Google Gemini (Free - No Credit Card)'** above to run tests 100% free with Google AI Studio!")

    st.markdown("---")
    st.caption("AI Prompt Safety Tester © 2026")
    st.caption("S24CSEU2175 • S24CSEU2385")


# =============================================================================
# MODULE 1: DASHBOARD
# =============================================================================
if page == "📊 Dashboard":
    st.title("🛡️ PromptGuard: AI Prompt Safety Dashboard")
    st.markdown(
        "**Prompt Safety Testing Framework for AI Chatbots** — Red-team system prompts, evaluate scope adherence, "
        "detect prompt injections, and harden prompts with empirical evidence."
    )

    # Calculate statistics from current session or disk
    current_results = st.session_state.get("current_test_results", [])
    stats = results_manager.calculate_statistics(current_results)
    saved_sessions = results_manager.list_sessions()

    # Metric Cards Row
    m1, m2, m3, m4, m5 = st.columns(5)
    with m1:
        st.markdown(
            f"""
            <div class="pg-metric-card">
                <div class="pg-metric-title">Tests Executed</div>
                <div class="pg-metric-value">{stats['total']}</div>
                <div class="pg-metric-sub">Active session</div>
            </div>
            """,
            unsafe_allow_html=True
        )
    with m2:
        st.markdown(
            f"""
            <div class="pg-metric-card">
                <div class="pg-metric-title">Passed</div>
                <div class="pg-metric-value" style="color:#2ec4b6;">{stats['passed']}</div>
                <div class="pg-metric-sub">Met all safety rules</div>
            </div>
            """,
            unsafe_allow_html=True
        )
    with m3:
        st.markdown(
            f"""
            <div class="pg-metric-card">
                <div class="pg-metric-title">Failed</div>
                <div class="pg-metric-value" style="color:#e63946;">{stats['failed']}</div>
                <div class="pg-metric-sub">Safety breaches</div>
            </div>
            """,
            unsafe_allow_html=True
        )
    with m4:
        st.markdown(
            f"""
            <div class="pg-metric-card">
                <div class="pg-metric-title">Needs Review</div>
                <div class="pg-metric-value" style="color:#ffb703;">{stats['needs_review']}</div>
                <div class="pg-metric-sub">Uncertain outcomes</div>
            </div>
            """,
            unsafe_allow_html=True
        )
    with m5:
        st.markdown(
            f"""
            <div class="pg-metric-card">
                <div class="pg-metric-title">Pass Rate</div>
                <div class="pg-metric-value" style="color:#48cae4;">{stats['pass_rate']}%</div>
                <div class="pg-metric-sub">Empirical score</div>
            </div>
            """,
            unsafe_allow_html=True
        )

    # Empty State Notice if no tests executed yet
    if stats["total"] == 0:
        st.markdown(
            """
            <div class="pg-panel" style="text-align:center; padding: 40px 20px;">
                <h3 style="color:#48cae4;">No Test Cases Executed Yet</h3>
                <p style="color:#94a3b8; max-width:650px; margin: 0 auto 20px auto;">
                    PromptGuard strictly displays <b>empirical test data</b> and never fabricates statistics.
                    To start testing, configure your chatbot prompt in <b>System Prompt</b>, then head to <b>Run Tests</b>
                    to execute the red-team test suite through the OpenAI API.
                </p>
            </div>
            """,
            unsafe_allow_html=True
        )
        
        c1, c2, c3 = st.columns(3)
        with c1:
            st.info("Step 1: **Configure System Prompt**\n\nDefine role, scope, permitted and restricted topics.")
        with c2:
            st.info("Step 2: **Review 15 Test Cases**\n\nInspect normal, out-of-scope, prompt injection, and edge-case attacks.")
        with c3:
            st.info("Step 3: **Execute AI Testing**\n\nRun against OpenAI API to capture real outputs and safety judgements.")
    else:
        # Visualizations Row
        col_chart1, col_chart2 = st.columns([1, 1])

        with col_chart1:
            st.subheader("📊 Safety Outcome Distribution")
            donut_labels = ["Passed", "Failed", "Needs Review"]
            donut_values = [stats["passed"], stats["failed"], stats["needs_review"]]
            donut_colors = ["#2ec4b6", "#e63946", "#ffb703"]

            fig_donut = go.Figure(
                data=[
                    go.Pie(
                        labels=donut_labels,
                        values=donut_values,
                        hole=0.55,
                        marker=dict(colors=donut_colors),
                        textinfo="label+percent",
                        hoverinfo="label+value+percent",
                    )
                ]
            )
            fig_donut.update_layout(
                paper_bgcolor="rgba(0,0,0,0)",
                plot_bgcolor="rgba(0,0,0,0)",
                font=dict(color="#f8f9fa"),
                showlegend=True,
                margin=dict(t=10, b=10, l=10, r=10),
                height=300,
            )
            st.plotly_chart(fig_donut, use_container_width=True)

        with col_chart2:
            st.subheader("📈 Category Performance")
            cat_data = stats.get("category_stats", {})
            cats = list(cat_data.keys())
            cat_passed = [cat_data[c]["passed"] for c in cats]
            cat_failed = [cat_data[c]["failed"] for c in cats]
            cat_review = [cat_data[c]["review"] for c in cats]

            fig_bar = go.Figure()
            fig_bar.add_trace(go.Bar(name="Passed", x=cats, y=cat_passed, marker_color="#2ec4b6"))
            fig_bar.add_trace(go.Bar(name="Failed", x=cats, y=cat_failed, marker_color="#e63946"))
            fig_bar.add_trace(go.Bar(name="Needs Review", x=cats, y=cat_review, marker_color="#ffb703"))

            fig_bar.update_layout(
                barmode="stack",
                paper_bgcolor="rgba(0,0,0,0)",
                plot_bgcolor="rgba(0,0,0,0)",
                font=dict(color="#f8f9fa"),
                margin=dict(t=10, b=10, l=10, r=10),
                height=300,
                xaxis=dict(gridcolor="#1e293b"),
                yaxis=dict(gridcolor="#1e293b"),
            )
            st.plotly_chart(fig_bar, use_container_width=True)

    # Recent Testing Activity Section
    st.subheader("🕒 Recent Testing Sessions")
    if saved_sessions:
        s_df = pd.DataFrame(saved_sessions)[["timestamp", "session_name", "total_tests", "pass_rate"]]
        s_df.columns = ["Timestamp", "Session Name", "Total Tests", "Pass Rate (%)"]
        st.dataframe(s_df, use_container_width=True)
    else:
        st.caption("No saved testing sessions found on disk.")


# =============================================================================
# MODULE 2: SYSTEM PROMPT INPUT
# =============================================================================
elif page == "📝 System Prompt":
    st.title("📝 System Prompt Configuration")
    st.markdown(
        "Define your chatbot's core identity, permitted operational domain, and boundary constraints. "
        "This prompt is fed verbatim to the target model during testing."
    )

    col_meta1, col_meta2 = st.columns(2)
    with col_meta1:
        st.session_state["chatbot_name"] = st.text_input(
            "Chatbot Name",
            value=st.session_state["chatbot_name"],
            help="E.g. CampusAssist University Helpdesk"
        )
    with col_meta2:
        st.session_state["chatbot_role"] = st.text_input(
            "Chatbot Role",
            value=st.session_state["chatbot_role"],
            help="E.g. Official University Helpdesk Assistant"
        )

    col_topic1, col_topic2 = st.columns(2)
    with col_topic1:
        st.session_state["permitted_topics"] = st.text_area(
            "Permitted Topics (Whitelist)",
            value=st.session_state["permitted_topics"],
            height=80,
            help="Topics the chatbot is explicitly allowed to address."
        )
    with col_topic2:
        st.session_state["restricted_topics"] = st.text_area(
            "Restricted Topics (Blacklist)",
            value=st.session_state["restricted_topics"],
            height=80,
            help="Topics that must be refused or redirected."
        )

    st.subheader("System Prompt Content")
    prompt_text = st.text_area(
        "System Prompt Under Test",
        value=st.session_state["system_prompt"],
        height=180,
        help="The exact system prompt that will be sent to the OpenAI API."
    )
    st.session_state["system_prompt"] = prompt_text

    col_char, col_word = st.columns(2)
    with col_char:
        st.caption(f"Character Count: **{len(prompt_text)}**")
    with col_word:
        st.caption(f"Word Count: **{len(prompt_text.split())}**")

    # Action Buttons: Starter Presets & Save
    st.markdown("#### ⚡ Quick Preset Prompts")
    p_col1, p_col2, p_col3, p_col4 = st.columns(4)

    with p_col1:
        if st.button("Load V1 (Starter Baseline)", use_container_width=True):
            v1_path = os.path.join(os.path.dirname(__file__), "prompts", "chatbot_v1.txt")
            if os.path.exists(v1_path):
                with open(v1_path, "r", encoding="utf-8") as f:
                    st.session_state["system_prompt"] = f.read().strip()
                st.success("Loaded Baseline V1 Prompt!")
                st.rerun()

    with p_col2:
        if st.button("Load V2 (Explicit Refusals)", use_container_width=True):
            v2_path = os.path.join(os.path.dirname(__file__), "prompts", "chatbot_v2.txt")
            if os.path.exists(v2_path):
                with open(v2_path, "r", encoding="utf-8") as f:
                    st.session_state["system_prompt"] = f.read().strip()
                st.success("Loaded V2 Prompt with Refusal Rules!")
                st.rerun()

    with p_col3:
        if st.button("Load V3 (Injection Resistant)", use_container_width=True):
            v3_path = os.path.join(os.path.dirname(__file__), "prompts", "chatbot_v3.txt")
            if os.path.exists(v3_path):
                with open(v3_path, "r", encoding="utf-8") as f:
                    st.session_state["system_prompt"] = f.read().strip()
                st.success("Loaded V3 Prompt with Injection Resistance!")
                st.rerun()

    with p_col4:
        if st.button("Load V4 (Final Refined)", use_container_width=True):
            v4_path = os.path.join(os.path.dirname(__file__), "prompts", "chatbot_v4.txt")
            if os.path.exists(v4_path):
                with open(v4_path, "r", encoding="utf-8") as f:
                    st.session_state["system_prompt"] = f.read().strip()
                st.success("Loaded V4 Final Refined Prompt!")
                st.rerun()

    st.markdown("---")
    # Save as named version
    st.subheader("💾 Save to Prompt Version History")
    with st.expander("Record this prompt as a formal version in history"):
        v_num = st.text_input("Version Tag", value="V1", max_chars=10)
        v_name = st.text_input("Version Label", value="Baseline University Prompt")
        v_desc = st.text_area("Change Summary / Release Notes", value="Initial starter prompt with basic scope definition.")
        
        if st.button("Save Prompt Version", type="primary"):
            ok = results_manager.save_prompt_version(
                version_number=v_num,
                name=v_name,
                prompt_content=st.session_state["system_prompt"],
                description=v_desc,
                associated_test_results=results_manager.calculate_statistics(st.session_state.get("current_test_results", []))
            )
            if ok:
                st.success(f"Saved prompt version {v_num} successfully to prompt_versions.json!")
            else:
                st.error("Failed to save prompt version.")


# =============================================================================
# MODULE 3: TEST CASE MANAGER
# =============================================================================
elif page == "🧪 Test Cases":
    st.title("🧪 Red-Team Test Case Manager")
    st.markdown(
        "Manage the test suite designed to probe for role breaches, scope leakages, "
        "instruction overrides, hallucinations, and unhandled edge inputs."
    )

    all_tests = test_manager.get_all()

    # Category Filter and Metrics
    col_f1, col_f2 = st.columns([1, 2])
    with col_f1:
        cat_filter = st.selectbox("Filter Category", ["All"] + TEST_CATEGORIES)
    with col_f2:
        search_query = st.text_input("Search Tests", placeholder="Search by test name or query text...")

    filtered_tests = test_manager.get_by_category(cat_filter)
    if search_query:
        filtered_tests = [
            t for t in filtered_tests
            if search_query.lower() in t.get("name", "").lower()
            or search_query.lower() in t.get("input", "").lower()
            or search_query.lower() in t.get("id", "").lower()
        ]

    st.caption(f"Displaying **{len(filtered_tests)}** of **{len(all_tests)}** test cases.")

    # Table View of Tests
    table_data = []
    for t in filtered_tests:
        table_data.append({
            "ID": t.get("id"),
            "Category": t.get("category"),
            "Name": t.get("name"),
            "Input Query": t.get("input"),
            "Severity": t.get("severity", "Medium"),
        })
    st.dataframe(pd.DataFrame(table_data), use_container_width=True)

    # Detailed Expanders for individual tests
    with st.expander("🔍 Inspect Full Test Details"):
        for t in filtered_tests:
            st.markdown(f"**[{t.get('id')}] {t.get('name')}** (`{t.get('category')}` | Severity: `{t.get('severity')}`)")
            st.markdown(f"> **Input:** *\"{t.get('input')}\"*")
            st.markdown(f"> **Expected Behavior:** {t.get('expected_behavior')}")
            st.markdown("---")

    # Add / Edit / Delete Test Form Tabs
    st.subheader("🛠️ Test Suite Management")
    tab_add, tab_edit, tab_del, tab_gen = st.tabs([
        "➕ Add Custom Test",
        "✏️ Edit Test",
        "🗑️ Delete Test",
        "🤖 AI Test Generator"
    ])

    with tab_add:
        st.markdown("##### Create a New Red-Team Test Case")
        a_id = st.text_input("Test ID (leave blank to auto-generate)", placeholder="e.g. TC-16")
        a_cat = st.selectbox("Category", TEST_CATEGORIES, key="add_cat")
        a_name = st.text_input("Test Name", placeholder="Short descriptive name")
        a_input = st.text_area("User Test Input (Prompt)", placeholder="Enter the exact adversarial or normal query...")
        a_exp = st.text_area("Expected Behavior", placeholder="What should a safe chatbot do?")
        a_sev = st.selectbox("Severity", ["Low", "Medium", "High"], index=1, key="add_sev")

        if st.button("Add Test Case to Suite", type="primary"):
            if not a_name or not a_input:
                st.error("Please provide at least a test name and input query.")
            else:
                new_tc = {
                    "id": a_id.strip() if a_id else None,
                    "category": a_cat,
                    "name": a_name.strip(),
                    "input": a_input.strip(),
                    "expected_behavior": a_exp.strip(),
                    "severity": a_sev
                }
                if test_manager.add_test(new_tc):
                    st.success(f"Added test case {new_tc['id']} successfully!")
                    st.rerun()
                else:
                    st.error("Failed to save test case.")

    with tab_edit:
        st.markdown("##### Modify an Existing Test Case")
        test_ids = [t["id"] for t in all_tests]
        if test_ids:
            selected_id = st.selectbox("Select Test to Edit", test_ids)
            target = test_manager.get_by_id(selected_id)
            if target:
                e_name = st.text_input("Edit Name", value=target.get("name", ""))
                e_cat = st.selectbox("Edit Category", TEST_CATEGORIES, index=TEST_CATEGORIES.index(target.get("category", "Normal")))
                e_input = st.text_area("Edit Input", value=target.get("input", ""))
                e_exp = st.text_area("Edit Expected Behavior", value=target.get("expected_behavior", ""))
                e_sev = st.selectbox("Edit Severity", ["Low", "Medium", "High"], index=["Low", "Medium", "High"].index(target.get("severity", "Medium")))

                if st.button("Save Changes to Test Case"):
                    ok = test_manager.update_test(selected_id, {
                        "name": e_name,
                        "category": e_cat,
                        "input": e_input,
                        "expected_behavior": e_exp,
                        "severity": e_sev
                    })
                    if ok:
                        st.success(f"Updated test case {selected_id}!")
                        st.rerun()
                    else:
                        st.error("Failed to update test.")
        else:
            st.info("No test cases available to edit.")

    with tab_del:
        st.markdown("##### Remove a Test Case")
        if test_ids:
            del_id = st.selectbox("Select Test to Delete", test_ids, key="del_select")
            if st.button("Confirm Delete Test", type="secondary"):
                if test_manager.delete_test(del_id):
                    st.success(f"Deleted test case {del_id}!")
                    st.rerun()
                else:
                    st.error("Failed to delete test case.")
        else:
            st.info("No test cases to delete.")

    with tab_gen:
        st.markdown("##### Synthesize New Tests Using OpenAI API")
        if not openai_handler.is_configured():
            st.warning("⚠️ OpenAI API key is required to use AI test generation.")
        else:
            g_cat = st.selectbox("Target Generation Category", TEST_CATEGORIES, key="gen_cat")
            g_count = st.slider("Number of Test Cases to Generate", min_value=1, max_value=5, value=2)
            if st.button("Generate Tests with AI", type="primary"):
                with st.spinner("Generating adversarial test vectors with OpenAI..."):
                    gen_res = test_manager.generate_ai_tests(
                        openai_handler=openai_handler,
                        chatbot_role=st.session_state.get("chatbot_role", "University Helpdesk"),
                        permitted_topics=st.session_state.get("permitted_topics", "Admissions, exams"),
                        restricted_topics=st.session_state.get("restricted_topics", "Hacking, crypto"),
                        category=g_cat,
                        count=g_count
                    )
                    if gen_res.get("success"):
                        new_items = gen_res.get("test_cases", [])
                        for item in new_items:
                            test_manager.add_test(item)
                        st.success(f"Successfully generated and added {len(new_items)} new test cases!")
                        st.rerun()
                    else:
                        st.error(f"Generation error: {gen_res.get('error')}")


# =============================================================================
# MODULE 4 & 5: RUN TESTS (AI TESTING & SAFETY EVALUATION ENGINE)
# =============================================================================
elif page == "▶️ Run Tests":
    st.title("▶️ Execute Red-Team Safety Testing")
    st.markdown(
        "Run the target system prompt through the OpenAI API against the selected red-team test inputs. "
        "Every response is captured in raw form and evaluated against the 5 safety criteria."
    )

    # Display active system prompt preview
    with st.expander("👀 View Active System Prompt Under Test", expanded=False):
        st.code(st.session_state["system_prompt"], language="text")

    # API Key requirement check
    if not openai_handler.is_configured():
        st.error(
            "🛑 **OpenAI API Key Missing:** Please provide an OpenAI API key in the sidebar under "
            "'Runtime API Settings' to execute live model tests."
        )

    all_tests = test_manager.get_all()
    if not all_tests:
        st.warning("No test cases found in test suite. Please add test cases in the Test Cases manager.")

    # Selection Controls
    st.subheader("1. Select Test Cases to Execute")
    select_all = st.checkbox("Select All 15 Tests", value=True)

    selected_test_ids = []
    if select_all:
        selected_test_ids = [t["id"] for t in all_tests]
    else:
        # Multi-select
        options = [f"{t['id']} - {t['name']} ({t['category']})" for t in all_tests]
        chosen = st.multiselect("Choose specific tests:", options=options, default=options[:5])
        selected_test_ids = [c.split(" - ")[0] for c in chosen]

    selected_tests = [t for t in all_tests if t["id"] in selected_test_ids]
    st.info(f"📋 **{len(selected_tests)}** test case(s) selected for execution.")

    # Execution Parameters
    col_p1, col_p2 = st.columns(2)
    with col_p1:
        temperature = st.slider("Model Temperature", min_value=0.0, max_value=1.0, value=0.2, step=0.05,
                               help="Lower temperatures yield more deterministic responses.")
    with col_p2:
        session_label = st.text_input("Session Name / Tag", value="University_Safety_Run")

    # Big Run Button
    st.markdown("---")
    if st.button("🚀 Run Selected Tests Now", type="primary", disabled=len(selected_tests) == 0):
        if not openai_handler.is_configured():
            st.error("Cannot proceed: OpenAI API key is required for live runtime testing.")
        else:
            progress_bar = st.progress(0.0)
            status_text = st.empty()

            total_count = len(selected_tests)
            completed_runs = []

            # Step 1: Execute Chatbot Inference
            status_text.markdown("⏳ **Phase 1/2: Generating actual chatbot responses from OpenAI...**")
            for i, tc in enumerate(selected_tests):
                status_text.markdown(f"🤖 Generating response for **{tc.get('id')}**: *{tc.get('name')}* ({i+1}/{total_count})...")
                run_res = testing_engine.run_single_test(
                    system_prompt=st.session_state["system_prompt"],
                    test_case=tc,
                    temperature=temperature
                )
                completed_runs.append(run_res)
                progress_bar.progress((i + 1) / (total_count * 2))

            # Step 2: Evaluate Responses
            status_text.markdown("⚖️ **Phase 2/2: Safety Evaluation Engine assessing responses...**")
            evaluated_runs = []
            for j, run in enumerate(completed_runs):
                status_text.markdown(f"🔍 Evaluating safety criteria for **{run.get('test_id')}** ({j+1}/{total_count})...")
                eval_res = safety_evaluator.evaluate_response(
                    system_prompt=st.session_state["system_prompt"],
                    test_case=run,
                    actual_response=run.get("actual_response", "")
                )
                
                # Merge
                merged = dict(run)
                merged.update({
                    "overall_status": eval_res.get("overall_status", "NEEDS REVIEW"),
                    "eval_reason": eval_res.get("reason", "Evaluation completed."),
                    "eval_suggestions": eval_res.get("suggestions", ""),
                    "criteria": eval_res.get("criteria", {})
                })
                evaluated_runs.append(merged)
                progress_bar.progress(0.5 + ((j + 1) / (total_count * 2)))

            # Save Session to Disk and State
            session_file = results_manager.save_session(
                session_name=session_label,
                system_prompt=st.session_state["system_prompt"],
                results=evaluated_runs,
                notes=f"Model: {st.session_state['model_name']}, Temp: {temperature}"
            )

            st.session_state["current_test_results"] = evaluated_runs
            st.session_state["latest_session_id"] = session_file

            status_text.empty()
            progress_bar.progress(1.0)
            st.success(f"🎉 Testing session completed! Executed {len(evaluated_runs)} tests. Saved to results.")
            st.balloons()


# =============================================================================
# MODULE 6: RESULTS DASHBOARD
# =============================================================================
elif page == "📈 Results":
    st.title("📈 Red-Team Testing Results & Audit Log")
    st.markdown(
        "Analyze real model outputs, evaluation decisions, criteria breakdowns, "
        "and security weaknesses identified during testing."
    )

    # Session Selector: Current active run or historical sessions from disk
    saved_sessions = results_manager.list_sessions()
    session_options = ["Current Active Session"] + [f"{s['session_name']} ({s['timestamp']})" for s in saved_sessions]
    
    selected_sess = st.selectbox("Select Session to Inspect", session_options)

    if selected_sess == "Current Active Session":
        active_results = st.session_state.get("current_test_results", [])
    else:
        chosen_idx = session_options.index(selected_sess) - 1
        filepath = saved_sessions[chosen_idx]["filepath"]
        loaded = results_manager.load_session(filepath)
        active_results = loaded.get("results", []) if loaded else []

    if not active_results:
        st.info("No test results found for this session. Run tests in 'Run Tests' to inspect real results.")
    else:
        stats = results_manager.calculate_statistics(active_results)

        # Top KPIs
        r1, r2, r3, r4, r5 = st.columns(5)
        with r1:
            st.metric("Total Tests", stats["total"])
        with r2:
            st.metric("Passed", stats["passed"])
        with r3:
            st.metric("Failed", stats["failed"])
        with r4:
            st.metric("Needs Review", stats["needs_review"])
        with r5:
            st.metric("Pass Rate", f"{stats['pass_rate']}%")

        # Interactive Charts Row
        c_left, c_right = st.columns(2)
        with c_left:
            st.subheader("Outcome Distribution")
            fig_p = px.pie(
                names=["Passed", "Failed", "Needs Review"],
                values=[stats["passed"], stats["failed"], stats["needs_review"]],
                color=["Passed", "Failed", "Needs Review"],
                color_discrete_map={"Passed": "#2ec4b6", "Failed": "#e63946", "Needs Review": "#ffb703"},
                hole=0.45
            )
            fig_p.update_layout(paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)", font=dict(color="#f8f9fa"))
            st.plotly_chart(fig_p, use_container_width=True)

        with c_right:
            st.subheader("Category Breakdown")
            c_data = stats.get("category_stats", {})
            cats = list(c_data.keys())
            c_df = pd.DataFrame([
                {"Category": c, "Passed": c_data[c]["passed"], "Failed": c_data[c]["failed"], "Review": c_data[c]["review"]}
                for c in cats
            ])
            if not c_df.empty:
                fig_c = px.bar(
                    c_df,
                    x="Category",
                    y=["Passed", "Failed", "Review"],
                    color_discrete_map={"Passed": "#2ec4b6", "Failed": "#e63946", "Review": "#ffb703"},
                    barmode="group"
                )
                fig_c.update_layout(paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)", font=dict(color="#f8f9fa"))
                st.plotly_chart(fig_c, use_container_width=True)

        # Identified Weaknesses Summary Box
        st.subheader("⚠️ Common Weaknesses Diagnosed")
        failures = [r for r in active_results if r.get("overall_status") == "FAIL"]
        if failures:
            st.warning(f"Detected **{len(failures)} failure(s)** requiring prompt hardening:")
            for f in failures:
                st.markdown(f"- **[{f.get('category')}] {f.get('test_name', f.get('test_id'))}:** {f.get('eval_reason')}")
        else:
            st.success("✅ Zero critical failures detected! Chatbot respected all safety boundaries.")

        # Detailed Test Results Table with Expanders
        st.subheader("📋 Comprehensive Test Logs")
        
        # Filter by status
        status_filter = st.radio("Filter Status", ["All", "PASS", "FAIL", "NEEDS REVIEW"], horizontal=True)
        display_results = active_results
        if status_filter != "All":
            display_results = [r for r in active_results if r.get("overall_status", "").upper() == status_filter]

        for r in display_results:
            st_val = r.get("overall_status", "NEEDS REVIEW")
            badge_class = "badge-pass" if st_val == "PASS" else ("badge-fail" if st_val == "FAIL" else "badge-review")

            with st.expander(f"[{r.get('test_id')}] {r.get('test_name')} — {r.get('category')} ({st_val})"):
                st.markdown(f"<span class='{badge_class}'>{st_val}</span>", unsafe_allow_html=True)
                st.markdown(f"**Test Input (User Prompt):**\n> *\"{r.get('test_input')}\"*")
                
                st.markdown("**Actual Chatbot Response:**")
                st.code(r.get("actual_response", ""), language="text")

                st.markdown(f"**Evaluator Decision Reason:**\n{r.get('eval_reason', 'N/A')}")
                if r.get("eval_suggestions"):
                    st.markdown(f"💡 **Suggestion:** {r.get('eval_suggestions')}")

                # Criteria Breakdown Table
                crit = r.get("criteria", {})
                if crit:
                    st.markdown("**Five Safety Criteria Breakdown:**")
                    crit_rows = []
                    for c_key, c_val in crit.items():
                        crit_rows.append({
                            "Criterion": c_key.replace("_", " ").title(),
                            "Passed": "✅ Yes" if c_val.get("passed") else "❌ No",
                            "Details": c_val.get("reason", "")
                        })
                    st.dataframe(pd.DataFrame(crit_rows), use_container_width=True)

                st.caption(f"Latency: {r.get('latency_sec', 0.0)}s | Tokens: {r.get('tokens_used', 0)} | Timestamp: {r.get('timestamp')}")


# =============================================================================
# MODULE 7: PROMPT IMPROVEMENT ENGINE
# =============================================================================
elif page == "💡 Improve Prompt":
    st.title("💡 AI Prompt Improvement Engine")
    if st.session_state.get("just_adopted_msg"):
        st.success(f"🎉 **{st.session_state.pop('just_adopted_msg')}**")
    st.markdown(
        "Diagnose prompt vulnerabilities and automatically generate a hardened system prompt "
        "using OpenAI API based on empirical test failures."
    )

    current_results = st.session_state.get("current_test_results", [])
    failed_tests = [r for r in current_results if r.get("overall_status") == "FAIL"]

    col_orig, col_fail = st.columns([1, 1])
    with col_orig:
        st.subheader("Current Active Prompt")
        st.code(st.session_state["system_prompt"], language="text")

    with col_fail:
        st.subheader("Targeted Failures to Remediate")
        if failed_tests:
            st.error(f"Found **{len(failed_tests)}** test failure(s) in active test run.")
            for ft in failed_tests:
                st.markdown(f"- **[{ft.get('category')}] {ft.get('test_name')}:** {ft.get('eval_reason')}")
        else:
            st.info("No failures found in current active test session. You can still generate a defensively hardened prompt.")

    st.markdown("---")
    if st.button("🚀 Analyze Weaknesses & Synthesize Improved Prompt", type="primary"):
        if not openai_handler.is_configured():
            st.error("OpenAI API key is required to synthesize improved system prompts.")
        else:
            with st.spinner("Analyzing vulnerabilities and generating hardened prompt via OpenAI..."):
                imp_res = prompt_improver.improve_prompt(
                    original_prompt=st.session_state["system_prompt"],
                    chatbot_role=st.session_state.get("chatbot_role", "University Helpdesk"),
                    permitted_topics=st.session_state.get("permitted_topics", "Admissions, exams"),
                    restricted_topics=st.session_state.get("restricted_topics", "Hacking, crypto"),
                    failed_tests=failed_tests
                )

                if imp_res.get("success"):
                    st.session_state["suggested_prompt"] = imp_res.get("improved_prompt")
                    st.session_state["suggested_explanation"] = imp_res.get("explanation_of_changes")
                    st.session_state["suggested_weaknesses"] = imp_res.get("weaknesses_addressed")
                    st.session_state["suggested_techniques"] = imp_res.get("hardening_techniques_applied")
                    st.success("Hardened system prompt generated successfully!")
                else:
                    st.error(f"Error generating improvement: {imp_res.get('error')}")

    # Display Suggested Prompt if available
    if "suggested_prompt" in st.session_state:
        st.subheader("🛡️ Suggested Improved System Prompt")
        edited_improved_prompt = st.text_area(
            "Review and edit the suggested prompt before adopting:",
            value=st.session_state["suggested_prompt"],
            height=200
        )
        st.session_state["suggested_prompt"] = edited_improved_prompt

        st.markdown("#### 🔍 Architectural Changes & Remediation")
        st.info(st.session_state.get("suggested_explanation", ""))

        c_w, c_t = st.columns(2)
        with c_w:
            st.markdown("**Weaknesses Addressed:**")
            for w in st.session_state.get("suggested_weaknesses", []):
                st.markdown(f"- ✅ {w}")
        with c_t:
            st.markdown("**Hardening Techniques Applied:**")
            for t in st.session_state.get("suggested_techniques", []):
                st.markdown(f"- 🛡️ {t}")

        # Action: Save as Version & Adopt
        st.markdown("---")
        save_col1, save_col2 = st.columns(2)
        with save_col1:
            target_v = st.text_input("Save as Version Tag", value="V2", max_chars=10)
        with save_col2:
            target_label = st.text_input("Version Label", value="Hardened Injection-Resistant Prompt")

        if st.button("Adopt & Set as Current Active System Prompt", type="primary"):
            st.session_state["system_prompt"] = edited_improved_prompt
            results_manager.save_prompt_version(
                version_number=target_v,
                name=target_label,
                prompt_content=edited_improved_prompt,
                description=st.session_state.get("suggested_explanation", "Improved prompt synthesized from test failures.")
            )
            st.session_state["just_adopted_msg"] = f"Adopted hardened prompt as current active prompt and saved as version {target_v}!"
            st.rerun()


# =============================================================================
# MODULE 8: PROMPT VERSION HISTORY
# =============================================================================
elif page == "⚖️ Compare Versions":
    st.title("⚖️ Baseline vs Improved Prompt Comparison")
    st.markdown(
        "Demonstrate concrete empirical progress: Run identical test cases against two prompt versions "
        "(e.g. Baseline V1 vs Hardened V4) and compare pass rates, response fidelity, and vulnerability reductions."
    )

    versions = results_manager.get_prompt_versions()

    # Pre-populate sample versions if none saved yet
    if not versions:
        st.info(
            "No prompt versions have been formally saved to history yet. "
            "You can save versions in 'System Prompt' or 'Improve Prompt', or load starter benchmarks below."
        )
        if st.button("Seed Default Versions (V1 Baseline & V4 Hardened)"):
            v1_text = open(os.path.join(os.path.dirname(__file__), "prompts", "chatbot_v1.txt"), "r", encoding="utf-8").read().strip()
            v4_text = open(os.path.join(os.path.dirname(__file__), "prompts", "chatbot_v4.txt"), "r", encoding="utf-8").read().strip()
            results_manager.save_prompt_version("V1", "Baseline University Prompt", v1_text, "Basic role instructions without defensive constraints.")
            results_manager.save_prompt_version("V4", "Final Refined Prompt", v4_text, "Full instruction hierarchy, anti-hallucination, and injection defenses.")
            st.success("Seeded V1 and V4 versions!")
            st.rerun()
    else:
        v_keys = [f"{v['version']} - {v['name']}" for v in versions]

        col_va, col_vb = st.columns(2)
        with col_va:
            choice_a = st.selectbox("Baseline Prompt (Version A)", v_keys, index=0)
            target_a = next(v for v in versions if f"{v['version']} - {v['name']}" == choice_a)
            st.caption(f"**Prompt A Text ({target_a['version']}):**")
            st.code(target_a["prompt_content"], language="text")

        with col_vb:
            choice_b = st.selectbox("Improved Prompt (Version B)", v_keys, index=min(1, len(v_keys) - 1))
            target_b = next(v for v in versions if f"{v['version']} - {v['name']}" == choice_b)
            st.caption(f"**Prompt B Text ({target_b['version']}):**")
            st.code(target_b["prompt_content"], language="text")

        st.subheader("Select Comparison Test Set")
        all_tests = test_manager.get_all()
        categories_list = getattr(test_manager, "CATEGORIES", ["Normal", "Out-of-Scope", "Prompt Injection", "Edge Case"])
        comp_categories = st.multiselect("Filter Test Categories to Run", categories_list, default=categories_list)
        comp_tests = [t for t in all_tests if t.get("category") in comp_categories]

        st.caption(f"Will execute **{len(comp_tests)}** test cases against both Prompt A and Prompt B.")

        if st.button("🚀 Run Comparative Benchmark", type="primary", disabled=len(comp_tests) == 0):
            if not openai_handler.is_configured():
                st.error("OpenAI API key is required to execute comparative testing.")
            else:
                progress = st.progress(0.0)
                status = st.empty()

                tot = len(comp_tests)
                runs_a = []
                runs_b = []

                # Benchmark Version A
                status.markdown(f"⏳ Running Version A ({target_a['version']}) against test suite...")
                for i, tc in enumerate(comp_tests):
                    status.markdown(f"Running Version A on {tc['id']} ({i+1}/{tot})...")
                    r_a = testing_engine.run_single_test(target_a["prompt_content"], tc)
                    eval_a = safety_evaluator.evaluate_response(target_a["prompt_content"], r_a, r_a.get("actual_response", ""))
                    r_a.update({
                        "overall_status": eval_a.get("overall_status", "NEEDS REVIEW"),
                        "eval_reason": eval_a.get("reason", "")
                    })
                    runs_a.append(r_a)
                    progress.progress((i + 1) / (tot * 2))

                # Benchmark Version B
                status.markdown(f"⏳ Running Version B ({target_b['version']}) against test suite...")
                for j, tc in enumerate(comp_tests):
                    status.markdown(f"Running Version B on {tc['id']} ({j+1}/{tot})...")
                    r_b = testing_engine.run_single_test(target_b["prompt_content"], tc)
                    eval_b = safety_evaluator.evaluate_response(target_b["prompt_content"], r_b, r_b.get("actual_response", ""))
                    r_b.update({
                        "overall_status": eval_b.get("overall_status", "NEEDS REVIEW"),
                        "eval_reason": eval_b.get("reason", "")
                    })
                    runs_b.append(r_b)
                    progress.progress(0.5 + ((j + 1) / (tot * 2)))

                status.empty()
                progress.progress(1.0)

                # Store in session state
                st.session_state["comparison_data"] = {
                    "version_a": target_a["version"],
                    "version_b": target_b["version"],
                    "stats_a": results_manager.calculate_statistics(runs_a),
                    "stats_b": results_manager.calculate_statistics(runs_b),
                    "runs_a": runs_a,
                    "runs_b": runs_b
                }
                st.success("Comparative benchmark completed!")

        # Render Comparison Results if present
        if "comparison_data" in st.session_state:
            cmp = st.session_state["comparison_data"]
            s_a = cmp["stats_a"]
            s_b = cmp["stats_b"]

            st.markdown("### 📊 Benchmark Scoreboard")
            sc1, sc2, sc3, sc4 = st.columns(4)
            with sc1:
                st.metric(f"Pass Rate ({cmp['version_a']})", f"{s_a['pass_rate']}%")
            with sc2:
                delta_rate = round(s_b["pass_rate"] - s_a["pass_rate"], 1)
                st.metric(f"Pass Rate ({cmp['version_b']})", f"{s_b['pass_rate']}%", delta=f"{delta_rate:+}%")
            with sc3:
                st.metric(f"Failures ({cmp['version_a']})", s_a["failed"])
            with sc4:
                delta_fails = s_b["failed"] - s_a["failed"]
                st.metric(f"Failures ({cmp['version_b']})", s_b["failed"], delta=f"{delta_fails:+}", delta_color="inverse")

            # Comparative Grouped Bar Chart
            st.subheader("Category-Wise Performance Comparison")
            all_c = list(set(list(s_a.get("category_stats", {}).keys()) + list(s_b.get("category_stats", {}).keys())))
            rate_a = [
                round((s_a["category_stats"][c]["passed"] / s_a["category_stats"][c]["total"]) * 100, 1)
                if c in s_a["category_stats"] and s_a["category_stats"][c]["total"] > 0 else 0
                for c in all_c
            ]
            rate_b = [
                round((s_b["category_stats"][c]["passed"] / s_b["category_stats"][c]["total"]) * 100, 1)
                if c in s_b["category_stats"] and s_b["category_stats"][c]["total"] > 0 else 0
                for c in all_c
            ]

            fig_cmp = go.Figure()
            fig_cmp.add_trace(go.Bar(name=f"Baseline ({cmp['version_a']})", x=all_c, y=rate_a, marker_color="#3a86ff"))
            fig_cmp.add_trace(go.Bar(name=f"Improved ({cmp['version_b']})", x=all_c, y=rate_b, marker_color="#2ec4b6"))
            fig_cmp.update_layout(
                barmode="group",
                paper_bgcolor="rgba(0,0,0,0)",
                plot_bgcolor="rgba(0,0,0,0)",
                font=dict(color="#f8f9fa"),
                yaxis=dict(title="Pass Rate (%)", range=[0, 105], gridcolor="#1e293b"),
                xaxis=dict(gridcolor="#1e293b"),
                height=320
            )
            st.plotly_chart(fig_cmp, use_container_width=True)

            # Side-by-Side Test Response Diff Table
            st.subheader("🔍 Side-by-Side Test Response Audit")
            for ra, rb in zip(cmp["runs_a"], cmp["runs_b"]):
                with st.expander(f"[{ra.get('test_id')}] {ra.get('test_name')} ({ra.get('category')})"):
                    st.markdown(f"**Test Input:** *\"{ra.get('test_input')}\"*")
                    d_col1, d_col2 = st.columns(2)
                    with d_col1:
                        st.markdown(f"**Baseline {cmp['version_a']} Response ({ra.get('overall_status')}):**")
                        st.code(ra.get("actual_response"), language="text")
                        st.caption(f"Reason: {ra.get('eval_reason')}")
                    with d_col2:
                        st.markdown(f"**Improved {cmp['version_b']} Response ({rb.get('overall_status')}):**")
                        st.code(rb.get("actual_response"), language="text")
                        st.caption(f"Reason: {rb.get('eval_reason')}")


# =============================================================================
# MODULE 10: EXPORT AND REPORTS
# =============================================================================
elif page == "📥 Export Reports":
    st.title("📥 Export Data & Technical Reports")
    st.markdown(
        "Download empirical testing data, CSV audit logs, test suite JSON, and formal Markdown summary reports "
        "ready for your Milestone 2 submission package."
    )

    current_results = st.session_state.get("current_test_results", [])
    active_prompt = st.session_state.get("system_prompt", "")

    ex_tab1, ex_tab2, ex_tab3, ex_tab4 = st.tabs([
        "📄 Markdown Summary Report",
        "📊 CSV Test Results",
        "🧪 Test Suite JSON",
        "📜 Prompt Versions JSON"
    ])

    with ex_tab1:
        st.subheader("Formal Markdown Testing Report")
        if current_results:
            md_content = results_manager.generate_markdown_report(
                session_name="PromptGuard_Testing_Session",
                system_prompt=active_prompt,
                results=current_results
            )
            st.text_area("Report Preview", value=md_content, height=260)
            st.download_button(
                label="⬇️ Download Markdown Report (.md)",
                data=md_content,
                file_name="PromptGuard_Safety_Report.md",
                mime="text/markdown",
                type="primary"
            )
        else:
            st.info("Execute at least one test session in 'Run Tests' to generate a full report.")

    with ex_tab2:
        st.subheader("Export Results to CSV")
        if current_results:
            csv_data = results_manager.export_results_csv(current_results)
            st.download_button(
                label="⬇️ Download Results CSV (.csv)",
                data=csv_data,
                file_name="promptguard_test_results.csv",
                mime="text/csv",
                type="primary"
            )
            st.caption("CSV includes: Test ID, Category, Name, Input, Response, Status, Reason, and Timestamp.")
            st.dataframe(pd.DataFrame(current_results)[["test_id", "category", "overall_status", "latency_sec"]], use_container_width=True)
        else:
            st.info("No test results to export yet.")

    with ex_tab3:
        st.subheader("Export Test Cases Suite to JSON")
        suite = test_manager.get_all()
        suite_json = json.dumps(suite, indent=2, ensure_ascii=False)
        st.download_button(
            label="⬇️ Download Test Cases (.json)",
            data=suite_json,
            file_name="promptguard_test_cases.json",
            mime="application/json",
            type="primary"
        )
        st.caption(f"Exports all {len(suite)} test cases with categories, inputs, and expected behaviors.")

    with ex_tab4:
        st.subheader("Export Prompt Version History")
        versions = results_manager.get_prompt_versions()
        v_json = json.dumps(versions, indent=2, ensure_ascii=False)
        st.download_button(
            label="⬇️ Download Prompt Versions (.json)",
            data=v_json,
            file_name="promptguard_prompt_versions.json",
            mime="application/json",
            type="primary"
        )
        st.caption(f"Exports {len(versions)} recorded prompt versions with release descriptions and test records.")


# =============================================================================
# MODULE 11: ABOUT & RESPONSIBLE AI
# =============================================================================
elif page == "🛡️ About / Responsible AI":
    st.title("🛡️ About PromptGuard & Responsible AI")
    st.markdown(
        "**PromptGuard** is an open-source, empirical prompt safety testing framework designed to evaluate, red-team, "
        "and harden AI chatbot system prompts against adversarial jailbreaks, scope violations, and hallucinated claims."
    )

    col_meta1, col_meta2 = st.columns(2)
    with col_meta1:
        st.markdown(
            """
            <div class="pg-panel">
                <h4 style="color:#48cae4; margin-top:0;">🎓 Academic Project Metadata</h4>
                <ul style="line-height:1.8;">
                    <li><b>Course:</b> SCSE4041 – Prompt Engineering Mini Project (Milestone 2)</li>
                    <li><b>Problem Pool ID:</b> C23 – Prompt Safety Tester (Red-Team Kit)</li>
                    <li><b>Team ID:</b> PE-B49-54</li>
                    <li><b>Batch / Group:</b> B49–64</li>
                    <li><b>Team Name:</b> AI Prompt Safety Tester</li>
                </ul>
            </div>
            """,
            unsafe_allow_html=True
        )

    with col_meta2:
        st.markdown(
            """
            <div class="pg-panel">
                <h4 style="color:#48cae4; margin-top:0;">👥 Project Team & Contributions</h4>
                <ul style="line-height:1.8;">
                    <li><b>Team Leader:</b> Kommalapati Venkata Sai Gowtham (S24CSEU2175)
                        <br><span style="color:#94a3b8; font-size:0.85rem;">Application integration, OpenAI API connection, testing engine and final demonstration</span>
                    </li>
                    <li style="margin-top:6px;"><b>Team Member:</b> Pulkit Chahar (S24CSEU2385)
                        <br><span style="color:#94a3b8; font-size:0.85rem;">Test-case design, evaluation rubric, prompt versions, test evidence and documentation</span>
                    </li>
                </ul>
            </div>
            """,
            unsafe_allow_html=True
        )

    st.subheader("⚖️ Single Source of Truth — Milestone 2 Numbers")
    truth_df = pd.DataFrame([
        {"Metric / Parameter": "Number of Prompts in Final Solution", "Required Minimum": 4, "PromptGuard Implementation": "4 Prompts (Chatbot, Test Gen, Safety Evaluator, Prompt Improver)"},
        {"Metric / Parameter": "Number of Red-Team Test Cases", "Required Minimum": 10, "PromptGuard Implementation": "15 Test Cases (4 Normal, 3 Out-of-Scope, 4 Injections, 4 Edge)"},
        {"Metric / Parameter": "Number of Prompt Versions", "Required Minimum": 3, "PromptGuard Implementation": "4 Versions (V1 Baseline, V2 Refusal, V3 Injection Resist, V4 Final)"},
        {"Metric / Parameter": "Runtime AI Model", "Required Minimum": "Real API", "PromptGuard Implementation": "OpenAI Python SDK (Responses API / Chat Completions)"},
        {"Metric / Parameter": "Deliverable Type", "Required Minimum": "App with Code", "PromptGuard Implementation": "Python Streamlit Web Application + GitHub Repo"},
    ])
    st.dataframe(truth_df, use_container_width=True)

    st.subheader("🛡️ Responsible AI & Ethical Red-Teaming Principles")
    st.markdown(
        """
        1. **Educational & Defensive Purpose:** PromptGuard is built to identify security and safety vulnerabilities in prompt engineering workflows so that developers can harden their systems before public deployment.
        2. **No Absolute Security Guarantee:** Successfully passing 15 test cases does not imply that an LLM is invulnerable to all possible future jailbreaks. Continuous testing and defense-in-depth are required.
        3. **LLM Evaluation Limitations:** AI-assisted evaluators can exhibit subtle biases or false classifications. Users must manually review any results flagged as *NEEDS REVIEW*.
        4. **Privacy & PII Protection:** Do not submit real personal data, passwords, or confidential institutional secrets into test case prompts.
        5. **API Key Security:** API keys are processed strictly in local execution memory or environment variables and are never stored in exports, repository files, or logs.
        """
    )

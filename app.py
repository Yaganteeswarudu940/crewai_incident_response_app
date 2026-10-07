import os
import streamlit as st
from src.flow import IncidentResponseFlow, IncidentState

st.set_page_config(
    page_title="Agentic Incident Response Demo (Gemini)",
    page_icon="🤖",
    layout="wide"
)

st.title("🤖 CrewAI Agentic Flow: Incident Response Room")
st.caption("Demonstrating multi-agent orchestration powered by Google Gemini.")

# API Key Sidebar Configuration
with st.sidebar:
    st.header("⚙️ Configuration")
    gemini_key = st.text_input("Gemini API Key", type="password", help="Enter Google AI Studio key to run LLM tasks.")
    if gemini_key:
        os.environ["GEMINI_API_KEY"] = gemini_key

    st.markdown("---")
    st.markdown("### How the Flow Works")
    st.markdown("""
    1. **@start**: Diagnostician Agent triages raw logs.
    2. **@router**: Checks severity level.
    3. **@listen**: 
       - *High/Critical* ➔ Triggers Post-Mortem Writer.
       - *Low/Medium* ➔ Completes triage directly.
    """)

# UI Inputs
col1, col2 = st.columns([1, 2])

with col1:
    st.subheader("1. Incident Input")
    service = st.selectbox(
        "Affected Service",
        ["payment-gateway-v2", "auth-service", "inventory-db", "user-profile-api"]
    )
    
    sample_logs = {
        "High Severity": "ERROR 2026-10-08 00:12:01 [auth-service] Connection pool exhausted. 500 Internal Error rate > 85%. Database connection timeouts on primary node.",
        "Low Severity": "WARN 2026-10-08 00:14:22 [user-profile-api] Cache miss rate high (35%). Response time increased by 120ms. Minor latency spike."
    }
    
    log_preset = st.radio("Log Preset", list(sample_logs.keys()))
    logs_input = st.text_area("System Logs", value=sample_logs[log_preset], height=150)
    
    run_btn = st.button("🚀 Kickoff Agentic Flow", use_container_width=True)

# Flow Execution
with col2:
    st.subheader("2. Flow Execution & Output")
    
    if run_btn:
        if not os.environ.get("GEMINI_API_KEY"):
            st.error("Please enter your Gemini API Key in the sidebar to run the CrewAI Flow.")
        else:
            with st.spinner("Executing CrewAI Flow with Gemini..."):
                # Initialize state and flow
                flow = IncidentResponseFlow()
                flow.state.service_name = service
                flow.state.logs = logs_input
                
                # Kickoff execution
                flow.kickoff()
                
                # Display Results
                st.success("Flow Completed Successfully!")
                
                # Status Pills
                sev_color = "red" if flow.state.severity == "HIGH" else "green"
                st.markdown(f"**Assessed Severity Level:** :{sev_color}[{flow.state.severity}]")
                
                # Tabs for Outputs
                tab1, tab2 = st.tabs(["🔍 Triage & Diagnosis", "📄 Post-Mortem Report"])
                
                with tab1:
                    st.markdown(flow.state.diagnosis)
                    
                with tab2:
                    st.markdown(flow.state.postmortem)
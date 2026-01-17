"""
Recruitment Agent System - Streamlit UI
"""

import streamlit as st
import json
from datetime import datetime

# Page config
st.set_page_config(
    page_title="Recruitment Agent System",
    page_icon="👥",
    layout="wide"
)

# Initialize session state
if "initialized" not in st.session_state:
    st.session_state.initialized = False
    st.session_state.results = None
    st.session_state.processing = False

# Initialize system
@st.cache_resource
def init_system():
    """Initialize database and RAG system"""
    from database.db_connection import db
    from rag.policy_vectorstore import policy_rag

    try:
        db.init_database()

        # Add sample policy if empty
        count = db.fetch_one("SELECT COUNT(*) FROM policies")
        if count and count[0] == 0:
            sample_policy = """
            Compensation Policy COMP-POL-India-2025-v3.2

            Salary Structure:
            - Base salary ranges are determined by job level and location
            - SOE-1 Bangalore: INR 15,00,000 - 18,00,000
            - Equity bands: 100-200 stock options
            - Performance bonus: Up to 10% of base salary

            Benefits:
            - Healthcare coverage for employee and family
            - Provident Fund (PF) as per government regulations
            - Gratuity after 5 years of service
            - ESOP eligibility after 1 year

            Compliance Requirements:
            - Equal opportunity employer
            - No discrimination based on gender, religion, caste
            - Interview questions must be job-related only
            - Salary negotiations within approved band only
            """
            db.execute_query(
                """INSERT INTO policies (policy_id, policy_type, policy_name, policy_content, doc_id)
                   VALUES (:policy_id, :policy_type, :policy_name, :policy_content, :doc_id)""",
                {
                    "policy_id": "POL-COMP-001",
                    "policy_type": "compensation",
                    "policy_name": "Compensation Policy India 2025",
                    "policy_content": sample_policy,
                    "doc_id": "COMP-POL-India-2025-v3.2"
                }
            )

        policy_rag.refresh_vectorstore()
        return True
    except Exception as e:
        st.error(f"Initialization error: {e}")
        return False

# Sidebar
with st.sidebar:
    st.title("⚙️ Settings")

    st.subheader("Job Levels")
    job_levels = ["SOE-1", "SOE-2", "SOE-3", "Manager", "Senior Manager"]

    st.subheader("Locations")
    locations = ["Bangalore", "Mumbai", "Delhi", "Hyderabad", "Chennai"]

    st.divider()

    st.subheader("Database Info")
    if st.button("🔄 Refresh System"):
        st.cache_resource.clear()
        st.rerun()

    # Show database stats
    try:
        from database.db_connection import db
        candidates = db.fetch_one("SELECT COUNT(*) FROM candidates")
        interviews = db.fetch_one("SELECT COUNT(*) FROM interview_schedules")
        policies = db.fetch_one("SELECT COUNT(*) FROM policies")

        st.metric("Candidates", candidates[0] if candidates else 0)
        st.metric("Interviews", interviews[0] if interviews else 0)
        st.metric("Policies", policies[0] if policies else 0)
    except:
        pass

# Main content
st.title("👥 Recruitment Agent System")
st.markdown("*Multi-agent system for recruitment automation using LangGraph + Groq*")

# Initialize
with st.spinner("Initializing system..."):
    initialized = init_system()

if not initialized:
    st.error("Failed to initialize system. Please check your configuration.")
    st.stop()

st.success("✅ System ready!")

# Tabs
tab1, tab2, tab3 = st.tabs(["🚀 New Request", "📊 View Data", "📋 History"])

with tab1:
    st.subheader("Process Recruitment Request")

    # Quick templates
    col1, col2 = st.columns(2)
    with col1:
        template = st.selectbox(
            "Quick Templates",
            [
                "Custom Request",
                "Schedule interview for [Name] - SOE-1 Bangalore",
                "Process candidate [Name] for SOE-2 Mumbai",
                "Compute compensation for [Name] - Manager Delhi"
            ]
        )

    with col2:
        candidate_name = st.text_input("Candidate Name", value="Raja")

    # Build request
    if template == "Custom Request":
        user_request = st.text_area(
            "Enter your recruitment request:",
            height=100,
            placeholder="Example: Find candidate data for Raja. He's applying for SOE-1 Software Development Engineer position in Bangalore. Compute his compensation based on our salary bands and schedule an interview."
        )
    else:
        user_request = template.replace("[Name]", candidate_name)
        st.text_area("Request:", value=user_request, height=100, disabled=True)

    # Process button
    if st.button("🚀 Process Request", type="primary", disabled=st.session_state.processing):
        if not user_request.strip():
            st.warning("Please enter a recruitment request.")
        else:
            st.session_state.processing = True

            # Progress display
            progress_container = st.container()

            with progress_container:
                progress_bar = st.progress(0)
                status_text = st.empty()

                try:
                    from workflows.recruitment_graph import RecruitmentWorkflow

                    # Agent steps
                    steps = [
                        ("Interpreter Agent", "Understanding request..."),
                        ("Coordinator Agent", "Gathering data..."),
                        ("Researcher Agent", "Computing compensation..."),
                        ("Executor Agent", "Creating records..."),
                        ("Reviewer Agent", "Validating compliance...")
                    ]

                    status_text.info("🔄 Starting workflow...")
                    progress_bar.progress(10)

                    # Run workflow
                    workflow = RecruitmentWorkflow()

                    for i, (agent, desc) in enumerate(steps):
                        status_text.info(f"🤖 {agent}: {desc}")
                        progress_bar.progress(10 + (i + 1) * 15)

                    results = workflow.run(user_request)

                    progress_bar.progress(100)
                    status_text.success("✅ Workflow completed!")

                    st.session_state.results = results

                except Exception as e:
                    st.error(f"Error: {e}")
                    st.session_state.results = None

                st.session_state.processing = False

    # Display results
    if st.session_state.results:
        st.divider()
        st.subheader("📊 Results")

        results = st.session_state.results

        # Candidate info
        col1, col2, col3 = st.columns(3)

        candidate = results.get("candidate", {})
        research = results.get("research", {})
        review = results.get("review", {})

        with col1:
            st.markdown("### 👤 Candidate")
            st.write(f"**ID:** {candidate.get('candidate_id', 'N/A')}")
            verification = research.get("candidate_verification", {})
            st.write(f"**Name:** {verification.get('name', 'N/A')}")
            st.write(f"**Email:** {verification.get('email', 'N/A')}")
            st.write(f"**Location:** {verification.get('location', 'N/A')}")

        with col2:
            st.markdown("### 💰 Compensation")
            comp = research.get("compensation_proposal", {})
            st.write(f"**Base Salary:** ₹{comp.get('base_salary', 0):,.0f}")
            st.write(f"**Equity:** {comp.get('equity', 0)} options")
            st.write(f"**Bonus Target:** ₹{comp.get('bonus_target', 0):,.0f}")
            st.write(f"**Total:** ₹{comp.get('total_compensation', 0):,.0f}")

        with col3:
            st.markdown("### 📅 Interview")
            schedule = research.get("interview_schedule", {})
            st.write(f"**Type:** {schedule.get('interview_type', 'N/A')}")
            st.write(f"**Dates:** {', '.join(schedule.get('proposed_dates', []))}")
            st.write(f"**Time:** {schedule.get('availability_window', 'N/A')}")

        # Review status
        st.divider()

        validation_status = review.get("validation_status", "UNKNOWN")
        if validation_status == "APPROVED":
            st.success(f"✅ Compliance Status: {validation_status}")
        else:
            st.warning(f"⚠️ Compliance Status: {validation_status}")

        # Compliance checks
        with st.expander("📋 Compliance Details"):
            checks = review.get("compliance_checks", {})
            for check_name, check_data in checks.items():
                status = check_data.get("status", "UNKNOWN")
                icon = "✅" if status == "PASS" else "❌"
                st.write(f"{icon} **{check_name.replace('_', ' ').title()}:** {check_data.get('details', '')}")

            if review.get("recommendations"):
                st.markdown("**Recommendations:**")
                for rec in review.get("recommendations", []):
                    st.write(f"• {rec}")

        # Email draft
        with st.expander("📧 Email Draft"):
            st.text(candidate.get("email_draft", "No email generated"))

        # Raw JSON
        with st.expander("🔍 Raw JSON Response"):
            st.json(results)

with tab2:
    st.subheader("📊 Database Overview")

    from database.db_connection import db

    col1, col2 = st.columns(2)

    with col1:
        st.markdown("### 👥 Candidates")
        try:
            candidates = db.fetch_all("SELECT candidate_id, name, email, location, status FROM candidates ORDER BY created_at DESC LIMIT 10")
            if candidates:
                import pandas as pd
                df = pd.DataFrame(candidates, columns=["ID", "Name", "Email", "Location", "Status"])
                st.dataframe(df, use_container_width=True)
            else:
                st.info("No candidates yet")
        except Exception as e:
            st.error(f"Error: {e}")

    with col2:
        st.markdown("### 📅 Interviews")
        try:
            interviews = db.fetch_all("SELECT interview_log_id, candidate_id, interview_type, scheduled_date, status FROM interview_schedules ORDER BY created_at DESC LIMIT 10")
            if interviews:
                import pandas as pd
                df = pd.DataFrame(interviews, columns=["ID", "Candidate", "Type", "Date", "Status"])
                st.dataframe(df, use_container_width=True)
            else:
                st.info("No interviews yet")
        except Exception as e:
            st.error(f"Error: {e}")

    st.markdown("### 💰 Compensation Proposals")
    try:
        proposals = db.fetch_all("SELECT proposal_id, candidate_id, base_salary, equity_amount, bonus_target, status FROM compensation_proposals ORDER BY created_at DESC LIMIT 10")
        if proposals:
            import pandas as pd
            df = pd.DataFrame(proposals, columns=["ID", "Candidate", "Base Salary", "Equity", "Bonus", "Status"])
            st.dataframe(df, use_container_width=True)
        else:
            st.info("No proposals yet")
    except Exception as e:
        st.error(f"Error: {e}")

    st.markdown("### 📜 Salary Bands")
    try:
        bands = db.fetch_all("SELECT job_level, location, base_range_min, base_range_max, equity_band_min, equity_band_max FROM salary_bands LIMIT 10")
        if bands:
            import pandas as pd
            df = pd.DataFrame(bands, columns=["Level", "Location", "Min Salary", "Max Salary", "Min Equity", "Max Equity"])
            st.dataframe(df, use_container_width=True)
        else:
            st.info("No salary bands configured")
    except Exception as e:
        st.error(f"Error: {e}")

with tab3:
    st.subheader("📋 Agent Execution History")

    try:
        from database.db_connection import db
        logs = db.fetch_all("SELECT agent_name, action, status, execution_time_ms, created_at FROM agent_logs ORDER BY created_at DESC LIMIT 20")
        if logs:
            import pandas as pd
            df = pd.DataFrame(logs, columns=["Agent", "Action", "Status", "Time (ms)", "Timestamp"])
            st.dataframe(df, use_container_width=True)
        else:
            st.info("No execution history yet")
    except Exception as e:
        st.error(f"Error: {e}")

# Footer
st.divider()
st.markdown("*Powered by LangGraph + Groq (Llama 3.3 70B) + SQLite*")

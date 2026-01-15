from langchain_core.prompts import ChatPromptTemplate
from config.settings import get_llm, AGENT_CONFIG
from config.prompts import EXECUTOR_PROMPT
from database.db_connection import db
from datetime import datetime
import json

class ExecutorAgent:
    """
    Creates candidate shells, schedules interviews, drafts emails, computes breakdowns
    """

    def __init__(self):
        self.config = AGENT_CONFIG["EXECUTOR"]
        self.llm = get_llm(temperature=self.config["temperature"])
        self.name = self.config["name"]

    def execute(self, research_results: dict, coordinated_data: dict) -> dict:
        """
        Execute actions: create records, schedule interviews, draft emails

        Args:
            research_results: Results from Researcher Agent
            coordinated_data: Data from Coordinator

        Returns:
            Execution results with IDs and confirmations
        """
        print(f"\n[{self.name}] Executing actions...")

        candidate_data = coordinated_data.get("candidate_data", {})

        # 1. Create/update candidate record
        candidate_id = self._create_candidate_record(candidate_data, research_results)

        # 2. Schedule interviews
        schedule_ids = self._schedule_interviews(candidate_id, research_results)

        # 3. Draft email
        email_draft = self._draft_email(candidate_data, research_results)

        # 4. Create compensation proposal record
        proposal_id = self._create_compensation_proposal(candidate_id, research_results)

        result = {
            "candidate_id": candidate_id,
            "schedule_ids": schedule_ids,
            "proposal_id": proposal_id,
            "email_draft": email_draft,
            "execution_status": "completed",
            "timestamp": datetime.now().isoformat()
        }

        print(f"[{self.name}] Execution completed successfully")
        return result

    def _create_candidate_record(self, candidate_data: dict, research_results: dict) -> str:
        """Create or update candidate in database"""
        verification = research_results.get("candidate_verification", {})

        candidate_id = candidate_data.get("candidate_id", f"CAND-{datetime.now().strftime('%Y%m%d-%H%M%S')}")

        query = """
            INSERT INTO candidates (candidate_id, name, email, location, resume_attached, status)
            VALUES (:candidate_id, :name, :email, :location, :resume_attached, :status)
            ON DUPLICATE KEY UPDATE
                name = :name,
                email = :email,
                location = :location,
                status = :status
        """

        try:
            db.execute_query(query, {
                "candidate_id": candidate_id,
                "name": verification.get("name", candidate_data.get("name", "Unknown")),
                "email": verification.get("email", candidate_data.get("email", "unknown@example.com")),
                "location": verification.get("location", candidate_data.get("location", "Unknown")),
                "resume_attached": candidate_data.get("resume_attached", False),
                "status": "interview_scheduled"
            })
            print(f"[{self.name}] Created/updated candidate record: {candidate_id}")
        except Exception as e:
            print(f"[{self.name}] Error creating candidate record: {e}")

        return candidate_id

    def _schedule_interviews(self, candidate_id: str, research_results: dict) -> list:
        """Schedule interviews in database"""
        interview_schedule = research_results.get("interview_schedule", {})

        schedule_ids = []

        # Create interview schedule records
        for date in interview_schedule.get("proposed_dates", [])[:1]:  # Take first date
            query = """
                INSERT INTO interview_schedules
                (candidate_id, interview_type, interview_log_id, scheduled_date,
                 recruiter, tech_interviewer, availability_window, status)
                VALUES
                (:candidate_id, :interview_type, :interview_log_id, :scheduled_date,
                 :recruiter, :tech_interviewer, :availability_window, :status)
            """

            interview_log_id = f"INT-{datetime.now().strftime('%Y%m%d-%H%M%S')}"

            try:
                db.execute_query(query, {
                    "candidate_id": candidate_id,
                    "interview_type": interview_schedule.get("interview_type", "Technical Interview"),
                    "interview_log_id": interview_log_id,
                    "scheduled_date": f"{date} 14:00:00",
                    "recruiter": interview_schedule.get("recruiters", ["Recruiter"])[0],
                    "tech_interviewer": ", ".join(interview_schedule.get("tech_interviewers", ["Tech Lead"])),
                    "availability_window": interview_schedule.get("availability_window", "10:00-16:00"),
                    "status": "scheduled"
                })
                schedule_ids.append(interview_log_id)
                print(f"[{self.name}] Scheduled interview: {interview_log_id}")
            except Exception as e:
                print(f"[{self.name}] Error scheduling interview: {e}")

        return schedule_ids

    def _draft_email(self, candidate_data: dict, research_results: dict) -> str:
        """Draft email invitation"""
        verification = research_results.get("candidate_verification", {})
        interview_schedule = research_results.get("interview_schedule", {})

        prompt = f"""Draft a professional interview invitation email:

Candidate: {verification.get('name', candidate_data.get('name'))}
Interview Type: {interview_schedule.get('interview_type')}
Proposed Dates: {', '.join(interview_schedule.get('proposed_dates', []))}
Time Window: {interview_schedule.get('availability_window')}

Keep it concise and professional."""

        messages = ChatPromptTemplate.from_template(prompt).format_messages()
        response = self.llm.invoke(messages)

        return response.content

    def _create_compensation_proposal(self, candidate_id: str, research_results: dict) -> int:
        """Create compensation proposal record"""
        compensation = research_results.get("compensation_proposal", {})

        query = """
            INSERT INTO compensation_proposals
            (candidate_id, base_salary, equity_amount, bonus_target, benefits_summary, status)
            VALUES
            (:candidate_id, :base_salary, :equity_amount, :bonus_target, :benefits_summary, :status)
        """

        try:
            result = db.execute_query(query, {
                "candidate_id": candidate_id,
                "base_salary": compensation.get("base_salary", 0),
                "equity_amount": compensation.get("equity", 0),
                "bonus_target": compensation.get("bonus_target", 0),
                "benefits_summary": compensation.get("justification", ""),
                "status": "draft"
            })
            proposal_id = result.lastrowid
            print(f"[{self.name}] Created compensation proposal: {proposal_id}")
            return proposal_id
        except Exception as e:
            print(f"[{self.name}] Error creating compensation proposal: {e}")
            return 0

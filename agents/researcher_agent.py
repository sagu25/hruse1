from langchain_core.prompts import ChatPromptTemplate
from config.settings import get_llm, AGENT_CONFIG
from config.prompts import RESEARCHER_PROMPT
import json

class ResearcherAgent:
    """
    Identifies/verifies candidates, computes compensation, proposes interview schedules
    """

    def __init__(self):
        self.config = AGENT_CONFIG["RESEARCHER"]
        self.llm = get_llm(temperature=self.config["temperature"])
        self.name = self.config["name"]

    def research(self, task: dict, coordinated_data: dict) -> dict:
        """
        Research and propose compensation and interview schedule

        Args:
            task: Original task from Interpreter
            coordinated_data: Data from Coordinator (salary bands, policies, candidate)

        Returns:
            Research results with compensation and interview proposals
        """
        print(f"\n[{self.name}] Researching candidate and computing compensation...")

        candidate_data = coordinated_data.get("candidate_data", {})
        salary_band = coordinated_data.get("salary_bands", {})
        policies = coordinated_data.get("policies", [])

        # Format policies for prompt
        policy_text = "\n".join([p["content"][:500] for p in policies[:3]]) if policies else "No specific policies retrieved"

        prompt = ChatPromptTemplate.from_template(
            RESEARCHER_PROMPT + """

Return JSON with this structure:
{{
    "candidate_verification": {{
        "name": "candidate name",
        "email": "candidate email",
        "location": "location",
        "suitability": "brief assessment"
    }},
    "compensation_proposal": {{
        "base_salary": number,
        "equity": number,
        "bonus_target": number,
        "total_compensation": number,
        "justification": "why this amount"
    }},
    "interview_schedule": {{
        "interview_type": "type",
        "proposed_dates": ["date options"],
        "recruiters": ["recruiter names"],
        "tech_interviewers": ["interviewer names"],
        "availability_window": "time window"
    }},
    "compliance_notes": ["any compliance considerations"]
}}"""
        )

        messages = prompt.format_messages(
            task=json.dumps(task, indent=2),
            candidate_data=json.dumps(candidate_data, indent=2),
            salary_band=json.dumps(salary_band, indent=2),
            policies=policy_text
        )

        response = self.llm.invoke(messages)

        # Parse response
        try:
            content = response.content
            if "```json" in content:
                content = content.split("```json")[1].split("```")[0].strip()
            elif "```" in content:
                content = content.split("```")[1].split("```")[0].strip()

            result = json.loads(content)
            print(f"[{self.name}] Research completed")
            return result

        except json.JSONDecodeError as e:
            print(f"[{self.name}] Error parsing response: {e}")
            # Return fallback with reasonable defaults from salary band
            return self._create_fallback_proposal(candidate_data, salary_band)

    def _create_fallback_proposal(self, candidate_data: dict, salary_band: dict) -> dict:
        """Create fallback proposal if LLM response parsing fails"""
        base_min = salary_band.get("base_range_min", 1500000)
        base_max = salary_band.get("base_range_max", 1800000)
        equity_min = salary_band.get("equity_band_min", 100)
        equity_max = salary_band.get("equity_band_max", 200)

        # Use midpoint of ranges
        base_salary = (base_min + base_max) / 2
        equity = (equity_min + equity_max) / 2

        return {
            "candidate_verification": {
                "name": candidate_data.get("name", "Unknown"),
                "email": candidate_data.get("email", "unknown@example.com"),
                "location": candidate_data.get("location", "Unknown"),
                "suitability": "Candidate meets basic requirements"
            },
            "compensation_proposal": {
                "base_salary": base_salary,
                "equity": equity,
                "bonus_target": base_salary * 0.1,
                "total_compensation": base_salary + (base_salary * 0.1),
                "justification": "Midpoint of salary band range"
            },
            "interview_schedule": {
                "interview_type": "Technical + HR Interview",
                "proposed_dates": ["2026-01-20", "2026-01-21", "2026-01-22"],
                "recruiters": ["Recruiter 1"],
                "tech_interviewers": ["Tech Lead 1", "Senior Engineer 1"],
                "availability_window": "10:00-16:00 IST"
            },
            "compliance_notes": ["Standard compliance checks required"]
        }

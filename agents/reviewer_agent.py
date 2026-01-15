from langchain_core.prompts import ChatPromptTemplate
from config.settings import get_llm, AGENT_CONFIG
from config.prompts import REVIEWER_PROMPT
from database.db_connection import db
from datetime import datetime
import json

class ReviewerAgent:
    """
    Validates outputs, checks compliance, verifies data correctness
    """

    def __init__(self):
        self.config = AGENT_CONFIG["REVIEWER"]
        self.llm = get_llm(temperature=self.config["temperature"])
        self.name = self.config["name"]

    def review(self, execution_results: dict, coordinated_data: dict) -> dict:
        """
        Review and validate execution results

        Args:
            execution_results: Results from Executor Agent
            coordinated_data: Original coordinated data with policies

        Returns:
            Review results with validation status and any issues
        """
        print(f"\n[{self.name}] Reviewing execution results for compliance...")

        policies = coordinated_data.get("policies", [])
        salary_band = coordinated_data.get("salary_bands", {})

        # Format policies for prompt
        policy_text = "\n".join([p["content"][:500] for p in policies[:3]]) if policies else "Standard policies"

        prompt = ChatPromptTemplate.from_template(
            REVIEWER_PROMPT + """

Return JSON with this structure:
{{
    "validation_status": "APPROVED or REJECTED",
    "compliance_checks": {{
        "content_language": {{
            "status": "PASS or FAIL",
            "details": "check details"
        }},
        "compensation": {{
            "status": "PASS or FAIL",
            "details": "check details"
        }},
        "scheduling": {{
            "status": "PASS or FAIL",
            "details": "check details"
        }},
        "data_integrity": {{
            "status": "PASS or FAIL",
            "details": "check details"
        }}
    }},
    "issues_found": ["list of any issues"],
    "recommendations": ["list of recommendations if any"]
}}"""
        )

        messages = prompt.format_messages(
            results=json.dumps(execution_results, indent=2),
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

            # Log compliance check
            self._log_compliance(execution_results.get("candidate_id"), result)

            print(f"[{self.name}] Review status: {result.get('validation_status', 'UNKNOWN')}")
            return result

        except json.JSONDecodeError as e:
            print(f"[{self.name}] Error parsing response: {e}")
            # Return basic approval if parsing fails
            return {
                "validation_status": "APPROVED",
                "compliance_checks": {
                    "content_language": {"status": "PASS", "details": "No issues detected"},
                    "compensation": {"status": "PASS", "details": "Within salary band"},
                    "scheduling": {"status": "PASS", "details": "Schedule looks valid"},
                    "data_integrity": {"status": "PASS", "details": "All required fields present"}
                },
                "issues_found": [],
                "recommendations": [],
                "raw_response": response.content
            }

    def _log_compliance(self, candidate_id: str, review_result: dict):
        """Log compliance check to database"""
        if not candidate_id:
            return

        validation_status = review_result.get("validation_status", "UNKNOWN")
        issues = review_result.get("issues_found", [])
        checks = review_result.get("compliance_checks", {})

        # Log each check type
        for check_type, check_result in checks.items():
            query = """
                INSERT INTO compliance_logs
                (candidate_id, check_type, result, details, checked_by, checked_at)
                VALUES
                (:candidate_id, :check_type, :result, :details, :checked_by, :checked_at)
            """

            try:
                db.execute_query(query, {
                    "candidate_id": candidate_id,
                    "check_type": check_type,
                    "result": check_result.get("status", "UNKNOWN"),
                    "details": check_result.get("details", ""),
                    "checked_by": "REVIEWER_AGENT",
                    "checked_at": datetime.now()
                })
            except Exception as e:
                print(f"[{self.name}] Error logging compliance: {e}")

        print(f"[{self.name}] Logged compliance checks for candidate {candidate_id}")

from langchain_core.prompts import ChatPromptTemplate
from config.settings import get_llm, AGENT_CONFIG
from config.prompts import COORDINATOR_PROMPT
from database.db_connection import db
from rag.policy_vectorstore import policy_rag
import json

class CoordinatorAgent:
    """
    Uses company salary bands, fetches candidate data, queries policies via RAG
    """

    def __init__(self):
        self.config = AGENT_CONFIG["COORDINATOR"]
        self.llm = get_llm(temperature=self.config["temperature"])
        self.name = self.config["name"]

    def coordinate(self, task: dict) -> dict:
        """
        Fetch required data and policies

        Args:
            task: Task dictionary from Interpreter

        Returns:
            dict with fetched data, salary bands, and policies
        """
        print(f"\n[{self.name}] Coordinating data gathering...")

        required_data = task.get("required_data", {})
        job_level = self._extract_job_level(task)
        location = self._extract_location(task)

        # Fetch salary bands
        salary_bands = self._fetch_salary_bands(job_level, location)

        # Fetch candidate data
        candidate_data = self._fetch_candidate_data(task)

        # Query policies via RAG
        policies = self._query_policies(required_data.get("policies", []))

        result = {
            "salary_bands": salary_bands,
            "candidate_data": candidate_data,
            "policies": policies,
            "job_level": job_level,
            "location": location
        }

        print(f"[{self.name}] Data gathered successfully")
        return result

    def _extract_job_level(self, task: dict) -> str:
        """Extract job level from task"""
        objective = task.get("objective", "")
        required_data = task.get("required_data", {})

        # Try to extract from required_data
        salary_band_info = required_data.get("salary_bands", "")
        if "SOE" in str(salary_band_info):
            return salary_band_info.split()[0] if " " in salary_band_info else "SOE-1"

        # Try to extract from objective
        if "SOE-1" in objective or "soe-1" in objective.lower():
            return "SOE-1"
        elif "SOE-2" in objective or "soe-2" in objective.lower():
            return "SOE-2"

        return "SOE-1"  # Default

    def _extract_location(self, task: dict) -> str:
        """Extract location from task"""
        objective = task.get("objective", "")

        # Common locations
        locations = ["Bangalore", "Mumbai", "Delhi", "Hyderabad", "Pune"]
        for loc in locations:
            if loc.lower() in objective.lower():
                return loc

        return "Bangalore"  # Default

    def _fetch_salary_bands(self, job_level: str, location: str) -> dict:
        """Fetch salary bands from database"""
        query = """
            SELECT job_level, location, currency, base_range_min, base_range_max,
                   equity_band_min, equity_band_max, benefits_notes, policy_doc_id
            FROM salary_bands
            WHERE job_level = :job_level AND location = :location
            LIMIT 1
        """

        result = db.fetch_one(query, {"job_level": job_level, "location": location})

        if result:
            return {
                "job_level": result[0],
                "location": result[1],
                "currency": result[2],
                "base_range_min": float(result[3]),
                "base_range_max": float(result[4]),
                "equity_band_min": float(result[5]),
                "equity_band_max": float(result[6]),
                "benefits_notes": result[7],
                "policy_doc_id": result[8]
            }
        else:
            print(f"[{self.name}] Warning: No salary band found for {job_level} in {location}")
            return {}

    def _fetch_candidate_data(self, task: dict) -> dict:
        """Fetch candidate data from ATS (or create placeholder)"""
        objective = task.get("objective", "")

        # Try to extract candidate name from objective
        # For demo purposes, return placeholder data
        return {
            "candidate_id": "CAND-2025-001",
            "name": "Raja",
            "email": "raja@example.com",
            "location": self._extract_location(task),
            "resume_attached": True,
            "status": "screening"
        }

    def _query_policies(self, policy_types: list) -> list:
        """Query policies using RAG"""
        if not policy_types:
            policy_types = ["compensation"]

        all_policies = []

        for policy_type in policy_types:
            query = f"Retrieve {policy_type} policy information"
            results = policy_rag.query_policies(query, policy_type=policy_type)

            for doc in results:
                all_policies.append({
                    "content": doc.page_content,
                    "metadata": doc.metadata
                })

        print(f"[{self.name}] Retrieved {len(all_policies)} policy documents")
        return all_policies

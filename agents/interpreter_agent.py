from langchain_core.prompts import ChatPromptTemplate
from config.settings import get_llm, AGENT_CONFIG
from config.prompts import INTERPRETER_PROMPT
import json

class InterpreterAgent:
    """
    Interprets user intent, decomposes tasks, sets constraints & success criteria
    """

    def __init__(self):
        self.config = AGENT_CONFIG["INTERPRETER"]
        self.llm = get_llm(temperature=self.config["temperature"])
        self.name = self.config["name"]

    def interpret(self, user_input: str) -> dict:
        """
        Interpret user request and decompose into tasks

        Args:
            user_input: Raw user request

        Returns:
            dict with objective, required_data, constraints, success_criteria
        """
        print(f"\n[{self.name}] Interpreting user request...")

        prompt = ChatPromptTemplate.from_template(
            INTERPRETER_PROMPT + """

Return your analysis as JSON with this structure:
{{
    "objective": "clear statement of what user wants",
    "required_data": {{
        "candidate_info": ["list of candidate fields needed"],
        "job_details": ["list of job fields needed"],
        "salary_bands": "job level and location",
        "policies": ["list of policy types needed"]
    }},
    "constraints": ["list of constraints to apply"],
    "success_criteria": ["list of success criteria"],
    "next_agent": "name of next agent to invoke"
}}"""
        )

        messages = prompt.format_messages(user_input=user_input)
        response = self.llm.invoke(messages)

        # Parse response
        try:
            # Extract JSON from markdown if present
            content = response.content
            if "```json" in content:
                content = content.split("```json")[1].split("```")[0].strip()
            elif "```" in content:
                content = content.split("```")[1].split("```")[0].strip()

            result = json.loads(content)
            print(f"[{self.name}] Objective: {result.get('objective', 'N/A')}")
            return result

        except json.JSONDecodeError as e:
            print(f"[{self.name}] Error parsing response: {e}")
            # Return structured fallback
            return {
                "objective": user_input,
                "required_data": {
                    "candidate_info": ["name", "email", "location"],
                    "job_details": ["title", "level", "location"],
                    "salary_bands": "unknown",
                    "policies": ["compensation", "hiring"]
                },
                "constraints": ["Follow company policies"],
                "success_criteria": ["Valid output", "Compliant with policies"],
                "next_agent": "COORDINATOR",
                "raw_response": response.content
            }

    def decompose_task(self, objective: str) -> list:
        """
        Break down objective into subtasks

        Args:
            objective: Main objective from interpretation

        Returns:
            List of subtasks
        """
        prompt = f"""Break down this recruitment task into specific subtasks:
Objective: {objective}

Return a JSON list of subtasks in order:
["subtask 1", "subtask 2", ...]"""

        messages = ChatPromptTemplate.from_template(prompt).format_messages()
        response = self.llm.invoke(messages)

        try:
            content = response.content
            if "```json" in content:
                content = content.split("```json")[1].split("```")[0].strip()
            elif "```" in content:
                content = content.split("```")[1].split("```")[0].strip()

            subtasks = json.loads(content)
            return subtasks if isinstance(subtasks, list) else [objective]

        except:
            return [objective]

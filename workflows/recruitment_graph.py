from langgraph.graph import StateGraph, END
from typing import TypedDict, Annotated
import operator
from agents.interpreter_agent import InterpreterAgent
from agents.coordinator_agent import CoordinatorAgent
from agents.researcher_agent import ResearcherAgent
from agents.executor_agent import ExecutorAgent
from agents.reviewer_agent import ReviewerAgent

# Define the state that will be passed between agents
class RecruitmentState(TypedDict):
    user_input: str
    interpreted_task: dict
    coordinated_data: dict
    research_results: dict
    execution_results: dict
    review_results: dict
    final_output: dict
    messages: Annotated[list, operator.add]

class RecruitmentWorkflow:
    """
    LangGraph workflow orchestrating all recruitment agents
    """

    def __init__(self):
        # Initialize all agents
        self.interpreter = InterpreterAgent()
        self.coordinator = CoordinatorAgent()
        self.researcher = ResearcherAgent()
        self.executor = ExecutorAgent()
        self.reviewer = ReviewerAgent()

        # Build the graph
        self.workflow = self._build_graph()

    def _build_graph(self):
        """Build the agent workflow graph"""
        workflow = StateGraph(RecruitmentState)

        # Add nodes for each agent
        workflow.add_node("interpreter", self._interpreter_node)
        workflow.add_node("coordinator", self._coordinator_node)
        workflow.add_node("researcher", self._researcher_node)
        workflow.add_node("executor", self._executor_node)
        workflow.add_node("reviewer", self._reviewer_node)

        # Define the flow
        workflow.set_entry_point("interpreter")
        workflow.add_edge("interpreter", "coordinator")
        workflow.add_edge("coordinator", "researcher")
        workflow.add_edge("researcher", "executor")
        workflow.add_edge("executor", "reviewer")
        workflow.add_edge("reviewer", END)

        return workflow.compile()

    def _interpreter_node(self, state: RecruitmentState) -> RecruitmentState:
        """Interpreter agent node"""
        interpreted_task = self.interpreter.interpret(state["user_input"])
        state["interpreted_task"] = interpreted_task
        state["messages"].append(f"[INTERPRETER] Interpreted task: {interpreted_task.get('objective', 'N/A')}")
        return state

    def _coordinator_node(self, state: RecruitmentState) -> RecruitmentState:
        """Coordinator agent node"""
        coordinated_data = self.coordinator.coordinate(state["interpreted_task"])
        state["coordinated_data"] = coordinated_data
        state["messages"].append(f"[COORDINATOR] Gathered data for {coordinated_data.get('job_level', 'N/A')}")
        return state

    def _researcher_node(self, state: RecruitmentState) -> RecruitmentState:
        """Researcher agent node"""
        research_results = self.researcher.research(
            state["interpreted_task"],
            state["coordinated_data"]
        )
        state["research_results"] = research_results
        comp = research_results.get("compensation_proposal", {})
        state["messages"].append(
            f"[RESEARCHER] Proposed compensation: {comp.get('base_salary', 0)} base"
        )
        return state

    def _executor_node(self, state: RecruitmentState) -> RecruitmentState:
        """Executor agent node"""
        execution_results = self.executor.execute(
            state["research_results"],
            state["coordinated_data"]
        )
        state["execution_results"] = execution_results
        state["messages"].append(
            f"[EXECUTOR] Created candidate {execution_results.get('candidate_id', 'N/A')}"
        )
        return state

    def _reviewer_node(self, state: RecruitmentState) -> RecruitmentState:
        """Reviewer agent node"""
        review_results = self.reviewer.review(
            state["execution_results"],
            state["coordinated_data"]
        )
        state["review_results"] = review_results
        state["messages"].append(
            f"[REVIEWER] Validation: {review_results.get('validation_status', 'N/A')}"
        )

        # Compile final output
        state["final_output"] = {
            "candidate": state["execution_results"],
            "research": state["research_results"],
            "review": review_results
        }

        return state

    def run(self, user_input: str) -> dict:
        """
        Run the recruitment workflow

        Args:
            user_input: User's recruitment request

        Returns:
            Final workflow results
        """
        print("\n" + "="*80)
        print("RECRUITMENT AGENT SYSTEM - WORKFLOW EXECUTION")
        print("="*80)

        initial_state = {
            "user_input": user_input,
            "interpreted_task": {},
            "coordinated_data": {},
            "research_results": {},
            "execution_results": {},
            "review_results": {},
            "final_output": {},
            "messages": []
        }

        # Execute the workflow
        final_state = self.workflow.invoke(initial_state)

        # Print execution log
        print("\n" + "-"*80)
        print("EXECUTION LOG:")
        for msg in final_state.get("messages", []):
            print(msg)
        print("-"*80)

        return final_state["final_output"]

"""
Recruitment Agent System - Main Entry Point

A multi-agent system using LangChain, LangGraph, and Gemini API for recruitment automation
"""

import os
import sys
from database.db_connection import db
from workflows.recruitment_graph import RecruitmentWorkflow
from rag.policy_vectorstore import policy_rag
import json

def initialize_system():
    """Initialize database and RAG system"""
    print("Initializing Recruitment Agent System...")

    # Initialize database
    print("\n1. Setting up database...")
    try:
        db.init_database()
        print("   [OK] Database initialized")
    except Exception as e:
        print(f"   [ERROR] Database initialization error: {e}")
        return False

    # Initialize RAG vectorstore
    print("\n2. Setting up RAG system...")
    try:
        # Add sample policy if database is empty
        sample_policy_query = "SELECT COUNT(*) FROM policies"
        count = db.fetch_one(sample_policy_query)

        if count and count[0] == 0:
            print("   Adding sample policy...")
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

            Scheduling Guidelines:
            - Minimum 2-hour buffer between interviews
            - Time zone considerations for remote candidates
            - Confirmation required 24 hours before interview
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
            print("   [OK] Sample policy added")

        # Refresh RAG vectorstore
        policy_rag.refresh_vectorstore()
        print("   [OK] RAG system initialized")
    except Exception as e:
        print(f"   [WARNING] RAG initialization error: {e}")
        print("   System will continue with fallback policy retrieval")

    print("\n[OK] System initialization complete!\n")
    return True

def run_example():
    """Run an example recruitment workflow"""
    print("\n" + "="*80)
    print("EXAMPLE: Scheduling interview for Raja (SOE-1 position in Bangalore)")
    print("="*80 + "\n")

    user_request = """
    Find candidate data for Raja. He's applying for SOE-1 Software Development Engineer
    position in Bangalore. Compute his compensation based on our salary bands and policy
    COMP-POL-India-2025-v3.2. Schedule an interview and send him the details.
    """

    # Create workflow and run
    workflow = RecruitmentWorkflow()
    results = workflow.run(user_request)

    # Display results
    print("\n" + "="*80)
    print("FINAL RESULTS:")
    print("="*80)
    print(json.dumps(results, indent=2, default=str))

def interactive_mode():
    """Run in interactive mode"""
    print("\n" + "="*80)
    print("RECRUITMENT AGENT SYSTEM - INTERACTIVE MODE")
    print("="*80)
    print("\nEnter recruitment requests (or 'quit' to exit)")
    print("Example: Schedule interview for candidate John for SOE-2 position in Mumbai\n")

    workflow = RecruitmentWorkflow()

    while True:
        try:
            user_input = input("\n> ").strip()

            if not user_input:
                continue

            if user_input.lower() in ['quit', 'exit', 'q']:
                print("Exiting...")
                break

            # Run workflow
            results = workflow.run(user_input)

            # Display key results
            print("\n" + "-"*80)
            print("RESULTS:")
            print(json.dumps(results, indent=2, default=str))
            print("-"*80)

        except KeyboardInterrupt:
            print("\n\nExiting...")
            break
        except Exception as e:
            print(f"\nError: {e}")

def main():
    """Main entry point"""
    # Check if .env file exists
    if not os.path.exists(".env"):
        print("ERROR: .env file not found!")
        print("Please copy .env.example to .env and configure your API keys")
        return 1

    # Initialize system
    if not initialize_system():
        print("\nSystem initialization failed. Please check the errors above.")
        return 1

    # Check command line arguments
    if len(sys.argv) > 1:
        if sys.argv[1] == "example":
            run_example()
        elif sys.argv[1] == "interactive":
            interactive_mode()
        else:
            print(f"Unknown command: {sys.argv[1]}")
            print("Usage: python main.py [example|interactive]")
    else:
        # Default: run example
        run_example()

    return 0

if __name__ == "__main__":
    sys.exit(main())

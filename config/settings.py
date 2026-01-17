import os
from dotenv import load_dotenv

load_dotenv()

# LLM Provider Configuration
LLM_PROVIDER = os.getenv("LLM_PROVIDER", "groq")  # Options: "groq", "gemini"

# Groq API Configuration
GROQ_API_KEY = os.getenv("GROQ_API_KEY")
GROQ_MODEL = os.getenv("GROQ_MODEL", "llama-3.3-70b-versatile")

# Gemini API Configuration (fallback)
GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY")
GEMINI_MODEL = os.getenv("GEMINI_MODEL", "gemini-2.0-flash")

# Common Configuration
TEMPERATURE = float(os.getenv("TEMPERATURE", "0.7"))

# Initialize LLM based on provider
def get_llm(temperature=None):
    """Get configured LLM instance based on provider"""
    temp = temperature or TEMPERATURE

    if LLM_PROVIDER == "groq":
        from langchain_groq import ChatGroq

        if not GROQ_API_KEY:
            raise ValueError("GROQ_API_KEY not found in environment variables. Please set it in .env file")

        return ChatGroq(
            model=GROQ_MODEL,
            temperature=temp,
            groq_api_key=GROQ_API_KEY
        )

    elif LLM_PROVIDER == "gemini":
        from langchain_google_genai import ChatGoogleGenerativeAI

        if not GOOGLE_API_KEY:
            raise ValueError("GOOGLE_API_KEY not found in environment variables. Please set it in .env file")

        return ChatGoogleGenerativeAI(
            model=GEMINI_MODEL,
            temperature=temp,
            google_api_key=GOOGLE_API_KEY
        )

    else:
        raise ValueError(f"Unsupported LLM provider: {LLM_PROVIDER}. Use 'groq' or 'gemini'")

# Agent Configuration
AGENT_CONFIG = {
    "INTERPRETER": {
        "name": "Interpreter Agent",
        "description": "Interprets user intent, decomposes tasks, sets constraints & success criteria",
        "temperature": 0.7
    },
    "COORDINATOR": {
        "name": "Coordinator Agent",
        "description": "Uses company salary bands, fetches candidate data, queries policies via RAG",
        "temperature": 0.5
    },
    "RESEARCHER": {
        "name": "Researcher Agent",
        "description": "Identifies/verifies candidates, computes compensation, proposes interview schedules",
        "temperature": 0.6
    },
    "EXECUTOR": {
        "name": "Executor Agent",
        "description": "Creates candidate shells, schedules interviews, drafts emails, computes breakdowns",
        "temperature": 0.5
    },
    "REVIEWER": {
        "name": "Reviewer Agent",
        "description": "Validates outputs, checks compliance, verifies data correctness",
        "temperature": 0.3
    }
}

# Database Configuration
DB_CONFIG = {
    "type": os.getenv("DB_TYPE", "sqlite"),
    "host": os.getenv("DB_HOST", "localhost"),
    "port": int(os.getenv("DB_PORT", "3306")),
    "name": os.getenv("DB_NAME", "recruitment_db"),
    "user": os.getenv("DB_USER", ""),
    "password": os.getenv("DB_PASSWORD", ""),
    "sqlite_path": os.getenv("SQLITE_DB_PATH", "recruitment.db")
}

# RAG Configuration
RAG_CONFIG = {
    "chunk_size": 1000,
    "chunk_overlap": 200,
    "top_k": 3,
    "vectorstore_path": "vectorstore/policies"
}

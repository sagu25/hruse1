# Recruitment Agent System

A multi-agent recruitment automation system using **LangChain**, **LangGraph**, **Gemini API**, and **SQL** for intelligent candidate processing, compensation calculation, and interview scheduling.

## Architecture

This system implements 5 specialized agents working together:

1. **Interpreter Agent** - Interprets user requests and decomposes tasks
2. **Coordinator Agent** - Fetches data from SQL database and queries policies via RAG
3. **Researcher Agent** - Computes compensation and proposes interview schedules
4. **Executor Agent** - Creates records, schedules interviews, drafts emails
5. **Reviewer Agent** - Validates outputs and checks compliance

## Tech Stack

- **LangChain + LangGraph** - Agent orchestration
- **Google Gemini API** - LLM (gemini-1.5-pro)
- **SQLAlchemy** - Database ORM
- **ChromaDB** - Vector database for RAG
- **SQLite/MySQL** - Relational database

## Setup on Company Laptop

### Step 1: Get Gemini API Key

1. Go to [Google AI Studio](https://makersuite.google.com/app/apikey)
2. Create a new API key
3. Copy the key (keep it secure!)

### Step 2: Install Python Dependencies

```bash
# Navigate to project directory
cd C:\Users\Admin\Desktop\ggd

# Install dependencies
pip install -r requirements.txt
```

### Step 3: Configure Environment

1. Copy `.env.example` to `.env`:
   ```bash
   copy .env.example .env
   ```

2. Edit `.env` and add your Gemini API key:
   ```
   GOOGLE_API_KEY=your_actual_gemini_api_key_here
   ```

3. For company laptop, use SQLite (no MySQL setup needed):
   ```
   DB_TYPE=sqlite
   SQLITE_DB_PATH=recruitment.db
   ```

### Step 4: Initialize and Run

```bash
# Run example workflow
python main.py example

# Or run in interactive mode
python main.py interactive
```

## Project Structure

```
ggd/
├── config/
│   ├── settings.py          # Gemini API configuration
│   └── prompts.py           # Agent prompts
├── database/
│   ├── schema.sql           # Database schema
│   └── db_connection.py     # SQL connection handler
├── agents/
│   ├── interpreter_agent.py
│   ├── coordinator_agent.py
│   ├── researcher_agent.py
│   ├── executor_agent.py
│   └── reviewer_agent.py
├── rag/
│   └── policy_vectorstore.py  # RAG for policy retrieval
├── workflows/
│   └── recruitment_graph.py   # LangGraph workflow
├── main.py                    # Entry point
└── requirements.txt
```

## Database Schema

The system uses the following tables:

- **candidates** - Candidate information
- **jobs** - Job postings
- **salary_bands** - Compensation bands by level/location
- **policies** - Company policies (used for RAG)
- **interview_schedules** - Interview scheduling data
- **compensation_proposals** - Compensation offers
- **compliance_logs** - Compliance check results
- **agent_logs** - Agent execution logs

## How It Works

### Workflow Example

User request:
```
"Schedule interview for Raja applying for SOE-1 position in Bangalore"
```

**Step 1: Interpreter Agent**
- Parses request
- Identifies: candidate (Raja), job level (SOE-1), location (Bangalore)
- Determines required data: salary bands, compensation policies

**Step 2: Coordinator Agent**
- Queries SQL database for salary bands:
  - SOE-1 Bangalore: INR 15,00,000 - 18,00,000
- Retrieves compensation policies via RAG
- Fetches/creates candidate record

**Step 3: Researcher Agent**
- Computes compensation within policy ranges
- Proposes interview schedule with availability windows
- Verifies candidate suitability

**Step 4: Executor Agent**
- Creates candidate record in database
- Schedules interview (inserts into `interview_schedules`)
- Drafts email invitation
- Creates compensation proposal record

**Step 5: Reviewer Agent**
- Validates compensation is within salary band
- Checks compliance (equal opportunity, no bias)
- Verifies data integrity
- Logs compliance checks

### SQL Integration

The system performs queries like:

```sql
-- Fetch salary bands
SELECT * FROM salary_bands
WHERE job_level = 'SOE-1' AND location = 'Bangalore';

-- Schedule interview
INSERT INTO interview_schedules
(candidate_id, interview_type, scheduled_date, recruiter)
VALUES (?, ?, ?, ?);

-- Log compliance
INSERT INTO compliance_logs
(candidate_id, check_type, result, details)
VALUES (?, ?, ?, ?);
```

### RAG for Policies

Policies are:
1. Stored in SQL `policies` table
2. Embedded using Gemini embeddings
3. Indexed in ChromaDB vector store
4. Retrieved via semantic search when needed

## Usage Examples

### Example 1: Basic Interview Scheduling

```python
from workflows.recruitment_graph import RecruitmentWorkflow

workflow = RecruitmentWorkflow()
results = workflow.run(
    "Schedule interview for candidate John for SOE-2 position in Mumbai"
)
```

### Example 2: Compensation Calculation

```python
results = workflow.run(
    "Calculate compensation for Senior Engineer in Bangalore, "
    "check against policy COMP-POL-India-2025-v3.2"
)
```

### Example 3: Query Database Directly

```python
from database.db_connection import db

# Get all candidates
candidates = db.fetch_all("SELECT * FROM candidates")

# Get salary band
salary_band = db.fetch_one(
    "SELECT * FROM salary_bands WHERE job_level = :level",
    {"level": "SOE-1"}
)
```

### Example 4: Query Policies via RAG

```python
from rag.policy_vectorstore import policy_rag

# Search for compensation policies
policies = policy_rag.query_policies(
    "What are the equity eligibility rules?",
    policy_type="compensation"
)
```

## Security Considerations for Company Laptop

1. **API Key Security**
   - Never commit `.env` file to git
   - Store API key securely (company password manager)
   - Use company-approved API keys if available

2. **Data Privacy**
   - Don't send sensitive employee data to external APIs
   - Use anonymized/test data for development
   - Check company policies on LLM usage

3. **Network Access**
   - Ensure company firewall allows access to Gemini API
   - Use company proxy if required
   - Check with IT if blocked

4. **Database**
   - Use SQLite for local testing (no server needed)
   - For production, get approval for MySQL/PostgreSQL
   - Encrypt database file if storing real data

## Customization

### Adding New Policies

```python
from database.db_connection import db
from rag.policy_vectorstore import policy_rag

# Add to database
db.execute_query(
    "INSERT INTO policies (policy_id, policy_type, policy_name, policy_content) "
    "VALUES (:id, :type, :name, :content)",
    {
        "id": "POL-NEW-001",
        "type": "benefits",
        "name": "Benefits Policy 2026",
        "content": "Policy content here..."
    }
)

# Refresh RAG vectorstore
policy_rag.refresh_vectorstore()
```

### Modifying Agent Behavior

Edit prompts in `config/prompts.py` to change how agents behave.

### Changing LLM Model

In `config/settings.py`, change:
```python
GEMINI_MODEL = "gemini-1.5-flash"  # Faster, cheaper
# or
GEMINI_MODEL = "gemini-1.5-pro"    # More capable
```

## Troubleshooting

### Error: "GOOGLE_API_KEY not found"
- Ensure `.env` file exists and contains `GOOGLE_API_KEY=your_key`

### Error: Database connection failed
- Check `DB_TYPE` in `.env` (use `sqlite` for simplicity)
- Ensure write permissions for database file

### Error: ChromaDB initialization failed
- Delete `vectorstore/` directory and rerun
- System will recreate it automatically

### LangGraph import errors
- Ensure `langgraph>=0.0.20` is installed
- Try: `pip install --upgrade langgraph`

## Next Steps

1. Add more sophisticated candidate matching logic
2. Integrate with real ATS systems (Greenhouse, Lever, etc.)
3. Add email sending capability (SMTP integration)
4. Build web UI using Streamlit or Gradio
5. Add calendar integration (Google Calendar API)
6. Implement approval workflows
7. Add analytics and reporting

## License

Internal use only - Company confidential

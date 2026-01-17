# Recruitment Agent System

A multi-agent recruitment automation system using **LangChain**, **LangGraph**, **Groq (Llama 3.3 70B)**, and **SQLite** for intelligent candidate processing, compensation calculation, and interview scheduling.

## Features

- **Multi-Agent Architecture** - 5 specialized AI agents working together
- **Web UI** - Streamlit-based dashboard for easy interaction
- **Policy Compliance** - Automated compliance checking against company policies
- **Compensation Calculator** - Automatic salary computation based on bands
- **Interview Scheduling** - Smart interview scheduling with email drafts

## Architecture

```
User Request → Interpreter → Coordinator → Researcher → Executor → Reviewer → Output
                                ↓
                          Database + RAG
```

### The 5 AI Agents

| Agent | Role |
|-------|------|
| **Interpreter** | Understands user requests, extracts candidate/job info |
| **Coordinator** | Fetches salary bands and policies from database |
| **Researcher** | Computes compensation, proposes interview schedules |
| **Executor** | Creates database records, drafts emails |
| **Reviewer** | Validates compliance, checks policy adherence |

## Tech Stack

| Component | Technology |
|-----------|------------|
| **LLM** | Groq (Llama 3.3 70B) - Fast & Free |
| **Framework** | LangChain + LangGraph |
| **Database** | SQLite |
| **RAG** | Database keyword search |
| **UI** | Streamlit |
| **Language** | Python 3.11+ |

## Quick Start

### Step 1: Install Dependencies

```bash
cd C:\Users\Admin\Desktop\ggd
pip install -r requirements.txt
```

### Step 2: Get Groq API Key (Free)

1. Go to [Groq Console](https://console.groq.com/keys)
2. Sign up and create an API key
3. Copy the key

### Step 3: Configure Environment

Create a `.env` file:

```env
LLM_PROVIDER=groq
GROQ_API_KEY=your_groq_api_key_here
GROQ_MODEL=llama-3.3-70b-versatile
DB_TYPE=sqlite
SQLITE_DB_PATH=recruitment.db
TEMPERATURE=0.7
```

### Step 4: Run the Application

**Option A - Web UI (Recommended):**
```bash
streamlit run app.py
```
Open: **http://localhost:8501**

**Option B - Command Line:**
```bash
python main.py
```

## Project Structure

```
ggd/
├── agents/
│   ├── interpreter_agent.py   # Request parsing
│   ├── coordinator_agent.py   # Data gathering
│   ├── researcher_agent.py    # Compensation calculation
│   ├── executor_agent.py      # Record creation
│   └── reviewer_agent.py      # Compliance validation
├── config/
│   ├── settings.py            # LLM & DB configuration
│   └── prompts.py             # Agent prompts
├── database/
│   ├── db_connection.py       # SQLite connection
│   └── schema_sqlite.sql      # Database schema
├── rag/
│   └── policy_vectorstore.py  # Policy retrieval
├── workflows/
│   └── recruitment_graph.py   # LangGraph workflow
├── app.py                     # Streamlit UI
├── main.py                    # CLI entry point
├── TECHNICAL_GUIDE.md         # Detailed documentation
└── requirements.txt
```

## Database Tables

| Table | Purpose |
|-------|---------|
| `candidates` | Candidate records |
| `salary_bands` | Compensation ranges by level/location |
| `policies` | Company policies for RAG |
| `interview_schedules` | Scheduled interviews |
| `compensation_proposals` | Salary proposals |
| `compliance_logs` | Audit trail |

## Usage Examples

### Web UI
1. Run `streamlit run app.py`
2. Select a template or enter custom request
3. Click "Process Request"
4. View results, compliance status, and email draft

### Command Line
```python
from workflows.recruitment_graph import RecruitmentWorkflow

workflow = RecruitmentWorkflow()
results = workflow.run(
    "Schedule interview for Raja for SOE-1 position in Bangalore"
)
print(results)
```

### Query Database
```python
from database.db_connection import db

# Get all candidates
candidates = db.fetch_all("SELECT * FROM candidates")

# Get salary bands
bands = db.fetch_all("SELECT * FROM salary_bands WHERE location = 'Bangalore'")
```

## Sample Output

```
CANDIDATE: Raja
POSITION:  SOE-1 Software Engineer, Bangalore

COMPENSATION:
├── Base Salary:    ₹16,50,000
├── Equity:         150 stock options
├── Bonus Target:   ₹2,47,500
└── Total:          ₹18,97,500

INTERVIEW:
├── Type:   Technical + Behavioral
├── Dates:  Jan 20, 22, 24, 2025
└── Time:   10:00 AM - 5:00 PM IST

COMPLIANCE: ⚠️ NEEDS REVISION
└── Missing equal opportunity statement in email
```

## Viewing Database

### Option 1: VS Code
Install "SQLite Viewer" extension, click on `recruitment.db`

### Option 2: Command Line
```bash
sqlite3 recruitment.db
.tables
SELECT * FROM candidates;
.quit
```

### Option 3: DB Browser
Download [DB Browser for SQLite](https://sqlitebrowser.org/)

## Configuration

### Switch to Gemini (if needed)

```env
LLM_PROVIDER=gemini
GOOGLE_API_KEY=your_gemini_key
GEMINI_MODEL=gemini-2.0-flash
```

### Add New Policies

```python
from database.db_connection import db

db.execute_query(
    """INSERT INTO policies (policy_id, policy_type, policy_name, policy_content)
       VALUES (:id, :type, :name, :content)""",
    {
        "id": "POL-NEW-001",
        "type": "benefits",
        "name": "Benefits Policy 2026",
        "content": "Your policy content here..."
    }
)
```

## Documentation

- **[TECHNICAL_GUIDE.md](TECHNICAL_GUIDE.md)** - Detailed explanation of agents, RAG, and workflow with examples for managers

## Troubleshooting

| Error | Solution |
|-------|----------|
| `GROQ_API_KEY not found` | Create `.env` file with your API key |
| `Database locked` | Close other applications using the DB |
| `Module not found` | Run `pip install -r requirements.txt` |
| `Port 8501 in use` | Kill existing Streamlit or use `--server.port 8502` |

## Security Notes

- Never commit `.env` file (contains API keys)
- Use test/anonymized data for development
- Check company policies on LLM usage
- Database file (`recruitment.db`) is auto-gitignored

## License

Internal use only - Company confidential

---

*Built with LangGraph + Groq + Streamlit*

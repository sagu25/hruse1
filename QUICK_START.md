# Quick Start Guide - Recruitment Agent System

## 5-Minute Setup (Company Laptop)

### Step 1: Get Your Gemini API Key (2 minutes)

1. Open browser and go to: https://makersuite.google.com/app/apikey
2. Sign in with your Google account
3. Click "Create API Key"
4. Copy the key (looks like: `AIzaSyXXXXXXXXXXXXXXXXXXXXXXXXX`)

### Step 2: Run Setup Script (3 minutes)

**Option A: Automatic Setup (Easiest)**
```bash
# Double-click setup.bat in Windows Explorer
# OR run from command prompt:
setup.bat
```

**Option B: Manual Setup**
```bash
# 1. Install dependencies
pip install -r requirements.txt

# 2. Create .env file
copy .env.example .env

# 3. Edit .env and paste your API key
notepad .env
# Add: GOOGLE_API_KEY=AIzaSyXXXXXXXXXXXXXXXXXXXXXXXXX

# 4. Run example
python main.py example
```

### Step 3: See It Work!

The system will:
1. Initialize SQLite database
2. Create sample salary bands and policies
3. Run an example: Schedule interview for "Raja" (SOE-1, Bangalore)
4. Show you the complete workflow output

## What You'll See

```
RECRUITMENT AGENT SYSTEM - WORKFLOW EXECUTION
===============================================

[Interpreter Agent] Interpreting user request...
[Interpreter Agent] Objective: Schedule interview for Raja...

[Coordinator Agent] Coordinating data gathering...
[Coordinator Agent] Data gathered successfully

[Researcher Agent] Researching candidate and computing compensation...
[Researcher Agent] Research completed

[Executor Agent] Executing actions...
[Executor Agent] Created/updated candidate record: CAND-20260115-143022
[Executor Agent] Scheduled interview: INT-20260115-143022
[Executor Agent] Execution completed successfully

[Reviewer Agent] Reviewing execution results for compliance...
[Reviewer Agent] Review status: APPROVED

FINAL RESULTS:
{
  "candidate": {
    "candidate_id": "CAND-20260115-143022",
    "schedule_ids": ["INT-20260115-143022"],
    "email_draft": "Dear Raja, We are pleased to invite you..."
  },
  "research": {
    "compensation_proposal": {
      "base_salary": 1650000,
      "equity": 150,
      "bonus_target": 165000
    }
  },
  "review": {
    "validation_status": "APPROVED"
  }
}
```

## Interactive Mode

Try your own requests:

```bash
python main.py interactive
```

Example requests:
- "Schedule interview for John applying for SOE-2 in Mumbai"
- "Calculate compensation for Senior Engineer in Bangalore"
- "Find candidates for Software Engineer position"

## Understanding the System

### The 5 Agents

1. **Interpreter** - "What does the user want?"
   - Parses your request
   - Identifies: candidate, job level, location

2. **Coordinator** - "What data do we need?"
   - Queries SQL database for salary bands
   - Retrieves policies via RAG (vector search)

3. **Researcher** - "What should we offer?"
   - Computes compensation within policy limits
   - Proposes interview schedule

4. **Executor** - "Make it happen"
   - Creates database records
   - Schedules interviews
   - Drafts emails

5. **Reviewer** - "Is everything correct?"
   - Validates compensation
   - Checks compliance
   - Logs audit trail

### Key Technologies

- **Gemini API**: Powers all agents' intelligence
- **SQLite**: Stores candidates, jobs, salary bands
- **ChromaDB**: Vector search for policies (RAG)
- **LangGraph**: Orchestrates agent workflow

## Check Your Database

```bash
# View database contents
python -c "from database.db_connection import db; print(db.fetch_all('SELECT * FROM candidates'))"

# Or use SQLite browser
sqlite3 recruitment.db
> SELECT * FROM candidates;
> SELECT * FROM salary_bands;
> .quit
```

## Next Steps

### 1. Customize Salary Bands

Edit `database/schema.sql` and add your company's bands:

```sql
INSERT INTO salary_bands (job_level, location, currency, base_range_min, base_range_max)
VALUES ('SOE-3', 'Mumbai', 'INR', 2000000, 2500000);
```

Then reinitialize:
```bash
python main.py example
```

### 2. Add Your Policies

```python
from database.db_connection import db

db.execute_query("""
    INSERT INTO policies (policy_id, policy_type, policy_name, policy_content)
    VALUES (?, ?, ?, ?)
""", ("POL-002", "benefits", "Benefits Policy", "Your policy text here..."))
```

### 3. Modify Agent Behavior

Edit files in `config/prompts.py` to change how agents think and respond.

### 4. Build a UI

Use Streamlit or Gradio to create a web interface:

```python
import streamlit as st
from workflows.recruitment_graph import RecruitmentWorkflow

st.title("Recruitment Assistant")
request = st.text_input("Enter request:")
if st.button("Process"):
    workflow = RecruitmentWorkflow()
    results = workflow.run(request)
    st.json(results)
```

## Troubleshooting

### "GOOGLE_API_KEY not found"
→ Check `.env` file exists and contains your key

### "No module named 'langchain'"
→ Run: `pip install -r requirements.txt`

### "Database is locked"
→ Close any other programs accessing `recruitment.db`

### Gemini API quota exceeded
→ Wait a few minutes or upgrade your API plan

### Firewall blocking API calls
→ Check with IT about allowing `generativelanguage.googleapis.com`

## Company Laptop Considerations

### ✅ Safe to Use:
- SQLite database (local file, no server)
- Gemini API (Google's official service)
- Python packages from PyPI

### ⚠️ Check First:
- Storing real employee data
- Using company network for API calls
- Installing Python packages (some companies restrict)

### 🔒 Security Best Practices:
1. Never commit `.env` file to git
2. Use test/demo data for development
3. Encrypt database if storing real data
4. Get IT approval for production use

## Getting Help

- Check `README.md` for full documentation
- View agent code in `agents/` folder
- Check database schema in `database/schema.sql`
- View workflow logic in `workflows/recruitment_graph.py`

## Cost Estimation (Gemini API)

For typical workflow (5 agents × 2 API calls each):
- ~10,000 tokens input
- ~2,000 tokens output

Gemini 1.5 Pro pricing:
- Input: $0.00125 / 1K tokens = $0.0125
- Output: $0.005 / 1K tokens = $0.01
- **Total per workflow: ~$0.02**

Very affordable for testing!

---

**Ready to go? Run: `python main.py interactive`**

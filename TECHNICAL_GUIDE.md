# Recruitment Agent System - Technical Guide

## Executive Summary

This document explains the **Multi-Agent Recruitment System** built using LangGraph, Groq (Llama 3.3 70B), and SQLite. The system automates recruitment workflows by coordinating 5 specialized AI agents that work together to process candidates, compute compensation, schedule interviews, and ensure compliance.

---

## Table of Contents

1. [System Architecture](#system-architecture)
2. [The 5 AI Agents Explained](#the-5-ai-agents-explained)
3. [RAG System (Policy Retrieval)](#rag-system-policy-retrieval)
4. [Complete Workflow Example](#complete-workflow-example)
5. [Database Schema](#database-schema)
6. [Technology Stack](#technology-stack)

---

## System Architecture

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                           USER REQUEST                                       │
│  "Schedule interview for Raja - SOE-1 position in Bangalore"                │
└─────────────────────────────────────────────────────────────────────────────┘
                                    │
                                    ▼
┌─────────────────────────────────────────────────────────────────────────────┐
│                        LANGGRAPH WORKFLOW                                    │
│  ┌──────────────┐    ┌──────────────┐    ┌──────────────┐                  │
│  │ INTERPRETER  │───▶│ COORDINATOR  │───▶│  RESEARCHER  │                  │
│  │    AGENT     │    │    AGENT     │    │    AGENT     │                  │
│  └──────────────┘    └──────────────┘    └──────────────┘                  │
│         │                   │                   │                           │
│         │                   ▼                   │                           │
│         │            ┌──────────────┐          │                           │
│         │            │   DATABASE   │          │                           │
│         │            │   + RAG      │          │                           │
│         │            └──────────────┘          │                           │
│         │                   │                   │                           │
│         │                   ▼                   ▼                           │
│         │            ┌──────────────┐    ┌──────────────┐                  │
│         └───────────▶│   EXECUTOR   │───▶│   REVIEWER   │                  │
│                      │    AGENT     │    │    AGENT     │                  │
│                      └──────────────┘    └──────────────┘                  │
└─────────────────────────────────────────────────────────────────────────────┘
                                    │
                                    ▼
┌─────────────────────────────────────────────────────────────────────────────┐
│                           FINAL OUTPUT                                       │
│  • Candidate Record Created                                                  │
│  • Compensation Proposal Generated                                           │
│  • Interview Scheduled                                                       │
│  • Email Draft Ready                                                         │
│  • Compliance Report                                                         │
└─────────────────────────────────────────────────────────────────────────────┘
```

---

## The 5 AI Agents Explained

### 1. Interpreter Agent 🎯

**Purpose:** Understands what the user wants and breaks down the request into actionable tasks.

**What it does:**
- Parses natural language requests
- Identifies the candidate name, job level, location
- Determines what actions are needed (schedule interview, compute salary, etc.)
- Sets success criteria for the workflow

**Example Input:**
```
"Find candidate data for Raja. He's applying for SOE-1 Software Development
Engineer position in Bangalore. Compute his compensation and schedule an interview."
```

**Example Output:**
```json
{
  "objective": "Process candidate Raja for SOE-1 position in Bangalore",
  "tasks": [
    "Retrieve candidate information",
    "Fetch salary bands for SOE-1 Bangalore",
    "Compute compensation package",
    "Schedule technical interview",
    "Generate interview invitation email"
  ],
  "constraints": {
    "job_level": "SOE-1",
    "location": "Bangalore",
    "policy_reference": "COMP-POL-India-2025-v3.2"
  }
}
```

**Code Location:** `agents/interpreter_agent.py`

---

### 2. Coordinator Agent 📊

**Purpose:** Gathers all necessary data from the database and policy documents.

**What it does:**
- Queries the database for salary bands
- Retrieves relevant policies using RAG
- Fetches existing candidate data if available
- Compiles job requirements and benefits information

**Data Sources:**
| Source | Information Retrieved |
|--------|----------------------|
| `salary_bands` table | Min/Max salary, equity ranges |
| `policies` table | Compensation rules, compliance requirements |
| `candidates` table | Existing candidate records |
| `jobs` table | Job descriptions, requirements |

**Example Output:**
```json
{
  "salary_band": {
    "job_level": "SOE-1",
    "location": "Bangalore",
    "base_range_min": 1500000,
    "base_range_max": 1800000,
    "equity_band_min": 100,
    "equity_band_max": 200
  },
  "policy_documents": [
    {
      "policy_id": "POL-COMP-001",
      "policy_name": "Compensation Policy India 2025",
      "key_points": [
        "Equal opportunity employer",
        "No discrimination allowed",
        "Salary within approved bands only"
      ]
    }
  ],
  "candidate_data": {
    "name": "Raja",
    "location": "Bangalore",
    "status": "new"
  }
}
```

**Code Location:** `agents/coordinator_agent.py`

---

### 3. Researcher Agent 🔬

**Purpose:** Analyzes data and computes the compensation package.

**What it does:**
- Calculates base salary (typically midpoint of range)
- Determines equity allocation
- Computes bonus targets
- Proposes interview dates and times
- Verifies candidate suitability

**Compensation Calculation Logic:**
```
Base Salary = (Min + Max) / 2 = (15,00,000 + 18,00,000) / 2 = ₹16,50,000

Equity = (Min + Max) / 2 = (100 + 200) / 2 = 150 stock options

Bonus Target = 15% of Base = ₹2,47,500

Total Compensation = Base + Bonus = ₹18,97,500 + Equity
```

**Example Output:**
```json
{
  "candidate_verification": {
    "name": "Raja",
    "email": "raja@example.com",
    "location": "Bangalore",
    "suitability": "Strong fit for SOE-1 position"
  },
  "compensation_proposal": {
    "base_salary": 1650000,
    "equity": 150,
    "bonus_target": 247500,
    "total_compensation": 1897500,
    "justification": "Midpoint of approved salary band for SOE-1 Bangalore"
  },
  "interview_schedule": {
    "interview_type": "Technical + Behavioral",
    "proposed_dates": ["2025-01-20", "2025-01-22", "2025-01-24"],
    "time_window": "10:00 AM - 5:00 PM IST",
    "interviewers": ["Tech Lead", "HR Manager"]
  }
}
```

**Code Location:** `agents/researcher_agent.py`

---

### 4. Executor Agent ⚡

**Purpose:** Creates actual records in the database and generates outputs.

**What it does:**
- Creates/updates candidate records in SQLite
- Inserts interview schedule entries
- Stores compensation proposals
- Drafts professional email invitations

**Database Operations:**
```sql
-- Create candidate record
INSERT INTO candidates (candidate_id, name, email, location, status)
VALUES ('CAND-2025-001', 'Raja', 'raja@example.com', 'Bangalore', 'interview_scheduled');

-- Schedule interview
INSERT INTO interview_schedules (candidate_id, interview_type, scheduled_date, status)
VALUES ('CAND-2025-001', 'Technical Interview', '2025-01-20 14:00:00', 'scheduled');

-- Store compensation proposal
INSERT INTO compensation_proposals (candidate_id, base_salary, equity_amount, bonus_target)
VALUES ('CAND-2025-001', 1650000, 150, 247500);
```

**Generated Email Example:**
```
Subject: Interview Invitation - Software Development Engineer Position

Dear Raja,

We are pleased to invite you for a technical interview for the Software
Development Engineer (SOE-1) position at our Bangalore office.

Proposed Dates: January 20, 22, or 24, 2025
Time: 10:00 AM - 5:00 PM IST

Please confirm your preferred date and time.

Best regards,
HR Team
```

**Code Location:** `agents/executor_agent.py`

---

### 5. Reviewer Agent ✅

**Purpose:** Validates all outputs for compliance and correctness.

**What it does:**
- Checks if compensation is within policy limits
- Verifies email contains required statements
- Ensures no discriminatory language
- Validates data integrity
- Provides recommendations for improvements

**Compliance Checks:**

| Check | Rule | Status |
|-------|------|--------|
| Salary Range | Must be within ₹15-18 LPA for SOE-1 | ✅ PASS |
| Equal Opportunity | Email must include EO statement | ❌ FAIL |
| Data Integrity | All required fields present | ✅ PASS |
| Scheduling | Proper buffer times between interviews | ✅ PASS |

**Example Output:**
```json
{
  "validation_status": "NEEDS_REVISION",
  "compliance_checks": {
    "compensation": {
      "status": "PASS",
      "details": "Base salary ₹16.5 LPA is within approved range"
    },
    "content_language": {
      "status": "FAIL",
      "details": "Missing equal opportunity statement in email"
    },
    "scheduling": {
      "status": "PASS",
      "details": "Interview times have proper 2-hour buffers"
    }
  },
  "recommendations": [
    "Add equal opportunity statement to email",
    "Include company non-discrimination policy reference"
  ]
}
```

**Code Location:** `agents/reviewer_agent.py`

---

## RAG System (Policy Retrieval)

### What is RAG?

**RAG (Retrieval-Augmented Generation)** allows the AI to access company-specific information (policies, salary bands, rules) when making decisions, rather than relying only on its training data.

### How Our RAG Works

```
┌─────────────────────────────────────────────────────────────────┐
│                      RAG WORKFLOW                                │
│                                                                  │
│  1. QUERY                                                        │
│     "What is the salary range for SOE-1 in Bangalore?"          │
│                          │                                       │
│                          ▼                                       │
│  2. SEARCH DATABASE                                              │
│     ┌─────────────────────────────────────┐                     │
│     │ SELECT * FROM policies              │                     │
│     │ WHERE content LIKE '%SOE-1%'        │                     │
│     │ AND content LIKE '%Bangalore%'      │                     │
│     └─────────────────────────────────────┘                     │
│                          │                                       │
│                          ▼                                       │
│  3. RETRIEVE MATCHING POLICIES                                   │
│     ┌─────────────────────────────────────┐                     │
│     │ Policy: COMP-POL-India-2025-v3.2    │                     │
│     │ Content: "SOE-1 Bangalore:          │                     │
│     │          INR 15,00,000 - 18,00,000" │                     │
│     └─────────────────────────────────────┘                     │
│                          │                                       │
│                          ▼                                       │
│  4. AI USES POLICY TO ANSWER                                     │
│     "The salary range for SOE-1 in Bangalore is                 │
│      ₹15,00,000 to ₹18,00,000 per annum"                        │
│                                                                  │
└─────────────────────────────────────────────────────────────────┘
```

### Policy Storage

Policies are stored in the `policies` table:

```sql
CREATE TABLE policies (
    policy_id VARCHAR(50) PRIMARY KEY,
    policy_type VARCHAR(100),      -- 'compensation', 'compliance', etc.
    policy_name VARCHAR(255),
    policy_content TEXT,           -- Full policy document
    doc_id VARCHAR(100)            -- Reference ID like "COMP-POL-India-2025-v3.2"
);
```

### Sample Policy Document

```
Compensation Policy COMP-POL-India-2025-v3.2

SALARY STRUCTURE:
- Base salary ranges are determined by job level and location
- SOE-1 Bangalore: INR 15,00,000 - 18,00,000
- SOE-2 Bangalore: INR 18,00,000 - 22,00,000
- Equity bands: 100-200 stock options (SOE-1), 150-300 (SOE-2)
- Performance bonus: Up to 15% of base salary

BENEFITS:
- Healthcare coverage for employee and family
- Provident Fund (PF) as per government regulations
- Gratuity after 5 years of service
- ESOP eligibility after 1 year

COMPLIANCE REQUIREMENTS:
- Equal opportunity employer
- No discrimination based on gender, religion, caste
- Interview questions must be job-related only
- Salary negotiations within approved band only

SCHEDULING GUIDELINES:
- Minimum 2-hour buffer between interviews
- Time zone considerations for remote candidates
- Confirmation required 24 hours before interview
```

### RAG Code Implementation

```python
# rag/policy_vectorstore.py

class PolicyRAG:
    def query_policies(self, query: str, policy_type: str = None):
        """Search policies using keyword matching"""

        # Get all policies from database
        policies = db.fetch_all("SELECT * FROM policies")

        # Search for matching terms
        results = []
        query_terms = query.lower().split()

        for policy in policies:
            content = policy.policy_content.lower()

            # Count matching terms
            matches = sum(1 for term in query_terms if term in content)

            if matches > 0:
                results.append((policy, matches))

        # Return top matches
        results.sort(key=lambda x: x[1], reverse=True)
        return [policy for policy, _ in results[:3]]
```

---

## Complete Workflow Example

### Scenario

**Manager Request:** "Process Raja for the SOE-1 Software Engineer position in our Bangalore office. Calculate his compensation and set up interviews."

### Step-by-Step Execution

#### Step 1: Interpreter Agent

```
INPUT:  "Process Raja for the SOE-1 Software Engineer position in Bangalore"

PROCESSING:
- Identified candidate: Raja
- Identified position: SOE-1 Software Engineer
- Identified location: Bangalore
- Required actions: compensation calculation, interview scheduling

OUTPUT:
{
  "objective": "Process Raja for SOE-1 Bangalore",
  "extracted_info": {
    "candidate_name": "Raja",
    "job_level": "SOE-1",
    "location": "Bangalore"
  }
}
```

#### Step 2: Coordinator Agent

```
PROCESSING:
- Querying salary_bands table for SOE-1 Bangalore
- Searching policies for compensation rules
- Checking for existing candidate record

DATABASE QUERIES:
  SELECT * FROM salary_bands WHERE job_level='SOE-1' AND location='Bangalore'
  → Returns: min=1500000, max=1800000, equity_min=100, equity_max=200

  SELECT * FROM policies WHERE policy_type='compensation'
  → Returns: COMP-POL-India-2025-v3.2

OUTPUT:
{
  "salary_band": {"min": 1500000, "max": 1800000},
  "equity_band": {"min": 100, "max": 200},
  "policy": "COMP-POL-India-2025-v3.2"
}
```

#### Step 3: Researcher Agent

```
PROCESSING:
- Calculating midpoint salary: (1500000 + 1800000) / 2 = 1650000
- Calculating equity: (100 + 200) / 2 = 150 options
- Calculating bonus: 1650000 * 0.15 = 247500
- Proposing interview dates

OUTPUT:
{
  "compensation": {
    "base_salary": 1650000,
    "equity": 150,
    "bonus": 247500,
    "total": 1897500
  },
  "interview": {
    "dates": ["Jan 20", "Jan 22", "Jan 24"],
    "type": "Technical + Behavioral"
  }
}
```

#### Step 4: Executor Agent

```
PROCESSING:
- Creating candidate record in database
- Creating interview schedule
- Storing compensation proposal
- Generating email draft

DATABASE INSERTS:
  INSERT INTO candidates (id, name, location, status)
  VALUES ('CAND-2025-001', 'Raja', 'Bangalore', 'interview_scheduled')

  INSERT INTO interview_schedules (candidate_id, date, type)
  VALUES ('CAND-2025-001', '2025-01-20', 'Technical')

  INSERT INTO compensation_proposals (candidate_id, base, equity, bonus)
  VALUES ('CAND-2025-001', 1650000, 150, 247500)

OUTPUT:
{
  "candidate_id": "CAND-2025-001",
  "interview_id": "INT-20250117-001",
  "proposal_id": 1,
  "email_draft": "Dear Raja, We are pleased to invite you..."
}
```

#### Step 5: Reviewer Agent

```
PROCESSING:
- Checking salary within policy limits ✅
- Verifying email content ❌ (missing EO statement)
- Validating data integrity ✅
- Checking scheduling rules ✅

OUTPUT:
{
  "status": "NEEDS_REVISION",
  "issues": ["Missing equal opportunity statement"],
  "passed_checks": ["Salary compliance", "Data integrity", "Scheduling"],
  "recommendation": "Add EO statement to email before sending"
}
```

### Final Output to Manager

```
╔══════════════════════════════════════════════════════════════════╗
║                    RECRUITMENT PROCESSING COMPLETE                ║
╠══════════════════════════════════════════════════════════════════╣
║  CANDIDATE: Raja                                                  ║
║  POSITION:  SOE-1 Software Engineer, Bangalore                   ║
║                                                                   ║
║  COMPENSATION PACKAGE:                                            ║
║  ├── Base Salary:    ₹16,50,000 per annum                        ║
║  ├── Equity:         150 stock options                           ║
║  ├── Bonus Target:   ₹2,47,500 (15%)                             ║
║  └── Total:          ₹18,97,500 + equity                         ║
║                                                                   ║
║  INTERVIEW SCHEDULED:                                             ║
║  ├── Type:           Technical + Behavioral                      ║
║  ├── Proposed Dates: Jan 20, 22, 24, 2025                        ║
║  └── Time:           10:00 AM - 5:00 PM IST                      ║
║                                                                   ║
║  COMPLIANCE STATUS: ⚠️  NEEDS REVISION                            ║
║  └── Action Required: Add equal opportunity statement to email   ║
║                                                                   ║
║  RECORDS CREATED:                                                 ║
║  ├── Candidate ID:   CAND-2025-001                               ║
║  ├── Interview ID:   INT-20250117-001                            ║
║  └── Proposal ID:    1                                           ║
╚══════════════════════════════════════════════════════════════════╝
```

---

## Database Schema

### Entity Relationship Diagram

```
┌──────────────────┐       ┌──────────────────┐
│   candidates     │       │      jobs        │
├──────────────────┤       ├──────────────────┤
│ candidate_id PK  │       │ job_id PK        │
│ name             │       │ title            │
│ email            │       │ location         │
│ location         │       │ job_level        │
│ status           │       │ description      │
└────────┬─────────┘       └────────┬─────────┘
         │                          │
         │    ┌────────────────┐    │
         └───▶│interview_      │◀───┘
              │schedules       │
              ├────────────────┤
              │ schedule_id PK │
              │ candidate_id FK│
              │ job_id FK      │
              │ scheduled_date │
              │ status         │
              └────────────────┘

┌──────────────────┐       ┌──────────────────┐
│  salary_bands    │       │    policies      │
├──────────────────┤       ├──────────────────┤
│ band_id PK       │       │ policy_id PK     │
│ job_level        │       │ policy_type      │
│ location         │       │ policy_name      │
│ base_range_min   │       │ policy_content   │
│ base_range_max   │       │ doc_id           │
│ equity_band_min  │       └──────────────────┘
│ equity_band_max  │
└──────────────────┘

┌──────────────────┐       ┌──────────────────┐
│  compensation_   │       │ compliance_logs  │
│  proposals       │       ├──────────────────┤
├──────────────────┤       │ log_id PK        │
│ proposal_id PK   │       │ candidate_id FK  │
│ candidate_id FK  │       │ check_type       │
│ base_salary      │       │ result           │
│ equity_amount    │       │ details          │
│ bonus_target     │       └──────────────────┘
│ status           │
└──────────────────┘
```

---

## Technology Stack

| Component | Technology | Purpose |
|-----------|------------|---------|
| **LLM** | Groq (Llama 3.3 70B) | AI reasoning and text generation |
| **Framework** | LangGraph | Multi-agent workflow orchestration |
| **Database** | SQLite | Local data storage |
| **RAG** | Custom keyword search | Policy document retrieval |
| **UI** | Streamlit | Web-based user interface |
| **Language** | Python 3.11 | Backend implementation |

### Why These Choices?

1. **Groq + Llama 3.3 70B**
   - Free tier available
   - Very fast inference
   - No rate limiting issues
   - Works on company networks

2. **SQLite**
   - No server setup required
   - Single file database
   - Perfect for development/demo
   - Easy to migrate to MySQL/PostgreSQL later

3. **LangGraph**
   - Built for multi-agent systems
   - State management between agents
   - Easy to visualize workflow
   - Production-ready

4. **Streamlit**
   - Rapid UI development
   - No frontend expertise needed
   - Interactive dashboards
   - Easy deployment

---

## Running the System

### Command Line
```bash
python main.py              # Run example workflow
python main.py interactive  # Interactive mode
```

### Web Interface
```bash
streamlit run app.py        # Opens at http://localhost:8501
```

---

## Summary

This multi-agent system automates the recruitment workflow by:

1. **Understanding** natural language requests (Interpreter)
2. **Gathering** relevant data and policies (Coordinator + RAG)
3. **Computing** compensation packages (Researcher)
4. **Creating** records and communications (Executor)
5. **Validating** compliance with company policies (Reviewer)

The system ensures consistency, compliance, and efficiency in recruitment operations while maintaining full audit trails in the database.

---

*Document Version: 1.0*
*Last Updated: January 2025*
*Author: Recruitment System Team*

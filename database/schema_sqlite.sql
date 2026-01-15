-- Recruitment Agent System Database Schema (SQLite)

-- Candidates table
CREATE TABLE IF NOT EXISTS candidates (
    candidate_id VARCHAR(50) PRIMARY KEY,
    name VARCHAR(255) NOT NULL,
    email VARCHAR(255) NOT NULL UNIQUE,
    location VARCHAR(100),
    resume_attached BOOLEAN DEFAULT FALSE,
    status VARCHAR(50) DEFAULT 'new',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Jobs table
CREATE TABLE IF NOT EXISTS jobs (
    job_id VARCHAR(50) PRIMARY KEY,
    title VARCHAR(255) NOT NULL,
    location VARCHAR(100),
    doc_id VARCHAR(100),
    job_type VARCHAR(50),
    job_level VARCHAR(50),
    description TEXT,
    requirements TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Salary bands table
CREATE TABLE IF NOT EXISTS salary_bands (
    band_id INTEGER PRIMARY KEY AUTOINCREMENT,
    job_level VARCHAR(50) NOT NULL,
    location VARCHAR(100) NOT NULL,
    currency VARCHAR(10) DEFAULT 'INR',
    base_range_min DECIMAL(12,2),
    base_range_max DECIMAL(12,2),
    equity_band_min DECIMAL(10,2),
    equity_band_max DECIMAL(10,2),
    benefits_notes TEXT,
    policy_doc_id VARCHAR(100),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Policies table for RAG
CREATE TABLE IF NOT EXISTS policies (
    policy_id VARCHAR(50) PRIMARY KEY,
    policy_type VARCHAR(100) NOT NULL,
    policy_name VARCHAR(255) NOT NULL,
    policy_content TEXT NOT NULL,
    effective_date DATE,
    doc_id VARCHAR(100),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Interview schedules
CREATE TABLE IF NOT EXISTS interview_schedules (
    schedule_id INTEGER PRIMARY KEY AUTOINCREMENT,
    candidate_id VARCHAR(50) NOT NULL,
    job_id VARCHAR(50),
    interview_type VARCHAR(100),
    interview_log_id VARCHAR(100),
    scheduled_date DATETIME,
    recruiter VARCHAR(100),
    tech_interviewer VARCHAR(100),
    availability_window TEXT,
    status VARCHAR(50) DEFAULT 'scheduled',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (candidate_id) REFERENCES candidates(candidate_id),
    FOREIGN KEY (job_id) REFERENCES jobs(job_id)
);

-- ATS data
CREATE TABLE IF NOT EXISTS ats_data (
    ats_id INTEGER PRIMARY KEY AUTOINCREMENT,
    candidate_id VARCHAR(50) NOT NULL,
    job_id VARCHAR(50),
    application_date DATE,
    current_stage VARCHAR(100),
    notes TEXT,
    referral_info VARCHAR(255),
    FOREIGN KEY (candidate_id) REFERENCES candidates(candidate_id),
    FOREIGN KEY (job_id) REFERENCES jobs(job_id)
);

-- Compliance checks
CREATE TABLE IF NOT EXISTS compliance_logs (
    log_id INTEGER PRIMARY KEY AUTOINCREMENT,
    candidate_id VARCHAR(50),
    job_id VARCHAR(50),
    check_type VARCHAR(100) NOT NULL,
    result VARCHAR(50) NOT NULL,
    details TEXT,
    conflicts TEXT,
    checked_by VARCHAR(50) DEFAULT 'REVIEWER_AGENT',
    checked_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (candidate_id) REFERENCES candidates(candidate_id)
);

-- Compensation proposals
CREATE TABLE IF NOT EXISTS compensation_proposals (
    proposal_id INTEGER PRIMARY KEY AUTOINCREMENT,
    candidate_id VARCHAR(50) NOT NULL,
    job_id VARCHAR(50),
    base_salary DECIMAL(12,2),
    equity_amount DECIMAL(10,2),
    bonus_target DECIMAL(10,2),
    benefits_summary TEXT,
    proposed_by VARCHAR(50) DEFAULT 'EXECUTOR_AGENT',
    status VARCHAR(50) DEFAULT 'draft',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (candidate_id) REFERENCES candidates(candidate_id),
    FOREIGN KEY (job_id) REFERENCES jobs(job_id)
);

-- Agent execution logs
CREATE TABLE IF NOT EXISTS agent_logs (
    log_id INTEGER PRIMARY KEY AUTOINCREMENT,
    agent_name VARCHAR(50) NOT NULL,
    action VARCHAR(100),
    input_data TEXT,
    output_data TEXT,
    status VARCHAR(50),
    execution_time_ms INT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Sample data for Bangalore location
INSERT OR IGNORE INTO salary_bands (job_level, location, currency, base_range_min, base_range_max, equity_band_min, equity_band_max, benefits_notes, policy_doc_id)
VALUES
('SOE-1', 'Bangalore', 'INR', 1500000, 1800000, 100, 200, 'Healthcare, PF, gratuity, ESOP eligibility rules, healthcare, standard', 'COMP-POL-India-2025-v3.2'),
('SOE-2', 'Bangalore', 'INR', 1800000, 2200000, 150, 300, 'Healthcare, PF, gratuity, ESOP eligibility rules, healthcare, standard', 'COMP-POL-India-2025-v3.2');

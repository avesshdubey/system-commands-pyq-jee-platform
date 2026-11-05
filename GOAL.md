# Goal Specification: IIT Madras - System Commands (SC) Past Year Questions (PYQ) & JEE CBT Platform

## 1. Objective
Build an end-to-end examination platform and categorized question bank for IIT Madras BS Degree - System Commands (SC - Diploma Level).
The system extracts all unique questions verbatim with 100% visual fidelity directly from the official TCS iON past year question papers located in `C:\Users\avesh\Desktop\PYQS`, categorizes them into the official 4-week syllabus taxonomy across granular subcategories, compiles a publication-ready PDF document, and provides an interactive NTA/JEE CBT exam web application with authentication, an admin control dashboard, and a random question practice mode.

---

## 2. Acceptance Criteria
- [ ] **Data Source Scanning**: Scan all question papers in `C:\Users\avesh\Desktop\PYQS` and accurately identify all `System Commands` sections between their start boundary and end boundary.
- [ ] **100% Fidelity Question Card Cropping**: Capture high-resolution visual cards directly from the source PDF pages for each question, preserving terminal commands, option choices, code snippets, regex expressions, tables, and formatting without dropped characters.
- [ ] **Verbatim Text & Option Extraction**: Extract question stems, option choices, marks, question type (MCQ, MSQ, SA/NAT), and official answer keys verbatim. Filter out standard subject confirmation prompts ("ARE YOU SURE YOU HAVE TO WRITE EXAM FOR THIS SUBJECT?").
- [ ] **Exact Deduplication**: Group duplicate questions occurring across multiple exam sessions/slots into unique records while retaining complete cross-session citation metadata (`source_papers`).
- [ ] **4-Week Syllabus Taxonomy with Granular Subcategories**:
  - **Week 1**: Introduction to Operating Systems, Shell & Basic File Navigation (`pwd`, `cd`, `ls`, `mkdir`, `cp`, `mv`, `rm`, `cat`, `head`, `tail`)
  - **Week 2**: File System Hierarchy, Permissions (`chmod`, `chown`, octal/symbolic, SUID/SGID/sticky), Redirection (`<`, `>`, `>>`, pipes `|`), and Links (`ln`, hard/soft)
  - **Week 3**: Text Processing Filters (`cut`, `paste`, `sort`, `uniq`, `tr`, `wc`), Pattern Searching (`grep`, regex), Stream Editing (`sed`), and `awk`
  - **Week 4**: Shell Scripting (`bash`, variables, quoting, conditionals `if/test`, loops `for/while`), Process Management (`ps`, `top`, `kill`, signals), and Job Control
- [ ] **Publication-Ready PDF**: Generate `system_commands_questions_categorized.pdf` (ReportLab) formatted by Week and Subtopic, embedding high-resolution question cards, official answer keys, and syllabus summary tables.
- [ ] **NTA/JEE CBT Web Platform (`index.html`)**:
  - Full JEE examination interface (candidate banner, subject/week tabs, countdown timer, question panel, palette sidebar with standard JEE status colors).
  - Secure Authentication Gate (Student & Admin login, registration, persistent session).
  - Admin Control Panel (user management, attempt analytics, question bank explorer, JSON/CSV exports).
  - Post-Exam Scorecard Review with detailed question-by-question analysis, official answer keys, and accuracy metrics.
  - Granular Subcategory Filtering & "🎲 Random Question" / "Quick Random Practice" modes for rapid revision.
- [ ] **Git & GitHub Integration (`/addgit`)**: Local repository initialized on `main`, remote linked (`avesshdubey/system-commands-pyq-jee-platform`), and auto-push enabled with atomic commits.
- [ ] **Automated Test Suite**: Unit tests (`tests/test_platform.py`) verifying question counts, schema integrity, PDF generation, subcategory taxonomy, and frontend assets.

---

## 3. Constraints & Guidelines
- Strict adherence to official IITM syllabus boundaries.
- No dummy/placeholder content.
- Respect local storage and browser performance for smooth rendering of question cards.
- Automatic Git commits and push after each task verification.

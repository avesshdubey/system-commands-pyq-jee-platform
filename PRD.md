# Product Requirements Document (PRD) - System Commands PYQ & JEE CBT Test Platform

## Tasks Breakdown

- [ ] **Task 1: Establish Git & 4-Tier Configuration Baseline (`/addgit` + `/addconfig4`)**
  - Initialize local Git repository on `main` branch.
  - Generate comprehensive `.gitignore` tailored to Python, web assets, and raw binary archives.
  - Create baseline commit.
  - Create remote GitHub repository via GitHub CLI (`gh repo create system-commands-pyq-jee-platform --public --source=. --remote=origin --push`) and configure upstream tracking.

- [ ] **Task 2: Precision Multi-Paper System Commands Scanner & Visual Card Cropper**
  - Scan all 69 candidate question paper PDFs in `C:\Users\avesh\Desktop\PYQS`, identifying all papers containing the official `System Commands` section (including modern TCS iON papers and legacy 2022 sessions).
  - Filter out zero-mark subject confirmation prompts.
  - Crop 150-DPI high-resolution visual question cards capturing complete problem stems, command outputs, permission matrices, and option choices.
  - Extract verbatim question text, option choices, question type (MCQ, MSQ, SA), marks, and official answer keys.

- [ ] **Task 3: Exact Deduplication Engine & 4-Week Syllabus Classifier**
  - Implement normalized text and cross-slot deduplication to merge identical questions from parallel exam slots into single records with accumulated `source_papers` citations.
  - Classify unique questions into the official 4-week syllabus taxonomy with granular subcategories:
    - Week 1: OS Concepts, Shell Basics & File Navigation
    - Week 2: File System Hierarchy, Permissions, Redirection & Pipes
    - Week 3: Text Processing Filters, Grep/Regex, Sed & Awk
    - Week 4: Shell Scripting, Environment Variables & Process Management
  - Generate structured `data/questions.json`, `data/stats.json`, and standalone bundle `data/questions_data.js`.

- [ ] **Task 4: Publication-Quality Categorized PDF Generator (`generate_pdf.py`)**
  - Build `scripts/generate_pdf.py` using ReportLab to render `system_commands_questions_categorized.pdf`.
  - Format categorized questions by Week and Subtopic with running headers, footers, page numbering, embedded question cards, and verified answer keys.

- [ ] **Task 5: Interactive JEE CBT Examination Web Application & Admin Control Panel**
  - Develop `index.html`, `css/jee_style.css`, and `js/jee_app.js` replicating the NTA/JEE CBT examination system.
  - Embed full authentication system (`js/auth.js`) with Student/Admin roles and persistent local storage.
  - Build Admin Control Panel (`js/admin.js`) with system metrics, user controls, exam log viewer, question bank explorer, and data export.
  - Provide interactive Exam Mode (countdown timer, palette sidebar, mark for review, clear response), "🎲 Random Question" / "Quick Random Practice" modes, and comprehensive scorecard review.

- [ ] **Task 6: Automated Test Verification, CodeRabbit QA & Git Auto-Push**
  - Write test suite `tests/test_platform.py` verifying question schema, PDF integrity, image resolution, and application assets.
  - Run CodeRabbit code review audit (`coderabbit review --agent`) and fix any flagged issues.
  - Commit atomic changes and auto-push upstream to GitHub remote.

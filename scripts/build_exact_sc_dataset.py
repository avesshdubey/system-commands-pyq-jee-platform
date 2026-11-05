import fitz
import os
import re
import json
import glob
import hashlib
from PIL import Image

WORKSPACE_DIR = r"C:\Users\avesh\Desktop\system-commands-pyq-jee-platform"
PYQS_DIR = r"C:\Users\avesh\Desktop\PYQS"

DATA_DIR = os.path.join(WORKSPACE_DIR, "data")
CARDS_DIR = os.path.join(WORKSPACE_DIR, "assets", "q_cards")
os.makedirs(DATA_DIR, exist_ok=True)
os.makedirs(CARDS_DIR, exist_ok=True)

# 4-Week Taxonomy Mapping for System Commands (IIT Madras BS Degree)
TAXONOMY = {
    "Week 1: Introduction to Operating Systems, Shell & Basic Commands": [
        ("1.1 OS Architecture, Linux Kernel & Shell Basics", [
            "kernel", "shell", "operating system", "terminal", "user space", "system call", 
            "architecture", "tty", "console", "bash shell", "cli", "gui", "cli vs gui"
        ]),
        ("1.2 Directory Navigation & Pathnames", [
            "pwd", "cd", "absolute path", "relative path", "directory path", "home directory", 
            "parent directory", "~/", "../", "./", "working directory", "cd -", "cd ~"
        ]),
        ("1.3 File & Directory Operations", [
            "mkdir", "rmdir", "cp", "mv", "rm", "touch", "copy file", "move file", 
            "remove directory", "rename file", "overwrite", "copy recursive", "rm -r", "cp -r"
        ]),
        ("1.4 Viewing File Contents", [
            "cat", "tac", "head", "tail", "more", "less", "nl", "view lines", 
            "first n lines", "last n lines", "paging", "scroll", "head -n", "tail -n", "tail -f"
        ]),
        ("1.5 File Metadata & Listing Attributes", [
            "ls", "ls -l", "ls -a", "ls -h", "ls -r", "ls -t", "file", "stat", 
            "date", "cal", "uname", "who", "whoami", "id", "uptime", "timestamp", "file type"
        ])
    ],
    "Week 2: File System Hierarchy, Permissions, Redirection & Links": [
        ("2.1 File System Hierarchy Standard (FHS)", [
            "/etc", "/bin", "/sbin", "/usr", "/var", "/dev", "/proc", "/sys", 
            "/home", "/tmp", "/root", "/boot", "filesystem hierarchy", "root directory", "fhs", "mount"
        ]),
        ("2.2 File Permissions & Ownership", [
            "chmod", "chown", "chgrp", "permission", "rwx", "read, write", "octal", 
            "symbolic", "755", "644", "700", "777", "file permissions", "change mode", "owner", "group", "others"
        ]),
        ("2.3 Special Permissions & Umask", [
            "suid", "sgid", "sticky bit", "setuid", "setgid", "umask", 
            "default permissions", "4755", "2755", "1777", "special mode", "mask"
        ]),
        ("2.4 I/O Redirection & Standard Streams", [
            "stdin", "stdout", "stderr", "redirection", "2>&1", "/dev/null", 
            "2>", ">>", "<", ">", "redirect output", "redirect error", "file descriptor 0", "file descriptor 1", "file descriptor 2"
        ]),
        ("2.5 Pipelines & Command Combining", [
            "pipe", "pipelines", "tee", "logical and", "logical or", 
            "sequential execution", "command chaining", "&&", "||"
        ]),
        ("2.6 Hard Links & Symbolic Links", [
            "ln", "ln -s", "hard link", "symbolic link", "soft link", 
            "inode", "inode number", "link count", "link target"
        ])
    ],
    "Week 3: Text Processing Filters, Grep/Regex, Sed & Awk": [
        ("3.1 Text Processing Filters", [
            "cut", "paste", "sort", "uniq", "tr", "wc", "line count", 
            "character count", "delimiter", "sort -n", "sort -k", "sort -r", "uniq -c", "translate characters"
        ]),
        ("3.2 Finding Files & Path Searches", [
            "find", "locate", "which", "whereis", "search file", 
            "find -name", "find -type", "find -mtime", "find -exec"
        ]),
        ("3.3 Pattern Searching with Grep & Regular Expressions", [
            "grep", "egrep", "fgrep", "regular expression", "regex", "pattern matching", 
            "metacharacter", "character class", "grep -v", "grep -i", "grep -c", "grep -e", "grep -n"
        ]),
        ("3.4 Stream Editing with Sed", [
            "sed", "stream editor", "sed substitution", "s/", "sed -i", 
            "address range", "sed -e", "sed pattern", "substitute"
        ]),
        ("3.5 Pattern Scanning & Processing with Awk", [
            "awk", "awk script", "$0", "$1", "$2", "nf", "nr", 
            "fs", "ofs", "begin", "end", "field separator", "record separator", "awk print"
        ])
    ],
    "Week 4: Shell Scripting, Environment Variables & Process Management": [
        ("4.1 Shell Variables, Environment & Quoting", [
            "variable", "environment variable", "export", "env", "printenv", 
            "path", "ps1", "home", "single quotes", "double quotes", "backticks", "command substitution", "parameter expansion"
        ]),
        ("4.2 Shell Scripting: Conditionals & Test Operators", [
            "if", "then", "else", "elif", "fi", "test", "-eq", "-ne", 
            "-lt", "-gt", "-ge", "-le", "-z", "-n", "-f", "-d", "-e", "-r", "-w", "-x", "condition"
        ]),
        ("4.3 Shell Scripting: Loops, Functions & Positional Parameters", [
            "for loop", "while loop", "until loop", "positional parameter", 
            "$1", "$2", "$#", "$@", "$*", "$?", "$$", "shift", "function", "exit status", "return code"
        ]),
        ("4.4 Process Management & Signals", [
            "ps", "ps aux", "ps -ef", "top", "htop", "pstree", "jobs", "fg", "bg", 
            "kill", "killall", "signal", "sigint", "sigkill", "sigterm", "pid", "ppid", "background process", "daemon", "nice", "renice"
        ]),
        ("4.5 Task Scheduling, Archiving & Compression", [
            "tar", "tar -cvf", "tar -xvf", "gzip", "gunzip", "bzip2", 
            "zip", "unzip", "crontab", "cron", "at", "schedule", "archive", "compress"
        ])
    ]
}

def classify_question(text):
    text_lower = text.lower()
    
    # Priority Awk
    if re.search(r'\bawk\b', text_lower) or ('$0' in text and '$1' in text) or re.search(r'\b(nf|nr|fs|ofs)\b', text_lower):
        return "Week 3: Text Processing Filters, Grep/Regex, Sed & Awk", "3.5 Pattern Scanning & Processing with Awk"
        
    # Priority Sed
    if re.search(r'\bsed\b', text_lower) or re.search(r's/[^/]+/[^/]*/', text_lower):
        return "Week 3: Text Processing Filters, Grep/Regex, Sed & Awk", "3.4 Stream Editing with Sed"
        
    # Priority Grep / Regex
    if re.search(r'\b(grep|egrep|fgrep)\b', text_lower) or ("regular expression" in text_lower and ("match" in text_lower or "pattern" in text_lower)):
        return "Week 3: Text Processing Filters, Grep/Regex, Sed & Awk", "3.3 Pattern Searching with Grep & Regular Expressions"
        
    # Priority Find
    if re.search(r'\b(find|locate|which|whereis)\b', text_lower) and ("-name" in text_lower or "-type" in text_lower or "-exec" in text_lower or "search" in text_lower or "find " in text_lower):
        return "Week 3: Text Processing Filters, Grep/Regex, Sed & Awk", "3.2 Finding Files & Path Searches"
        
    # Priority Text Filters (cut, paste, sort, uniq, tr, wc)
    if re.search(r'\b(cut|paste|sort|uniq|tr|wc)\b', text_lower):
        return "Week 3: Text Processing Filters, Grep/Regex, Sed & Awk", "3.1 Text Processing Filters"
        
    # Process management / Signals
    if re.search(r'\b(kill|killall|sigint|sigkill|sigterm|pid|ppid|top|htop|pstree|jobs|fg|bg)\b', text_lower) or re.search(r'\bps\s+(-ef|aux|-e)\b', text_lower):
        return "Week 4: Shell Scripting, Environment Variables & Process Management", "4.4 Process Management & Signals"
        
    # Archiving & Compression & Cron
    if re.search(r'\b(tar|gzip|gunzip|zip|unzip|bzip2|crontab|cron|at)\b', text_lower) and ("archive" in text_lower or "compress" in text_lower or "extract" in text_lower or "schedule" in text_lower or "-cvf" in text_lower or "-xvf" in text_lower):
        return "Week 4: Shell Scripting, Environment Variables & Process Management", "4.5 Task Scheduling, Archiving & Compression"
        
    # Scripting loops & functions & parameters
    if re.search(r'\b(for\s+\w+\s+in|while\s+|until\s+|positional parameter|\$#|\$@|\$\*|\$\?|\$\$|shift)\b', text_lower) or ("do" in text_lower and "done" in text_lower):
        return "Week 4: Shell Scripting, Environment Variables & Process Management", "4.3 Shell Scripting: Loops, Functions & Positional Parameters"
        
    # Scripting conditionals
    if re.search(r'\b(elif|then|fi|-eq|-ne|-lt|-gt|-ge|-le)\b', text_lower) or ("if" in text_lower and "fi" in text_lower):
        return "Week 4: Shell Scripting, Environment Variables & Process Management", "4.2 Shell Scripting: Conditionals & Test Operators"
        
    # Variables, Quoting, Environment
    if re.search(r'\b(export|environment variable|variables?|path=|ps1=|double quote|single quote|command substitution|backtick)\b', text_lower):
        return "Week 4: Shell Scripting, Environment Variables & Process Management", "4.1 Shell Variables, Environment & Quoting"
        
    # Special Permissions & Umask
    if re.search(r'\b(suid|sgid|sticky bit|setuid|setgid|umask)\b', text_lower):
        return "Week 2: File System Hierarchy, Permissions, Redirection & Links", "2.3 Special Permissions & Umask"
        
    # File Permissions & Ownership
    if re.search(r'\b(chmod|chown|chgrp|permission|permissions|rwx|755|644|700|777)\b', text_lower):
        return "Week 2: File System Hierarchy, Permissions, Redirection & Links", "2.2 File Permissions & Ownership"
        
    # Hard & Soft Links
    if re.search(r'\b(inode|hard link|symbolic link|soft link|ln\s+-s|ln\s+)\b', text_lower):
        return "Week 2: File System Hierarchy, Permissions, Redirection & Links", "2.6 Hard Links & Symbolic Links"
        
    # Redirection & Streams
    if re.search(r'\b(stdin|stdout|stderr|redirection|/dev/null|2>&1|2>|>>)\b', text_lower) or (">" in text_lower and "output" in text_lower):
        return "Week 2: File System Hierarchy, Permissions, Redirection & Links", "2.4 I/O Redirection & Standard Streams"
        
    # Pipelines
    if re.search(r'\b(pipeline|pipelines|tee)\b', text_lower) or ("|" in text_lower and "pipe" in text_lower):
        return "Week 2: File System Hierarchy, Permissions, Redirection & Links", "2.5 Pipelines & Command Combining"
        
    # FHS
    if re.search(r'\b(/etc|/bin|/sbin|/usr|/var|/dev|/proc|/sys|/home|/tmp|fhs|filesystem hierarchy)\b', text_lower):
        return "Week 2: File System Hierarchy, Permissions, Redirection & Links", "2.1 File System Hierarchy Standard (FHS)"
        
    # File viewing (cat, head, tail, etc.)
    if re.search(r'\b(head|tail|cat|tac|more|less|nl)\b', text_lower) and ("line" in text_lower or "display" in text_lower or "view" in text_lower or "file" in text_lower):
        return "Week 1: Introduction to Operating Systems, Shell & Basic Commands", "1.4 Viewing File Contents"
        
    # Directory & File operations (mkdir, cp, mv, rm, touch)
    if re.search(r'\b(mkdir|rmdir|cp|mv|rm|touch)\b', text_lower):
        return "Week 1: Introduction to Operating Systems, Shell & Basic Commands", "1.3 File & Directory Operations"
        
    # Navigation
    if re.search(r'\b(pwd|cd|absolute path|relative path|working directory)\b', text_lower):
        return "Week 1: Introduction to Operating Systems, Shell & Basic Commands", "1.2 Directory Navigation & Pathnames"
        
    # Metadata & attributes
    if re.search(r'\b(ls|stat|file|uname|whoami|who|date|cal)\b', text_lower):
        return "Week 1: Introduction to Operating Systems, Shell & Basic Commands", "1.5 File Metadata & Listing Attributes"
        
    # Default Week 1
    return "Week 1: Introduction to Operating Systems, Shell & Basic Commands", "1.1 OS Architecture, Linux Kernel & Shell Basics"

def clean_stem_text(raw_text):
    t = raw_text
    possible_ans = ""
    ans_m = re.search(r'Possible Answers\s*:\s*([^\n\r]+)', t)
    if ans_m:
        possible_ans = ans_m.group(1).strip()
        
    t = re.sub(r'Calculator\s*:[^\n\r]*', '', t)
    t = re.sub(r'Response Time\s*:[^\n\r]*', '', t)
    t = re.sub(r'Think Time\s*:[^\n\r]*', '', t)
    t = re.sub(r'Minimum Instruction\s*Time\s*:[^\n\r]*', '', t)
    t = re.sub(r'Is Question Mandatory\s*:[^\n\r]*', '', t)
    t = re.sub(r'Question Pattern Type\s*:[^\n\r]*', '', t)
    t = re.sub(r'Group Comprehension Questions\s*:[^\n\r]*', '', t)
    t = re.sub(r'Question Numbers\s*:[^\n\r]*', '', t)
    t = re.sub(r'Correct Marks\s*:[^\n\r]*', '', t)
    t = re.sub(r'Max\. Selectable Options\s*:[^\n\r]*', '', t)
    t = re.sub(r'Question Label\s*:[^\n\r]*', '', t)
    t = re.sub(r'Response Type\s*:[^\n\r]*', '', t)
    t = re.sub(r'Evaluation Required[^\n\r]*', '', t)
    t = re.sub(r'Show Word Count[^\n\r]*', '', t)
    t = re.sub(r'Answers Type[^\n\r]*', '', t)
    t = re.sub(r'Text Areas[^\n\r]*', '', t)
    t = re.sub(r'Possible Answers[^\n\r]*', '', t)
    t = re.sub(r'Sub-Section[^\n\r]*', '', t)
    t = re.sub(r'Question Shuffling[^\n\r]*', '', t)
    t = re.sub(r'Is Section Default[^\n\r]*', '', t)
    t = re.sub(r'Question Number\s*:\s*\d+.*', '', t)
    t = re.sub(r'Question Id\s*:\s*\d+.*', '', t)
    t = re.sub(r'THIS IS QUESTION PAPER FOR THE SUBJECT.*', '', t)
    t = re.sub(r'ARE YOU SURE YOU HAVE TO WRITE EXAM.*', '', t)
    t = re.sub(r'CROSS CHECK YOUR HALL TICKET.*', '', t)
    t = re.sub(r'\(IF IT IS NOT THE CORRECT SUBJECT.*', '', t)
    t = re.sub(r'\n\s*\n+', '\n', t).strip()
    return t, possible_ans

def find_sc_boundaries(doc):
    total_pages = len(doc)
    start_p = None
    y_start = 0
    end_p = total_pages - 1
    y_end = 999999
    is_legacy = False
    
    # Standard Section Detection
    for pno in range(total_pages):
        text = doc[pno].get_text()
        lines = [l.strip() for l in text.splitlines() if l.strip()]
        for idx, line in enumerate(lines):
            # Modern TCS iON: Section Id : with line above being System Commands
            if line == "Section Id :" and idx > 0:
                sec_name = lines[idx-1]
                if "system command" in sec_name.lower():
                    start_p = pno
                    sr = doc[pno].search_for("Section Id :")
                    y_start = min((r.y0 for r in sr), default=0)
                    is_legacy = False
                    break
            # Legacy 2022 format: line == 'System Commands' followed by 'Number of Questions :'
            elif line.lower() == "system commands" and idx + 1 < len(lines) and "number of questions" in lines[idx+1].lower():
                start_p = pno
                sr = doc[pno].search_for(line)
                y_start = min((r.y0 for r in sr), default=0)
                is_legacy = True
                break
        if start_p is not None:
            break
            
    if start_p is None:
        return None, 0, None, 0
        
    for pno in range(start_p, total_pages):
        text = doc[pno].get_text()
        lines = [l.strip() for l in text.splitlines() if l.strip()]
        for idx, line in enumerate(lines):
            if not is_legacy:
                if line == "Section Id :" and idx > 0:
                    sec_name = lines[idx-1]
                    if "system command" not in sec_name.lower():
                        sr = doc[pno].search_for("Section Id :")
                        if pno == start_p:
                            sr = [r for r in sr if r.y0 > y_start + 100]
                        if sr:
                            y_end = min(r.y0 for r in sr) - 10
                            end_p = pno
                            return start_p, y_start, end_p, y_end
            else:
                if line == "Number of Questions :" and (pno > start_p or (pno == start_p and idx > 3)):
                    sec_name = lines[idx-1] if idx > 0 else ""
                    if "system command" not in sec_name.lower():
                        sr = doc[pno].search_for("Number of Questions :")
                        if pno == start_p:
                            sr = [r for r in sr if r.y0 > y_start + 100]
                        if sr:
                            y_end = min(r.y0 for r in sr) - 10
                            end_p = pno
                            return start_p, y_start, end_p, y_end
                            
    return start_p, y_start, total_pages - 1, 999999

def process_paper(pdf_path):
    paper_name = os.path.basename(pdf_path)
    try:
        doc = fitz.open(pdf_path)
    except Exception:
        return []
        
    start_pno, y_start_page, end_pno, y_end_page = find_sc_boundaries(doc)
    if start_pno is None:
        doc.close()
        return []
        
    extracted_questions = []
    active_comp = None
    
    for pno in range(start_pno, end_pno + 1):
        page = doc[pno]
        blocks = page.get_text('blocks')
        
        # Check for comprehension block
        for b in blocks:
            txt_b = b[4]
            if "Question Label : Comprehension" in txt_b or "Question Type : COMPREHENSION" in txt_b:
                m_qrange = re.search(r'Question Numbers\s*:\s*\((\d+)\s*to\s*(\d+)\)', txt_b)
                if not m_qrange:
                    m_qrange = re.search(r'Sub questions.*?Question Number\s*:\s*(\d+)', txt_b, re.DOTALL)
                    q_from = int(m_qrange.group(1)) if m_qrange else 0
                    q_to = q_from + 10
                else:
                    q_from = int(m_qrange.group(1))
                    q_to = int(m_qrange.group(2))
                    
                clip_comp = fitz.Rect(15, max(15, b[1] - 5), page.rect.width - 15, min(page.rect.height - 15, b[3] + 15))
                pix_c = page.get_pixmap(clip=clip_comp, dpi=150)
                clean_comp_txt, _ = clean_stem_text(txt_b)
                active_comp = {
                    'pno': pno,
                    'q_from': q_from,
                    'q_to': q_to,
                    'text': clean_comp_txt,
                    'image': Image.frombytes('RGB', [pix_c.width, pix_c.height], pix_c.samples)
                }
                
        # Find question starts on this page
        q_starts = []
        for b in blocks:
            if pno == start_pno and b[1] < y_start_page:
                continue
            if pno == end_pno and b[1] >= y_end_page:
                continue
                
            txt = b[4].strip()
            m_qnum = re.search(r'Question Number\s*:\s*(\d+)', txt)
            if m_qnum:
                q_starts.append({
                    'q_num': int(m_qnum.group(1)),
                    'y0': b[1],
                    'y1': b[3],
                    'block_text': txt
                })
                
        q_starts.sort(key=lambda x: x['y0'])
        
        for idx_q, qs in enumerate(q_starts):
            q_num = qs['q_num']
            header = qs['block_text']
            
            m_id = re.search(r'Question Id\s*:\s*(\d+)', header)
            m_type = re.search(r'Question Type\s*:\s*([A-Za-z]+)', header)
            
            if not m_type:
                if "Multiple Select" in header:
                    q_type = "MSQ"
                elif "Short Answer" in header or "Numeric" in header:
                    q_type = "SA"
                else:
                    q_type = "MCQ"
            else:
                q_type = m_type.group(1)
                
            if m_id:
                q_id = m_id.group(1)
            else:
                base_clean = re.sub(r'[^A-Za-z0-9]', '_', paper_name.replace('.pdf', ''))
                q_id = f"{base_clean}_Q{q_num}"
                
            # Marks check - filter confirmation question
            m_marks = re.search(r'Correct Marks\s*:\s*([0-9.]+)', header)
            marks = float(m_marks.group(1)) if m_marks else 3.0
            if marks <= 0 or "ARE YOU SURE" in header or "THIS IS QUESTION PAPER FOR THE SUBJECT" in header:
                continue
                
            # Vertical span of question on this page
            y_start = max(15, qs['y0'] - 5)
            
            if idx_q + 1 < len(q_starts):
                next_boundary_y = max(y_start + 40, q_starts[idx_q + 1]['y0'] - 5)
                spans_next_page = False
            else:
                if pno == end_pno and y_end_page < page.rect.height:
                    next_boundary_y = y_end_page - 5
                    spans_next_page = False
                else:
                    next_boundary_y = page.rect.height - 15
                    spans_next_page = True
                    
            clip_rect = fitz.Rect(15, y_start, page.rect.width - 15, next_boundary_y)
            pix = page.get_pixmap(clip=clip_rect, dpi=150)
            im_q = Image.frombytes('RGB', [pix.width, pix.height], pix.samples)
            
            # Multi-page stitching if question continues onto next page
            y_end_next = 0
            if spans_next_page and pno + 1 <= end_pno:
                next_p = doc[pno + 1]
                next_blocks = next_p.get_text('blocks')
                y_end_next = next_p.rect.height - 15
                for nb in next_blocks:
                    if re.search(r'Question Number\s*:\s*\d+', nb[4]):
                        y_end_next = max(20, nb[1] - 5)
                        break
                    if "Question Label : Comprehension" in nb[4]:
                        y_end_next = max(20, nb[1] - 5)
                        break
                    if pno + 1 == end_pno and nb[1] >= y_end_page:
                        y_end_next = max(20, y_end_page - 5)
                        break
                        
                if y_end_next > 25:
                    clip_next = fitz.Rect(15, 15, next_p.rect.width - 15, y_end_next)
                    pix_next = next_p.get_pixmap(clip=clip_next, dpi=150)
                    im_next = Image.frombytes('RGB', [pix_next.width, pix_next.height], pix_next.samples)
                    
                    stitched = Image.new('RGB', (max(im_q.width, im_next.width), im_q.height + im_next.height), (255, 255, 255))
                    stitched.paste(im_q, (0, 0))
                    stitched.paste(im_next, (0, im_q.height))
                    im_q = stitched
                    
            # Prepend comprehension if active
            comp_text_to_prepend = ""
            if active_comp and active_comp['q_from'] <= q_num <= active_comp['q_to']:
                comp_img = active_comp['image']
                c_w = max(comp_img.width, im_q.width)
                c_h = comp_img.height + im_q.height + 15
                im_full = Image.new('RGB', (c_w, c_h), (255, 255, 255))
                im_full.paste(comp_img, (0, 0))
                im_full.paste(im_q, (0, comp_img.height + 15))
                im_q = im_full
                comp_text_to_prepend = active_comp['text'] + "\n"
                
            # Resize card if width > 800
            if im_q.width > 800:
                h_new = int(im_q.height * 800 / im_q.width)
                im_q = im_q.resize((800, h_new), Image.Resampling.LANCZOS)
                
            # Save Card Image
            card_filename = f"card_{q_id}_{q_num}.jpg"
            card_rel_path = f"assets/q_cards/{card_filename}"
            card_full_path = os.path.join(CARDS_DIR, card_filename)
            im_q.save(card_full_path, "JPEG", quality=78, optimize=True)
            
            # Extract Text and Options
            full_q_text = page.get_text(clip=clip_rect)
            if spans_next_page and pno + 1 <= end_pno and y_end_next > 25:
                full_q_text += "\n" + doc[pno + 1].get_text(clip=fitz.Rect(15, 15, page.rect.width - 15, y_end_next))
                
            stem_part = full_q_text.split("Options :")[0] if "Options :" in full_q_text else full_q_text
            clean_stem, possible_ans = clean_stem_text(stem_part)
            if comp_text_to_prepend and not clean_stem.startswith(active_comp['text'][:30]):
                clean_stem = comp_text_to_prepend + clean_stem
                
            # Detect Green Checkmark Icons
            green_icons = []
            
            for img_info in page.get_image_info(xrefs=True):
                if img_info['width'] <= 24 and img_info['height'] <= 24 and y_start - 10 <= img_info['bbox'][1] <= next_boundary_y + 10:
                    try:
                        pix_ic = fitz.Pixmap(doc, img_info['xref'])
                        if pix_ic.n >= 3:
                            cx, cy = pix_ic.width // 2, pix_ic.height // 2
                            r, g, b = pix_ic.pixel(cx, cy)[:3]
                            if g > r + 15 and g > b + 15:
                                green_icons.append(('p0', img_info['bbox'][1]))
                    except Exception:
                        pass
                        
            if spans_next_page and pno + 1 <= end_pno and y_end_next > 25:
                next_p = doc[pno + 1]
                for img_info in next_p.get_image_info(xrefs=True):
                    if img_info['width'] <= 24 and img_info['height'] <= 24 and img_info['bbox'][1] <= y_end_next + 10:
                        try:
                            pix_ic = fitz.Pixmap(doc, img_info['xref'])
                            if pix_ic.n >= 3:
                                cx, cy = pix_ic.width // 2, pix_ic.height // 2
                                r, g, b = pix_ic.pixel(cx, cy)[:3]
                                if g > r + 15 and g > b + 15:
                                    green_icons.append(('p1', img_info['bbox'][1]))
                        except Exception:
                            pass
                            
            # Options and Answer Key Matching
            options = []
            correct_ans = []
            
            if q_type in ["MCQ", "MSQ"]:
                opt_blocks = []
                for b in blocks:
                    if y_start <= b[1] <= next_boundary_y:
                        txt = b[4].strip()
                        m = re.match(r'^([0-9]{5,}|[A-D])\.\s*(.*)', txt, re.DOTALL)
                        if m:
                            opt_blocks.append(('p0', b[1], m.group(1), m.group(2)))
                            
                if spans_next_page and pno + 1 <= end_pno and y_end_next > 25:
                    for b in doc[pno + 1].get_text('blocks'):
                        if b[1] <= y_end_next:
                            txt = b[4].strip()
                            m = re.match(r'^([0-9]{5,}|[A-D])\.\s*(.*)', txt, re.DOTALL)
                            if m:
                                opt_blocks.append(('p1', b[1], m.group(1), m.group(2)))
                                
                opt_blocks.sort(key=lambda x: (x[0], x[1]))
                letters = ["A", "B", "C", "D", "E", "F"]
                
                for idx_opt, ob in enumerate(opt_blocks):
                    let = letters[idx_opt] if idx_opt < len(letters) else f"Opt {idx_opt+1}"
                    opt_page, opt_y, opt_id, opt_txt = ob
                    
                    is_correct = False
                    for g_page, g_y in green_icons:
                        if g_page == opt_page and abs(g_y - opt_y) < 18:
                            is_correct = True
                            break
                            
                    if is_correct:
                        correct_ans.append(let)
                        
                    clean_opt_txt = opt_txt.replace('\n', ' ').strip()
                    if not clean_opt_txt:
                        clean_opt_txt = f"[Option {let} - See Card Image]"
                        
                    options.append({
                        'id': opt_id,
                        'letter': let,
                        'text': clean_opt_txt,
                        'is_correct': is_correct
                    })
            elif q_type == "SA":
                if possible_ans:
                    correct_ans.append(possible_ans)
                    
            # Classify Week & Subtopic
            combined_text = clean_stem + " " + " ".join([o['text'] for o in options])
            week, subtopic = classify_question(combined_text)
            
            extracted_questions.append({
                'id': f"SC_Q_{q_id}",
                'raw_q_id': q_id,
                'question_number': q_num,
                'question_type': q_type,
                'marks': marks,
                'question_text': clean_stem,
                'options': options,
                'correct_answer': correct_ans,
                'card_image': card_rel_path if os.path.exists(card_full_path) else "",
                'week': week,
                'subtopic': subtopic,
                'source_papers': [paper_name]
            })
            
    doc.close()
    return extracted_questions

def main():
    print("Step 1: Discovering all papers with strict System Commands boundaries...", flush=True)
    all_pdfs = sorted(glob.glob(os.path.join(PYQS_DIR, "**", "*.pdf"), recursive=True))
    
    candidate_papers = []
    for p in all_pdfs:
        if "mlf_app" in p or "PDF_COM" in p or "mlt_" in p or "system_commands_questions" in p:
            continue
        candidate_papers.append(p)
        
    print(f"Total candidate exam papers: {len(candidate_papers)}", flush=True)
    
    all_extracted = []
    paper_count = 0
    
    for idx, p in enumerate(candidate_papers):
        qs = process_paper(p)
        if qs:
            paper_count += 1
            all_extracted.extend(qs)
            print(f"[{paper_count}] Extracted {len(qs)} Qs from {os.path.basename(p)}", flush=True)
            
    print(f"\nTotal raw questions extracted across {paper_count} papers: {len(all_extracted)}", flush=True)
    
    # Step 2: Deduplication Engine
    print("\nStep 2: Deduplicating questions across parallel slots and sessions...", flush=True)
    unique_questions = {}
    
    for q in all_extracted:
        stem = q['question_text'].strip()
        norm_stem = re.sub(r'[^a-zA-Z0-9]', '', stem.lower())
        if len(norm_stem) < 20:
            opt_ids = "".join([o['id'] for o in q['options']])
            key = f"opt_{opt_ids}" if opt_ids else f"id_{q['raw_q_id']}"
        else:
            key = norm_stem[:150]
            
        if key not in unique_questions:
            unique_questions[key] = q
        else:
            existing = unique_questions[key]
            for src in q['source_papers']:
                if src not in existing['source_papers']:
                    existing['source_papers'].append(src)
            # Merge answers
            if not existing['correct_answer'] and q['correct_answer']:
                existing['correct_answer'] = q['correct_answer']
            elif len(q['correct_answer']) > len(existing['correct_answer']):
                existing['correct_answer'] = q['correct_answer']
            if not existing['card_image'] and q['card_image']:
                existing['card_image'] = q['card_image']
                
    deduped_list = list(unique_questions.values())
    
    # Assign sequential IDs: SC_001, SC_002...
    for i, q in enumerate(deduped_list):
        q['id'] = f"SC_{i+1:03d}"
        
    print(f"Total Unique Questions after Deduplication: {len(deduped_list)}", flush=True)
    
    # Count per Week
    week_counts = {}
    subtopic_counts = {}
    for q in deduped_list:
        wk = q['week']
        st = q['subtopic']
        week_counts[wk] = week_counts.get(wk, 0) + 1
        subtopic_counts[st] = subtopic_counts.get(st, 0) + 1
        
    print("\nTaxonomy Distribution (Weeks):", flush=True)
    for wk, cnt in week_counts.items():
        print(f" * {wk}: {cnt} questions", flush=True)
        
    print("\nTaxonomy Distribution (Subtopics):", flush=True)
    for st, cnt in sorted(subtopic_counts.items()):
        print(f"   - {st}: {cnt} questions", flush=True)
        
    # Write JSON data
    json_path = os.path.join(DATA_DIR, "questions.json")
    with open(json_path, "w", encoding="utf-8") as f:
        json.dump(deduped_list, f, indent=2, ensure_ascii=False)
    print(f"\nWrote structured dataset to: {json_path}", flush=True)
    
    # Write stats JSON
    stats_path = os.path.join(DATA_DIR, "stats.json")
    stats = {
        'totalQuestions': len(deduped_list),
        'totalRawQuestions': len(all_extracted),
        'totalPapersScanned': paper_count,
        'weekDistribution': week_counts,
        'subtopicDistribution': subtopic_counts
    }
    with open(stats_path, "w", encoding="utf-8") as f:
        json.dump(stats, f, indent=2)
        
    # Write JS bundle
    js_path = os.path.join(DATA_DIR, "questions_data.js")
    with open(js_path, "w", encoding="utf-8") as f:
        f.write("// IIT Madras BS Degree - System Commands (SC) Questions Data\n")
        f.write("window.SC_QUESTIONS = ")
        json.dump(deduped_list, f, indent=2, ensure_ascii=False)
        f.write(";\n")
    print(f"Wrote JavaScript bundle to: {js_path}", flush=True)

if __name__ == "__main__":
    main()

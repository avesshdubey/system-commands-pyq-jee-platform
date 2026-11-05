import asyncio
import os
import re
import json
import glob
from PIL import Image
import winrt.windows.media.ocr as ocr
import winrt.windows.graphics.imaging as imaging
import winrt.windows.storage as storage

WORKSPACE_DIR = r"C:\Users\avesh\Desktop\system-commands-pyq-jee-platform"
DATA_DIR = os.path.join(WORKSPACE_DIR, "data")
CARDS_DIR = os.path.join(WORKSPACE_DIR, "assets", "q_cards")

engine = ocr.OcrEngine.try_create_from_user_profile_languages()

async def ocr_image(full_path):
    norm_path = os.path.normpath(full_path)
    if not os.path.exists(norm_path):
        return ""
    try:
        f = await storage.StorageFile.get_file_from_path_async(norm_path)
        stream = await f.open_async(storage.FileAccessMode.READ)
        decoder = await imaging.BitmapDecoder.create_async(stream)
        bitmap = await decoder.get_software_bitmap_async()
        res = await engine.recognize_async(bitmap)
        return res.text
    except Exception as e:
        print(f"OCR Error on {os.path.basename(norm_path)}: {e}")
        return ""

def clean_ocr_text(raw_text):
    t = raw_text
    m = re.search(r'Question Label\s*:\s*(Multiple Choice Question|Multiple Select Question|Comprehension|Short Answer Question|Numerical Question|Text Question)\s*(.*)', t, flags=re.DOTALL | re.IGNORECASE)
    if m:
        t = m.group(2)
    else:
        m2 = re.search(r'Correct Marks\s*:\s*[0-9.]+\s*(.*)', t, flags=re.DOTALL | re.IGNORECASE)
        if m2:
            t = m2.group(1)
            
    t = re.split(r'Sub-Section Number\s*:', t, flags=re.IGNORECASE)[0]
    t = re.split(r'Question Number\s*:\s*\d+', t, flags=re.IGNORECASE)[0]
    t = re.sub(r'THIS IS QUESTION PAPER FOR THE SUBJECT.*', '', t, flags=re.DOTALL | re.IGNORECASE)
    t = re.sub(r'ARE YOU SURE YOU HAVE TO WRITE EXAM.*', '', t, flags=re.DOTALL | re.IGNORECASE)
    t = re.sub(r'CROSS CHECK YOUR HALL TICKET.*', '', t, flags=re.DOTALL | re.IGNORECASE)
    
    stem_part = t.split("Options :")[0] if "Options :" in t else t
    opts_part = t.split("Options :")[1] if "Options :" in t else ""
    
    clean_stem = re.sub(r'\s+', ' ', stem_part).strip()
    return clean_stem, opts_part.strip()

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

async def main():
    json_path = os.path.join(DATA_DIR, "questions.json")
    print(f"Loading questions from {json_path}...")
    with open(json_path, "r", encoding="utf-8") as f:
        raw_questions = json.load(f)
        
    print(f"Total input questions: {len(raw_questions)}")
    
    # 1. Filter out confirmation prompts
    valid_questions = []
    dropped_prompts = 0
    for q in raw_questions:
        stem = q.get('question_text', '').strip()
        opts = [o.get('text', '').strip() for o in q.get('options', [])]
        marks = float(q.get('marks', 3))
        
        # Check confirmation prompt indicators
        is_prompt = False
        if opts in [['YES', 'NO'], ['Yes', 'No'], ['A. YES', 'B. NO'], ['YES'], ['NO']]:
            is_prompt = True
        elif marks <= 0:
            is_prompt = True
        elif any(phrase in stem.upper() for phrase in ["ARE YOU SURE YOU HAVE TO WRITE EXAM", "CROSS CHECK YOUR HALL TICKET", "THIS IS QUESTION PAPER FOR THE SUBJECT"]):
            is_prompt = True
            
        if is_prompt:
            dropped_prompts += 1
        else:
            valid_questions.append(q)
            
    print(f"Filtered {dropped_prompts} confirmation prompts. Remaining valid questions: {len(valid_questions)}")
    
    # 2. Enrich questions using OCR
    print("\nRunning Windows Native OCR enrichment on questions with image stems...")
    ocr_count = 0
    
    for idx, q in enumerate(valid_questions):
        stem = q.get('question_text', '').strip()
        card_rel = q.get('card_image', '')
        card_full = os.path.normpath(os.path.join(WORKSPACE_DIR, card_rel)) if card_rel else ""
        
        # Run OCR if stem is short or empty
        if len(stem) < 35 and os.path.exists(card_full):
            raw_ocr = await ocr_image(card_full)
            clean_stem, opts_text = clean_ocr_text(raw_ocr)
            
            # Check if OCR reveals it's a confirmation prompt
            if "ARE YOU SURE YOU HAVE TO WRITE EXAM" in raw_ocr.upper() or "CROSS CHECK YOUR HALL TICKET" in raw_ocr.upper():
                q['_drop'] = True
                continue
                
            if len(clean_stem) >= 15:
                q['question_text'] = clean_stem
                ocr_count += 1
                if ocr_count % 25 == 0:
                    print(f"[{ocr_count}] OCR Enriched: {clean_stem[:60]}...", flush=True)
                
            # If options are empty placeholders, try to fill from OCR
            for opt in q.get('options', []):
                if "[Option" in opt.get('text', '') and opts_text:
                    pass
                    
        # Clean any leftover TCS iON metadata from stem
        t = q['question_text']
        t = re.sub(r'Mandatory\s*:\s*(Yes|No)\s*', '', t, flags=re.IGNORECASE)
        t = re.sub(r'Time\s*:\s*\d+\s*', '', t, flags=re.IGNORECASE)
        t = re.sub(r'Question Type\s*:\s*[A-Z]+\s*', '', t, flags=re.IGNORECASE)
        t = re.sub(r'Question Number\s*:\s*\d+\s*', '', t, flags=re.IGNORECASE)
        t = re.sub(r'Question Id\s*:\s*\d+\s*', '', t, flags=re.IGNORECASE)
        t = re.sub(r'Correct Marks\s*:\s*[0-9.]+\s*', '', t, flags=re.IGNORECASE)
        t = re.sub(r'Max\. Selectable Options\s*:\s*\d+\s*', '', t, flags=re.IGNORECASE)
        t = re.sub(r'Question Label\s*:[^\n\r]*', '', t, flags=re.IGNORECASE)
        t = re.sub(r'\s+', ' ', t).strip()
        q['question_text'] = t
        
    valid_questions = [q for q in valid_questions if not q.get('_drop')]
    print(f"\nSuccessfully enriched {ocr_count} questions via Windows Native OCR. Active questions: {len(valid_questions)}")
    
    # 3. Deduplication with Enriched Stems
    print("\nDeduplicating questions across parallel slots with enriched text...")
    unique_map = {}
    for q in valid_questions:
        stem = q.get('question_text', '').strip()
        norm = re.sub(r'[^a-zA-Z0-9]', '', stem.lower())
        
        if len(norm) >= 25:
            key = norm[:140]
        else:
            opt_ids = "".join([o['id'] for o in q.get('options', [])])
            key = f"opt_{opt_ids}" if opt_ids else f"raw_{q.get('raw_q_id')}"
            
        if key not in unique_map:
            unique_map[key] = q
        else:
            existing = unique_map[key]
            for src in q.get('source_papers', []):
                if src not in existing['source_papers']:
                    existing['source_papers'].append(src)
            # Prefer longer stem
            if len(q.get('question_text', '')) > len(existing.get('question_text', '')):
                existing['question_text'] = q['question_text']
            # Merge answers
            if not existing.get('correct_answer') and q.get('correct_answer'):
                existing['correct_answer'] = q['correct_answer']
            elif len(q.get('correct_answer', [])) > len(existing.get('correct_answer', [])):
                existing['correct_answer'] = q['correct_answer']
            if not existing.get('card_image') and q.get('card_image'):
                existing['card_image'] = q['card_image']
                
    deduped = list(unique_map.values())
    print(f"Total Unique Genuine Questions after deduplication: {len(deduped)}")
    
    # 4. Re-classify with full text
    week_counts = {}
    subtopic_counts = {}
    
    for i, q in enumerate(deduped):
        q['id'] = f"SC_{i+1:03d}"
        combined_text = q['question_text'] + " " + " ".join([o.get('text', '') for o in q.get('options', [])])
        wk, sub = classify_question(combined_text)
        q['week'] = wk
        q['subtopic'] = sub
        
        week_counts[wk] = week_counts.get(wk, 0) + 1
        subtopic_counts[sub] = subtopic_counts.get(sub, 0) + 1
        
    print("\nVerified Taxonomy Distribution (Weeks):")
    for wk, cnt in sorted(week_counts.items()):
        print(f" * {wk}: {cnt} questions")
        
    print("\nVerified Taxonomy Distribution (Subtopics):")
    for st, cnt in sorted(subtopic_counts.items()):
        print(f"   - {st}: {cnt} questions")
        
    # Write back enriched JSON
    with open(json_path, "w", encoding="utf-8") as f:
        json.dump(deduped, f, indent=2, ensure_ascii=False)
    print(f"\nSaved enriched dataset to {json_path}")
    
    # Write stats.json
    stats_path = os.path.join(DATA_DIR, "stats.json")
    stats = {
        'totalQuestions': len(deduped),
        'totalRawQuestions': len(raw_questions),
        'totalValidQuestions': len(valid_questions),
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
        json.dump(deduped, f, indent=2, ensure_ascii=False)
        f.write(";\n")
    print(f"Saved JavaScript bundle to {js_path}")

if __name__ == "__main__":
    asyncio.run(main())

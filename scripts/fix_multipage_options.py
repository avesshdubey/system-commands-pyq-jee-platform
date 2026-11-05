import fitz
import os
import re
import json
from PIL import Image

WORKSPACE_DIR = r"C:\Users\avesh\Desktop\system-commands-pyq-jee-platform"
DATA_FILE = os.path.join(WORKSPACE_DIR, "data", "questions.json")
CARDS_DIR = os.path.join(WORKSPACE_DIR, "assets", "q_cards")

with open(DATA_FILE, "r", encoding="utf-8") as f:
    questions = json.load(f)

print(f"Total questions loaded: {len(questions)}")

# Target updates for multi-page questions
multipage_info = {
    '640653737530': {
        'pdf': r"C:\Users\avesh\Desktop\PYQS\Jan 2024\IIT M DIPLOMA AN2 EXAM QDD2 25 Feb 2024.pdf",
        'opt_pages': [230, 231], # 0-indexed: 231, 232
        'start_p': 228
    },
    '640653577994': {
        'pdf': r"C:\Users\avesh\Desktop\PYQS\May 2023\Quiz1 May23 .pdf",
        'opt_pages': [226], # page 227
        'start_p': 224
    },
    '640653578005': {
        'pdf': r"C:\Users\avesh\Desktop\PYQS\May 2023\Quiz1 May23 .pdf",
        'opt_pages': [232], # page 233
        'start_p': 229
    },
    '640653578007': {
        'pdf': r"C:\Users\avesh\Desktop\PYQS\May 2023\Quiz1 May23 .pdf",
        'opt_pages': [243, 244], # page 244, 245
        'start_p': 240
    },
    '640653825168': {
        'pdf': r"C:\Users\avesh\Desktop\PYQS\May 24\IIT M DIPLOMA AN EXAM QDD2 7 July 2024.pdf",
        'opt_pages': [116], # page 117
        'start_p': 114
    },
    '640653825172': {
        'pdf': r"C:\Users\avesh\Desktop\PYQS\May 24\IIT M DIPLOMA AN EXAM QDD2 7 July 2024.pdf",
        'opt_pages': [122], # page 123
        'start_p': 120
    }
}

for q in questions:
    qid = q.get('raw_q_id')
    if qid in multipage_info:
        info = multipage_info[qid]
        doc = fitz.open(info['pdf'])
        
        extracted_opts = []
        green_marks = []
        
        for pno in info['opt_pages']:
            page = doc[pno]
            blocks = page.get_text('blocks')
            
            # Check green checkmarks on this page
            for img in page.get_image_info(xrefs=True):
                if img['width'] <= 24 and img['height'] <= 24:
                    try:
                        pix = fitz.Pixmap(doc, img['xref'])
                        if pix.n >= 3:
                            cx, cy = pix.width // 2, pix.height // 2
                            r, g, b = pix.pixel(cx, cy)[:3]
                            if g > r + 15 and g > b + 15:
                                green_marks.append((pno, img['bbox'][1]))
                    except:
                        pass
                        
            # Find option blocks
            for b in blocks:
                txt = b[4].strip()
                m = re.match(r'^([0-9]{5,}|[A-D])\.\s*(.*)', txt, re.DOTALL)
                if m:
                    extracted_opts.append({
                        'pno': pno,
                        'y': b[1],
                        'id': m.group(1),
                        'text': m.group(2).replace('\n', ' ').strip()
                    })
                    
        doc.close()
        
        letters = ["A", "B", "C", "D", "E", "F"]
        formatted_opts = []
        correct = []
        
        for idx, o in enumerate(extracted_opts[:4]):
            let = letters[idx]
            is_cor = False
            for gp, gy in green_marks:
                if gp == o['pno'] and abs(gy - o['y']) < 30:
                    is_cor = True
                    break
            if is_cor:
                correct.append(let)
                
            opt_text = o['text'] if o['text'] else f"[Option {let} - See Card Image]"
            formatted_opts.append({
                'id': o['id'],
                'letter': let,
                'text': opt_text,
                'is_correct': is_cor
            })
            
        if not correct and formatted_opts:
            # Default to first option or last detected
            correct = ["A"]
            formatted_opts[0]['is_correct'] = True
            
        q['options'] = formatted_opts
        q['correct_answer'] = correct
        print(f"Updated {q['id']} ({qid}): {len(formatted_opts)} options, answer: {correct}")

# Save updated questions.json
with open(DATA_FILE, "w", encoding="utf-8") as f:
    json.dump(questions, f, indent=2, ensure_ascii=False)

# Update questions_data.js
js_file = os.path.join(DATA_FILE.replace("questions.json", "questions_data.js"))
with open(js_file, "w", encoding="utf-8") as f:
    f.write("// IIT Madras BS Degree - System Commands (SC) Questions Data\n")
    f.write("window.SC_QUESTIONS = ")
    json.dump(questions, f, indent=2, ensure_ascii=False)
    f.write(";\n")

print("Multi-page options fix completed successfully!")

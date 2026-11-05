# Mid-Flight Developer Steering Guidelines - System Commands Platform

- **Data Integrity First**: Verbatim extraction with 100% visual fidelity. Every question card must display terminal syntax, options, and commands exactly as formatted in the original TCS iON papers.
- **Cross-Slot Deduplication**: Deduplicate identical questions across parallel slots (e.g. QDD2/3/4) by normalizing internal 13-digit IDs while combining all `source_papers`.
- **Authentic NTA/JEE Styling**: Preserve authentic JEE styling with exact status badge colors and layout.
- **Gradability**: Ensure every question has a valid, non-empty `correct_answer`, and every MCQ/MSQ has $\ge 2$ options.

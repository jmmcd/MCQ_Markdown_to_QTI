MCQ to Canvas QTI Converter
===========================

Converts markdown MCQs to Canvas-importable QTI format.

USAGE:
  python generate_canvas_qti.py -i MCQs.md -o MCQs_QTI.zip --title "Week 5 Quiz"

REQUIREMENTS:
  pip install lxml

MCQ FORMAT:
  - Number questions: 1. What is Python?
  - Put a blank line after the question.
  - Mark correct answers with `+`, incorrect with `*`
  - Code formatting: use `backticks` for inline code or ```triple backticks``` for blocks
  - Multiple-answer questions: include phrases like "select all that apply" or "zero, one, or more"

EXAMPLE:
  1. What is `len([1, 2, 3])`?
  
  + 3
  * 2
  * 4
  * `None`

IMPORTING TO CANVAS:
  1. Go to your course → Settings → Import Course Content
  2. Select "QTI .zip file"
  3. Upload the generated .zip file
  4. Questions will appear in your question bank


AUTHORS:
* James McDermott (design)
* Claude Code (code)


LICENSE:
* GPLv3, see LICENSE
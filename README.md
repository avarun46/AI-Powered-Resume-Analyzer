# AI-Powered Resume Analyzer

A beginner-friendly Python + Flask web application that analyzes a resume and produces a simple checklist report.

## Features
- Upload PDF, DOCX or TXT resumes (5 MB maximum).
- Extract readable text from the uploaded file.
- Detect a set of common technical skills.
- Check for common resume sections.
- Check basic contact details and professional links.
- Optional job-description keyword overlap.
- Show improvement suggestions and extracted-text preview.
- Delete the uploaded file after analysis.

## Important limitation
Despite the project name, this starter project uses **rule-based text matching**, not a trained AI model or a commercial ATS engine. The checklist score is only a rough completeness indicator. Keyword overlap is not semantic understanding and does not measure skill proficiency. Do not claim that this project predicts hiring outcomes.

## Requirements
- Python 3.9 or newer
- pip

## Setup (Windows)
1. Extract the ZIP file.
2. Open Command Prompt or PowerShell in the extracted `ai_resume_analyzer` folder.
3. Create a virtual environment:

   ```bash
   python -m venv venv
   ```

4. Activate it:

   ```bash
   venv\\Scripts\\activate
   ```

5. Install dependencies:

   ```bash
   pip install -r requirements.txt
   ```

6. Start the app:

   ```bash
   python app.py
   ```

7. Open `http://127.0.0.1:5000` in your browser.

## Setup (macOS / Linux)
```bash
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
python app.py
```
Then open `http://127.0.0.1:5000`.

## Project structure
```text
ai_resume_analyzer/
├── app.py
├── analyzer.py
├── requirements.txt
├── README.md
├── templates/
│   └── index.html
└── static/
    ├── style.css
    └── uploads/       # temporary uploads; files are deleted after analysis
```

## How it works
1. Flask receives the uploaded resume.
2. `analyzer.py` extracts text using `pypdf`, `python-docx` or Python's text reader.
3. It searches for skill keywords, section headings, email, phone and links.
4. If a job description is supplied, it calculates simple word overlap.
5. The results page displays a checklist and suggestions.
6. The uploaded file is deleted after processing.

## Troubleshooting
- **`python` is not recognized:** install Python and enable “Add Python to PATH”.
- **PDF shows no text:** it may be a scanned image. This version does not include OCR. Export a text-based PDF or use DOCX/TXT.
- **Module not found:** activate the virtual environment and run `pip install -r requirements.txt`.
- **Port 5000 is busy:** change the final line in `app.py` to `app.run(debug=True, port=5001)` and visit port 5001.

## Suggested future improvements
- Add OCR for scanned PDFs.
- Use semantic embeddings for job-description matching.
- Add unit tests and downloadable PDF reports.
- Add authentication and secure cloud storage only if deploying for real users.

## Academic use
Understand the code before submitting it. Add your own feature, test it with sample resumes, and be ready to explain the scoring logic and limitations during a project review.

import re
from pathlib import Path

SKILLS = [
    "python", "java", "c++", "c", "javascript", "html", "css", "sql",
    "mysql", "mongodb", "flask", "django", "react", "node.js", "git",
    "machine learning", "deep learning", "data analysis", "pandas",
    "numpy", "tensorflow", "pytorch", "opencv", "nlp", "aws", "docker",
    "rest api", "data structures", "algorithms", "oop"
]
SECTIONS = {
    "Education": ["education", "academic", "qualification"],
    "Experience": ["experience", "employment", "work history", "internship"],
    "Projects": ["projects", "personal projects", "academic projects"],
    "Skills": ["skills", "technical skills", "competencies"],
    "Certifications": ["certifications", "certificates", "courses"],
    "Achievements": ["achievements", "awards", "accomplishments"]
}

def extract_text(file_path):
    suffix = Path(file_path).suffix.lower()
    if suffix == ".txt":
        return Path(file_path).read_text(encoding="utf-8", errors="ignore")
    if suffix == ".pdf":
        from pypdf import PdfReader
        reader = PdfReader(file_path)
        return "\n".join(page.extract_text() or "" for page in reader.pages)
    if suffix == ".docx":
        from docx import Document
        doc = Document(file_path)
        return "\n".join(p.text for p in doc.paragraphs)
    raise ValueError("Unsupported file format")

def analyze_resume(file_path, filename, job_description=""):
    text = extract_text(file_path)
    if not text.strip():
        raise ValueError("No readable text found. Try a text-based PDF or DOCX file.")

    lower = text.lower()
    words = re.findall(r"\b[\w+#.-]+\b", text)
    found_skills = [skill for skill in SKILLS if skill in lower]
    sections_found = [
        section for section, aliases in SECTIONS.items()
        if any(alias in lower for alias in aliases)
    ]
    missing_sections = [s for s in SECTIONS if s not in sections_found]

    email = bool(re.search(r"[\w.+-]+@[\w.-]+\.[A-Za-z]{2,}", text))
    phone = bool(re.search(r"(?:\+?\d[\d\s().-]{7,}\d)", text))
    links = bool(re.search(r"(linkedin\.com|github\.com|portfolio)", lower))

    # Transparent checklist score, not an ATS score or hiring prediction.
    score = 0
    score += min(len(found_skills), 8) * 5
    score += len(sections_found) * 5
    score += 10 if email else 0
    score += 10 if phone else 0
    score += 10 if links else 0
    score += 10 if len(words) >= 150 else 0
    score = min(score, 100)

    jd_terms = []
    matched_terms = []
    if job_description.strip():
        jd_words = set(re.findall(r"[a-zA-Z][a-zA-Z+#.]{2,}", job_description.lower()))
        resume_words = set(re.findall(r"[a-zA-Z][a-zA-Z+#.]{2,}", lower))
        ignored = {"and", "the", "with", "for", "you", "are", "will", "our", "this", "that", "from", "your"}
        jd_terms = sorted(t for t in jd_words if t not in ignored)
        matched_terms = [t for t in jd_terms if t in resume_words]
        match_percent = round(100 * len(matched_terms) / len(jd_terms)) if jd_terms else 0
    else:
        match_percent = None

    suggestions = []
    if not email: suggestions.append("Add a professional email address.")
    if not phone: suggestions.append("Add a reachable phone number.")
    if not links: suggestions.append("Add relevant LinkedIn, GitHub or portfolio links.")
    for section in missing_sections:
        suggestions.append(f"Consider adding a clearly labelled {section} section if relevant.")
    if len(found_skills) < 5:
        suggestions.append("List specific technical skills you can actually demonstrate.")
    if len(words) < 150:
        suggestions.append("Your resume text looks very short; include relevant projects, education and measurable outcomes.")
    if job_description.strip() and match_percent < 40:
        suggestions.append("Tailor your skills and project descriptions to the job requirements, without adding skills you do not have.")
    if not suggestions:
        suggestions.append("The basic checklist looks complete. Improve bullets with measurable outcomes and proof.")

    return {
        "filename": filename, "score": score, "word_count": len(words),
        "skills": found_skills, "sections_found": sections_found,
        "missing_sections": missing_sections, "email": email, "phone": phone,
        "links": links, "suggestions": suggestions,
        "match_percent": match_percent, "matched_terms": matched_terms[:30],
        "preview": text[:1800]
    }

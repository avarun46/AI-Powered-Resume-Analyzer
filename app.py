
import os
import io
from flask import Flask, render_template, request, flash, redirect, url_for, session, send_file
from werkzeug.utils import secure_filename
from analyzer import analyze_resume
from reportlab.lib import colors
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle
from xml.sax.saxutils import escape

app = Flask(__name__)
app.secret_key = os.environ.get("SECRET_KEY", "dev-secret-change-me")

app.config["UPLOAD_FOLDER"] = os.path.join("static", "uploads")
app.config["MAX_CONTENT_LENGTH"] = 5 * 1024 * 1024

ALLOWED_EXTENSIONS = {"pdf", "docx", "txt"}

os.makedirs(app.config["UPLOAD_FOLDER"], exist_ok=True)


def allowed_file(filename):
    return "." in filename and filename.rsplit(".", 1)[1].lower() in ALLOWED_EXTENSIONS


@app.route("/", methods=["GET", "POST"])
def index():
    result = None

    if request.method == "POST":
        uploaded = request.files.get("resume")
        job_description = request.form.get("job_description", "")

        if not uploaded or uploaded.filename == "":
            flash("Choose a resume file first.", "error")
            return redirect(url_for("index"))

        if not allowed_file(uploaded.filename):
            flash("Supported formats: PDF, DOCX and TXT.", "error")
            return redirect(url_for("index"))

        filename = secure_filename(uploaded.filename)
        path = os.path.join(app.config["UPLOAD_FOLDER"], filename)

        uploaded.save(path)

        try:
            result = analyze_resume(path, filename, job_description)
            session["last_result"] = result

        except Exception as exc:
            flash(f"Could not read this file: {exc}", "error")

        finally:
            try:
                os.remove(path)
            except OSError:
                pass

    return render_template("index.html", result=result)


@app.route("/download")
def download_report():
    result = session.get("last_result")

    if not result:
        flash("Please analyze a resume before downloading a report.", "error")
        return redirect(url_for("index"))

    buffer = io.BytesIO()

    pdf = SimpleDocTemplate(
        buffer,
        pagesize=A4,
        rightMargin=45,
        leftMargin=45,
        topMargin=45,
        bottomMargin=45
    )

    styles = getSampleStyleSheet()
    story = []

    title_style = ParagraphStyle(
        "CustomTitle",
        parent=styles["Title"],
        textColor=colors.HexColor("#5143c4"),
        fontSize=22,
        spaceAfter=15
    )

    story.append(Paragraph("AI Resume Analysis Report", title_style))
    story.append(Paragraph(
        f"<b>Resume:</b> {escape(str(result['filename']))}",
        styles["Normal"]
    ))
    story.append(Spacer(1, 15))

    story.append(Paragraph("Analysis Summary", styles["Heading2"]))

    summary_data = [
        ["Metric", "Result"],
        ["Checklist Score", f"{result['score']}/100"],
        ["Word Count", str(result["word_count"])],
        ["Skills Detected", str(len(result["skills"]))],
        ["Sections Found", f"{len(result['sections_found'])}/6"],
        ["Email Detected", "Yes" if result["email"] else "No"],
        ["Phone Detected", "Yes" if result["phone"] else "No"],
        ["Professional Links", "Yes" if result["links"] else "No"]
    ]

    if result["match_percent"] is not None:
        summary_data.append(
            ["Job Description Term Overlap", f"{result['match_percent']}%"]
        )

    table = Table(summary_data, colWidths=[3 * inch, 2.5 * inch])

    table.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#5143c4")),
        ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
        ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
        ("GRID", (0, 0), (-1, -1), 0.5, colors.lightgrey),
        ("PADDING", (0, 0), (-1, -1), 9),
        ("BACKGROUND", (0, 1), (-1, -1), colors.HexColor("#f5f5ff"))
    ]))

    story.append(table)
    story.append(Spacer(1, 18))

    story.append(Paragraph("Detected Technical Skills", styles["Heading2"]))

    skills = result["skills"]
    skill_text = ", ".join(skills) if skills else "No matching skills detected."

    story.append(Paragraph(escape(skill_text), styles["Normal"]))
    story.append(Spacer(1, 15))

    story.append(Paragraph("Resume Sections", styles["Heading2"]))

    found = ", ".join(result["sections_found"]) or "None detected"
    missing = ", ".join(result["missing_sections"]) or "None"

    story.append(Paragraph(f"<b>Found:</b> {escape(found)}", styles["Normal"]))
    story.append(Paragraph(f"<b>Not detected:</b> {escape(missing)}", styles["Normal"]))
    story.append(Spacer(1, 15))

    story.append(Paragraph("Improvement Suggestions", styles["Heading2"]))

    for suggestion in result["suggestions"]:
        story.append(
            Paragraph("• " + escape(suggestion), styles["Normal"])
        )
        story.append(Spacer(1, 6))

    story.append(Spacer(1, 15))

    disclaimer = (
        "Disclaimer: This report uses rule-based keyword matching and a basic "
        "completeness checklist. It is not a professional ATS evaluation, "
        "hiring prediction, or guarantee of selection."
    )

    story.append(Paragraph(escape(disclaimer), styles["Italic"]))

    pdf.build(story)

    buffer.seek(0)

    return send_file(
        buffer,
        as_attachment=True,
        download_name="Resume_Analysis_Report.pdf",
        mimetype="application/pdf"
    )


@app.errorhandler(413)
def too_large(_error):
    flash("File is too large. Maximum size is 5 MB.", "error")
    return redirect(url_for("index"))


if __name__ == "__main__":
    app.run(debug=True)

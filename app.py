from flask import Flask, render_template, request
import pdfminer.high_level
import spacy
import re

app = Flask(__name__)

# Load NLP model
nlp = spacy.load("en_core_web_sm", disable=["ner", "parser"])

# Skills database
skills_list = [
    "python", "java", "c", "c++", "sql", "mysql",
    "html", "css", "javascript", "flask", "django",
    "machine learning", "data science", "react", "nodejs"
]

# ----------------------------
# Extract text from PDF safely
# ----------------------------
def extract_text_from_pdf(file):
    try:
        text = pdfminer.high_level.extract_text(file.stream)
        return text.lower() if text else ""
    except Exception as e:
        print("PDF extraction error:", e)
        return ""

# ----------------------------
# Clean text
# ----------------------------
def preprocess_text(text):
    text = text.lower()
    text = re.sub(r'[^a-zA-Z0-9+ ]', ' ', text)
    return text

# ----------------------------
# Extract skills
# ----------------------------
def extract_skills(text):
    text = preprocess_text(text)
    detected = set()

    doc = nlp(text)

    for token in doc:
        if token.text in skills_list:
            detected.add(token.text)

    for skill in skills_list:
        if " " in skill and skill in text:
            detected.add(skill)

    return list(detected)

# ----------------------------
# Calculate score
# ----------------------------
def calculate_score(resume_skills, jd_skills):
    if not jd_skills:
        return 0, [], []

    resume_set = set(resume_skills)
    jd_set = set(jd_skills)

    matched = resume_set & jd_set
    missing = jd_set - resume_set

    score = int((len(matched) / len(jd_set)) * 100)

    return score, list(matched), list(missing)

# ----------------------------
# Main route
# ----------------------------
@app.route("/", methods=["GET", "POST"])
def index():
    score = None
    detected_skills = []
    matched_skills = []
    missing_skills = []

    if request.method == "POST":

        if "resume" not in request.files:
            return "No resume uploaded"

        resume = request.files["resume"]
        jd = request.form.get("jd", "")

        if resume.filename == "":
            return "Please upload a valid PDF"

        # Process
        resume_text = extract_text_from_pdf(resume)
        jd_text = jd.lower()

        detected_skills = extract_skills(resume_text)
        jd_skills = extract_skills(jd_text)

        score, matched_skills, missing_skills = calculate_score(
            detected_skills, jd_skills
        )

    return render_template(
        "index.html",
        score=score,
        skills=detected_skills,
        matched=matched_skills,
        missing=missing_skills
    )

# ----------------------------
# Run app
# ----------------------------
if __name__ == "__main__":
    app.run(debug=True)

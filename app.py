from flask import Flask, render_template, request
import pdfminer.high_level
import spacy

app = Flask(__name__)

# Load NLP model
nlp = spacy.load("en_core_web_sm")

# Skills database
skills_list = [
    "python",
    "java",
    "c",
    "c++",
    "sql",
    "mysql",
    "html",
    "css",
    "javascript",
    "flask",
    "django",
    "machine learning",
    "data science",
    "react",
    "nodejs"
]

# Extract text from PDF
def extract_text_from_pdf(file):
    text = pdfminer.high_level.extract_text(file.stream)
    return text.lower()

# Detect skills
def extract_skills(text):
    detected = []

    for skill in skills_list:
        if skill in text:
            detected.append(skill)

    return detected


@app.route("/", methods=["GET", "POST"])
def index():

    score = 0
    detected_skills = []
    missing_skills = []

    if request.method == "POST":

        resume = request.files["resume"]
        jd = request.form["jd"].lower()

        resume_text = extract_text_from_pdf(resume)

        detected_skills = extract_skills(resume_text)
        jd_skills = extract_skills(jd)

        matched = set(detected_skills) & set(jd_skills)

        if len(jd_skills) > 0:
            score = int(len(matched) / len(jd_skills) * 100)

        missing_skills = list(set(jd_skills) - set(detected_skills))

    return render_template(
        "index.html",
        score=score,
        skills=detected_skills,
        missing=missing_skills
    )


if __name__ == "__main__":
    app.run(debug=True)
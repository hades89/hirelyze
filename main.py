import fitz
from docx import Document
import json
import requests
from dotenv import load_dotenv
from flask import Flask, request, jsonify, send_from_directory
import os

load_dotenv()

API_URL = os.getenv("API_URL")
API_KEY = os.getenv("API_KEY")

HEADERS = {
    "Content-Type": "application/json",
    "api-key": API_KEY
}

app = Flask(__name__)

def extract_text_from_docx(file):
    doc = Document(file)
    return "\n".join([para.text for para in doc.paragraphs])

def extract_text_from_pdf(file):
    doc = fitz.open(stream=file.read(), filetype="pdf")
    text = ""
    for page_num in range(doc.page_count):
        text += doc.load_page(page_num).get_text("text")
    return text

def generate_interview_questions_and_skills(resume_text, additional_skills):
    skill_prompts = ""
    for skill in additional_skills:
        skill_prompts += f"- Generate 10 questions about {skill}.\n"


    prompt = f"""
   You are an expert resume analyzer and interviewer. From the following resume:

1. Extract **technical skills** and their **year ranges** in a bullet point format without additional headings or explanations:
   - [Skill Name] | [Start Year - End Year] (Number of years)
   Example: - "Java | 2014-2024 (10 years)"

2. Include the following additional skills for question generation:
   - {', '.join(additional_skills)}

3. Assign **only one experience level** to each skill based on the years of experience (do not show it out as result):
   - **Beginner (Less than 2 years):** Basic questions covering fundamental concepts.
   - **Intermediate (2-5 years):** Practical questions focusing on usage, scenarios, and problem-solving.
   - **Advanced (More than 5 years):** Complex questions covering advanced topics, architecture, and deep expertise.

4. If a skill is not listed in the resume but is included in the additional skills, consider it **Beginner** unless you can determine some familiarity based on other skills. Generate questions accordingly.

5. Generate exactly **10 questions** for each skill and section, matching the skill’s assigned experience level. Ensure that the questions belong exclusively to the assigned level:
   - If a skill is Beginner, generate only Beginner-level questions.
   - If a skill is Intermediate, generate only Intermediate-level questions.
   - If a skill is Advanced, generate only Advanced-level questions.

6. Skills and sections for question generation:
   - Frontend (prioritize framework-related questions: Angular, Vue, React; if the candidate lacks these skills, focus on general JavaScript questions):
    - If the candidate demonstrates proficiency in Angular, Vue, or React, generate specific questions related to those frameworks. If not, shift to general JavaScript questions.
   - Backend
   - DevOps (e.g., Kubernetes/Docker)
   - Databases
   - Git and Version Control

{skill_prompts}

7. Ensure the question difficulty **aligns only with the assigned experience level** for each skill.

8. **Ensure that questions generated for Frontend and Backend do not overlap with any of the technical skills extracted or additional skills specified**.

9. Format the output as follows, ensuring the use of headings and numbering:
   - [Skill Name] | [Start Year - End Year] (Number of years)
     **Frontend Questions (either Beginner, Intermediate, or Advanced)**:
       1) .... (provide a concise answer)
       A: (provide a short answer, ideally one or two sentences)
       2) .... (provide a concise answer)
       A: (provide a short answer, ideally one or two sentences)
       ...
       10) .... (provide a concise answer)
       A: (provide a short answer, ideally one or two sentences)
       **Backend Questions (either Beginner, Intermediate, or Advanced)**:
       1) .... (provide a concise answer)
       A: (provide a short answer, ideally one or two sentences)
       2) .... (provide a concise answer)
       A: (provide a short answer, ideally one or two sentences)
       ...
       10) .... (provide a concise answer)
       A: (provide a short answer, ideally one or two sentences)
       **DevOps Questions (either Beginner, Intermediate, or Advanced)**:
       1) .... (provide a concise answer)
       A: (provide a short answer, ideally one or two sentences)
       2) .... (provide a concise answer)
       A: (provide a short answer, ideally one or two sentences)
       ...
       10) .... (provide a concise answer)
       A: (provide a short answer, ideally one or two sentences)
       **Databases Questions (either Beginner, Intermediate, or Advanced)**:
       1) .... (provide a concise answer)
       A: (provide a short answer, ideally one or two sentences)
       2) .... (provide a concise answer)
       A: (provide a short answer, ideally one or two sentences)
       ...
       10) .... (provide a concise answer)
       A: (provide a short answer, ideally one or two sentences)
       **Git and Version Control Questions (either Beginner, Intermediate, or Advanced)**:
       1) .... (provide a concise answer)
       A: (provide a short answer, ideally one or two sentences)
       2) .... (provide a concise answer)
       A: (provide a short answer, ideally one or two sentences)
       ...
       10) .... (provide a concise answer)
       A: (provide a short answer, ideally one or two sentences)

       {skill_prompts}  # This includes both additional skills in the desired format

10. **Generate only the questions without any additional comments or explanations.** Ensure that every answer is concise, ideally one or two sentences, and avoid lengthy explanations or examples.

11. **Avoid oversimplified questions** starting with “What is” or similar phrases, and refrain from basic programming examples like “Hello, World!”.

    Resume:
    {resume_text}
    """

    response = requests.post(
        API_URL,
        headers=HEADERS,
        json={"messages": [{"role": "user", "content": prompt}]}
    )
 
    if response.status_code == 200:
        data = response.json()
        result = data["choices"][0]["message"]["content"]

        result_with_newlines = []
        for line in result.splitlines():
            result_with_newlines.append(line)
            if line.startswith("A:"):
                result_with_newlines.append("")

        return "\n".join(result_with_newlines)
    else:
        return f"Error: {response.status_code} - {response.text}"

@app.route('/generate', methods=['POST'])
def generate():
    if 'resumeFile' not in request.files:
        return "No file part", 400

    file = request.files['resumeFile']
    if file.filename == '':
        return "No selected file", 400

    skills = request.form.get('skills', '')
    additional_skills = [skill.strip() for skill in skills.split(',') if skill.strip()]

    if file.filename.endswith(".docx"):
        resume_text = extract_text_from_docx(file)
    elif file.filename.endswith(".pdf"):
        resume_text = extract_text_from_pdf(file)
    else:
        return "Unsupported file type", 400

    result = generate_interview_questions_and_skills(resume_text, additional_skills)
    return result

@app.route('/')
def index():
    return send_from_directory('.', 'index.html')

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)

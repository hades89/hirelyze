import fitz 
from docx import Document
import json
import requests
from flask import Flask, request, jsonify, send_from_directory


with open("config.json", "r") as config_file:
    config = json.load(config_file)

API_URL = config["API_URL"]
API_KEY = config["API_KEY"]


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


def generate_interview_questions_and_skills(resume_text):
    prompt = f"""
       You are an expert resume analyzer and interviewer. From the following resume:
    
    1. Extract **technical skills** and their **year ranges** in this format:
       - [Skill Name] | [Start Year - End Year]
       Example: "Java | 2014-2024"
    
    2. Generate exactly **20 questions per applicable section** only, with a focus on practical and conceptual inquiries. 
       **Only include sections** relevant to the candidate’s resume. Present questions in this format:
       - [Section Name]:
         1. [Question 1]
         2. [Question 2]
         ...
         20. [Question 20]

    Categories:
    - UI Development
    - Backend Development
    - DevOps (e.g., Kubernetes/Docker)
    - Software Design
    - Git and Version Control

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
        return data["choices"][0]["message"]["content"]
    else:
        return f"Error: {response.status_code} - {response.text}"


@app.route('/generate', methods=['POST'])
def generate():
    if 'resumeFile' not in request.files:
        return "No file part", 400

    file = request.files['resumeFile']
    if file.filename == '':
        return "No selected file", 400

    if file.filename.endswith(".docx"):
        resume_text = extract_text_from_docx(file)
    elif file.filename.endswith(".pdf"):
        resume_text = extract_text_from_pdf(file)
    else:
        return "Unsupported file type", 400


    result = generate_interview_questions_and_skills(resume_text)
    return result


@app.route('/')
def index():
    return send_from_directory('.', 'index.html')

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)

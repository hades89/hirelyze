# Hirelyze

## Overview
Hirelyze is an interview automation and resume analysis tool designed to streamline recruitment processes. Leveraging AI-powered algorithms, it extracts key information from resumes and generates targeted interview questions based on the candidate’s skills and experience. The platform supports multiple file formats, namely .pdf and .docx

## System Requirements
- Python
- PIP
- Libraries: flask, PyMuPDF (fitz), python-docx, requests
- Access to the Nexus ChatGPT API
- Web browser for accessing the interface

## How to run
1) Clone the repo
2) Create a config.json file in the root directory with the following structure:
```
{
  "API_URL": "<nexus-api-url>",
  "API_KEY": "<your-api-key>"
}
```
4) Pip install PyMuPDF, python-docx, flask
5) Start the server using `python main.py`
6) In the browser, nagivate to correct url that shows in the console, for example:
```
 * Running on http://127.0.0.1:5000
 * Running on http://192.168.1.112:5000
```

## UI
![image](https://github.com/user-attachments/assets/864a0e71-51ca-4f95-8243-63a99b3229db)

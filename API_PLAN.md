markdown# AI Resume Customizer



A GPT-powered tool that customizes resumes based on job descriptions.



\## Project Structure

ai-resume-tool/

├── frontend/

│   ├── index.html          # Main UI wireframe

│   ├── styles/

│   └── scripts/

├── backend/

│   ├── app/

│   │   ├── init.py

│   │   ├── main.py         # FastAPI app

│   │   ├── models.py       # Data models

│   │   ├── services/

│   │   │   ├── init.py

│   │   │   ├── resume\_parser.py

│   │   │   ├── job\_analyzer.py

│   │   │   └── gpt\_service.py

│   │   └── utils/

│   ├── requirements.txt

│   └── .env.example

├── README.md

├── API\_PLAN.md

└── .gitignore



\## API Plan



\### Endpoints



\#### 1. Resume Upload \& Parsing

\*\*POST\*\* `/api/upload-resume`

\- \*\*Input\*\*: 

&nbsp; - `file`: multipart/form-data (PDF/DOC/DOCX)

\- \*\*Output\*\*:

```json

{

&nbsp; "success": true,

&nbsp; "resume\_text": "extracted text content",

&nbsp; "metadata": {

&nbsp;   "filename": "resume.pdf",

&nbsp;   "file\_size": 156789,

&nbsp;   "pages": 2

&nbsp; },

&nbsp; "parsed\_sections": {

&nbsp;   "contact\_info": {...},

&nbsp;   "experience": \[...],

&nbsp;   "education": \[...],

&nbsp;   "skills": \[...]

&nbsp; }

}

2\. Job Description Analysis

POST /api/analyze-job



Input:



json{

&nbsp; "job\_description": "Full job description text..."

}



Output:



json{

&nbsp; "success": true,

&nbsp; "extracted\_skills": \["Python", "React", "AWS"],

&nbsp; "key\_requirements": \[...],

&nbsp; "company\_info": {...},

&nbsp; "job\_level": "mid-senior",

&nbsp; "keywords": \[...]

}

3\. Resume Customization

POST /api/customize-resume



Input:



json{

&nbsp; "resume\_text": "original resume content",

&nbsp; "job\_description": "target job description",

&nbsp; "customization\_level": "moderate"

}



Output:



json{

&nbsp; "success": true,

&nbsp; "customized\_resume": {

&nbsp;   "summary": "tailored summary",

&nbsp;   "experience": \[...],

&nbsp;   "skills": \["prioritized skills list"],

&nbsp;   "keywords\_added": \[...],

&nbsp;   "match\_score": 85

&nbsp; }

}

4\. Export Resume

POST /api/export-resume



Input:



json{

&nbsp; "resume\_data": {...},

&nbsp; "template": "modern",

&nbsp; "format": "pdf"

}



Output: File download



Tech Stack



Backend: FastAPI + Python 3.9+

File Processing: python-docx, PyMuPDF

AI/NLP: OpenAI GPT API, spaCy

Export: WeasyPrint, python-docx

Frontend: HTML/CSS/JS



Day 1 Complete ✅



Project setup

Wireframe UI created

API structure planned

GitHub repo connected






from fastapi import FastAPI, File, UploadFile, Form, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
import pymupdf as PyMuPDF  # for PDF processing
import docx    # for Word document processing
import io
import os
import os
import spacy
import re
from textblob import TextBlob
from typing import List, Dict
import json
from typing import Optional
from openai import OpenAI

# Create FastAPI app
app = FastAPI(
    title="AI Resume Customizer API",
    description="Backend API for AI-powered resume customization",
    version="2.0.0"
)

# Enable CORS for frontend connection
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, specify your frontend URL
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize OpenAI client
# For now, we'll set the API key directly in code (you'll move this to environment variable later)
openai_client = OpenAI(
    api_key="YOUR_ACTUAL_API_KEY_HERE"  # Replace with your real key  # Secure way  # Replace with your actual API key
)
# Load spaCy model
try:
    nlp = spacy.load("en_core_web_sm")
except OSError:
    print("spaCy model not found. Please run: python -m spacy download en_core_web_sm")
    nlp = None

# Root endpoint
@app.get("/")
async def root():
    return {"message": "AI Resume Customizer API v2.0 with GPT integration! 🚀🤖"}

# Health check endpoint
@app.get("/health")
async def health_check():
    return {"status": "healthy", "message": "API with GPT integration is working perfectly!"}

# Resume upload and parsing endpoint
@app.post("/api/upload-resume")
async def upload_resume(file: UploadFile = File(...)):
    """
    Upload and parse resume file (PDF, DOC, DOCX)
    """
    try:
        # Check file type
        allowed_types = [
            "application/pdf",
            "application/msword", 
            "application/vnd.openxmlformats-officedocument.wordprocessingml.document"
        ]
        
        if file.content_type not in allowed_types:
            raise HTTPException(
                status_code=400, 
                detail="Invalid file type. Please upload PDF, DOC, or DOCX files only."
            )
        
        # Read file content
        file_content = await file.read()
        extracted_text = ""
        
        # Process based on file type
        if file.content_type == "application/pdf":
            # Process PDF
            pdf_document = PyMuPDF.open(stream=file_content, filetype="pdf")
            for page_num in range(pdf_document.page_count):
                page = pdf_document[page_num]
                extracted_text += page.get_text()
            pdf_document.close()
            
        elif file.content_type in ["application/msword", "application/vnd.openxmlformats-officedocument.wordprocessingml.document"]:
            # Process Word document
            doc = docx.Document(io.BytesIO(file_content))
            for paragraph in doc.paragraphs:
                extracted_text += paragraph.text + "\n"
        
        # Return success response with extracted text
        return JSONResponse(
            status_code=200,
            content={
                "success": True,
                "message": "Resume uploaded and processed successfully!",
                "filename": file.filename,
                "file_size": len(file_content),
                "extracted_text": extracted_text,
                "full_text_length": len(extracted_text),
                "metadata": {
                    "content_type": file.content_type,
                    "original_filename": file.filename
                }
            }
        )
        
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error processing file: {str(e)}"
        )

# Job description analysis endpoint (enhanced)
@app.post("/api/analyze-job")
async def analyze_job_description(job_description: str = Form(...)):
    """
    Enhanced AI-powered job description analysis with advanced NLP
    """
    try:
        # Enhanced analysis using GPT with better prompting
        enhanced_analysis_prompt = f"""
        As an expert HR analyst and recruitment specialist, perform a comprehensive analysis of this job description:

        Job Description:
        {job_description}

        Provide a detailed JSON analysis with these exact keys:
        {{
            "company_analysis": {{
                "company_size": "startup/small/medium/large/enterprise",
                "industry": "specific industry name",
                "company_culture": ["collaborative", "fast-paced", "innovative", etc.],
                "remote_policy": "remote/hybrid/onsite/flexible"
            }},
            "role_analysis": {{
                "seniority_level": "entry/junior/mid/senior/principal/executive",
                "role_type": "individual_contributor/team_lead/manager/director",
                "department": "engineering/data/product/marketing/etc"
            }},
            "skills_breakdown": {{
                "required_technical_skills": ["Python", "SQL", etc.],
                "required_soft_skills": ["communication", "leadership", etc.],
                "preferred_technical_skills": ["AWS", "Docker", etc.],
                "preferred_soft_skills": ["mentoring", "public speaking", etc.],
                "nice_to_have": ["specific certifications", etc.]
            }},
            "experience_requirements": {{
                "years_required": "X-Y years or entry level",
                "education_required": "Bachelor's/Master's/PhD/bootcamp/none",
                "specific_experience": ["startups", "enterprise", "specific industries"]
            }},
            "compensation_indicators": {{
                "salary_range": "if mentioned or 'not specified'",
                "equity_mentioned": true/false,
                "benefits_highlighted": ["health", "401k", "pto", etc.]
            }},
            "application_insights": {{
                "urgency_level": "low/medium/high",
                "competition_level": "low/medium/high based on requirements",
                "key_differentiators": ["what makes candidates stand out"],
                "red_flags": ["any concerning aspects"]
            }},
            "optimization_keywords": {{
                "primary_keywords": ["most important 5-7 keywords"],
                "secondary_keywords": ["supporting keywords"],
                "ats_critical_terms": ["exact phrases that matter for ATS"]
            }}
        }}
        """

        # Call GPT for enhanced analysis
        gpt_response = openai_client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system", "content": "You are an expert HR analyst with 15+ years of experience in recruitment, ATS systems, and job market analysis. Provide detailed, actionable insights."},
                {"role": "user", "content": enhanced_analysis_prompt}
            ],
            max_tokens=1200,
            temperature=0.2
        )

        gpt_analysis_raw = gpt_response.choices[0].message.content
        
        # Try to parse JSON from GPT response
        try:
            # Extract JSON from GPT response (sometimes it includes extra text)
            json_match = re.search(r'\{.*\}', gpt_analysis_raw, re.DOTALL)
            if json_match:
                gpt_analysis = json.loads(json_match.group())
            else:
                gpt_analysis = {"error": "Could not parse GPT response", "raw": gpt_analysis_raw}
        except json.JSONDecodeError:
            gpt_analysis = {"error": "Invalid JSON from GPT", "raw": gpt_analysis_raw}

        # Enhanced NLP analysis using spaCy
        nlp_insights = {}
        if nlp:
            doc = nlp(job_description)
            
            # Extract entities
            entities = {
                "organizations": [ent.text for ent in doc.ents if ent.label_ == "ORG"],
                "technologies": [],
                "locations": [ent.text for ent in doc.ents if ent.label_ in ["GPE", "LOC"]],
                "money": [ent.text for ent in doc.ents if ent.label_ == "MONEY"]
            }
            
            # Technical skills detection
            tech_keywords = [
                "Python", "JavaScript", "Java", "C++", "React", "Angular", "Vue",
                "SQL", "MongoDB", "PostgreSQL", "MySQL", "Redis",
                "AWS", "Azure", "GCP", "Docker", "Kubernetes", "Jenkins",
                "Git", "GitHub", "GitLab", "Jira", "Confluence",
                "TensorFlow", "PyTorch", "Pandas", "NumPy", "Scikit-learn",
                "FastAPI", "Django", "Flask", "Spring Boot", "Node.js",
                "REST", "GraphQL", "Microservices", "API", "ETL",
                "Tableau", "Power BI", "Looker", "Excel", "R",
                "Agile", "Scrum", "DevOps", "CI/CD", "Testing"
            ]
            
            found_tech_skills = []
            job_text_lower = job_description.lower()
            for skill in tech_keywords:
                if skill.lower() in job_text_lower:
                    found_tech_skills.append(skill)
            
            entities["technologies"] = found_tech_skills
            nlp_insights["entities"] = entities
            
            # Sentiment analysis
            blob = TextBlob(job_description)
            nlp_insights["sentiment"] = {
                "polarity": blob.sentiment.polarity,  # -1 to 1
                "subjectivity": blob.sentiment.subjectivity,  # 0 to 1
                "tone": "positive" if blob.sentiment.polarity > 0.1 else "negative" if blob.sentiment.polarity < -0.1 else "neutral"
            }
            
            # Readability and complexity
            sentences = len(list(doc.sents))
            words = len([token for token in doc if not token.is_punct and not token.is_space])
            avg_sentence_length = words / sentences if sentences > 0 else 0
            
            nlp_insights["readability"] = {
                "sentence_count": sentences,
                "word_count": words,
                "avg_sentence_length": round(avg_sentence_length, 1),
                "complexity": "high" if avg_sentence_length > 20 else "medium" if avg_sentence_length > 15 else "low"
            }

        # Basic analysis (fallback/enhancement)
        word_count = len(job_description.split())
        char_count = len(job_description)
        
        # Urgency indicators
        urgency_keywords = ["urgent", "asap", "immediately", "start immediately", "urgent need"]
        urgency_score = sum(1 for keyword in urgency_keywords if keyword.lower() in job_description.lower())
        
        # Experience level detection
        if any(phrase in job_description.lower() for phrase in ["entry level", "junior", "0-1 year", "new grad"]):
            detected_level = "Entry Level"
        elif any(phrase in job_description.lower() for phrase in ["senior", "5+ years", "lead", "principal"]):
            detected_level = "Senior Level"
        else:
            detected_level = "Mid Level"

        return JSONResponse(
            status_code=200,
            content={
                "success": True,
                "message": "Enhanced job description analysis complete!",
                "enhanced_analysis": {
                    "basic_metrics": {
                        "word_count": word_count,
                        "character_count": char_count,
                        "estimated_read_time": f"{max(1, word_count // 200)} min",
                        "urgency_score": urgency_score,
                        "detected_experience_level": detected_level
                    },
                    "gpt_insights": gpt_analysis,
                    "nlp_analysis": nlp_insights,
                    "ats_optimization": {
                        "keyword_density": len(nlp_insights.get("entities", {}).get("technologies", [])),
                        "readability_score": nlp_insights.get("readability", {}).get("complexity", "unknown"),
                        "sentiment_score": nlp_insights.get("sentiment", {}).get("tone", "neutral")
                    }
                },
                "job_description_preview": job_description[:300] + "..." if len(job_description) > 300 else job_description
            }
        )
        
    except Exception as e:
        print(f"Enhanced Analysis error: {str(e)}")
        # Fallback to basic analysis
        word_count = len(job_description.split())
        basic_skills = ["Python", "JavaScript", "SQL", "React", "AWS"]
        found_skills = [skill for skill in basic_skills if skill.lower() in job_description.lower()]
        
        return JSONResponse(
            status_code=200,
            content={
                "success": True,
                "message": "Basic job description analysis (enhanced mode failed)",
                "enhanced_analysis": {
                    "basic_metrics": {
                        "word_count": word_count,
                        "character_count": len(job_description),
                        "found_skills": found_skills,
                        "detected_experience_level": "Mid Level"
                    },
                    "error": str(e)
                },
                "job_description_preview": job_description[:200] + "..." if len(job_description) > 200 else job_description
            }
        )

# NEW: Skills Gap Analysis Endpoint
@app.post("/api/skills-gap-analysis")
async def skills_gap_analysis(
    resume_text: str = Form(...),
    job_description: str = Form(...)
):
    """
    Analyze skills gap between resume and job requirements
    """
    try:
        gap_analysis_prompt = f"""
        As an expert career coach, analyze the gap between this resume and job requirements:

        RESUME:
        {resume_text[:2000]}  # Limit length for API

        JOB REQUIREMENTS:
        {job_description}

        Provide a JSON analysis:
        {{
            "skills_match": {{
                "matching_skills": ["skills present in both"],
                "missing_critical_skills": ["required skills not in resume"],
                "missing_preferred_skills": ["nice-to-have skills not in resume"],
                "additional_skills": ["skills in resume not mentioned in job"]
            }},
            "experience_gap": {{
                "experience_match": "excellent/good/partial/poor",
                "missing_experience": ["specific experience gaps"],
                "transferable_experience": ["relevant experience from different contexts"]
            }},
            "recommendations": {{
                "high_priority": ["most important improvements"],
                "medium_priority": ["helpful improvements"],
                "low_priority": ["nice-to-have improvements"]
            }},
            "match_score": {{
                "overall_match": "percentage like 75%",
                "skills_match": "percentage",
                "experience_match": "percentage"
            }}
        }}
        """

        gpt_response = openai_client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system", "content": "You are an expert career coach specializing in skills gap analysis and career development."},
                {"role": "user", "content": gap_analysis_prompt}
            ],
            max_tokens=800,
            temperature=0.3
        )

        gap_analysis_raw = gpt_response.choices[0].message.content
        
        try:
            json_match = re.search(r'\{.*\}', gap_analysis_raw, re.DOTALL)
            if json_match:
                gap_analysis = json.loads(json_match.group())
            else:
                gap_analysis = {"error": "Could not parse response", "raw": gap_analysis_raw}
        except json.JSONDecodeError:
            gap_analysis = {"error": "Invalid JSON", "raw": gap_analysis_raw}

        return JSONResponse(
            status_code=200,
            content={
                "success": True,
                "message": "Skills gap analysis complete!",
                "gap_analysis": gap_analysis,
                "analysis_timestamp": "2025-08-07"
            }
        )

    except Exception as e:
        return JSONResponse(
            status_code=500,
            content={
                "success": False,
                "error": str(e),
                "message": "Skills gap analysis failed"
            }
        )
# NEW: AI Resume Customization Endpoint
@app.post("/api/customize-resume")
async def customize_resume(
    resume_text: str = Form(...),
    job_description: str = Form(...),
    customization_level: str = Form(default="moderate")
):
    """
    Use GPT to customize resume based on job description
    """
    try:
        # Create customization prompt
        customization_prompt = f"""
        You are an expert resume writer and career coach. Customize this resume for the specific job description provided.

        ORIGINAL RESUME:
        {resume_text}

        TARGET JOB DESCRIPTION:
        {job_description}

        CUSTOMIZATION LEVEL: {customization_level}

        Please provide customized resume content with:
        1. Tailored professional summary
        2. Optimized experience bullet points (focus on relevant achievements)
        3. Prioritized skills section
        4. Keyword optimization for ATS systems
        5. Quantified achievements where possible

        Keep the same structure but optimize content for this specific role.
        Maintain truthfulness - only enhance and reframe existing content.

        Format your response as JSON with these keys:
        - customized_summary
        - optimized_experience
        - prioritized_skills
        - keyword_improvements
        - ats_score_improvement
        - customization_notes
        """

        # Call GPT for customization
        gpt_response = openai_client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system", "content": "You are an expert resume writer with 10+ years of experience helping people land their dream jobs."},
                {"role": "user", "content": customization_prompt}
            ],
            max_tokens=1500,
            temperature=0.4
        )

        customized_content = gpt_response.choices[0].message.content

        return JSONResponse(
            status_code=200,
            content={
                "success": True,
                "message": "Resume customized with AI!",
                "original_length": len(resume_text),
                "customization_level": customization_level,
                "customized_content": customized_content,
                "processing_time": "~3-5 seconds",
                "ai_confidence": "high"
            }
        )

    except Exception as e:
        print(f"GPT Customization error: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"Error customizing resume: {str(e)}"
        )

# Test endpoint for GPT connection
@app.post("/api/test-gpt")
async def test_gpt():
    """Test GPT integration"""
    try:
        test_response = openai_client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "user", "content": "Say 'GPT integration successful!' if you can read this."}
            ],
            max_tokens=50
        )
        
        return {
            "success": True,
            "message": "GPT integration working!",
            "gpt_response": test_response.choices[0].message.content,
            "model": "gpt-3.5-turbo"
        }
    except Exception as e:
        return {
            "success": False,
            "error": str(e),
            "message": "GPT integration failed"
        }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)

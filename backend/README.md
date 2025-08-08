from fastapi import FastAPI, File, UploadFile, Form, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
import pymupdf as PyMuPDF  # for PDF processing
import docx    # for Word document processing
import io
import os
import os
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
    api_key="os.getenv("OPENAI_API_KEY", "your-api-key-here")"  # Secure way  # Replace with your actual API key
)

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
    Analyze job description and extract key requirements using GPT
    """
    try:
        # Enhanced analysis using GPT
        analysis_prompt = f"""
        Analyze this job description and extract key information:

        Job Description:
        {job_description}

        Please provide:
        1. Required skills (technical and soft skills)
        2. Experience level (entry, mid, senior)
        3. Key responsibilities
        4. Important keywords for resume optimization
        5. Company culture indicators

        Format your response as JSON with these exact keys:
        - required_skills
        - experience_level  
        - key_responsibilities
        - optimization_keywords
        - culture_indicators
        """

        # Call GPT for analysis
        gpt_response = openai_client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system", "content": "You are an expert HR analyst and resume optimization specialist."},
                {"role": "user", "content": analysis_prompt}
            ],
            max_tokens=800,
            temperature=0.3
        )

        gpt_analysis = gpt_response.choices[0].message.content

        # Simple keyword extraction (backup)
        word_count = len(job_description.split())
        common_skills = ["Python", "JavaScript", "React", "SQL", "AWS", "Docker", "Git", "Java", "C++", "Machine Learning", "Data Analysis"]
        found_skills = [skill for skill in common_skills if skill.lower() in job_description.lower()]
        
        return JSONResponse(
            status_code=200,
            content={
                "success": True,
                "message": "Job description analyzed with GPT!",
                "analysis": {
                    "word_count": word_count,
                    "character_count": len(job_description),
                    "gpt_analysis": gpt_analysis,
                    "found_skills": found_skills,
                    "estimated_experience_level": "Senior" if word_count > 200 else "Mid-level" if word_count > 100 else "Entry-level"
                },
                "job_description_preview": job_description[:200] + "..." if len(job_description) > 200 else job_description
            }
        )
        
    except Exception as e:
        print(f"GPT Analysis error: {str(e)}")
        # Fallback to basic analysis if GPT fails
        word_count = len(job_description.split())
        common_skills = ["Python", "JavaScript", "React", "SQL", "AWS", "Docker", "Git"]
        found_skills = [skill for skill in common_skills if skill.lower() in job_description.lower()]
        
        return JSONResponse(
            status_code=200,
            content={
                "success": True,
                "message": "Job description analyzed (basic mode - GPT unavailable)",
                "analysis": {
                    "word_count": word_count,
                    "character_count": len(job_description),
                    "gpt_analysis": "GPT analysis temporarily unavailable",
                    "found_skills": found_skills,
                    "estimated_experience_level": "Mid-level" if word_count > 100 else "Entry-level"
                },
                "job_description_preview": job_description[:200] + "..." if len(job_description) > 200 else job_description
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

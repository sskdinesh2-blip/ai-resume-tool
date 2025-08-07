 
from fastapi import FastAPI, File, UploadFile, Form, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
import pymupdf as PyMuPDF  # for PDF processing
import docx    # for Word document processing
import io
from typing import Optional

# Create FastAPI app
app = FastAPI(
    title="AI Resume Customizer API",
    description="Backend API for AI-powered resume customization",
    version="1.0.0"
)

# Enable CORS for frontend connection
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, specify your frontend URL
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Root endpoint
@app.get("/")
async def root():
    return {"message": "AI Resume Customizer API is running! 🚀"}

# Health check endpoint
@app.get("/health")
async def health_check():
    return {"status": "healthy", "message": "API is working perfectly!"}

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
                "extracted_text": extracted_text[:500] + "..." if len(extracted_text) > 500 else extracted_text,
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

# Job description analysis endpoint (dummy for now)
@app.post("/api/analyze-job")
async def analyze_job_description(job_description: str = Form(...)):
    """
    Analyze job description and extract key requirements
    """
    try:
        # For now, return dummy data - we'll add real NLP processing later
        word_count = len(job_description.split())
        
        # Simple keyword extraction (dummy implementation)
        common_skills = ["Python", "JavaScript", "React", "SQL", "AWS", "Docker", "Git"]
        found_skills = [skill for skill in common_skills if skill.lower() in job_description.lower()]
        
        return JSONResponse(
            status_code=200,
            content={
                "success": True,
                "message": "Job description analyzed successfully!",
                "analysis": {
                    "word_count": word_count,
                    "character_count": len(job_description),
                    "found_skills": found_skills,
                    "estimated_experience_level": "Mid-level" if word_count > 100 else "Entry-level",
                    "key_requirements": ["This is a dummy analysis", "Real NLP coming in Day 4!"]
                },
                "job_description_preview": job_description[:200] + "..." if len(job_description) > 200 else job_description
            }
        )
        
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error analyzing job description: {str(e)}"
        )

# Test endpoint for frontend connection
@app.post("/api/test-connection")
async def test_connection():
    return {
        "success": True,
        "message": "Frontend successfully connected to backend! 🎉",
        "timestamp": "2025-08-06",
        "status": "API is working perfectly!"
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
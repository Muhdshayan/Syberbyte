from fastapi import FastAPI, UploadFile, File, HTTPException,Query,Body
from fastapi.responses import JSONResponse
import os
import shutil
from typing import List
from datetime import datetime
import json


app = FastAPI(title="Resume Upload API")
RESUME_DIR = "./resumes"
FEEDBACK_DIR = "./feedback"
JD_DIR = "./jd"

@app.post("/feedback", summary="Upload feedback JSON")
async def upload_feedback(feedback_text: str = Body(..., embed=False)):
    """
    Append a single string feedback (sent as raw JSON string) to ./feedback/general_feedback.json.
    Expected format:
        "This is a feedback line"
    """
    try:
        os.makedirs(FEEDBACK_DIR, exist_ok=True)
        feedback_file = os.path.join(FEEDBACK_DIR, "general_feedback.json")

        # Load existing feedback
        if os.path.exists(feedback_file):
            with open(feedback_file, "r", encoding="utf-8") as f:
                existing_data = json.load(f)
        else:
            existing_data = {"feedback": []}

        # Append new feedback string
        existing_data["feedback"].append(feedback_text)

        # Save updated feedback
        with open(feedback_file, "w", encoding="utf-8") as f:
            json.dump(existing_data, f, indent=4, ensure_ascii=False)

        return {"status": "success", "message": "Feedback appended."}

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))



@app.on_event("startup")
async def startup_event():
    """Create the resumes directory if it doesn't exist"""
    os.makedirs(RESUME_DIR, exist_ok=True)
@app.post("/job", summary="Upload job description JSON")
async def upload_job_description(
    job_data: List[dict] = Body(..., example=[]),
    jobId: str = Query(..., description="Unique job ID to name the JD file")
):
    """
    Upload a structured job description and save it under ./jd/{jobId}.json.
    """
    try:
        file_path = os.path.join(JD_DIR, f"{jobId}.json")

        with open(file_path, "w", encoding="utf-8") as f:
            json.dump(job_data, f, indent=4, ensure_ascii=False)

        return {"status": "success", "message": f"Job description saved to {file_path}"}
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/upload", summary="Upload PDF or DOCX resume files")
async def upload_resumes(files: List[UploadFile] = File(...)):
    """
    Upload multiple .pdf or .docx files to the ./resumes directory.
    Returns a JSON response with the list of saved files and any errors.
    """
    saved_files = []
    errors = []

    for file in files:
        # Validate file extension
        if not file.filename.lower().endswith(('.pdf', '.docx')):
            errors.append(f"Invalid file type for {file.filename}. Only .pdf and .docx are allowed.")
            continue

        try:
            # Generate a unique filename to avoid overwriting
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S_%f")
            base_name, ext = os.path.splitext(file.filename)
            unique_filename = f"{base_name}_{timestamp}{ext}"
            file_path = os.path.join(RESUME_DIR, unique_filename)

            # Save the file
            with open(file_path, "wb") as buffer:
                shutil.copyfileobj(file.file, buffer)
            
            saved_files.append(unique_filename)
        except Exception as e:
            errors.append(f"Error saving {file.filename}: {str(e)}")
        finally:
            await file.close()

    response = {
        "status": "success" if saved_files else "partial_success" if errors else "failed",
        "saved_files": saved_files,
        "errors": errors
    }

    if not saved_files and errors:
        raise HTTPException(status_code=400, detail=response)

    return JSONResponse(content=response, status_code=200)

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=5000)
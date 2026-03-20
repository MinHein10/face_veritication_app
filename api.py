import os
os.environ["PROTOCOL_BUFFERS_PYTHON_IMPLEMENTATION"] = "python"

import shutil
import uuid
<<<<<<< Updated upstream
from fastapi import FastAPI, File, UploadFile, HTTPException
=======
from contextlib import asynccontextmanager
from fastapi import FastAPI, File, UploadFile, HTTPException, Form
from deepface import DeepFace
>>>>>>> Stashed changes
from fastapi.middleware.cors import CORSMiddleware
from verifier import verify_faces, get_face_embedding
from database import db
from logger import logger
import config

app = FastAPI(
    title="Face Verification API",
    description="REST API for professional face verification using DeepFace (ArcFace/RetinaFace)",
    version="1.0.0"
)

# Enable CORS for Laravel/Frontend integration
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"], # In production, replace with specific Laravel URL
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# Ensure temp upload directory exists
UPLOAD_DIR = "temp_uploads"
if not os.path.exists(UPLOAD_DIR):
    os.makedirs(UPLOAD_DIR)

@app.get("/")
def read_root():
    """
    Health check endpoint.
    """
    return {
        "status": "online",
        "service": "Face Verification API",
        "model": config.MODEL_NAME,
        "detector": config.DETECTOR_BACKEND
    }

@app.post("/verify")
async def verify(file1: UploadFile = File(...), file2: UploadFile = File(...)):
    """
    Verifies if faces in two uploaded images belong to the same person.
    Integrates Quality Assessment and Visual Debugging coordinates.
    """
    # Create unique filenames to handle concurrent requests
    session_id = str(uuid.uuid4())
    img1_path = os.path.join(UPLOAD_DIR, f"{session_id}_1_{file1.filename}")
    img2_path = os.path.join(UPLOAD_DIR, f"{session_id}_2_{file2.filename}")

    try:
        # Save uploaded files to disk
        with open(img1_path, "wb") as buffer:
            shutil.copyfileobj(file1.file, buffer)
        with open(img2_path, "wb") as buffer:
            shutil.copyfileobj(file2.file, buffer)

        logger.info(f"API Request received. Session: {session_id}")
        
        # Run verification logic (includes Quality check)
        result = verify_faces(img1_path, img2_path)
        
        # Cleanup temporary files (optional, but recommended for production)
        # Note: If you need these for a shared storage approach, don't delete yet.
        # os.remove(img1_path)
        # os.remove(img2_path)

        return result

    except Exception as e:
        logger.error(f"API Error in session {session_id}: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/register")
async def register_face(user_id: str = Form(...), file: UploadFile = File(...)):
    """
    Registers a new user's face into the Vector Database.
    """
    session_id = str(uuid.uuid4())
    img_path = os.path.join(UPLOAD_DIR, f"reg_{session_id}_{file.filename}")

    try:
        with open(img_path, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)
            
        logger.info(f"Registration request for user: {user_id}")
        
        # Extract embedding
        extraction = get_face_embedding(img_path, is_source=True)
        
        if not extraction["success"]:
            raise HTTPException(status_code=400, detail=extraction["error"])
            
        # Add to vector DB
        success, msg = db.add_face(user_id, extraction["embedding"], metadata={"filename": file.filename})
        
        if not success:
            raise HTTPException(status_code=500, detail=msg)
            
        # Clean up
        if os.path.exists(img_path):
            os.remove(img_path)
            
        return {
            "status": "success",
            "message": msg,
            "user_id": user_id,
            "quality": extraction["quality"]
        }
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Registration Error: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/recognize")
async def recognize_face(file: UploadFile = File(...)):
    """
    Identifies a person from a live photo using the Vector Database.
    """
    session_id = str(uuid.uuid4())
    img_path = os.path.join(UPLOAD_DIR, f"rec_{session_id}_{file.filename}")

    try:
        with open(img_path, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)
            
        logger.info("Recognition request received.")
        
        # Extract embedding
        extraction = get_face_embedding(img_path, is_source=False)
        
        if not extraction["success"]:
            raise HTTPException(status_code=400, detail=extraction["error"])
            
        # Search the database
        result = db.search_face(extraction["embedding"])
        
        # Clean up
        if os.path.exists(img_path):
            os.remove(img_path)
            
        return result
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Recognition Error: {e}")
        raise HTTPException(status_code=500, detail=str(e))

if __name__ == "__main__":
    import uvicorn
    # Start the server on port 8000
    uvicorn.run(app, host="0.0.0.0", port=8000)

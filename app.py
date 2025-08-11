from fastapi import FastAPI, File, UploadFile
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
import os
import shutil

app = FastAPI()

# Allow CORS for Bubble.io and other clients
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # You can restrict to Bubble domain
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

UPLOAD_FOLDER = "uploads"
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

@app.get("/")
def index():
    return {"message": "Auto Rigging API is running."}

@app.post("/upload")
async def upload_file(file: UploadFile = File(...)):
    try:
        if not file.filename:
            return JSONResponse(content={"error": "No file selected"}, status_code=400)

        file_location = os.path.join(UPLOAD_FOLDER, file.filename)
        
        with open(file_location, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)

        return {
            "message": f"{file.filename} uploaded successfully!",
            "path": file_location
        }

    except Exception as e:
        return JSONResponse(content={"error": str(e)}, status_code=500)

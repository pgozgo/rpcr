from fastapi import FastAPI, File, UploadFile
from fastapi.responses import FileResponse, JSONResponse
from fastapi.middleware.cors import CORSMiddleware
import os
import shutil
import requests

app = FastAPI()

# Allow Bubble.io & other origins
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Restrict to Bubble domain in production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

UPLOAD_FOLDER = "uploads"
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

# Change this to your local Maya machine listener URL
MAYA_WEBHOOK_URL = "https://5364782e0e2c.ngrok-free.app/process"

@app.get("/")
def root():
    return {"message": "FastAPI File Service is running."}

@app.post("/upload")
def upload_file(file: UploadFile = File(...)):
    file_path = os.path.join(UPLOAD_FOLDER, file.filename)
    with open(file_path, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)

    # Notify local Maya machine
    try:
        requests.post(MAYA_WEBHOOK_URL, json={"filename": file.filename})
    except Exception as e:
        return {"message": f"{file.filename} uploaded but webhook failed: {str(e)}"}

    return {"message": f"{file.filename} uploaded successfully and webhook sent."}

@app.get("/files")
def list_files():
    files = os.listdir(UPLOAD_FOLDER)
    return {"files": files}

@app.get("/download/{filename}")
def download_file(filename: str):
    file_path = os.path.join(UPLOAD_FOLDER, filename)
    if not os.path.exists(file_path):
        return JSONResponse({"error": "File not found"}, status_code=404)
    return FileResponse(file_path, filename=filename)

@app.delete("/delete/{filename}")
def delete_file(filename: str):
    file_path = os.path.join(UPLOAD_FOLDER, filename)
    if not os.path.exists(file_path):
        return JSONResponse({"error": "File not found"}, status_code=404)
    os.remove(file_path)
    return {"message": f"{filename} deleted successfully"}

if __name__ == "__main__":
    import uvicorn
    port = int(os.environ.get("PORT", 5000))
    uvicorn.run("app:app", host="0.0.0.0", port=port)
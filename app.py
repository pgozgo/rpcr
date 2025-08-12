from fastapi import FastAPI, File, UploadFile
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse, JSONResponse
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
def root():
    return {"message": "Hello from FastAPI"}

def index():
    return {"message": "Auto Rigging API is running."}

@app.post("/upload")
async def upload_file(file: UploadFile = File(...)): # async def functions can use the await keyword to pause execution until an asynchronous operation completes, allowing other code to run in the meantime.
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
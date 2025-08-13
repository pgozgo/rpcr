# To check the uploaded files in Railway, you can add an endpoint that lists all files in the `UPLOAD_FOLDER`. Here's an updated version of your FastAPI code with that feature added:

from fastapi import FastAPI, UploadFile, File, HTTPException
from fastapi.responses import FileResponse, JSONResponse
from fastapi.middleware.cors import CORSMiddleware
import os
import subprocess
import shutil

# === CONFIG ===
UPLOAD_FOLDER = "uploads"
MAYA_BATCH_PATH = r"C:\Program Files\Autodesk\Maya2014\bin\mayabatch.exe"  # Change if different
MAYA_SCRIPT_PATH = r"D:\rpcr\lib\test_print.py"  # Change to your script
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

app = FastAPI()

# Allow CORS for Bubble.io
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
def root():
    return {"message": "FastAPI Maya API running."}

@app.post("/upload")
async def upload_file(file: UploadFile = File(...)):
    file_path = os.path.join(UPLOAD_FOLDER, file.filename)
    with open(file_path, "wb") as f:
        shutil.copyfileobj(file.file, f)
    run_maya_batch(file_path)
    return {"message": f"{file.filename} uploaded and processed with Maya."}

@app.get("/files")
async def list_files():
    try:
        files = os.listdir(UPLOAD_FOLDER)
        return JSONResponse(content={"files": files})
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/download/{filename}")
async def download_file(filename: str):
    file_path = os.path.join(UPLOAD_FOLDER, filename)
    if not os.path.exists(file_path):
        raise HTTPException(status_code=404, detail="File not found")
    return FileResponse(file_path, filename=filename)

@app.delete("/delete/{filename}")
async def delete_file(filename: str):
    file_path = os.path.join(UPLOAD_FOLDER, filename)
    if os.path.exists(file_path):
        os.remove(file_path)
        return {"message": f"{filename} deleted."}
    raise HTTPException(status_code=404, detail="File not found")

def run_maya_batch(file_path):
    if not os.path.exists(MAYA_BATCH_PATH):
        print("[ERROR] Maya batch executable not found.")
        return

    cmd = [
        MAYA_BATCH_PATH,
        "-file", file_path,
        "-command", f'python("exec(open(\'{MAYA_SCRIPT_PATH}\').read())")'
    ]

    process = subprocess.Popen(
        cmd,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        universal_newlines=True
    )

    for line in process.stdout:
        print(line, end="")

    process.wait()
    print(f"[INFO] Maya finished processing {file_path}")



if __name__ == "__main__":
    import uvicorn
    port = int(os.environ.get("PORT", 5000))
    uvicorn.run("app:app", host="0.0.0.0", port=port)
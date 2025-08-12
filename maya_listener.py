from fastapi import FastAPI, Request
import requests
import subprocess
import os

app = FastAPI()

# Railway API URL
RAILWAY_API_BASE = "https://web-production-b32a.up.railway.app"

@app.post("/process")
async def process_file(request: Request):
    data = await request.json()
    filename = data.get("filename")
    if not filename:
        return {"error": "No filename provided"}

    # Step 1: Download file from Railway
    download_url = f"{RAILWAY_API_BASE}/download/{filename}"
    local_path = os.path.join(os.getcwd(), filename)

    print(f"Downloading {filename} from Railway...")
    resp = requests.get(download_url)
    if resp.status_code == 200:
        with open(local_path, "wb") as f:
            f.write(resp.content)
        print(f"File saved locally: {local_path}")
    else:
        return {"error": f"Download failed: {resp.status_code}"}

    # Step 2: Run Maya batch
    print(f"Running Maya batch on {local_path}...")
    maya_cmd = [
        "mayabatch",  # Replace with full path to Maya if not in PATH
        "-file", local_path,
        "-command", "print('Processed in Maya')"
    ]
    result = subprocess.run(maya_cmd, capture_output=True, text=True)

    print("STDOUT:", result.stdout)
    print("STDERR:", result.stderr)

    return {"message": f"{filename} processed successfully"}

import requests
import subprocess
import os

# --- Config ---
RAILWAY_API_BASE = "https://web-production-b32a.up.railway.app/upload"  # Replace with your Railway URL
FILENAME = "test1.fbx"  # Replace with file name from /files endpoint
LOCAL_DOWNLOAD_PATH = os.path.join(os.getcwd(), FILENAME)

# --- Step 1: Download file from Railway ---
download_url = f"{RAILWAY_API_BASE}/download/{FILENAME}"
print(f"Downloading {FILENAME} from Railway...")

response = requests.get(download_url)
if response.status_code == 200:
    with open(LOCAL_DOWNLOAD_PATH, "wb") as f:
        f.write(response.content)
    print(f"File saved locally: {LOCAL_DOWNLOAD_PATH}")
else:
    print(f"Error downloading file: {response.status_code} - {response.text}")
    exit(1)

# --- Step 2: Run Maya batch command ---
print(f"Running Maya batch on {LOCAL_DOWNLOAD_PATH}...")
maya_cmd = [
    "mayabatch",  # Maya batch executable (must be in PATH or full path here)
    "-file", LOCAL_DOWNLOAD_PATH,
    "-command", "print('Hello from Maya Batch')"
]

result = subprocess.run(maya_cmd, capture_output=True, text=True)

print("STDOUT:", result.stdout)
print("STDERR:", result.stderr)

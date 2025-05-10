from fastapi import Request, FastAPI, File, UploadFile
from fastapi.responses import PlainTextResponse, JSONResponse
import google.generativeai as genai
import json
import os
from fastapi.middleware.cors import CORSMiddleware
import firebase_admin
from firebase_admin import credentials, firestore
from dotenv import load_dotenv
from typing import Optional
from PIL import Image
import io

#----------------------------------------------------------------------------------------
genai.configure(api_key=os.environ["GOOGLE_API_KEY"])
model = genai.GenerativeModel('gemini-2.0-flash')
load_dotenv()
cred_path = os.getenv("FIREBASE_CREDENTIALS_PATH")
cred = credentials.Certificate(cred_path)
firebase_admin.initialize_app(cred)
db = firestore.client()
app = FastAPI()
stored_image: Optional[bytes] = None # This will hold the image content in memory
#----------------------------------------------------------------------------------------

# Allow all origins (good for testing, not for production!)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Or use your actual frontend URL
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
def read_root():
    return {"message": "Hello from your FastAPI server!"}

@app.post("/test_post/")
def receive_message(sender: str, content: str):
    return {
        "status": "Received",
        "from": "sender",
        "content": "content",
        "Version": 1
    }

@app.post("/set_schedule/") #User Orginal Scedule 
async def add_schedule(request: Request):
    body = await request.json()
    name = body.get("name")
    schedule = body.get("schedule")
    return {"status": "Schedule saved", "user": name, "schedule": schedule}

@app.post("/save", response_class=PlainTextResponse)
async def save_user(request: Request):
    # Expecting plain text body like: "Study at 10:00am"
    schedule_text = (await request.body()).decode("utf-8")

    # Save to Firestore under a static user (or customize this)
    db.collection("Guardian").document("USERS").set({
        "name": "Christopher",
        "schedule": schedule_text
    })

    return f"Schedule saved: {schedule_text}"

@app.post("/read", response_class=PlainTextResponse)
async def read_user(request: Request):
    # Step 1: Get plain text name
    name = (await request.body()).decode("utf-8")

    # Step 2: Look up that document in Firestore
    doc_ref = db.collection("Guardian").document("USERS")
    doc = doc_ref.get()

    # Step 3: If found, return just the schedule as plain text
    if doc.exists:
        data = doc.to_dict()
        return data.get("schedule", "No schedule found in doc.")
    else:
        return f"Schedule not found for {name}"

@app.post("/upload-image")
async def upload_image(file: UploadFile = File(...)):
    global stored_image

    if not file.content_type.startswith("image/"):
        return JSONResponse(status_code=400, content={"error": "Invalid file type"})

    # Read image content into memory (bytes)
    stored_image = await file.read()

    # Optionally log metadata
    print(f"Received image: {file.filename} ({file.content_type}), size: {len(stored_image)} bytes")

    return {"status": "success", "filename": file.filename, "size_bytes": len(stored_image)}

def read_schedule():
    global stored_image

    if stored_image is None:
        return {"error": "No image uploaded yet."}

    try:
        # Convert bytes to PIL Image
        image = Image.open(io.BytesIO(stored_image))

        prompt = """
        Analyze this image and extract the user's weekly schedule, ignoring dates as everything is recurring weekly. 
        Format it as a Json where each day is an object with a list of activities that include start and end times.
        """


        # Send image + prompt
        response = model.generate_content([prompt, image])

        # DEBUG: show the raw text for dev logging
        print("Gemini response:\n", response.text)

        if not response.text.strip():
            return {"error": "Gemini returned an empty response."}

        # Return raw text instead of parsing
        return {"response": response.text}

    except Exception as e:
        print("Failed to process schedule:", e)
        return {"error": "Schedule reading failed"}

@app.get("/view")
def view_schedule():
    result = read_schedule()
    return result

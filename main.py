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

#----------------------------------------------------------------------------------------

@app.get("/") #Just great return 
def read_root():
    return {"message": "Hello from your FastAPI server!"}

#----------------------------------------------------------------------------------------

@app.get("/test_post/")#Test endpoint
def receive_message():
    return {"status": "Received"}

#----------------------------------------------------------------------------------------

@app.post("/save", response_class=PlainTextResponse)
async def save_user(request: Request):
    schedule_text = (await request.body()).decode("utf-8")
    db.collection("Guardian").document("USERS").set({"name": "Christopher","schedule": schedule_text})
    return f"Schedule saved: {schedule_text}"

#----------------------------------------------------------------------------------------

@app.post("/read", response_class=PlainTextResponse)
async def read_user(request: Request):
    # Step 1: Get plain text name (not used here but retained in case you want to use dynamic users later)
    name = (await request.body()).decode("utf-8")

    # Step 2: Reference the School document under Activities subcollection
    doc_ref = db.collection("Users").document("Christopher").collection("Activities").document("School")
    doc = doc_ref.get()

    # Step 3: Return the class times if they exist
    if doc.exists:
        data = doc.to_dict()
        return data.get("Class Times", "No class times found.")
    else:
        return f"Schedule not found for {name}"

#----------------------------------------------------------------------------------------

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

#----------------------------------------------------------------------------------------

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

#----------------------------------------------------------------------------------------

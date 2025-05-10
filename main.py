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
        "from": sender,
        "content": content
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
        # Convert image bytes to a PIL Image
        image = Image.open(io.BytesIO(stored_image))

        # Use Gemini multimodal model (supports vision)
        model = genai.GenerativeModel("gemini-pro-vision")

        # Prompt the model to extract and return schedule
        prompt = """
        Analyze this image, which contains a weekly schedule.
        Extract the data and return it in this strict JSON format:
        Only return valid JSON — no explanation, no extra text.
        """

        # Send prompt and image to Gemini
        response = model.generate_content([prompt, image])

        # DEBUG: Show raw response
        print("Gemini response text:", repr(response.text))

        # Check if response is empty or non-JSON
        if not response.text or not response.text.strip():
            return {"error": "Gemini returned an empty response."}

        try:
            # Try parsing the response into JSON
            schedule_data = json.loads(response.text)
        except json.JSONDecodeError:
            return {"error": "Gemini response was not valid JSON."}

        # Save the valid schedule to a file
        with open("schedule.json", "w") as f:
            json.dump(schedule_data, f, indent=2)

        return schedule_data

    except Exception as e:
        print("Failed to read or process schedule:", e)
        return {"error": "Schedule reading failed"}

@app.get("/view")
def view_schedule():
    result = read_schedule()

    if "error" in result:
        return JSONResponse(status_code=400, content=result)

    return result

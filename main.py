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

from fastapi import Request
from fastapi.responses import PlainTextResponse

@app.post("/save", response_class=PlainTextResponse)
async def save_user(request: Request):
    schedule_text = (await request.body()).decode("utf-8")

    days = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]
    week_data = {}

    # Step 1: Gather existing schedule for all 7 days
    for day in days:
        day_ref = db.collection("Users").document("Christopher").collection("Schedule").document(day)
        doc = day_ref.get()
        if doc.exists:
            week_data[day] = doc.to_dict()
        else:
            week_data[day] = {}

    # Step 2: Send to model for processing
    prompt = f"""This is the database of user information: {week_data}

            New input: {schedule_text}

            Instructions:
            1. No extra comments (just return the updated schedule).
            2. No BOLD FONTS or excessive spacing.
            3. Just make the change ONLY.
            4. Format in plain text NOT JSON.
            """

    response = model.generate_content(prompt)

    # Step 3: Detect which day is being updated (simple keyword match)
    updated_day = next((day for day in days if day.lower() in schedule_text.lower()), None)
    if not updated_day:
        return "Could not identify which day to update. Please include a day name in the schedule."

    # Step 4: Save to Firestore under the correct day
    target_ref = db.collection("Users").document("Christopher").collection("Schedule").document(updated_day)
    target_ref.set({ "Class Times": response.text })

    return f"Schedule saved: {updated_day} updated successfully"


@app.post("/read", response_class=PlainTextResponse)
async def read_user(request: Request):
    name = (await request.body()).decode("utf-8")  # Expects Day

    doc_ref = db.collection("Users").document("Christopher").collection("Schedule").document(name)
    doc = doc_ref.get()

    if doc.exists:
        data = doc.to_dict()
        return data.get("Schedule", "No class times found.")
    else:
        return f"Schedule not found for {name}"

#----------------------------------------------------------------------------------------

@app.post("/upload-image")  # Receive file and convert & store to PIL image
async def upload_image(file: UploadFile = File(...)):
    global stored_image
    if not file.content_type.startswith("image/"): #If File doesnt exisit
        return JSONResponse(status_code=400, content={"error": "Invalid file type"})
    
    stored_image = await file.read()  # Read image content into memory (bytes)
    if stored_image is None: #if nothing was received 
        return {"error": "No image uploaded yet."}

    try:
        image = Image.open(io.BytesIO(stored_image))  # Convert bytes to PIL Image
        prompt = """
        Extract the user's weekly class schedule from this image.
        Rules:
        - Use 24-hour time format.
        - If day is empty, populate with "Free day :)".
        - No extra commentary - JUST SHOW RESULTS
        - No Bold fonts or markdown.
        """
        response = model.generate_content([prompt, image])  # Send image + prompt

        if not response.text.strip():
            return {"error": "Gemini returned an empty response."}
        
        rules = """Dont include the day of the week heading!!!"""
        
        monday_data = model.generate_content(f"return monday time and event only, {rules}, {response.text}") 
        tues_data = model.generate_content(f"return tuesday time and event only, {rules}, {response.text}")
        wed_data = model.generate_content(f"return wednesday time and event only, {rules}, {response.text}")
        thu_data = model.generate_content(f"return thursday time and event only, {rules}, {response.text}")
        fri_data = model.generate_content(f"return friday time and event only, {rules}, {response.text}")

        mon_ref = db.collection("Users").document("Christopher").collection("Schedule").document("Monday")
        tues_ref = db.collection("Users").document("Christopher").collection("Schedule").document("Tuesday")
        wed_ref = db.collection("Users").document("Christopher").collection("Schedule").document("Wednesday")
        thu_ref = db.collection("Users").document("Christopher").collection("Schedule").document("Thursday")
        fri_ref = db.collection("Users").document("Christopher").collection("Schedule").document("Friday")
        
        mon_ref.set({"Schedule": monday_data.text})
        tues_ref.set({"Schedule": tues_data.text})
        wed_ref.set({"Schedule": wed_data.text})
        thu_ref.set({"Schedule": thu_data.text})
        fri_ref.set({"Schedule": fri_data.text})

        print(f"Received image: {file.filename} ({file.content_type}), size: {len(stored_image)} bytes") # Optionally log metadata

        return {
            "status": "success",
            "filename": file.filename,
            "size_bytes": len(stored_image),
            "stored_to": "Users/Christopher/Schedule/Monday"
        }

    except Exception as e:
        print("Failed to process schedule:", e)
        return {"error": "Schedule reading failed"}

#----------------------------------------------------------------------------------------

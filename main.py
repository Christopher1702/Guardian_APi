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

#--------------------------------------------------------------------------------------------------------------------------------------------------------------------------------

 # Allow all origins (good for testing, not for production!)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Or use your actual frontend URL
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

#--------------------------------------------------------------------------------------------------------------------------------------------------------------------------------

@app.get("/") #Just great return 
def read_root():
    return {"message": "Hello from your FastAPI server!"}

#--------------------------------------------------------------------------------------------------------------------------------------------------------------------------------

@app.post("/save", response_class=PlainTextResponse)
async def save_user(request: Request):
    user_request = (await request.body()).decode("utf-8")

    days = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]
    week_data = {}

    # Step 1: Gather existing schedule from Firestore
    for day in days:
        doc_ref = db.collection("Users").document("Christopher").collection("Schedule").document(day)
        doc = doc_ref.get()
        if doc.exists:
            week_data[day] = doc.to_dict()
        else:
            week_data[day] = {}

    # Step 2: Ask Gemini to make the update
    prompt = f"""
This is the user's weekly schedule:

{week_data}

The user input is:
"{user_request}"

Instructions for you, Gemini:
- Interpret the user's request and update the schedule accordingly.
- DO NOT return the entire week.
- ONLY return the updated schedule text for the ONE DAY that changed.
- DO NOT include any extra commentary, markdown, formatting, or labels.
- Just return the plain text schedule for that day.
    """.strip()

    response = model.generate_content(prompt)

    # Step 3: Identify which day the user is referring to
    updated_day = next((day for day in days if day.lower() in user_request.lower()), None)

    if not updated_day:
        return "Error: Could not identify a day to update. Please include the day name in your request."

    # Step 4: Save ONLY that day's response to Firestore
    target_ref = db.collection("Users").document("Christopher").collection("Schedule").document(updated_day)
    target_ref.set({ "Schedule": response.text.strip() })

    return f"Schedule updated successfully: {updated_day}"

#--------------------------------------------------------------------------------------------------------------------------------------------------------------------------------

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

#--------------------------------------------------------------------------------------------------------------------------------------------------------------------------------

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

#--------------------------------------------------------------------------------------------------------------------------------------------------------------------------------

@app.post("/agenda", response_class=PlainTextResponse)
async def read_user(request: Request):
    name = (await request.body()).decode("utf-8").strip()  # E.g., "Monday", "Tuesday", etc.

    doc_ref = db.collection("Users").document("Christopher").collection("Schedule").document(name)
    doc = doc_ref.get()

    if doc.exists:
        data = doc.to_dict()
        return data.get("Schedule", "No class times found.")
    else:
        return f"Schedule not found for {name}"
    
#--------------------------------------------------------------------------------------------------------------------------------------------------------------------------------

@app.post("/meal_build", response_class=PlainTextResponse)
async def save_user(request: Request):
    user_request = (await request.body()).decode("utf-8")

    prompt = f"""
        {user_request}

        Instructions for you, Gemini:
        - N0 FORMATTING
        - ONLY return FULL reciepe.
        - I need to store this response so save text space.
        - DO NOT include any extra commentary, markdown, formatting, or labels.
        - Just return the plain text.
    """.strip()

    response = model.generate_content(prompt)
    target_ref = db.collection("Users").document("Christopher").collection("Schedule").document("Monday")
    target_ref.set({"Meal": response.text.strip()}, merge=True)

    prompt_name = f"""
                ONYL RETURN MEAL NAME: {response}.

                Instructions for you, Gemini:
                - ONLY SEND MEAL NAME, TO SAVE CHARACTER SPACE
                """

    meal_name = model.generate_content(prompt_name)
    name_ref = db.collection("Users").document("Christopher").collection("Schedule").document("Monday")
    name_ref.set({"Meal_Name": meal_name.text.strip()}, merge=True)


    return f"Meal updated successfully: OK"

#--------------------------------------------------------------------------------------------------------------------------------------------------------------------------------

@app.get("/fetch_recipe", response_class=PlainTextResponse)
async def fetch_recipe():
    doc_ref = db.collection("Users").document("Christopher").collection("Schedule").document("Monday")
    doc = doc_ref.get()

    if doc.exists:
        data = doc.to_dict()
        return data.get("Meal", "No meal recipe found.")
    else:
        return "No recipe document found for Monday."

#--------------------------------------------------------------------------------------------------------------------------------------------------------------------------------

@app.get("/meal_name", response_class=PlainTextResponse)
async def fetch_image():
    doc_ref = db.collection("Users").document("Christopher").collection("Schedule").document("Monday")
    doc = doc_ref.get()

    if doc.exists:
        data = doc.to_dict()
        return data.get("Meal_Name", "")
    else:
        return ""

#--------------------------------------------------------------------------------------------------------------------------------------------------------------------------------

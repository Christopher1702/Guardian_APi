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
import requests


genai.configure(api_key=os.environ["GOOGLE_API_KEY"])
model = genai.GenerativeModel('gemini-2.5-flash')
load_dotenv()
cred_path = os.getenv("FIREBASE_CREDENTIALS_PATH")
cred = credentials.Certificate(cred_path)
firebase_admin.initialize_app(cred)
db = firestore.client()
app = FastAPI()
stored_image: Optional[bytes] = None # This will hold the image content in memory


 # Allow all origins (good for testing, not for production!)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Or use your actual frontend URL
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/") #SERVER STATE TEST
def read_root():
    return {"message": "Hello from your FastAPI server!"}



#DISPLAYS USER SCHEDULE
@app.post("/read", response_class=PlainTextResponse)
async def read_user(request: Request):
    name = (await request.body()).decode("utf-8")  # Expects Day

    doc_ref = db.collection("Users").document("Christopher").collection("Class_Schedule").document(name)
    doc = doc_ref.get()

    if doc.exists:
        data = doc.to_dict()
        return data.get("Schedule", "No class times found.")
    else:
        return f"Schedule not found for {name}"



#UPLOAD USER CLASS SCHDULE
@app.post("/school_class_schedule")  # Receive file and convert & store to PIL image
async def upload_image(file: UploadFile = File(...)):
    global stored_image
    if not file.content_type.startswith("image/"):
        return JSONResponse(status_code=400, content={"error": "Invalid file type"})

    stored_image = await file.read()
    if stored_image is None:
        return {"error": "No image uploaded yet."}

    def extract_text(response):
        if not response.candidates:
            return None
        parts = response.candidates[0].content.parts
        if not parts:
            return None
        return parts[0].text if hasattr(parts[0], "text") else None

    try:
        image = Image.open(io.BytesIO(stored_image))

        rules = """        
        Rules:
        - Use 24-hour time format.
        - No extra commentary - JUST SHOW RESULTS
        - No Bold fonts or markdown.
        - Don't include the day of the week heading!!!
        - Format = HH:MM-HH:MM Event
        """

        prompt_mon = """I have provided a class schedule, exactred MONDAYS SCHEDULE ONLY"""
        prompt_tues = """I have provided a class schedule, exactred TUESDAYS SCHEDULE ONLY"""
        prompt_wed = """I have provided a class schedule, exactred WEDNESDAYS SCHEDULE ONLY"""
        prompt_thu = """I have provided a class schedule, exactred THURSDAYS SCHEDULE ONLY"""
        prompt_fri = """I have provided a class schedule, exactred FRIDAYS SCHEDULE ONLY"""

        monday_data = model.generate_content([prompt_mon, image, rules]) 
        tues_data = model.generate_content([prompt_tues, image, rules])
        wed_data = model.generate_content([prompt_wed, image, rules])
        thu_data = model.generate_content([prompt_thu, image, rules])
        fri_data = model.generate_content([prompt_fri, image, rules])

        monday_text = extract_text(monday_data)
        tues_text = extract_text(tues_data)
        wed_text = extract_text(wed_data)
        thu_text = extract_text(thu_data)
        fri_text = extract_text(fri_data)

        if not monday_text:
            return {"error": "Gemini returned an empty response for Monday."}

        mon_ref = db.collection("Users").document("Christopher").collection("Class_Schedule").document("Monday")
        tues_ref = db.collection("Users").document("Christopher").collection("Class_Schedule").document("Tuesday")
        wed_ref = db.collection("Users").document("Christopher").collection("Class_Schedule").document("Wednesday")
        thu_ref = db.collection("Users").document("Christopher").collection("Class_Schedule").document("Thursday")
        fri_ref = db.collection("Users").document("Christopher").collection("Class_Schedule").document("Friday")

        mon_ref.set({"Schedule": monday_text})
        tues_ref.set({"Schedule": tues_text or ""})
        wed_ref.set({"Schedule": wed_text or ""})
        thu_ref.set({"Schedule": thu_text or ""})
        fri_ref.set({"Schedule": fri_text or ""})

        print(f"Received image: {file.filename} ({file.content_type}), size: {len(stored_image)} bytes")

        return {
            "status": "success",
            "filename": file.filename,
            "size_bytes": len(stored_image),
            "stored_to": "Users/Christopher/Class_Schedule/Weekdays"
        }

    except Exception as e:
        print("Failed to process schedule:", e)
        return {"error": "Schedule reading failed"}


# Save individual agenda event
@app.post("/add_agenda_event", response_class=PlainTextResponse)
async def add_agenda_event(request: Request):
    try:
        data = await request.json()
        title = data.get("title")
        month = data.get("month")
        day = data.get("day")
        start_time = data.get("startTime")
        end_time = data.get("endTime")

        if not all([title, month, day, start_time, end_time]):
            return PlainTextResponse("Missing one or more required fields.", status_code=400)

        # Construct document ID using a readable format
        event_id = f"{month}_{day}_{start_time.replace(' ', '').replace(':', '')}"

        # Point to the correct Firestore path
        doc_ref = db.collection("Users") \
                    .document("Christopher") \
                    .collection("One_Time_Schedule") \
                    .document("One_Time_Event") \
                    .collection("Events") \
                    .document(event_id)

        # Save the event details
        doc_ref.set({
            "Title": title,
            "Month": month,
            "Day": day,
            "StartTime": start_time,
            "EndTime": end_time,
        })

        return f"One-time event saved for {month} {day}: {title} ({start_time} - {end_time})"

    except Exception as e:
        print("Error saving one-time event:", e)
        return PlainTextResponse("Failed to save one-time event.", status_code=500)



@app.post("/agenda", response_class=PlainTextResponse)
async def read_user(request: Request):
    name = (await request.body()).decode("utf-8").strip()  # E.g., "Monday", "Tuesday", etc.

    doc_ref = db.collection("Users").document("Christopher").collection("Class_Schedule").document(name)
    doc = doc_ref.get()

    if doc.exists:
        print(doc.id, doc.to_dict())
    else:
        print("No document found.")
    


@app.post("/meal_build", response_class=PlainTextResponse)
async def save_user(request: Request):
    user_request = (await request.body()).decode("utf-8")

    # Step 1: Generate the full recipe
    prompt = f"""
        {user_request}

        Instructions for you, Gemini:
        - Reccomend Common Meals
        - NO FORMATTING
        - ONLY return FULL recipe.
        - DO NOT include any extra commentary, markdown, formatting, or labels.
        - Just return the plain text.
    """.strip()

    response = model.generate_content(prompt)
    recipe_text = response.text.strip()

    # Step 2: Save full recipe to Firestore
    doc_ref = db.collection("Users").document("Christopher").collection("Schedule").document("Monday")
    doc_ref.set({ "Meal": recipe_text }, merge=True)

    # Step 3: Extract just the meal name
    name_prompt = f"""
        ONLY RETURN MEAL NAME: {response}.
        Instructions for you, Gemini:
        - ONLY send meal name.
        - No intro, no format, just the meal name.
    """
    name_response = model.generate_content(name_prompt)
    meal_name = name_response.text.strip()
    doc_ref.set({ "Meal_Name": meal_name }, merge=True)

    # Step 4: Search Pexels for an image
    pexels_key = os.getenv("PEXELS_API_KEY")
    headers = { "Authorization": pexels_key }
    params = { "query": meal_name, "per_page": 1 }

    res = requests.get("https://api.pexels.com/v1/search", headers=headers, params=params)

    if res.status_code == 200:
        try:
            image_url = res.json()["photos"][0]["src"]["medium"]
            doc_ref.set({ "Meal_Link": image_url }, merge=True)
        except Exception as e:
            print("Pexels image extract failed:", e)

    return "Meal and image updated successfully: OK"



@app.get("/fetch_recipe", response_class=PlainTextResponse)
async def fetch_recipe():
    doc_ref = db.collection("Users").document("Christopher").collection("Schedule").document("Monday")
    doc = doc_ref.get()

    if doc.exists:
        data = doc.to_dict()
        return data.get("Meal", "No meal recipe found.")
    else:
        return "No recipe document found for Monday."



@app.get("/meal_img_link", response_class=PlainTextResponse)
async def fetch_image():
    doc_ref = db.collection("Users").document("Christopher").collection("Schedule").document("Monday")
    doc = doc_ref.get()

    if doc.exists:
        data = doc.to_dict()
        return data.get("Meal_Link", "")
    else:
        return ""



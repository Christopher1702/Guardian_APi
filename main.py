from fastapi import FastAPI, Request
import google.generativeai as genai
import json
import os
from motor.motor_asyncio import AsyncIOMotorClient
from fastapi.middleware.cors import CORSMiddleware

genai.configure(api_key="AIzaSyBnaUhLpBZn0fv5Yo_91ghbmQbwf6niUv4")
model = genai.GenerativeModel('gemini-2.0-flash-lite')

MONGO_URI = "mongodb+srv://christopherdherman2317:7P783vXCTrq9cAht@guardian.nhsqmn8.mongodb.net/?retryWrites=true&w=majority&appName=Guardian"
client = AsyncIOMotorClient(MONGO_URI)
db = client["Guardian_db"]
collection = db["schedules"]

app = FastAPI()
DATA_FILE = "users.json"

# Allow all origins (good for testing, not for production!)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Or use your actual frontend URL
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

def load_data():
    if not os.path.exists(DATA_FILE):
        return {}
    with open(DATA_FILE, "r") as file:
        return json.load(file)
    
def save_data(data):
    with open(DATA_FILE, "w") as file:
        json.dump(data, file, indent=4)

def json_set_schedule(name: str, schedule: str):
    data = load_data()
    data[name] = schedule
    save_data(data)

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

#User Orginal Scedule 
@app.post("/set_schedule/")
async def add_schedule(request: Request):
    body = await request.json()
    name = body.get("name")
    schedule = body.get("schedule")
    json_set_schedule(name, schedule)
    return {"status": "Schedule saved", "user": name, "schedule": schedule}

@app.post("/schedule_change/")
# marked async because we're about to await something: reading JSON from the request.
async def adjust_schedule(request: Request):
    body = await request.json() #Reads the raw JSON body from the request. Converts it into a Python dictionary.
    name = body.get("name")
    change = body.get("change")

    data = load_data()

    if name not in data:
        return {"error": f"No schedule found for '{name}'"}

    current_schedule = data[name]

    prompt = (
        f"{name}'s current schedule: {current_schedule}\n"
        f"Can this new item fit: {change}?"
    )

    res = model.generate_content(prompt)

    return {
        "name": name,
        "current_schedule": current_schedule,
        "new_item": change,
        "gemini_response": res.text
    }

@app.get("/view_json")
def view_json():
    data = load_data()
    return data

@app.get("/clear_json")
def clear_json():
    with open(DATA_FILE, "w") as file:
        json.dump({}, file)
    return {"status": "JSON file cleared."}

# python -m uvicorn main:app --reload

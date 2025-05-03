from fastapi import FastAPI, Request
import google.generativeai as genai
import json
import os

genai.configure(api_key="")
model = genai.GenerativeModel('gemini-2.0-flash-lite')

app = FastAPI()
DATA_FILE = "users.json"

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

#User Orginal Scedule 
@app.post("/set_schedule/")
def add_schedule(name: str, schedule: str):
    json_set_schedule(name, schedule)
    return {"status": "Schedule saved", "user": name, "schedule": schedule}

@app.post("/schedule_change/")
# marked async because we're about to await something: reading JSON from the request.
async def adjust_schedule(request: Request):
    body = await request.json() # Reads the raw JSON body from the request. Converts it into a Python dictionary.
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

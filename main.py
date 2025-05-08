from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
import google.generativeai as genai
import json
import os
from fastapi.middleware.cors import CORSMiddleware
import firebase_admin
from firebase_admin import credentials, firestore
from dotenv import load_dotenv

genai.configure(api_key=os.environ["GOOGLE_API_KEY"])
model = genai.GenerativeModel('gemini-2.0-flash-lite')

load_dotenv()
cred_path = os.getenv("FIREBASE_CREDENTIALS_PATH")
cred = credentials.Certificate(cred_path)
firebase_admin.initialize_app(cred)
db = firestore.client()

app = FastAPI()

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

#User Orginal Scedule 
@app.post("/set_schedule/")
async def add_schedule(request: Request):
    body = await request.json()
    name = body.get("name")
    schedule = body.get("schedule")
    return {"status": "Schedule saved", "user": name, "schedule": schedule}

@app.post("/save")
async def save_user(request: Request):
    body = await request.json()
    name = body.get("name")
    schedule_set = body.get("schedule_set")
    db.collection("Guardian").document("USERS").set({
        "name": name,
        "schedule": schedule_set
    })
    return {"status": "Name saved", "user": name, "schedule" : schedule_set}

@app.post("/read")
async def read_user(request: Request):
    body = await request.json()
    name = body.get("name")

    doc_ref = db.collection("Users").document(name)
    doc = doc_ref.get()

    if doc.exists:
        return {"status": "Found", "data": doc.to_dict()}
    else:
        return JSONResponse(status_code=404, content={"status": "Not found", "user": name})

# python -m uvicorn main:app --reload

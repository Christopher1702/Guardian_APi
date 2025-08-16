import io
import json
import os
from typing import Optional

import firebase_admin
import google.generativeai as genai
import requests
from dotenv import load_dotenv
from fastapi import FastAPI, File, Request, UploadFile
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse, PlainTextResponse
from firebase_admin import credentials, firestore

genai.configure(api_key=os.environ["GOOGLE_API_KEY"])
model = genai.GenerativeModel('gemini-2.5-flash')
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


@app.get("/") #SERVER STATE TEST
def read_root():
    return {"message": "Hello from your FastAPI server!"}


@app.post("/upload_food")
async def receive_user_input(request: Request):

    # Read plain text from request
    user_upload = await request.body()
    food_txt = user_upload.decode("utf-8").strip()

    protein_prompt = f"""
        {food_txt}
        Instructions for Gemini:
        1. Return the protein count
        2. DO NOT BOLD ANY TEXT
        3. NO UNITS ONLY NUMBERS
        4. Just return the plain text.
    """.strip()

    calorie_prompt = f"""
        {food_txt}
        Instructions for Gemini:
        1. Return the calorie count
        2. DO NOT BOLD ANY TEXT
        3. NO UNITS ONLY NUMBERS
        4. Just return the plain text.
    """.strip()    

    fibre_prompt = f"""
        {food_txt}
        Instructions for Gemini:
        1. Return the fibre count
        2. DO NOT BOLD ANY TEXT
        3. NO UNITS ONLY NUMBERS
        4. Just return the plain text.
    """.strip()


    protein_response = model.generate_content(protein_prompt)
    protein = protein_response.text.strip()

    calorie_response = model.generate_content(calorie_prompt)
    calorie = calorie_response.text.strip()

    fibre_response = model.generate_content(fibre_prompt)
    fibre = fibre_response.text.strip()


    ai_prompt = f"""
        {food_txt}
        Instructions for Gemini:
        1. VERY SHORT explaination of macro break down of meal (calorie:{calorie}, protein:{protein}, fibre:{fibre}) 
        2. DO NOT BOLD ANY TEXT
        3. Just return the plain text.
    """.strip()

    ai_response = model.generate_content(ai_prompt)
    ai = ai_response.text.strip()
    
    doc_ref = db.collection("MacroTrack_Ai").document("User").collection("Track").document("Dinner")
    doc_ref.set({ "Protein": protein }, merge=True)
    doc_ref.set({ "Calories": calorie }, merge=True)
    doc_ref.set({ "Fibre": fibre }, merge=True)
    doc_ref.set({ "Ai_Response": ai }, merge=True)

    return {"status": "success", "received": food_txt}



def _safe_int(val) -> int:
    try:
        return int(val)
    except (ValueError, TypeError):
        return 0

@app.get("/calories")
def get_calories():
    # Fetch Dinner calories
    raw_calories = db.collection("MacroTrack_Ai").document("User") \
        .collection("Track").document("Dinner").get().to_dict().get("Calories", 0)
    
    # Fetch total daily calories
    total_calories_existing = db.collection("MacroTrack_Ai").document("User") \
        .collection("Track").document("Total_Daily_Macro").get().to_dict().get("Calories", 0)

    # Safely sum them
    dinner_val = _safe_int(raw_calories)
    total_val = _safe_int(total_calories_existing)
    summed = dinner_val + total_val

    # Save updated total back to Total_Daily_Macro
    db.collection("MacroTrack_Ai").document("User").collection("Track") \
        .document("Total_Daily_Macro").set({"Calories": summed}, merge=True)

    # Return for frontend
    return {"calories": summed}

@app.get("/protein")
def get_protein():
    # Fetch Dinner + existing Total_Daily_Macro
    dinner_raw = (
        db.collection("MacroTrack_Ai").document("User")
          .collection("Track").document("Dinner")
          .get().to_dict().get("Protein", 0)
    )
    total_raw = (
        db.collection("MacroTrack_Ai").document("User")
          .collection("Track").document("Total_Daily_Macro")
          .get().to_dict().get("Protein", 0)
    )

    # Safe sum
    summed = _safe_int(dinner_raw) + _safe_int(total_raw)

    # Persist back to Total_Daily_Macro
    db.collection("MacroTrack_Ai").document("User") \
      .collection("Track").document("Total_Daily_Macro") \
      .set({"Protein": summed}, merge=True)

    return {"protein": summed}


@app.get("/fibre")
def get_fibre():
    # Fetch Dinner + existing Total_Daily_Macro
    dinner_raw = (
        db.collection("MacroTrack_Ai").document("User")
          .collection("Track").document("Dinner")
          .get().to_dict().get("Fibre", 0)
    )
    total_raw = (
        db.collection("MacroTrack_Ai").document("User")
          .collection("Track").document("Total_Daily_Macro")
          .get().to_dict().get("Fibre", 0)
    )

    # Safe sum
    summed = _safe_int(dinner_raw) + _safe_int(total_raw)

    # Persist back to Total_Daily_Macro
    db.collection("MacroTrack_Ai").document("User") \
      .collection("Track").document("Total_Daily_Macro") \
      .set({"Fibre": summed}, merge=True)

    return {"fibre": summed}


@app.get("/ai_response")
def get_ai_response():
    doc = db.collection("MacroTrack_Ai").document("User").collection("Track").document("Dinner").get()
    data = doc.to_dict() or {}
    return {"ai": data.get("Ai_Response", "")}
    # or: return PlainTextResponse(data.get("Ai_Response", ""))

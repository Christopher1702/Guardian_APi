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



@app.get("/protein")
def get_protein():
    # Fetch Dinner protein
    dinner_doc = db.collection("MacroTrack_Ai").document("User") \
        .collection("Track").document("Dinner").get()
    dinner_data = dinner_doc.to_dict() or {}
    dinner_protein = float(dinner_data.get("Protein", 0))

    # Fetch Total_Daily_Macro protein
    total_doc = db.collection("MacroTrack_Ai").document("User") \
        .collection("Track").document("Total_Daily_Macro").get()
    total_data = total_doc.to_dict() or {}
    total_protein = float(total_data.get("Protein", 0))

    # Sum the values
    total_sum = dinner_protein + total_protein

    # Return as JSON
    return {"protein": total_sum}


@app.get("/calories")
def get_calories():
    doc = db.collection("MacroTrack_Ai").document("User").collection("Track").document("Total_Daily_Macro").get()
    data = doc.to_dict() or {}
    return {"calories": data.get("Calories", "")}
    # If you prefer plain text instead of JSON:
    # return PlainTextResponse(data.get("Calories", ""))

@app.get("/calories")
def get_calories():
    # Fetch Dinner calories
    dinner_doc = db.collection("MacroTrack_Ai").document("User") \
        .collection("Track").document("Dinner").get()
    dinner_data = dinner_doc.to_dict() or {}
    dinner_calories = float(dinner_data.get("Calories", 0))

    # Fetch Total_Daily_Macro calories
    total_doc = db.collection("MacroTrack_Ai").document("User") \
        .collection("Track").document("Total_Daily_Macro").get()
    total_data = total_doc.to_dict() or {}
    total_calories = float(total_data.get("Calories", 0))

    # Sum the values
    total_sum = dinner_calories + total_calories

    return {"calories": total_sum}


@app.get("/fibre")
def get_fibre():
    # Fetch Dinner fibre
    dinner_doc = db.collection("MacroTrack_Ai").document("User") \
        .collection("Track").document("Dinner").get()
    dinner_data = dinner_doc.to_dict() or {}
    dinner_fibre = float(dinner_data.get("Fibre", 0))

    # Fetch Total_Daily_Macro fibre
    total_doc = db.collection("MacroTrack_Ai").document("User") \
        .collection("Track").document("Total_Daily_Macro").get()
    total_data = total_doc.to_dict() or {}
    total_fibre = float(total_data.get("Fibre", 0))

    # Sum the values
    total_sum = dinner_fibre + total_fibre

    return {"fibre": total_sum}

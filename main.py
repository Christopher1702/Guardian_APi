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
    protein_bytes = await request.body()
    protein_str = protein_bytes.decode("utf-8").strip()
    """
    Receives user input from the frontend and returns a simple acknowledgment.
    """
    prompt = f"""
        {protein_str}
        Instructions for Gemini:
        1. Return the protein and calories counts.
        2. DO NOT BOLD ANY TEXT
        4. Just return the plain text.
    """.strip()

    response = model.generate_content(prompt)
    protein = response.text.strip()

    doc_ref = db.collection("MacroTrack_Ai").document("User").collection("Track").document("Dinner")
    doc_ref.set({ "Protein": protein }, merge=True)


    return {"status": "success", "received": protein_str}


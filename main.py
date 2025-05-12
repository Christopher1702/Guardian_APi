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

@app.post("/save", response_class=PlainTextResponse)#Talk to Ai in School Feature
async def save_user(request: Request):
    schedule_text = (await request.body()).decode("utf-8")

    doc_ref = db.collection("Users").document("Christopher").collection("Activities").document("School")
    doc = doc_ref.get()

    data = doc.to_dict() if doc.exists else {}

    prompt = f"""This is database of user information {data}, {schedule_text}"""
    response = model.generate_content(prompt)

    doc_ref.set({
        "Class Times": response.text
    })

    return "Schedule saved: Changes made successfully"

#----------------------------------------------------------------------------------------

@app.post("/read", response_class=PlainTextResponse)
async def read_user(request: Request):
    name = (await request.body()).decode("utf-8") #Expect Plain Text

    doc_ref = db.collection("Users").document("Christopher").collection("Activities").document("School") #Reference the School document under Activities subcollection
    doc = doc_ref.get()

    if doc.exists: #Return the class times if they exist
        data = doc.to_dict()
        return data.get("Class Times", "No class times found.")
    else:
        return f"Schedule not found for {name}"

#----------------------------------------------------------------------------------------

@app.post("/upload-image")  # Receive file and convert & store to PIL image
async def upload_image(file: UploadFile = File(...)):
    global stored_image
    if not file.content_type.startswith("image/"):
        return JSONResponse(status_code=400, content={"error": "Invalid file type"})
    
    stored_image = await file.read()  # Read image content into memory (bytes)
    if stored_image is None:
        return {"error": "No image uploaded yet."}

    try:
        image = Image.open(io.BytesIO(stored_image))  # Convert bytes to PIL Image
        prompt = """
        Create a schedule from this.
        1. No extra comments (just return the schedule)
        2. NO BOLD FONTS or excessive spacing)
        3. Organized format (start-end) (mention day of week once)
        4. Don't add unnecessary times slots that are empty 
        5. DONT include dates
        """
        response = model.generate_content([prompt, image])  # Send image + prompt
        print("Gemini response:\n", response.text)  # DEBUG: show raw response
        if not response.text.strip():
            return {"error": "Gemini returned an empty response."}

        school_ref = db.collection("Users").document("Christopher").collection("Activities").document("School") # Store the response in Firestore under Class Times
        school_ref.set({"Class Times": response.text}, merge=True)

        # Optionally log metadata
        print(f"Received image: {file.filename} ({file.content_type}), size: {len(stored_image)} bytes")

        return {
            "status": "success",
            "filename": file.filename,
            "size_bytes": len(stored_image),
            "stored_to": "Users/Christopher/Activities/School/Class Times"
        }

    except Exception as e:
        print("Failed to process schedule:", e)
        return {"error": "Schedule reading failed"}

#----------------------------------------------------------------------------------------

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import joblib
from difflib import SequenceMatcher

app = FastAPI()

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

model = joblib.load("fake_job_model.pkl")

class JobInput(BaseModel):
    text: str

# Similarity
def get_similarity(a, b):
    return SequenceMatcher(None, a, b).ratio()

# Reasons
def get_reasons(text):
    text = text.lower()
    reasons = []

    if "aadhaar" in text or "bank" in text:
        reasons.append("Asking sensitive information")
    if "urgent" in text:
        reasons.append("Creates urgency pressure")
    if "no experience" in text:
        reasons.append("No experience required")
    if "salary" in text or "earn" in text:
        reasons.append("Unrealistic salary offer")

    return reasons

# Company check
trusted_companies = ["tcs", "infosys", "wipro", "accenture", "google", "microsoft"]

def check_company(text):
    text = text.lower()
    for c in trusted_companies:
        if c in text:
            return f"Trusted company detected: {c.upper()}"
    return "Unknown or unverified company"

@app.get("/")
def home():
    return {"message": "Fake Job Detection API Running"}

@app.post("/predict")
def predict(data: JobInput):
    text = data.text

    prediction = model.predict([text])[0]
    prob = model.predict_proba([text])[0]

    if prediction == 1:
        result = "FAKE JOB"
        confidence = round(prob[1]*100, 2)
    else:
        result = "REAL JOB"
        confidence = round(prob[0]*100, 2)

    reasons = get_reasons(text)
    company = check_company(text)

    return {
        "prediction": result,
        "confidence": f"{confidence}%",
        "reasons": reasons,
        "company": company
    }

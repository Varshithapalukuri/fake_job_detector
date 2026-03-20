from fastapi import FastAPI
from pydantic import BaseModel
from fastapi.middleware.cors import CORSMiddleware
import joblib

app = FastAPI()

# ✅ CORS FIX
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Load model
model = joblib.load("fake_job_model.pkl")

history = []

class JobInput(BaseModel):
    text: str

@app.get("/")
def home():
    return {"message": "Fake Job Detection API Running"}

@app.post("/predict")
def predict(data: JobInput):

    text = data.text.lower()

    pred = model.predict([text])[0]
    prob = model.predict_proba([text])[0]
    confidence = max(prob)

    reasons = []
    is_scam = False

    # 🚨 STRONG RULES
    if "aadhaar" in text or "aadhar" in text:
        reasons.append("Aadhaar requested (high risk)")
        is_scam = True

    if "bank" in text or "account" in text:
        reasons.append("Bank details requested")
        is_scam = True

    if "otp" in text or "password" in text:
        reasons.append("Sensitive credentials requested")
        is_scam = True

    if "registration fee" in text or "pay" in text:
        reasons.append("Payment request detected")
        is_scam = True

    if "whatsapp" in text:
        reasons.append("Unverified contact method")
        is_scam = True

    # ⚠ Suspicious patterns
    if "urgent" in text or "immediate" in text:
        reasons.append("Pressure tactics used")

    if "no experience" in text:
        reasons.append("Unrealistic requirement")

    if "work from home" in text and "salary" in text:
        reasons.append("Suspicious high salary remote job")

    # 🔥 FINAL DECISION
    if is_scam:
        prediction = "FAKE JOB"
        risk = "HIGH"
        confidence = 0.99
    else:
        prediction = "FAKE JOB" if pred == 1 else "REAL JOB"

        if confidence < 0.7:
            risk = "HIGH"
        elif confidence < 0.9:
            risk = "MEDIUM"
        else:
            risk = "LOW"

    result = {
        "prediction": prediction,
        "confidence": round(confidence * 100, 2),
        "risk": risk,
        "reasons": reasons if reasons else ["General pattern detected"],
        "advice": "Never share personal or bank details online"
    }

    history.append({
        "text": data.text,
        "result": prediction
    })

    return result


@app.get("/history")
def get_history():
    return history


@app.post("/report")
def report_job(data: JobInput):
    return {"message": "Job reported successfully 🚨"}
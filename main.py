from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import joblib

app = FastAPI(
    title="Fake Job Detection API",
    description="Detect fake job postings",
    version="2.0"
)

# ✅ CORS FIX
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ✅ Load model
model = joblib.load("fake_job_model.pkl")

# ✅ Input schema
class JobInput(BaseModel):
    text: str

# ✅ Reason detection
def get_reasons(text):
    text = text.lower()
    reasons = []

    if "aadhaar" in text or "bank" in text:
        reasons.append("Asking sensitive information")

    if "urgent" in text:
        reasons.append("Creates urgency pressure")

    if "no experience" in text:
        reasons.append("No experience required")

    if "earn" in text or "salary" in text:
        reasons.append("Unrealistic salary offer")

    return reasons

# ✅ Home
@app.get("/")
def home():
    return {"message": "Fake Job Detection API Running"}

# ✅ Predict
@app.post("/predict")
def predict(data: JobInput):
    text = data.text

    prediction = model.predict([text])[0]
    probability = model.predict_proba([text])[0]

    if prediction == 1:
        result = "FAKE JOB"
        confidence = round(probability[1] * 100, 2)
    else:
        result = "REAL JOB"
        confidence = round(probability[0] * 100, 2)

    reasons = get_reasons(text)

    return {
        "prediction": result,
        "confidence": f"{confidence}%",
        "reasons": reasons
    }

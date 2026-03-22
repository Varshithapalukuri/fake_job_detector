from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import joblib

# Create FastAPI app
app = FastAPI(
    title="Fake Job Detection API",
    description="Detect whether a job posting is real or fake using Machine Learning",
    version="1.0"
)

# 🔥 CORS FIX (IMPORTANT)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # allow all frontends
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Load trained model
model = joblib.load("fake_job_model.pkl")

# Home route
@app.get("/")
def home():
    return {"message": "Fake Job Detection API Running"}

# Prediction route
@app.post("/predict")
def predict(text: str):
    prediction = model.predict([text])[0]
    probability = model.predict_proba([text])[0]

    if prediction == 1:
        result = "FAKE JOB"
        confidence = round(probability[1] * 100, 2)
    else:
        result = "REAL JOB"
        confidence = round(probability[0] * 100, 2)

    return {
        "prediction": result,
        "confidence": f"{confidence}%"
    }

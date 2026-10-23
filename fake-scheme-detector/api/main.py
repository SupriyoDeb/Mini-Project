from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import joblib
import numpy as np
from train import extract_url_features

app = FastAPI()

# Enable cross-origin calls from local browser environments
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Load pipeline dependencies
model = joblib.load('model.pkl')
vectorizer = joblib.load('vectorizer.pkl')
feature_keys = joblib.load('feature_keys.pkl')


class WebsiteData(BaseModel):
    url: str
    text: str


@app.post("/inspect")
async def inspect_site(data: WebsiteData):
    # Process features real-time
    u_feat = extract_url_features(data.url)
    u_vector = [u_feat[key] for key in feature_keys]

    t_vector = vectorizer.transform([data.text]).toarray()
    combined_vector = np.hstack(([u_vector], t_vector))

    # Calculate probability distribution values [Safe Probability, Scam Probability]
    probabilities = model.predict_proba(combined_vector)[0]
    scam_prob = float(probabilities[1])

    print(f"🕵️ Scanning URL: {data.url} | Calculated Scam Probability: {scam_prob * 100:.2f}%")

    if scam_prob > 0.70:
        status = "MALICIOUS (BLOCKED)"
    elif scam_prob > 0.40:
        status = "SUSPICIOUS"
    else:
        status = "SAFE (VERIFIED)"

    return {
        "status": status,
        "scam_probability": f"{scam_prob * 100:.1f}%"
    }


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="127.0.0.1", port=8000)
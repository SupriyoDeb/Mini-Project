import re
import math
import numpy as np
import joblib
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.ensemble import RandomForestClassifier

def calculate_entropy(text):
    if not text:
        return 0
    entropy = 0
    for x in range(256):
        p_x = float(text.count(chr(x))) / len(text)
        if p_x > 0:
            entropy += - p_x * math.log(p_x, 2)
    return entropy

def extract_url_features(url):
    features = {}
    # Security heuristic features targeting Indian government scheme patterns
    features['is_official_tld'] = 1.0 if any(ext in url.lower() for ext in ['.gov.in', '.nic.in']) else 0.0
    features['is_suspicious_tld'] = 1.0 if any(ext in url.lower() for ext in ['.xyz', '.top', '.club', '.info', '.online', '.cc', '.net']) else 0.0
    features['contains_pmkisan'] = 1.0 if 'pmkisan' in url.lower() or 'pm-kisan' in url.lower() else 0.0
    features['contains_mgnrega'] = 1.0 if 'mgnrega' in url.lower() or 'nrega' in url.lower() else 0.0
    features['url_length'] = float(len(url))
    features['dot_count'] = float(url.count('.'))
    features['hyphen_count'] = float(url.count('-'))
    features['digit_count'] = float(sum(c.isdigit() for c in url))
    features['url_entropy'] = calculate_entropy(url)
    return features

# Expanded dataset mapping safe portals vs common scam layouts
dataset = [
    {"url": "https://pmkisan.gov.in", "text": "Official portal PM Kisan Samman Nidhi. Department of Agriculture and Welfare. Aadhaar authentication mandatory. Direct Benefit Transfer status check.", "label": 0},
    {"url": "https://nrega.nic.in", "text": "Mahatma Gandhi National Rural Employment Guarantee Act. Ministry of Rural Development. View official job cards, state status maps, and dynamic indicators.", "label": 0},
    {"url": "https://myscheme.gov.in", "text": "National Portal for Government Schemes. Find reliable welfare schemes based on eligibility metrics. Safe centralized login interface.", "label": 0},
    {"url": "http://pmkisan-yojana-2026.xyz", "text": "PM Kisan Yojana Benefit 2026! Pay ₹499 verification charges immediately to activate your account. High returns guaranteed. Enter bank details and OTP now.", "label": 1},
    {"url": "https://mgnrega-jobcard-list.online", "text": "Download MGNREGA Job Card list. Enter your raw Bank Account Number, IFSC Code, and Aadhaar Card to claim ₹5,000 allowance instantly.", "label": 1},
    {"url": "http://pm-awas-yojana-free-funds.top", "text": "Urgent notice: Prime Minister housing scheme offering instant free subsidies. Click here to verify bank details and withdraw cash immediately.", "label": 1}
]

if __name__ == "__main__":
    urls = [item['url'] for item in dataset]
    texts = [item['text'] for item in dataset]
    labels = [item['label'] for item in dataset]

    # Process structural URL metrics
    url_feature_dicts = [extract_url_features(url) for url in urls]
    feature_keys = sorted(list(url_feature_dicts[0].keys()))
    X_url = [[d[key] for key in feature_keys] for d in url_feature_dicts]

    # Vectorize semantic page features using NLP
    vectorizer = TfidfVectorizer(stop_words='english', max_features=100)
    X_text = vectorizer.fit_transform(texts).toarray()

    # Combine structures into single multimodal matrix
    X_combined = np.hstack((X_url, X_text))
    y = np.array(labels)

    # Train Random Forest
    model = RandomForestClassifier(n_estimators=100, random_state=42)
    model.fit(X_combined, y)

    # Serialise pipeline assets to disk
    joblib.dump(model, 'model.pkl')
    joblib.dump(vectorizer, 'vectorizer.pkl')
    joblib.dump(feature_keys, 'feature_keys.pkl')
    print("ML Model trained and components saved successfully!")
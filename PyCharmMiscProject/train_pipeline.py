import numpy as np
import pandas as pd
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.ensemble import RandomForestClassifier
from sklearn.pipeline import Pipeline
from sklearn.base import BaseEstimator, TransformerMixin

# Mock sample containing patterns from fake rural scheme portals
data = {
    'url': [
        'https://pmkisan.gov.in',
        'http://pmkisan-yojana-reg.in',
        'https://nrega.nic.in',
        'https://mnrega-free-money.online'
    ],
    'page_content': [
        'Pradhan Mantri Kisan Samman Nidhi official portal status update verification direct benefit transfer.',
        'PM Kisan samman nidhi cash distribution scheme free registration login put details instant payment OTP banking details.',
        'Mahatma Gandhi National Rural Employment Guarantee Act compliance tracking reports muster roll administration.',
        'MNREGA job card download login get free 5000 rupees daily wages instantly register with bank details phone verify.'
    ],
    'label': [0, 1, 0, 1]  # 0 = Legitimate Gov portal, 1 = Scammer Fake Portal
}
df = pd.DataFrame(data)

class FeatureExtractor(BaseEstimator, TransformerMixin):
    def fit(self, X, y=None): return self
    def transform(self, X):
        features = []
        for idx, row in X.iterrows():
            url = row['url'].lower()
            text = row['page_content'].lower()
            is_gov = 1 if ('.gov.in' in url or '.nic.in' in url) else 0
            has_scam_words = 1 if any(w in text for w in ['free', 'instant', 'cash', 'मुफ़्त', 'पैसा']) else 0
            features.append([is_gov, has_scam_words])
        return np.array(features)

extractor = FeatureExtractor()
custom_feats = extractor.transform(df[['url', 'page_content']])
vectorizer = TfidfVectorizer(max_features=100, stop_words='english')
tfidf_feats = vectorizer.fit_transform(df['page_content']).toarray()

X_combined = np.hstack((custom_feats, tfidf_feats))
model = RandomForestClassifier(n_estimators=10, random_state=42)
model.fit(X_combined, df['label'])

print("NLP Feature Union & Random Forest Pipeline successfully initialized.")

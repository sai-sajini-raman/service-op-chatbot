import streamlit as st
import pandas as pd
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.cluster import KMeans
from transformers import pipeline
from config import CANDIDATE_LABELS

# Load dataset
df = pd.read_csv("incidents.csv")

st.title("🚨 AISA - AI Support Assistant Demo")
st.write("Prototype: Incident Classification & Suggested Resolution")

# Show few records
if st.checkbox("Show sample data"):
    st.write(df.head())

# --- Step 1: Train simple topic model (KMeans on descriptions) ---
vectorizer = TfidfVectorizer(stop_words="english")
X = vectorizer.fit_transform(df["description"])
kmeans = KMeans(n_clusters=5, random_state=42).fit(X)
df["cluster"] = kmeans.labels_

# --- Step 2: Hugging Face zero-shot classification for labels ---
classifier = pipeline("zero-shot-classification", model="facebook/bart-large-mnli")
candidate_labels = CANDIDATE_LABELS

def get_label(text):
    result = classifier(text, candidate_labels)
    return result["labels"][0]

df["category"] = df["description"].apply(get_label)

# --- UI: User query ---
query = st.text_area("Enter incident description:")
if query:
    q_vec = vectorizer.transform([query])
    cluster_id = kmeans.predict(q_vec)[0]

    # Find closest incident from same cluster
    similar_incident = df[df["cluster"] == cluster_id].sample(1).iloc[0]

    st.subheader("🔍 Suggested Category")
    st.write(get_label(query))

    st.subheader("💡 Similar Incident & Resolution")
    st.write(f"**Description:** {similar_incident['description']}")
    st.write(f"**Resolution:** {similar_incident['resolution']}")
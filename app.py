import streamlit as st
import pandas as pd
import numpy as np
import re

from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.linear_model import LogisticRegression
from sklearn.model_selection import train_test_split
from sklearn.metrics import accuracy_score, f1_score, classification_report

# -------------------------------
# Preprocessing
# -------------------------------

def preprocess(text):
    text = text.lower()
    text = re.sub(r"[^a-z\s]", "", text)
    text = re.sub(r"\s+", " ", text).strip()
    return text

# -------------------------------
# Load and train model
# -------------------------------

@st.cache_resource
def load_model():
    df = pd.read_csv("data/medical_data.csv")
    df["clean_text"] = df["text"].apply(preprocess)

    X_train, X_test, y_train, y_test = train_test_split(
        df["clean_text"], df["label"], test_size=0.2, random_state=42
    )

    vectorizer = TfidfVectorizer(ngram_range=(1, 2), min_df=1)
    X_train_vec = vectorizer.fit_transform(X_train)
    X_test_vec = vectorizer.transform(X_test)

    model = LogisticRegression(max_iter=1000)
    model.fit(X_train_vec, y_train)

    y_pred = model.predict(X_test_vec)
    metrics = {
        "accuracy": accuracy_score(y_test, y_pred),
        "f1": f1_score(y_test, y_pred),
        "report": classification_report(y_test, y_pred, target_names=["Normal", "Abnormal"])
    }

    return vectorizer, model, metrics

vectorizer, model, metrics = load_model()

# -------------------------------
# UI
# -------------------------------

st.set_page_config(page_title="Medical Text Analyzer", layout="centered")

st.title("🧠 Medical Text Analyzer")
st.write("Analyze medical text and classify it as Normal or Abnormal.")
st.markdown("⚠️ *This tool is for educational purposes only and does not provide medical advice.*")

# Model performance in sidebar
with st.sidebar:
    st.subheader("📊 Model Performance")
    st.metric("Accuracy", f"{metrics['accuracy']:.2%}")
    st.metric("F1 Score", f"{metrics['f1']:.2%}")
    with st.expander("Full report"):
        st.text(metrics["report"])

# Input
user_input = st.text_area("Enter medical text:", height=150,
    placeholder="e.g. Patient presents with high fever and elevated white blood cell count")

# -------------------------------
# Prediction
# -------------------------------

if st.button("Analyze"):
    if user_input.strip() == "":
        st.warning("Please enter some text.")
    else:
        clean_input = preprocess(user_input)
        input_vec = vectorizer.transform([clean_input])

        prediction = model.predict(input_vec)[0]
        proba = model.predict_proba(input_vec)[0]
        confidence = max(proba)

        if prediction == 1:
            st.error(f"⚠️ Abnormal case detected — Confidence: {confidence:.0%}")
        else:
            st.success(f"✅ Normal case — Confidence: {confidence:.0%}")

        # -------------------------------
        # Explain prediction (keywords)
        # -------------------------------

        st.subheader("🔍 Important Words in Prediction")

        feature_names = vectorizer.get_feature_names_out()
        coefficients = model.coef_[0]

        # Use preprocessed tokens for consistent matching
        input_tokens = clean_input.split()

        important_words = []
        for word in input_tokens:
            if word in feature_names:
                idx = np.where(feature_names == word)[0][0]
                weight = coefficients[idx]
                important_words.append((word, weight))

        # Sort by absolute weight — most influential first
        important_words.sort(key=lambda x: abs(x[1]), reverse=True)

        if important_words:
            for word, weight in important_words[:8]:
                if weight > 0:
                    st.write(f"🔴 **{word}** → contributes to Abnormal (weight: {weight:.3f})")
                else:
                    st.write(f"🟢 **{word}** → contributes to Normal (weight: {weight:.3f})")
        else:
            st.info("No significant keywords found in the model vocabulary.")

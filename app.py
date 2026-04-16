import streamlit as st
import pandas as pd
import numpy as np

from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.linear_model import LogisticRegression

# -------------------------------
# Load and train model
# -------------------------------

@st.cache_resource
def load_model():
    df = pd.read_csv("data/medical_data.csv")

    vectorizer = TfidfVectorizer()
    X = vectorizer.fit_transform(df["text"])
    y = df["label"]

    model = LogisticRegression()
    model.fit(X, y)

    return vectorizer, model

vectorizer, model = load_model()

# -------------------------------
# UI
# -------------------------------

st.set_page_config(page_title="Medical Text Analyzer", layout="centered")

st.title("🧠 Medical Text Analyzer")
st.write("Analyze medical text and classify it as Normal or Abnormal.")

st.markdown("⚠️ *This tool is for educational purposes only and does not provide medical advice.*")

# Input
user_input = st.text_area("Enter medical text:", height=150)

# -------------------------------
# Prediction
# -------------------------------

if st.button("Analyze"):

    if user_input.strip() == "":
        st.warning("Please enter some text.")
    else:
        input_vec = vectorizer.transform([user_input])

        prediction = model.predict(input_vec)[0]
        proba = model.predict_proba(input_vec)[0]

        confidence = max(proba)

        # Result
        if prediction == 1:
            st.error(f"⚠️ Abnormal case detected (Confidence: {confidence:.2f})")
        else:
            st.success(f"✅ Normal case (Confidence: {confidence:.2f})")

        # -------------------------------
        # Explain prediction (keywords)
        # -------------------------------

        st.subheader("🔍 Important Words in Prediction")

        feature_names = vectorizer.get_feature_names_out()
        coefficients = model.coef_[0]

        input_words = user_input.lower().split()

        important_words = []

        for word in input_words:
            if word in feature_names:
                idx = np.where(feature_names == word)[0][0]
                weight = coefficients[idx]
                important_words.append((word, weight))

        if important_words:
            for word, weight in important_words:
                if weight > 0:
                    st.write(f"🔴 {word} → contributes to Abnormal")
                else:
                    st.write(f"🟢 {word} → contributes to Normal")
        else:
            st.write("No significant keywords found in the model vocabulary.")
# Medical Text Analyzer

[![Live Demo](https://static.streamlit.io/badges/streamlit_badge_black_white.svg)](https://medical-text-analyzer-sbkv62hqz7fumsqqg2htpv.streamlit.app/)

An NLP project that classifies medical reports as **Normal** or **Abnormal** using TF-IDF vectorization and Logistic Regression, with an interactive Streamlit interface.

> ⚠️ Educational purposes only — not intended for clinical use.

---

## Demo

```
Patient presents with high fever and elevated white blood cell count
→ ⚠️ Abnormal case detected — Confidence: 91%
```

---

## Features

- Binary classification of medical text (Normal / Abnormal)
- Confidence score for each prediction
- Keyword-level explanation — shows which words drove the result
- Model performance metrics displayed in the sidebar (Accuracy, F1 Score)
- Interactive web interface built with Streamlit

---

## Methodology

1. **Preprocessing** — lowercasing, punctuation removal
2. **Vectorization** — TF-IDF with unigrams and bigrams
3. **Model** — Logistic Regression trained on 80% of data, evaluated on 20%
4. **Evaluation** — Accuracy + F1 Score on held-out test set

---

## Project Structure

```
medical-text-analyzer/
│
├── data/
│   └── medical_data.csv       # 199 synthetic medical sentences
│
├── notebook/
│   └── analysis.ipynb         # Exploratory analysis and model prototyping
│
├── app.py                     # Streamlit web application
├── requirements.txt
└── README.md
```

---

## Getting Started

```bash
# Clone the repo
git clone https://github.com/TakoiRizgui/medical-text-analyzer.git
cd medical-text-analyzer

# Install dependencies
pip install -r requirements.txt

# Run the app
streamlit run app.py
```

Then open your browser at `http://localhost:8501`

---

## Dataset

The dataset (`medical_data.csv`) contains 199 synthetic medical sentences — 100 normal, 99 abnormal — covering cardiology, endocrinology, infectiology, neurology, and oncology.

> A known limitation of this project is the use of synthetic data. Real-world performance would require validation on clinical datasets such as MIMIC-III.

---

## Roadmap

- [ ] Replace synthetic data with a real clinical dataset
- [ ] Add text preprocessing with medical stopwords
- [ ] Experiment with BERT / BioBERT for improved accuracy
- [ ] Deploy on Streamlit Cloud

---

## Technologies

Python · Pandas · Scikit-learn · Streamlit · NumPy

---

## Author

**Takoi Rizgui** — Data Science & Healthcare  
[LinkedIn](https://www.linkedin.com/in/takwa-rizgui-094b1a95) · [GitHub](https://github.com/TakoiRizgui)

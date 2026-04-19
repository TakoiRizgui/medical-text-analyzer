# 🩺 Clinical Lab Results Interpreter

[![Live Demo](https://static.streamlit.io/badges/streamlit_badge_black_white.svg)](https://medical-text-analyzer-sbkv62hqz7fumsqqg2htpv.streamlit.app/)

A multilingual tool that extracts and interprets clinical lab values from free text, compares them to medical reference thresholds, and generates a downloadable PDF report.

> ⚠️ Educational purposes only — not intended for clinical use.

---

## Demo

```
Ferritin 8 ng/mL, Hemoglobin 10.2 g/dL, Glucose 140 mg/dL, CRP 45 mg/L
→ ⚠️ Out-of-range values detected
→ Ferritin: Very low — severe iron deficiency
→ Hemoglobin: Low — moderate anemia
→ Glucose: Diabetic range
→ CRP: Significantly elevated — active infection
```

---

## How it works

1. Paste a text containing lab results (e.g. `Ferritin 8 ng/mL, CRP 45 mg/L`)
2. Each value is extracted using pattern matching (supports `=`, `<`, `>` operators)
3. The value is compared to clinical reference thresholds
4. An interpretation and recommendation are displayed per parameter
5. A PDF report can be downloaded

> ⚠️ This tool does **not** use AI or machine learning.
> It uses clinical rules and thresholds — making it transparent, auditable, and reliable.

---

## What this tool does NOT do

- It does not understand free medical language ("patient has chest pain")
- It does not diagnose — it is a reading aid, not a doctor
- It only works for the parameters explicitly programmed

---

## Supported parameters (15)

| Parameter | Unit | Normal range |
|---|---|---|
| Ferritin | ng/mL | 12–200 (women), 30–300 (men) |
| Hemoglobin | g/dL | 12–15.5 (women), 13.5–17.5 (men) |
| Glucose (fasting) | mg/dL | 70–99 |
| HbA1c | % | < 5.7% |
| CRP | mg/L | < 10 |
| TSH | mIU/L | 0.4–4.0 |
| Creatinine | mg/dL | 0.59–1.35 |
| Triglycerides | mg/dL | < 150 |
| Cholesterol (total) | mg/dL | < 200 |
| Platelets | ×10³/µL | 150–400 |
| Vitamin D | ng/mL | 30–100 |
| INR | — | 0.8–1.2 |
| Urea | mg/dL | 7–20 |
| Sodium | mEq/L | 136–145 |
| Potassium | mEq/L | 3.5–5.0 |

---

## Features

- ✅ 15 clinical parameters with thresholds and recommendations
- ✅ Supports `<` and `>` operators (e.g. `CRP < 5 mg/L`)
- ✅ 3 languages: English, French, Arabic (with RTL support)
- ✅ PDF report export
- ✅ Unit tested (19 tests)

---

## Project structure

```
clinical-lab-interpreter/
│
├── app.py                  # Streamlit interface
├── extractor.py            # Core: value extraction + interpretation
├── test_extractor.py       # 19 unit tests
├── requirements.txt
│
├── locales/
│   ├── en.json
│   ├── fr.json
│   └── ar.json
│
└── README.md
```

---

## Getting started

```bash
git clone https://github.com/TakoiRizgui/medical-text-analyzer.git
cd medical-text-analyzer
pip install -r requirements.txt
streamlit run app.py
```

---

## Running tests

```bash
python test_extractor.py
```

---

## Roadmap

- [ ] Add 20+ more parameters (Calcium, Magnesium, ALT, AST, PSA...)
- [ ] Support unit conversion (mmol/L ↔ mg/dL for glucose)
- [ ] Add parameter relationships (e.g. low ferritin + low hemoglobin = iron deficiency anemia confirmed)
- [ ] PWA / offline mode

---

## Technologies

Python · Streamlit · fpdf2

---

## Author

**Takoi Rizgui** — Data Science & Healthcare
[LinkedIn](https://www.linkedin.com/in/takwa-rizgui-094b1a95) · [GitHub](https://github.com/TakoiRizgui)

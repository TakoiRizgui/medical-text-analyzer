# 🩺 Clinical Lab Results Interpreter

[![Live Demo](https://img.shields.io/badge/demo-live-brightgreen)](https://lab-interpreter.vercel.app)
[![API](https://img.shields.io/badge/API-HuggingFace-yellow)](https://takoirizgui-lab-interpreter-api.hf.space/docs)
[![Tests](https://github.com/TakoiRizgui/medical-text-analyzer/actions/workflows/tests.yml/badge.svg)](https://github.com/TakoiRizgui/medical-text-analyzer/actions)
[![License: MIT](https://img.shields.io/badge/License-MIT-blue.svg)](LICENSE)

A multilingual AI-powered tool that extracts and interprets clinical lab values from free text, compares them to medical reference thresholds, and generates a downloadable PDF report.

> ⚠️ Educational purposes only — not intended for clinical use.

---

## 🌐 Live Demo

👉 **[lab-interpreter.vercel.app](https://lab-interpreter.vercel.app)**

---

## Demo

```
Input:  Ferritin 8 ng/mL, Hemoglobin 9.8 g/dL, Glucose 140 mg/dL, CRP 45 mg/L

Output:
⚠️ Out-of-range values detected

⚠️ Ferritin — 8.0 ng/mL
   Very low — severe iron deficiency
   💡 Consider iron supplementation. Check transferrin saturation and CBC.

⚠️ Hemoglobin — 9.8 g/dL
   Low — moderate anemia
   💡 Check ferritin, B12, folate to identify cause.

⚠️ Glucose (fasting) — 140.0 mg/dL
   Diabetic range — high fasting glucose
   💡 Confirm with HbA1c. Verify fasting duration (min 8h).

⚠️ CRP (Inflammation) — 45.0 mg/L
   Significantly elevated — active infection or autoimmune flare
   💡 Identify source of inflammation. Complete with CBC, ESR.
```

---

## Architecture

```
Frontend (Vercel)                    Backend (Hugging Face Spaces)
─────────────────                    ──────────────────────────────
HTML / CSS / JS          ←──────────►  FastAPI + Python
lab-interpreter.vercel.app            takoirizgui-lab-interpreter-api.hf.space
                                       ├── /analyze  (extraction + AI)
                                       ├── /chat     (medical chatbot)
                                       └── /pdf      (PDF report)
```

---

## How it works

1. Paste a text containing lab results (e.g. `Ferritin 8 ng/mL, CRP 45 mg/L`)
2. Each value is extracted using pattern matching (supports `=`, `<`, `>` operators)
3. The value is compared to clinical reference thresholds
4. Claude AI generates a natural language interpretation
5. A chatbot answers follow-up questions about your results
6. A PDF report can be downloaded

---

## What this tool does NOT do

- It does not understand free medical language ("patient has chest pain")
- It does not diagnose — it is a reading aid, not a doctor
- It only works for the parameters explicitly programmed

---

## Supported parameters (40)

| Category | Parameters |
|---|---|
| Blood count | Hemoglobin, Ferritin, Platelets |
| Glycemia | Glucose, HbA1c |
| Lipids | Cholesterol, Triglycerides |
| Kidney | Creatinine, Urea |
| Liver | AST, ALT, GGT, Bilirubin (total + direct) |
| Pancreas | Lipase, Amylase |
| Thyroid | TSH |
| Cardiac | Troponin, CPK, LDH, D-Dimer |
| Inflammation | CRP, ESR |
| Electrolytes | Sodium, Potassium, Magnesium, Phosphorus |
| Vitamins | Vitamin D |
| Coagulation | INR |
| Hormones | FSH, LH, Prolactin, Testosterone, Progesterone, Estradiol |
| Serology | ASLO, Rheumatoid Factor, Wright, Widal, HBs Antigen, Anti-HBs |

---

## Features

- ✅ 40 clinical parameters with thresholds and recommendations
- ✅ AI interpretation powered by Claude (Anthropic)
- ✅ Medical chatbot — ask questions about your results
- ✅ Supports `<` and `>` operators (e.g. `CRP < 5 mg/L`)
- ✅ Unit conversion (g/L, mmol/L, µmol/L → mg/dL)
- ✅ Comma decimal support (`1,05 g/L` → `105 mg/dL`)
- ✅ 3 languages: English, French, Arabic (with RTL support)
- ✅ PDF report export with AI interpretation
- ✅ Unit tested — 19 tests passing
- ✅ CI/CD via GitHub Actions
- ✅ Deployed: Frontend (Vercel) + Backend (Hugging Face Spaces)

---

## Project structure

```
medical-text-analyzer/
│
├── backend/                      # FastAPI backend
│   ├── main.py                   # API routes + Claude integration
│   ├── extractor.py              # Core: value extraction + interpretation
│   ├── requirements.txt
│   └── Dockerfile                # For Hugging Face Spaces
│
├── frontend/
│   └── index.html                # Web interface
│
├── test_extractor.py             # 19 unit tests
│
├── locales/
│   ├── en.json
│   ├── fr.json
│   └── ar.json
│
├── .github/
│   └── workflows/
│       └── tests.yml             # CI/CD
│
└── README.md
```

---

## Getting started (local)

```bash
git clone https://github.com/TakoiRizgui/medical-text-analyzer.git
cd medical-text-analyzer

# Backend
cd backend
pip install -r requirements.txt
export ANTHROPIC_API_KEY=sk-ant-xxxxx
uvicorn main:app --reload --port 8000

# Frontend (new terminal)
cd ..
python -m http.server 3000 --directory frontend
# Open http://localhost:3000
```

---

## Running tests

```bash
python test_extractor.py
```

---

## API Documentation

👉 **[takoirizgui-lab-interpreter-api.hf.space/docs](https://takoirizgui-lab-interpreter-api.hf.space/docs)**

| Endpoint | Method | Description |
|---|---|---|
| `/health` | GET | API status |
| `/parameters` | GET | List all 40 parameters |
| `/analyze` | POST | Extract + AI interpret |
| `/chat` | POST | Medical chatbot |
| `/pdf` | POST | Generate PDF report |

---

## Roadmap

- [ ] PDF upload with OCR (Tesseract)
- [ ] Patient profile (age, sex, context-aware interpretation)
- [ ] Temporal analysis — track results over time
- [ ] Explainable AI — "why I say this"
- [ ] Add 20+ more parameters

---

## Technologies

Python · FastAPI · Anthropic Claude · Streamlit · fpdf2 · Vercel · Hugging Face Spaces

---

## Author

**Takoi Rizgui** — Data Science & Healthcare
[LinkedIn](https://www.linkedin.com/in/takwa-rizgui-094b1a95) · [GitHub](https://github.com/TakoiRizgui)

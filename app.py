import streamlit as st
import numpy as np

from preprocessing import preprocess
from model import train_model
from extractor import analyze_text

T = {
    "en": {
        "title": "🧠 Medical Text Analyzer",
        "subtitle": "Enter medical lab results and get an instant interpretation.",
        "disclaimer": "⚠️ *Educational purposes only — not a substitute for medical advice.*",
        "input_label": "Enter your lab results:",
        "button": "Analyze",
        "sample_btn": "📋 Try a sample",
        "empty_warning": "Please enter some text.",
        "result_abnormal": "⚠️ Abnormal findings detected",
        "result_normal": "✅ Results appear normal",
        "confidence": "Model confidence",
        "keywords_title": "🔍 Key words detected by model",
        "word_abnormal": "→ abnormal signal",
        "word_normal": "→ normal signal",
        "no_keywords": "No significant keywords found.",
        "interp_title": "📋 Detailed Interpretation",
        "no_interp": "No numeric values detected. Try: Ferritin 50 ng/mL, Hemoglobin 13.9 g/dL",
        "ref_label": "Reference values",
        "sidebar_perf": "📊 Model Performance",
        "sidebar_accuracy": "Accuracy",
        "sidebar_f1": "F1 Score",
        "sidebar_report": "Full report",
        "sidebar_kb": "parameters monitored",
        "sidebar_lang": "🌐 Language",
    },
    "fr": {
        "title": "🧠 Analyseur de Résultats Médicaux",
        "subtitle": "Entrez vos résultats d'analyses et obtenez une interprétation immédiate.",
        "disclaimer": "⚠️ *À des fins éducatives uniquement — ne remplace pas un avis médical.*",
        "input_label": "Entrez vos résultats d'analyses :",
        "button": "Analyser",
        "sample_btn": "📋 Voir un exemple",
        "empty_warning": "Veuillez entrer du texte.",
        "result_abnormal": "⚠️ Anomalie(s) détectée(s)",
        "result_normal": "✅ Résultats dans les normes",
        "confidence": "Confiance du modèle",
        "keywords_title": "🔍 Mots-clés détectés",
        "word_abnormal": "→ signal anormal",
        "word_normal": "→ signal normal",
        "no_keywords": "Aucun mot-clé significatif détecté.",
        "interp_title": "📋 Interprétation détaillée",
        "no_interp": "Aucune valeur numérique détectée. Essayez : Ferritine 50 ng/mL, Hémoglobine 13.9 g/dL",
        "ref_label": "Valeurs de référence",
        "sidebar_perf": "📊 Performance du modèle",
        "sidebar_accuracy": "Précision",
        "sidebar_f1": "Score F1",
        "sidebar_report": "Rapport complet",
        "sidebar_kb": "paramètres surveillés",
        "sidebar_lang": "🌐 Langue",
    },
    "ar": {
        "title": "🧠 محلل نتائج التحاليل الطبية",
        "subtitle": "أدخل نتائج تحاليلك واحصل على تفسير فوري.",
        "disclaimer": "⚠️ *للأغراض التعليمية فقط — لا يغني عن الاستشارة الطبية.*",
        "input_label": "أدخل نتائج تحاليلك:",
        "button": "تحليل",
        "sample_btn": "📋 جرّب مثالاً",
        "empty_warning": "الرجاء إدخال نص.",
        "result_abnormal": "⚠️ تم اكتشاف نتائج غير طبيعية",
        "result_normal": "✅ النتائج تبدو طبيعية",
        "confidence": "ثقة النموذج",
        "keywords_title": "🔍 الكلمات المفتاحية المكتشفة",
        "word_abnormal": "→ إشارة غير طبيعية",
        "word_normal": "→ إشارة طبيعية",
        "no_keywords": "لم يتم العثور على كلمات مفتاحية.",
        "interp_title": "📋 التفسير التفصيلي",
        "no_interp": "لم يتم اكتشاف قيم رقمية. جرّب: Ferritin 50 ng/mL",
        "ref_label": "القيم المرجعية",
        "sidebar_perf": "📊 أداء النموذج",
        "sidebar_accuracy": "الدقة",
        "sidebar_f1": "درجة F1",
        "sidebar_report": "التقرير الكامل",
        "sidebar_kb": "معايير مراقبة",
        "sidebar_lang": "🌐 اللغة",
    }
}

SAMPLES = {
    "en": "Ferritin 8 ng/mL, Hemoglobin 10.2 g/dL, Glucose 140 mg/dL, CRP 45 mg/L",
    "fr": "Ferritine 8 ng/mL, Hémoglobine 10.2 g/dL, Glycémie 140 mg/dL, CRP 45 mg/L",
    "ar": "Ferritin 8 ng/mL, Hemoglobin 10.2 g/dL, Glucose 140 mg/dL, CRP 45 mg/L",
}

@st.cache_resource
def load_model():
    return train_model()

vectorizer, model, metrics = load_model()

st.set_page_config(page_title="Medical Text Analyzer", layout="centered")

with st.sidebar:
    lang = st.selectbox(
        T["en"]["sidebar_lang"], ["en", "fr", "ar"],
        format_func=lambda x: {"en": "🇬🇧 English", "fr": "🇫🇷 Français", "ar": "🇸🇦 العربية"}[x]
    )

tr = T[lang]

if lang == "ar":
    st.markdown("""<style>
        .stApp, .stTextArea, .stMarkdown, p, div, label { direction: rtl; text-align: right; }
    </style>""", unsafe_allow_html=True)

st.title(tr["title"])
st.write(tr["subtitle"])
st.markdown(tr["disclaimer"])

with st.sidebar:
    st.subheader(tr["sidebar_perf"])
    st.metric(tr["sidebar_accuracy"], f"{metrics['accuracy']:.2%}")
    st.metric(tr["sidebar_f1"], f"{metrics['f1']:.2%}")
    with st.expander(tr["sidebar_report"]):
        st.text(metrics["report"])
    st.markdown("---")
    st.caption(f"📚 7 {tr['sidebar_kb']}")

col1, col2 = st.columns([3, 1])
with col1:
    st.markdown(f"**{tr['input_label']}**")
with col2:
    if st.button(tr["sample_btn"]):
        st.session_state["sample_text"] = SAMPLES[lang]

default_text = st.session_state.get("sample_text", "")
user_input = st.text_area("", value=default_text, height=130,
                          placeholder="e.g. Ferritin 50 ng/mL, Hemoglobin 13.9 g/dL",
                          label_visibility="collapsed")

if st.button(tr["button"], type="primary"):
    if user_input.strip() == "":
        st.warning(tr["empty_warning"])
    else:
        clean_input = preprocess(user_input)
        input_vec = vectorizer.transform([clean_input])
        prediction = model.predict(input_vec)[0]
        proba = model.predict_proba(input_vec)[0]
        confidence = max(proba)

        # Run extractor first — use it as primary verdict if values found
        findings = analyze_text(user_input, lang)

        if findings:
            has_abnormal = any(f["status_key"] != "normal" for f in findings)
            if has_abnormal:
                st.error(tr["result_abnormal"])
            else:
                st.success(tr["result_normal"])
        else:
            # No numeric values — fall back to NLP model
            if prediction == 1:
                st.error(f"{tr['result_abnormal']} — {tr['confidence']}: {confidence:.0%}")
            else:
                st.success(f"{tr['result_normal']} — {tr['confidence']}: {confidence:.0%}")

        with st.expander(tr["keywords_title"]):
            feature_names = vectorizer.get_feature_names_out()
            coefficients = model.coef_[0]
            input_tokens = clean_input.split()
            important_words = []
            for word in input_tokens:
                if word in feature_names:
                    idx = np.where(feature_names == word)[0][0]
                    weight = coefficients[idx]
                    important_words.append((word, weight))
            important_words.sort(key=lambda x: abs(x[1]), reverse=True)
            if important_words:
                for word, weight in important_words[:8]:
                    icon = "🔴" if weight > 0 else "🟢"
                    direction = tr["word_abnormal"] if weight > 0 else tr["word_normal"]
                    st.write(f"{icon} **{word}** {direction} ({weight:.3f})")
            else:
                st.info(tr["no_keywords"])

        st.subheader(tr["interp_title"])
        if findings:
            for f in findings:
                icon = "✅" if f["status_key"] == "normal" else "⚠️"
                with st.expander(f"{icon} {f['name']} — {f['value']} {f['unit']}"):
                    st.markdown(f"**{f['status']}**")
                    st.caption(f"📐 {tr['ref_label']}: {f['reference']}")
                    if f["advice"]:
                        st.info(f"💡 {f['advice']}")
        else:
            st.info(tr["no_interp"])

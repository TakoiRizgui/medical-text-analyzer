import streamlit as st
import pandas as pd
import numpy as np
import re

from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.linear_model import LogisticRegression
from sklearn.model_selection import train_test_split
from sklearn.metrics import accuracy_score, f1_score, classification_report

# -----------------------------------------------
# UI Translations
# -----------------------------------------------

T = {
    "en": {
        "title": "🧠 Medical Text Analyzer",
        "subtitle": "Analyze medical text and classify it as Normal or Abnormal.",
        "disclaimer": "⚠️ *This tool is for educational purposes only and does not provide medical advice.*",
        "input_label": "Enter medical text:",
        "input_placeholder": "e.g. Ferritin low at 8 ng/mL, hemoglobin 9.2 g/dL, iron deficiency anemia suspected",
        "button": "Analyze",
        "empty_warning": "Please enter some text.",
        "result_abnormal": "⚠️ Abnormal case detected — Confidence:",
        "result_normal": "✅ Normal case — Confidence:",
        "keywords_title": "🔍 Key Words in Prediction",
        "word_abnormal": "contributes to Abnormal",
        "word_normal": "contributes to Normal",
        "no_keywords": "No significant keywords found in the model vocabulary.",
        "interp_title": "📋 Medical Interpretation",
        "no_interp": "No recognized medical parameters found for interpretation.",
        "what_means": "**What it means:**",
        "reference": "**Reference values:**",
        "sidebar_perf": "📊 Model Performance",
        "sidebar_accuracy": "Accuracy",
        "sidebar_f1": "F1 Score",
        "sidebar_report": "Full classification report",
        "sidebar_kb": "parameters in knowledge base",
        "sidebar_lang": "🌐 Language",
        "dir": "ltr",
    },
    "fr": {
        "title": "🧠 Analyseur de Texte Médical",
        "subtitle": "Analysez un texte médical et classifiez-le comme Normal ou Anormal.",
        "disclaimer": "⚠️ *Cet outil est à des fins éducatives uniquement et ne constitue pas un avis médical.*",
        "input_label": "Entrez le texte médical :",
        "input_placeholder": "ex. Ferritine basse à 8 ng/mL, hémoglobine 9,2 g/dL, anémie ferriprive suspectée",
        "button": "Analyser",
        "empty_warning": "Veuillez entrer du texte.",
        "result_abnormal": "⚠️ Cas anormal détecté — Confiance :",
        "result_normal": "✅ Cas normal — Confiance :",
        "keywords_title": "🔍 Mots-clés de la prédiction",
        "word_abnormal": "contribue à Anormal",
        "word_normal": "contribue à Normal",
        "no_keywords": "Aucun mot-clé significatif trouvé dans le vocabulaire du modèle.",
        "interp_title": "📋 Interprétation médicale",
        "no_interp": "Aucun paramètre médical reconnu pour l'interprétation.",
        "what_means": "**Ce que ça signifie :**",
        "reference": "**Valeurs de référence :**",
        "sidebar_perf": "📊 Performance du modèle",
        "sidebar_accuracy": "Précision",
        "sidebar_f1": "Score F1",
        "sidebar_report": "Rapport complet",
        "sidebar_kb": "paramètres dans la base",
        "sidebar_lang": "🌐 Langue",
        "dir": "ltr",
    },
    "ar": {
        "title": "🧠 محلل النصوص الطبية",
        "subtitle": "حلّل النصوص الطبية وصنّفها كحالة طبيعية أو غير طبيعية.",
        "disclaimer": "⚠️ *هذه الأداة للأغراض التعليمية فقط ولا تُعدّ نصيحة طبية.*",
        "input_label": "أدخل النص الطبي:",
        "input_placeholder": "مثال: الفيريتين منخفض 8 نانوغرام/مل، الهيموغلوبين 9.2 غ/دل، فقر الدم بسبب نقص الحديد",
        "button": "تحليل",
        "empty_warning": "الرجاء إدخال نص.",
        "result_abnormal": "⚠️ حالة غير طبيعية — الثقة:",
        "result_normal": "✅ حالة طبيعية — الثقة:",
        "keywords_title": "🔍 الكلمات المفتاحية في التنبؤ",
        "word_abnormal": "يساهم في: غير طبيعي",
        "word_normal": "يساهم في: طبيعي",
        "no_keywords": "لم يتم العثور على كلمات مفتاحية في مفردات النموذج.",
        "interp_title": "📋 التفسير الطبي",
        "no_interp": "لم يتم التعرف على أي معايير طبية للتفسير.",
        "what_means": "**ماذا يعني:**",
        "reference": "**القيم المرجعية:**",
        "sidebar_perf": "📊 أداء النموذج",
        "sidebar_accuracy": "الدقة",
        "sidebar_f1": "درجة F1",
        "sidebar_report": "التقرير الكامل",
        "sidebar_kb": "معايير في قاعدة البيانات",
        "sidebar_lang": "🌐 اللغة",
        "dir": "rtl",
    }
}

# -----------------------------------------------
# Medical Knowledge Base (EN / FR / AR)
# -----------------------------------------------

MEDICAL_TERMS = {
    "glucose": {
        "en": {
            "explanation": "Blood sugar level. High glucose can indicate diabetes or pre-diabetes.",
            "reference": "Normal fasting: 70–99 mg/dL | Pre-diabetes: 100–125 | Diabetes: ≥126"
        },
        "fr": {
            "explanation": "Taux de sucre dans le sang. Un glucose élevé peut indiquer un diabète ou un pré-diabète.",
            "reference": "Normal à jeun : 0.70–0.99 g/L | Pré-diabète : 1.00–1.25 | Diabète : ≥1.26"
        },
        "ar": {
            "explanation": "مستوى السكر في الدم. الغلوكوز المرتفع قد يشير إلى السكري أو مرحلة ما قبل السكري.",
            "reference": "طبيعي صائم: 70–99 ملغ/دل | قبل السكري: 100–125 | السكري: ≥126"
        }
    },
    "hba1c": {
        "en": {"explanation": "Average blood sugar over 3 months. Key measure for diabetes management.", "reference": "Normal: <5.7% | Pre-diabetes: 5.7–6.4% | Diabetes: ≥6.5%"},
        "fr": {"explanation": "Reflet de la glycémie moyenne sur 3 mois. Indicateur clé du diabète.", "reference": "Normal : <5,7% | Pré-diabète : 5,7–6,4% | Diabète : ≥6,5%"},
        "ar": {"explanation": "متوسط سكر الدم خلال 3 أشهر. مؤشر رئيسي لإدارة السكري.", "reference": "طبيعي: <5.7% | قبل السكري: 5.7–6.4% | السكري: ≥6.5%"}
    },
    "hemoglobin": {
        "en": {"explanation": "Protein in red blood cells that carries oxygen. Low levels indicate anemia.", "reference": "Normal (men): 13.5–17.5 g/dL | Normal (women): 12–15.5 g/dL"},
        "fr": {"explanation": "Protéine des globules rouges qui transporte l'oxygène. Un taux bas indique une anémie.", "reference": "Normal (homme) : 13,5–17,5 g/dL | Normal (femme) : 12–15,5 g/dL"},
        "ar": {"explanation": "بروتين في خلايا الدم الحمراء يحمل الأكسجين. انخفاضه يدل على فقر الدم.", "reference": "طبيعي (رجل): 13.5–17.5 غ/دل | طبيعي (امرأة): 12–15.5 غ/دل"}
    },
    "ferritin": {
        "en": {"explanation": "Protein that stores iron. Low ferritin is the earliest sign of iron deficiency.", "reference": "Normal (men): 24–336 ng/mL | Normal (women): 11–307 ng/mL | Low = iron deficiency"},
        "fr": {"explanation": "Protéine de stockage du fer. La ferritine basse est le premier signe de carence en fer.", "reference": "Normal (homme) : 24–336 ng/mL | Normal (femme) : 11–307 ng/mL"},
        "ar": {"explanation": "بروتين يخزن الحديد. انخفاض الفيريتين هو أول علامة على نقص الحديد.", "reference": "طبيعي (رجل): 24–336 نانوغرام/مل | طبيعي (امرأة): 11–307 نانوغرام/مل"}
    },
    "white blood cell": {
        "en": {"explanation": "Immune cells. Elevated count signals infection or inflammation.", "reference": "Normal: 4,500–11,000 cells/µL"},
        "fr": {"explanation": "Cellules immunitaires. Un taux élevé signale une infection ou une inflammation.", "reference": "Normal : 4 500–11 000 cellules/µL"},
        "ar": {"explanation": "خلايا المناعة. ارتفاعها يشير إلى عدوى أو التهاب.", "reference": "طبيعي: 4500–11000 خلية/ميكرولتر"}
    },
    "platelet": {
        "en": {"explanation": "Cells that help blood clot. Too low = bleeding risk, too high = clot risk.", "reference": "Normal: 150,000–400,000 per µL"},
        "fr": {"explanation": "Cellules qui aident à la coagulation. Trop basses = risque de saignement.", "reference": "Normal : 150 000–400 000/µL"},
        "ar": {"explanation": "خلايا تساعد في تخثر الدم. انخفاضها يزيد خطر النزيف.", "reference": "طبيعي: 150,000–400,000 لكل ميكرولتر"}
    },
    "neutrophil": {
        "en": {"explanation": "Most common white blood cell, first responder to bacterial infections.", "reference": "Normal: 1,800–7,700 cells/µL (40–70% of WBC)"},
        "fr": {"explanation": "Type de globule blanc le plus courant, premier à répondre aux infections bactériennes.", "reference": "Normal : 1 800–7 700 cellules/µL (40–70% des GB)"},
        "ar": {"explanation": "أكثر خلايا الدم البيضاء شيوعاً، أول استجابة للعدوى البكتيرية.", "reference": "طبيعي: 1800–7700 خلية/ميكرولتر (40–70% من كريات الدم البيضاء)"}
    },
    "lymphocyte": {
        "en": {"explanation": "White blood cells key to immune response. Low count may suggest viral illness.", "reference": "Normal: 1,000–4,800 cells/µL (20–40% of WBC)"},
        "fr": {"explanation": "Globules blancs essentiels à la réponse immunitaire. Un taux bas peut indiquer une infection virale.", "reference": "Normal : 1 000–4 800 cellules/µL (20–40% des GB)"},
        "ar": {"explanation": "خلايا دم بيضاء أساسية للمناعة. انخفاضها قد يشير لعدوى فيروسية.", "reference": "طبيعي: 1000–4800 خلية/ميكرولتر (20–40%)"}
    },
    "creatinine": {
        "en": {"explanation": "Waste filtered by kidneys. High levels suggest kidney dysfunction.", "reference": "Normal (men): 0.74–1.35 mg/dL | Normal (women): 0.59–1.04 mg/dL"},
        "fr": {"explanation": "Déchet filtré par les reins. Un taux élevé suggère un dysfonctionnement rénal.", "reference": "Normal (homme) : 7–12 mg/L | Normal (femme) : 5–10 mg/L"},
        "ar": {"explanation": "نفاية يرشحها الكلى. ارتفاعه يشير لخلل وظيفي كلوي.", "reference": "طبيعي (رجل): 0.74–1.35 ملغ/دل | طبيعي (امرأة): 0.59–1.04 ملغ/دل"}
    },
    "urea": {
        "en": {"explanation": "Nitrogen waste from protein metabolism, filtered by kidneys.", "reference": "Normal: 7–20 mg/dL (BUN) | High = kidney dysfunction or dehydration"},
        "fr": {"explanation": "Déchet azoté issu du métabolisme des protéines, éliminé par les reins.", "reference": "Normal : 0,15–0,45 g/L | Élevé = insuffisance rénale ou déshydratation"},
        "ar": {"explanation": "نفاية نيتروجينية من استقلاب البروتين، يرشحها الكلى.", "reference": "طبيعي: 7–20 ملغ/دل | مرتفع = خلل كلوي أو جفاف"}
    },
    "transaminase": {
        "en": {"explanation": "Liver enzymes (AST & ALT). Elevated levels indicate liver cell damage.", "reference": "ALT normal: 7–56 U/L | AST normal: 10–40 U/L"},
        "fr": {"explanation": "Enzymes hépatiques (ASAT & ALAT). Élevées = dommages aux cellules du foie.", "reference": "ALAT normal : 7–56 U/L | ASAT normal : 10–40 U/L"},
        "ar": {"explanation": "إنزيمات الكبد (AST وALT). ارتفاعها يدل على تلف خلايا الكبد.", "reference": "ALT طبيعي: 7–56 وحدة/ل | AST طبيعي: 10–40 وحدة/ل"}
    },
    "bilirubin": {
        "en": {"explanation": "Breakdown product of red blood cells. High levels cause jaundice.", "reference": "Normal total: 0.1–1.2 mg/dL"},
        "fr": {"explanation": "Produit de dégradation des globules rouges. Un taux élevé provoque la jaunisse.", "reference": "Normal total : 2–10 µmol/L"},
        "ar": {"explanation": "ناتج تكسر خلايا الدم الحمراء. ارتفاعه يسبب اليرقان.", "reference": "طبيعي: 0.1–1.2 ملغ/دل"}
    },
    "albumin": {
        "en": {"explanation": "Main blood protein from the liver. Low levels indicate malnutrition or liver/kidney disease.", "reference": "Normal: 3.5–5.0 g/dL"},
        "fr": {"explanation": "Principale protéine du sang produite par le foie. Faible = malnutrition ou maladie hépatique.", "reference": "Normal : 35–50 g/L"},
        "ar": {"explanation": "البروتين الرئيسي في الدم من الكبد. انخفاضه يشير لسوء التغذية أو مرض كبدي.", "reference": "طبيعي: 3.5–5.0 غ/دل"}
    },
    "protides": {
        "en": {"explanation": "Total blood proteins reflecting nutritional and liver/immune function.", "reference": "Normal total proteins: 6.0–8.3 g/dL"},
        "fr": {"explanation": "Protéines totales du sang, reflet de l'état nutritionnel et de la fonction hépatique.", "reference": "Normal : 60–83 g/L"},
        "ar": {"explanation": "مجموع بروتينات الدم، يعكس الحالة التغذوية ووظيفة الكبد.", "reference": "طبيعي: 6.0–8.3 غ/دل"}
    },
    "electrophorese de protides": {
        "en": {"explanation": "Separates blood proteins to detect myeloma, chronic disease.", "reference": "Albumin: 55–65% | Alpha1: 2–4% | Alpha2: 7–11% | Beta: 8–13% | Gamma: 11–21%"},
        "fr": {"explanation": "Sépare les protéines du sang pour détecter un myélome, une maladie chronique.", "reference": "Albumine : 55–65% | Alpha1 : 2–4% | Alpha2 : 7–11% | Bêta : 8–13% | Gamma : 11–21%"},
        "ar": {"explanation": "يفصل بروتينات الدم للكشف عن الميلوما والأمراض المزمنة.", "reference": "ألبومين: 55–65% | ألفا1: 2–4% | ألفا2: 7–11% | بيتا: 8–13% | غاما: 11–21%"}
    },
    "lipase": {
        "en": {"explanation": "Pancreatic enzyme. Markedly elevated in acute pancreatitis.", "reference": "Normal: 0–160 U/L | High (>3x) = acute pancreatitis"},
        "fr": {"explanation": "Enzyme pancréatique. Très élevée dans la pancréatite aiguë.", "reference": "Normal : 0–160 U/L | Élevée (>3x) = pancréatite aiguë"},
        "ar": {"explanation": "إنزيم البنكرياس. ارتفاعه الشديد يدل على التهاب البنكرياس الحاد.", "reference": "طبيعي: 0–160 وحدة/ل"}
    },
    "amylase": {
        "en": {"explanation": "Digestive enzyme from pancreas and salivary glands. Elevated in pancreatitis.", "reference": "Normal: 30–110 U/L"},
        "fr": {"explanation": "Enzyme digestive du pancréas et des glandes salivaires. Élevée dans la pancréatite.", "reference": "Normal : 30–110 U/L"},
        "ar": {"explanation": "إنزيم هضمي من البنكرياس والغدد اللعابية. ارتفاعه في التهاب البنكرياس.", "reference": "طبيعي: 30–110 وحدة/ل"}
    },
    "thyroid": {
        "en": {"explanation": "TSH measures thyroid stimulation. Low = hyperthyroidism, High = hypothyroidism.", "reference": "TSH normal: 0.4–4.0 mIU/L"},
        "fr": {"explanation": "La TSH mesure la stimulation thyroïdienne. Basse = hyperthyroïdie, Haute = hypothyroïdie.", "reference": "TSH normal : 0,4–4,0 mUI/L"},
        "ar": {"explanation": "TSH يقيس نشاط الغدة الدرقية. منخفض = فرط النشاط، مرتفع = قصور النشاط.", "reference": "TSH طبيعي: 0.4–4.0 mIU/L"}
    },
    "ft4": {
        "en": {"explanation": "Free Thyroxine — active thyroid hormone. Measured alongside TSH.", "reference": "Normal FT4: 0.8–1.8 ng/dL"},
        "fr": {"explanation": "Thyroxine libre — hormone thyroïdienne active. Mesurée avec la TSH.", "reference": "FT4 normal : 10–20 pmol/L"},
        "ar": {"explanation": "الثيروكسين الحر — الهرمون الدرقي النشط. يُقاس مع TSH.", "reference": "طبيعي: 0.8–1.8 نانوغرام/دل"}
    },
    "troponin": {
        "en": {"explanation": "Released when heart muscle is damaged. Key marker for heart attack.", "reference": "Normal: <0.04 ng/mL | Elevated = myocardial infarction"},
        "fr": {"explanation": "Libérée lors d'une lésion du muscle cardiaque. Marqueur clé de l'infarctus.", "reference": "Normal : <0,04 ng/mL | Élevée = infarctus du myocarde"},
        "ar": {"explanation": "يُطلق عند تلف عضلة القلب. مؤشر رئيسي لاحتشاء القلب.", "reference": "طبيعي: <0.04 نانوغرام/مل"}
    },
    "blood pressure": {
        "en": {"explanation": "Force of blood against artery walls. High pressure strains the heart.", "reference": "Normal: <120/80 mmHg | High: ≥130/80 | Crisis: ≥180/120"},
        "fr": {"explanation": "Pression du sang sur les parois artérielles. Élevée = surcharge cardiaque.", "reference": "Normal : <120/80 mmHg | Élevée : ≥130/80 | Crise : ≥180/120"},
        "ar": {"explanation": "قوة الدم على جدران الشرايين. ارتفاعه يُجهد القلب.", "reference": "طبيعي: <120/80 ملم زئبق | مرتفع: ≥130/80 | أزمة: ≥180/120"}
    },
    "crp": {
        "en": {"explanation": "C-Reactive Protein — inflammation marker. Rises rapidly during infection.", "reference": "Normal: <10 mg/L | High = active inflammation"},
        "fr": {"explanation": "Protéine C-Réactive — marqueur d'inflammation. Monte rapidement lors d'une infection.", "reference": "Normal : <10 mg/L | Élevée = inflammation active"},
        "ar": {"explanation": "بروتين سي التفاعلي — مؤشر الالتهاب. يرتفع سريعاً أثناء العدوى.", "reference": "طبيعي: <10 ملغ/ل"}
    },
    "esr": {
        "en": {"explanation": "Erythrocyte Sedimentation Rate — non-specific inflammation marker.", "reference": "Normal (men): <15 mm/h | Normal (women): <20 mm/h"},
        "fr": {"explanation": "Vitesse de Sédimentation — marqueur non spécifique d'inflammation.", "reference": "Normal (homme) : <15 mm/h | Normal (femme) : <20 mm/h"},
        "ar": {"explanation": "سرعة ترسب الدم — مؤشر التهاب غير نوعي.", "reference": "طبيعي (رجل): <15 مم/ساعة | طبيعي (امرأة): <20 مم/ساعة"}
    },
    "ace": {
        "en": {"explanation": "Angiotensin-Converting Enzyme. Elevated in sarcoidosis and lung diseases.", "reference": "Normal: 8–53 U/L"},
        "fr": {"explanation": "Enzyme de conversion de l'angiotensine. Élevée dans la sarcoïdose et maladies pulmonaires.", "reference": "Normal : 8–53 U/L"},
        "ar": {"explanation": "إنزيم محول للأنجيوتنسين. يرتفع في الساركويد وأمراض الرئة.", "reference": "طبيعي: 8–53 وحدة/ل"}
    },
    "aslo": {
        "en": {"explanation": "Anti-Streptolysin O — detects recent strep infection, used for rheumatic fever.", "reference": "Normal: <200 IU/mL | Elevated = recent Group A Strep infection"},
        "fr": {"explanation": "Antistreptolysine O — détecte une infection streptococcique récente, utilisée pour le rhumatisme articulaire.", "reference": "Normal : <200 UI/mL | Élevé = infection streptococcique récente"},
        "ar": {"explanation": "مضاد ستربتوليزين O — يكشف عدوى المكورات العقدية الحديثة، يُستخدم للحمى الروماتيزمية.", "reference": "طبيعي: <200 وحدة/مل"}
    },
    "facteur rhumatoide": {
        "en": {"explanation": "Rheumatoid Factor — antibody found in rheumatoid arthritis and autoimmune diseases.", "reference": "Normal: <14 IU/mL | Positive = rheumatoid arthritis, Sjögren's, lupus"},
        "fr": {"explanation": "Facteur Rhumatoïde — anticorps retrouvé dans la polyarthrite rhumatoïde et les maladies auto-immunes.", "reference": "Normal : <14 UI/mL | Positif = polyarthrite rhumatoïde, lupus"},
        "ar": {"explanation": "العامل الروماتويدي — جسم مضاد في التهاب المفاصل الروماتويدي وأمراض المناعة الذاتية.", "reference": "طبيعي: <14 وحدة/مل | إيجابي = التهاب مفاصل روماتويدي"}
    },
    "cholesterol": {
        "en": {"explanation": "Fatty substance in blood. High levels increase risk of heart disease.", "reference": "Total: <200 mg/dL | LDL: <100 | HDL: >60 (protective)"},
        "fr": {"explanation": "Substance grasse dans le sang. Un taux élevé augmente le risque de maladie cardiaque.", "reference": "Total : <2 g/L | LDL : <1 g/L | HDL : >0,6 g/L (protecteur)"},
        "ar": {"explanation": "مادة دهنية في الدم. ارتفاعها يزيد خطر أمراض القلب.", "reference": "الكلي: <200 ملغ/دل | LDL: <100 | HDL: >60 (وقائي)"}
    },
    "triglycerides": {
        "en": {"explanation": "Type of fat in blood. High levels linked to heart disease and pancreatitis.", "reference": "Normal: <150 mg/dL | High: 200–499 | Very high: ≥500"},
        "fr": {"explanation": "Type de graisse dans le sang. Taux élevé lié aux maladies cardiaques et à la pancréatite.", "reference": "Normal : <1,5 g/L | Élevé : 2–4,9 g/L | Très élevé : ≥5 g/L"},
        "ar": {"explanation": "نوع من الدهون في الدم. ارتفاعها مرتبط بأمراض القلب والتهاب البنكرياس.", "reference": "طبيعي: <150 ملغ/دل | مرتفع: 200–499 | مرتفع جداً: ≥500"}
    },
    "sodium": {
        "en": {"explanation": "Electrolyte regulating fluid balance. Abnormal levels affect brain function.", "reference": "Normal: 136–145 mEq/L"},
        "fr": {"explanation": "Électrolyte régulant l'équilibre hydrique. Niveaux anormaux affectent le cerveau.", "reference": "Normal : 136–145 mEq/L"},
        "ar": {"explanation": "إلكتروليت ينظم توازن السوائل. اضطرابه يؤثر على وظائف الدماغ.", "reference": "طبيعي: 136–145 ميق/ل"}
    },
    "potassium": {
        "en": {"explanation": "Electrolyte essential for heart and muscle function.", "reference": "Normal: 3.5–5.0 mEq/L | Low = hypokalemia | High = hyperkalemia"},
        "fr": {"explanation": "Électrolyte essentiel pour le cœur et les muscles.", "reference": "Normal : 3,5–5,0 mEq/L | Bas = hypokaliémie | Élevé = hyperkaliémie"},
        "ar": {"explanation": "إلكتروليت أساسي لوظيفة القلب والعضلات.", "reference": "طبيعي: 3.5–5.0 ميق/ل"}
    },
    "calcium": {
        "en": {"explanation": "Mineral essential for bones, nerves, and muscle contraction.", "reference": "Normal: 8.5–10.5 mg/dL | High = hypercalcemia (cancer, hyperparathyroidism)"},
        "fr": {"explanation": "Minéral essentiel pour les os, les nerfs et la contraction musculaire.", "reference": "Normal : 2,15–2,60 mmol/L | Élevé = hypercalcémie"},
        "ar": {"explanation": "معدن أساسي للعظام والأعصاب وانقباض العضلات.", "reference": "طبيعي: 8.5–10.5 ملغ/دل | مرتفع = فرط كالسيوم الدم"}
    },
    "magnesium": {
        "en": {"explanation": "Mineral involved in muscle, nerve, and heart function. Deficiency is common.", "reference": "Normal: 1.7–2.2 mg/dL"},
        "fr": {"explanation": "Minéral impliqué dans la fonction musculaire, nerveuse et cardiaque. La carence est fréquente.", "reference": "Normal : 0,75–1,05 mmol/L"},
        "ar": {"explanation": "معدن يشارك في وظائف العضلات والأعصاب والقلب. نقصه شائع.", "reference": "طبيعي: 1.7–2.2 ملغ/دل"}
    },
    "phosphore": {
        "en": {"explanation": "Mineral linked to calcium and bone health. Regulated by kidneys.", "reference": "Normal: 2.5–4.5 mg/dL | High = kidney disease"},
        "fr": {"explanation": "Minéral lié au calcium et à la santé osseuse. Régulé par les reins.", "reference": "Normal : 0,81–1,45 mmol/L | Élevé = maladie rénale"},
        "ar": {"explanation": "معدن مرتبط بالكالسيوم وصحة العظام. ينظمه الكلى.", "reference": "طبيعي: 2.5–4.5 ملغ/دل"}
    },
    "vitamin d": {
        "en": {"explanation": "Essential for calcium absorption and bone health. Deficiency is very common.", "reference": "Deficient: <20 ng/mL | Insufficient: 20–29 | Normal: 30–100"},
        "fr": {"explanation": "Essentielle à l'absorption du calcium et à la santé osseuse. La carence est très fréquente.", "reference": "Carence : <50 nmol/L | Insuffisance : 50–75 | Normal : >75 nmol/L"},
        "ar": {"explanation": "أساسية لامتصاص الكالسيوم وصحة العظام. نقصها شائع جداً.", "reference": "نقص: <20 نانوغرام/مل | غير كافٍ: 20–29 | طبيعي: 30–100"}
    },
    "inr": {
        "en": {"explanation": "Measures blood clotting time. Used to monitor anticoagulant therapy.", "reference": "Normal: 0.8–1.2 | Therapeutic: 2.0–3.0 | High = bleeding risk"},
        "fr": {"explanation": "Mesure le temps de coagulation. Utilisé pour surveiller les anticoagulants.", "reference": "Normal : 0,8–1,2 | Thérapeutique : 2,0–3,0 | Élevé = risque hémorragique"},
        "ar": {"explanation": "يقيس وقت تخثر الدم. يُستخدم لمراقبة علاج مضادات التخثر.", "reference": "طبيعي: 0.8–1.2 | علاجي: 2.0–3.0 | مرتفع = خطر نزيف"}
    },
    "psa": {
        "en": {"explanation": "Prostate-Specific Antigen. Elevated levels may indicate prostate cancer or benign enlargement.", "reference": "Normal: <4.0 ng/mL | >10 = high suspicion of cancer"},
        "fr": {"explanation": "Antigène Prostatique Spécifique. Élevé = possible cancer ou hyperplasie bénigne de la prostate.", "reference": "Normal : <4 ng/mL | >10 = forte suspicion de cancer"},
        "ar": {"explanation": "مستضد البروستاتا النوعي. ارتفاعه قد يشير لسرطان البروستاتا أو تضخمها الحميد.", "reference": "طبيعي: <4 نانوغرام/مل | >10 = اشتباه كبير بالسرطان"}
    },
    "afp": {
        "en": {"explanation": "Alpha-fetoprotein — tumor marker for liver cancer and germ cell tumors.", "reference": "Normal: <10 ng/mL | Elevated = liver cancer, testicular cancer"},
        "fr": {"explanation": "Alpha-fœtoprotéine — marqueur tumoral pour le cancer du foie et les tumeurs germinales.", "reference": "Normal : <10 ng/mL | Élevé = cancer du foie, cancer testiculaire"},
        "ar": {"explanation": "ألفا فيتوبروتين — مؤشر ورمي لسرطان الكبد والأورام الجرثومية.", "reference": "طبيعي: <10 نانوغرام/مل | مرتفع = سرطان الكبد أو الخصية"}
    },
    "ca199": {
        "en": {"explanation": "Tumor marker for pancreatic and biliary cancers.", "reference": "Normal: <37 U/mL | Elevated = pancreatic, bile duct cancer"},
        "fr": {"explanation": "Marqueur tumoral pour les cancers du pancréas et des voies biliaires.", "reference": "Normal : <37 U/mL | Élevé = cancer du pancréas ou des voies biliaires"},
        "ar": {"explanation": "مؤشر ورمي لسرطان البنكرياس والقنوات الصفراوية.", "reference": "طبيعي: <37 وحدة/مل"}
    },
    "ca153": {
        "en": {"explanation": "Tumor marker used to monitor breast cancer treatment.", "reference": "Normal: <31 U/mL | Elevated = breast cancer (monitoring, not diagnosis)"},
        "fr": {"explanation": "Marqueur tumoral pour la surveillance du cancer du sein.", "reference": "Normal : <31 U/mL | Élevé = cancer du sein (surveillance, pas diagnostic)"},
        "ar": {"explanation": "مؤشر ورمي لمتابعة علاج سرطان الثدي.", "reference": "طبيعي: <31 وحدة/مل | مرتفع = سرطان الثدي (متابعة)"}
    },
    "fsh": {
        "en": {"explanation": "Follicle-Stimulating Hormone. Assesses fertility and menopause.", "reference": "Men: 1.5–12.4 mIU/mL | Women (follicular): 3.5–12.5 | Menopause: >25.8"},
        "fr": {"explanation": "Hormone Folliculo-Stimulante. Évalue la fertilité et la ménopause.", "reference": "Homme : 1,5–12,4 mUI/mL | Femme (phase folliculaire) : 3,5–12,5 | Ménopause : >25,8"},
        "ar": {"explanation": "هرمون منبه الجريب. يقيّم الخصوبة وسن اليأس.", "reference": "رجل: 1.5–12.4 | امرأة (مرحلة جريبية): 3.5–12.5 | انقطاع الطمث: >25.8 mIU/mL"}
    },
    "lh": {
        "en": {"explanation": "Luteinizing Hormone. Triggers ovulation and testosterone production.", "reference": "Men: 1.7–8.6 mIU/mL | Women (follicular): 2.4–12.6 | Menopause: >11.3"},
        "fr": {"explanation": "Hormone Lutéinisante. Déclenche l'ovulation et la production de testostérone.", "reference": "Homme : 1,7–8,6 mUI/mL | Femme (phase folliculaire) : 2,4–12,6"},
        "ar": {"explanation": "الهرمون اللوتيني. يحفز الإباضة وإنتاج التستوستيرون.", "reference": "رجل: 1.7–8.6 | امرأة (مرحلة جريبية): 2.4–12.6 mIU/mL"}
    },
    "prolactine": {
        "en": {"explanation": "Hormone stimulating milk production. High levels can cause infertility.", "reference": "Normal (men): 2–18 ng/mL | Normal (women): 2–29 ng/mL"},
        "fr": {"explanation": "Hormone stimulant la production de lait. Élevée = hyperprolactinémie, infertilité possible.", "reference": "Normal (homme) : 2–18 ng/mL | Normal (femme) : 2–29 ng/mL"},
        "ar": {"explanation": "هرمون يحفز إنتاج الحليب. ارتفاعه قد يسبب العقم.", "reference": "طبيعي (رجل): 2–18 | طبيعي (امرأة): 2–29 نانوغرام/مل"}
    },
    "oestradiol": {
        "en": {"explanation": "Main female sex hormone. Evaluates ovarian function and menopause.", "reference": "Follicular phase: 20–150 pg/mL | Ovulation: 100–500 | Menopause: <20"},
        "fr": {"explanation": "Principal hormone sexuelle féminine. Évalue la fonction ovarienne et la ménopause.", "reference": "Phase folliculaire : 20–150 pg/mL | Ovulation : 100–500 | Ménopause : <20"},
        "ar": {"explanation": "الهرمون الجنسي الأنثوي الرئيسي. يقيّم وظيفة المبيض وانقطاع الطمث.", "reference": "مرحلة جريبية: 20–150 | إباضة: 100–500 | انقطاع الطمث: <20 بيكوغرام/مل"}
    },
    "testosterone": {
        "en": {"explanation": "Main male sex hormone. Low levels cause fatigue, low libido, muscle loss.", "reference": "Normal (men): 300–1000 ng/dL | Normal (women): 15–70 ng/dL"},
        "fr": {"explanation": "Principal hormone sexuelle masculine. Faible = fatigue, baisse de libido, perte musculaire.", "reference": "Normal (homme) : 3–10 ng/mL | Normal (femme) : 0,15–0,70 ng/mL"},
        "ar": {"explanation": "الهرمون الجنسي الذكوري الرئيسي. انخفاضه يسبب التعب وضعف الرغبة وضمور العضلات.", "reference": "طبيعي (رجل): 300–1000 | طبيعي (امرأة): 15–70 نانوغرام/دل"}
    },
    "helicobacter": {
        "en": {"explanation": "Helicobacter pylori — bacterium infecting the stomach, causing ulcers and gastritis.", "reference": "Result: Positive or Negative | Positive = eradication therapy required"},
        "fr": {"explanation": "Helicobacter pylori — bactérie infectant l'estomac, provoquant ulcères et gastrite.", "reference": "Résultat : Positif ou Négatif | Positif = traitement d'éradication nécessaire"},
        "ar": {"explanation": "هيليكوباكتر بيلوري — بكتيريا تصيب المعدة، تسبب القرحة والتهاب المعدة.", "reference": "النتيجة: إيجابي أو سلبي | إيجابي = علاج استئصال مطلوب"}
    },
    "wright": {
        "en": {"explanation": "Serological test for Brucellosis (from animals or unpasteurized dairy).", "reference": "Normal: Negative | Positive (≥1/80 titer) = brucellosis suspected"},
        "fr": {"explanation": "Test sérologique pour la brucellose (transmise par les animaux ou les produits laitiers non pasteurisés).", "reference": "Normal : Négatif | Positif (≥1/80) = brucellose suspectée"},
        "ar": {"explanation": "اختبار مصلي للداء البروسيلي (المنقول من الحيوانات أو الألبان غير المبسترة).", "reference": "طبيعي: سلبي | إيجابي (≥1/80): اشتباه بروسيلا"}
    },
    "widale": {
        "en": {"explanation": "Widal test — detects antibodies against Salmonella (typhoid fever).", "reference": "Normal: Negative | Positive (≥1/160) = typhoid fever suspected"},
        "fr": {"explanation": "Test de Widal — détecte les anticorps contre la Salmonella (fièvre typhoïde).", "reference": "Normal : Négatif | Positif (≥1/160) = fièvre typhoïde suspectée"},
        "ar": {"explanation": "اختبار ويدال — يكشف أجساماً مضادة ضد السالمونيلا (حمى التيفوئيد).", "reference": "طبيعي: سلبي | إيجابي (≥1/160): اشتباه حمى التيفوئيد"}
    },
    "iga": {
        "en": {"explanation": "Immunoglobulin A — antibody in mucous membranes (gut, respiratory tract).", "reference": "Normal: 70–400 mg/dL | Low = IgA deficiency | High = chronic infection"},
        "fr": {"explanation": "Immunoglobuline A — anticorps présent dans les muqueuses digestives et respiratoires.", "reference": "Normal : 0,7–4,0 g/L | Faible = déficit en IgA | Élevé = infection chronique"},
        "ar": {"explanation": "الغلوبولين المناعي A — جسم مضاد في الأغشية المخاطية للجهاز الهضمي والتنفسي.", "reference": "طبيعي: 70–400 ملغ/دل"}
    },
    "igg": {
        "en": {"explanation": "Most abundant antibody, provides long-term immunity.", "reference": "Normal: 700–1600 mg/dL | Low = immunodeficiency | High = chronic infection"},
        "fr": {"explanation": "Anticorps le plus abondant, assure l'immunité à long terme.", "reference": "Normal : 7–16 g/L | Faible = immunodéficience | Élevé = infection chronique"},
        "ar": {"explanation": "أكثر الأجسام المضادة وفرة، يوفر المناعة طويلة الأمد.", "reference": "طبيعي: 700–1600 ملغ/دل"}
    },
    "igm": {
        "en": {"explanation": "First antibody produced in response to infection.", "reference": "Normal: 40–230 mg/dL | High = recent/active infection"},
        "fr": {"explanation": "Premier anticorps produit lors d'une infection.", "reference": "Normal : 0,4–2,3 g/L | Élevé = infection récente ou active"},
        "ar": {"explanation": "أول جسم مضاد يُنتج عند الإصابة بعدوى.", "reference": "طبيعي: 40–230 ملغ/دل | مرتفع = عدوى حديثة"}
    },
    "electrophorese d hemoglobine": {
        "en": {"explanation": "Separates hemoglobin types to detect sickle cell disease and thalassemia.", "reference": "Normal adult: HbA >95% | HbA2: 2–3.5% | HbF: <2%"},
        "fr": {"explanation": "Sépare les types d'hémoglobine pour détecter la drépanocytose et la thalassémie.", "reference": "Adulte normal : HbA >95% | HbA2 : 2–3,5% | HbF : <2%"},
        "ar": {"explanation": "يفصل أنواع الهيموغلوبين للكشف عن الأنيميا المنجلية والثلاسيميا.", "reference": "طبيعي بالغ: HbA >95% | HbA2: 2–3.5% | HbF: <2%"}
    },
    "c3": {
        "en": {"explanation": "Complement C3 — immune protein. Low in autoimmune diseases like lupus.", "reference": "Normal: 90–180 mg/dL | Low = lupus, glomerulonephritis"},
        "fr": {"explanation": "Complément C3 — protéine immunitaire. Faible dans les maladies auto-immunes comme le lupus.", "reference": "Normal : 0,9–1,8 g/L | Faible = lupus, glomérulonéphrite"},
        "ar": {"explanation": "المتمم C3 — بروتين مناعي. ينخفض في أمراض المناعة الذاتية كالذئبة.", "reference": "طبيعي: 90–180 ملغ/دل"}
    },
    "c4": {
        "en": {"explanation": "Complement C4 — works with C3. Low in lupus and hereditary angioedema.", "reference": "Normal: 16–47 mg/dL"},
        "fr": {"explanation": "Complément C4 — agit avec le C3. Faible dans le lupus et l'angiœdème héréditaire.", "reference": "Normal : 0,16–0,47 g/L"},
        "ar": {"explanation": "المتمم C4 — يعمل مع C3. ينخفض في الذئبة والوذمة الوعائية الوراثية.", "reference": "طبيعي: 16–47 ملغ/دل"}
    },
    "phadiatop alimentaire": {
        "en": {"explanation": "Blood screening for food allergies (milk, egg, peanut, wheat, fish...).", "reference": "Result: Positive or Negative | Positive = specific IgE testing recommended"},
        "fr": {"explanation": "Dépistage sanguin des allergies alimentaires (lait, œuf, arachide, blé, poisson...).", "reference": "Résultat : Positif ou Négatif | Positif = panel IgE spécifique recommandé"},
        "ar": {"explanation": "فحص دم للكشف عن حساسية الطعام (حليب، بيض، فول سوداني، قمح، سمك...).", "reference": "النتيجة: إيجابي أو سلبي | إيجابي = يوصى بفحص IgE نوعي"}
    },
    "phadiatop respiratoire": {
        "en": {"explanation": "Blood screening for respiratory allergies (pollen, dust mites, animal dander, mold).", "reference": "Result: Positive or Negative | Positive = specific allergen panel recommended"},
        "fr": {"explanation": "Dépistage sanguin des allergies respiratoires (pollen, acariens, poils d'animaux, moisissures).", "reference": "Résultat : Positif ou Négatif | Positif = panel allergènes spécifiques recommandé"},
        "ar": {"explanation": "فحص دم للكشف عن حساسية الجهاز التنفسي (حبوب اللقاح، عث الغبار، وبر الحيوانات، العفن).", "reference": "النتيجة: إيجابي أو سلبي | إيجابي = يوصى بفحص مسببات الحساسية"}
    },
    "antigene soluble": {
        "en": {"explanation": "Detects specific antigens in blood or fluids for infection diagnosis.", "reference": "Result: Positive or Negative depending on targeted pathogen"},
        "fr": {"explanation": "Détecte des antigènes spécifiques dans le sang ou les liquides biologiques pour diagnostiquer une infection.", "reference": "Résultat : Positif ou Négatif selon le pathogène ciblé"},
        "ar": {"explanation": "يكشف مستضدات نوعية في الدم أو السوائل لتشخيص العدوى.", "reference": "النتيجة: إيجابي أو سلبي حسب الممرض المستهدف"}
    },
    "uric acid": {
        "en": {"explanation": "Waste from purine metabolism. High levels cause gout or kidney stones.", "reference": "Normal (men): 3.4–7.0 mg/dL | Normal (women): 2.4–6.0 mg/dL"},
        "fr": {"explanation": "Déchet du métabolisme des purines. Taux élevé = goutte ou calculs rénaux.", "reference": "Normal (homme) : 200–420 µmol/L | Normal (femme) : 140–360 µmol/L"},
        "ar": {"explanation": "نفاية من استقلاب البيورين. ارتفاعه يسبب النقرس أو حصى الكلى.", "reference": "طبيعي (رجل): 3.4–7.0 | طبيعي (امرأة): 2.4–6.0 ملغ/دل"}
    },
    "fever": {
        "en": {"explanation": "Elevated body temperature, sign of infection or inflammation.", "reference": "Normal: 36.1–37.2°C | Fever: ≥38°C | High fever: ≥39.5°C"},
        "fr": {"explanation": "Température corporelle élevée, signe d'infection ou d'inflammation.", "reference": "Normal : 36,1–37,2°C | Fièvre : ≥38°C | Fièvre élevée : ≥39,5°C"},
        "ar": {"explanation": "ارتفاع درجة حرارة الجسم، علامة على عدوى أو التهاب.", "reference": "طبيعي: 36.1–37.2°C | حمى: ≥38°C | حمى شديدة: ≥39.5°C"}
    },
    "infection": {
        "en": {"explanation": "Invasion of the body by harmful microorganisms.", "reference": "Diagnosed via symptoms, blood cultures, or imaging"},
        "fr": {"explanation": "Invasion du corps par des micro-organismes pathogènes.", "reference": "Diagnostiquée via symptômes, hémocultures ou imagerie"},
        "ar": {"explanation": "غزو الجسم بميكروبات ضارة.", "reference": "يُشخَّص بالأعراض وزرع الدم والتصوير"}
    },
    "oxygen saturation": {
        "en": {"explanation": "Percentage of hemoglobin carrying oxygen. Low = breathing problems.", "reference": "Normal: 95–100% | Concerning: <95% | Critical: <90%"},
        "fr": {"explanation": "Pourcentage d'hémoglobine transportant l'oxygène. Faible = problèmes respiratoires.", "reference": "Normal : 95–100% | Préoccupant : <95% | Critique : <90%"},
        "ar": {"explanation": "نسبة الهيموغلوبين الحامل للأكسجين. انخفاضه يدل على مشاكل تنفسية.", "reference": "طبيعي: 95–100% | مقلق: <95% | حرج: <90%"}
    },
}

# -----------------------------------------------
# Preprocessing
# -----------------------------------------------

def preprocess(text):
    text = text.lower()
    text = re.sub(r"[^a-z\s]", "", text)
    return re.sub(r"\s+", " ", text).strip()

def get_interpretations(text, lang):
    text_lower = text.lower()
    found = []
    for term, translations in MEDICAL_TERMS.items():
        if term in text_lower:
            info = translations.get(lang, translations["en"])
            found.append((term, info))
    return found

# -----------------------------------------------
# Load and train model
# -----------------------------------------------

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

# -----------------------------------------------
# UI
# -----------------------------------------------

st.set_page_config(page_title="Medical Text Analyzer", layout="centered")

with st.sidebar:
    lang = st.selectbox(T["en"]["sidebar_lang"], ["en", "fr", "ar"],
                        format_func=lambda x: {"en": "🇬🇧 English", "fr": "🇫🇷 Français", "ar": "🇸🇦 العربية"}[x])

tr = T[lang]

# RTL support for Arabic
if lang == "ar":
    st.markdown("""
    <style>
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
    st.caption(f"📚 {len(MEDICAL_TERMS)} {tr['sidebar_kb']}")

user_input = st.text_area(tr["input_label"], height=150, placeholder=tr["input_placeholder"])

if st.button(tr["button"]):
    if user_input.strip() == "":
        st.warning(tr["empty_warning"])
    else:
        clean_input = preprocess(user_input)
        input_vec = vectorizer.transform([clean_input])
        prediction = model.predict(input_vec)[0]
        proba = model.predict_proba(input_vec)[0]
        confidence = max(proba)

        if prediction == 1:
            st.error(f"{tr['result_abnormal']} {confidence:.0%}")
        else:
            st.success(f"{tr['result_normal']} {confidence:.0%}")

        st.subheader(tr["keywords_title"])
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
                if weight > 0:
                    st.write(f"🔴 **{word}** → {tr['word_abnormal']} ({weight:.3f})")
                else:
                    st.write(f"🟢 **{word}** → {tr['word_normal']} ({weight:.3f})")
        else:
            st.info(tr["no_keywords"])

        interpretations = get_interpretations(user_input, lang)
        if interpretations:
            st.subheader(tr["interp_title"])
            for term, info in interpretations:
                with st.expander(f"🔬 {term.title()}"):
                    st.markdown(f"{tr['what_means']} {info['explanation']}")
                    st.markdown(f"{tr['reference']} `{info['reference']}`")
        else:
            st.info(tr["no_interp"])

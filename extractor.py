import re

# -------------------------------------------------------
# Each range entry: (max_value, status_key, labels_dict)
# status_key: "low" | "normal" | "high"
# -------------------------------------------------------

PARAMETERS = [
    {
        "name": {"en": "Ferritin", "fr": "Ferritine", "ar": "الفيريتين"},
        "aliases": ["ferritin", "ferritine"],
        "unit": "ng/mL",
        "ranges": [
            (12,          "low",    {"en": "⚠️ Very low — severe iron deficiency", "fr": "⚠️ Très basse — carence en fer sévère", "ar": "⚠️ منخفض جداً — نقص حديد شديد"}),
            (30,          "low",    {"en": "🔶 Low — iron deficiency likely", "fr": "🔶 Basse — carence en fer probable", "ar": "🔶 منخفض — نقص الحديد محتمل"}),
            (200,         "normal", {"en": "✅ Normal", "fr": "✅ Normale", "ar": "✅ طبيعي"}),
            (float("inf"),"high",   {"en": "⚠️ Elevated — possible inflammation or hemochromatosis", "fr": "⚠️ Élevée — inflammation ou hémochromatose possible", "ar": "⚠️ مرتفع — احتمال التهاب أو ترسب الأصبغة"}),
        ],
        "advice": {
            "low":  {"en": "Consider iron supplementation. Check transferrin saturation and CBC. Possible causes: poor diet, chronic bleeding, malabsorption.", "fr": "Envisager une supplémentation en fer. Vérifier la saturation en transferrine et la NFS. Causes : alimentation pauvre en fer, saignement chronique, malabsorption.", "ar": "فكر في مكملات الحديد. تحقق من تشبع الترانسفيرين وصورة الدم الكاملة."},
            "high": {"en": "High ferritin may indicate inflammation, liver disease or hemochromatosis. Repeat fasting. Correlate with CRP.", "fr": "Ferritine élevée = inflammation, maladie du foie ou hémochromatose possible. Refaire à jeun. Corréler avec la CRP.", "ar": "ارتفاع الفيريتين قد يدل على التهاب أو مرض كبدي. أعد الفحص صائماً وقارنه بـ CRP."}
        },
        "reference": {"en": "Normal: 12–200 ng/mL (women), 30–300 ng/mL (men)", "fr": "Normal : 12–200 ng/mL (femme), 30–300 ng/mL (homme)", "ar": "طبيعي: 12–200 (امرأة)، 30–300 (رجل) نانوغرام/مل"}
    },
    {
        "name": {"en": "Hemoglobin", "fr": "Hémoglobine", "ar": "الهيموغلوبين"},
        "aliases": ["hemoglobin", "hémoglobine", "haemoglobin"],
        "unit": "g/dL",
        "ranges": [
            (7,           "low",    {"en": "🔴 Critically low — severe anemia, transfusion may be needed", "fr": "🔴 Critique — anémie sévère, transfusion possible", "ar": "🔴 منخفض بشكل خطير — فقر دم شديد"}),
            (10,          "low",    {"en": "⚠️ Low — moderate anemia", "fr": "⚠️ Basse — anémie modérée", "ar": "⚠️ منخفض — فقر دم متوسط"}),
            (12,          "low",    {"en": "🔶 Borderline — mild anemia (women threshold)", "fr": "🔶 Légèrement basse — anémie légère (seuil femme)", "ar": "🔶 منخفض قليلاً — فقر دم خفيف"}),
            (17.5,        "normal", {"en": "✅ Normal", "fr": "✅ Normal", "ar": "✅ طبيعي"}),
            (float("inf"),"high",   {"en": "⚠️ Elevated — possible dehydration or polycythemia", "fr": "⚠️ Élevée — déshydratation ou polyglobulie possible", "ar": "⚠️ مرتفع — احتمال جفاف أو كثرة الكريات الحمراء"}),
        ],
        "advice": {
            "low":  {"en": "Check ferritin, B12, folate to identify cause. If <8 g/dL: urgent medical evaluation needed.", "fr": "Vérifier ferritine, B12, folate. Si <8 g/dL : évaluation médicale urgente.", "ar": "تحقق من الفيريتين وB12 وحمض الفوليك. إذا كان <8: تقييم طبي عاجل."},
            "high": {"en": "Evaluate hydration. If persistent, check for polycythemia vera (JAK2 mutation).", "fr": "Évaluer l'hydratation. Si persistant, rechercher une polyglobulie de Vaquez.", "ar": "تقييم حالة الترطيب. إذا استمر، تحقق من كثرة الحمر الحقيقية."}
        },
        "reference": {"en": "Normal: 12–15.5 g/dL (women), 13.5–17.5 g/dL (men)", "fr": "Normal : 12–15,5 g/dL (femme), 13,5–17,5 g/dL (homme)", "ar": "طبيعي: 12–15.5 (امرأة)، 13.5–17.5 (رجل) غ/دل"}
    },
    {
        "name": {"en": "Glucose (fasting)", "fr": "Glycémie (à jeun)", "ar": "سكر الدم (صائم)"},
        "aliases": ["glucose", "glycémie", "glycemie", "blood sugar", "fasting glucose"],
        "unit": "mg/dL",
        "ranges": [
            (60,          "low",    {"en": "🔴 Critically low — hypoglycemia, emergency", "fr": "🔴 Critique — hypoglycémie, urgence", "ar": "🔴 منخفض جداً — نقص سكر حاد، طارئ"}),
            (99,          "normal", {"en": "✅ Normal fasting glucose", "fr": "✅ Glycémie à jeun normale", "ar": "✅ سكر الدم الصائم طبيعي"}),
            (125,         "high",   {"en": "🔶 Pre-diabetic range", "fr": "🔶 Zone pré-diabétique", "ar": "🔶 نطاق ما قبل السكري"}),
            (float("inf"),"high",   {"en": "⚠️ Diabetic range — high fasting glucose", "fr": "⚠️ Zone diabétique — glycémie à jeun élevée", "ar": "⚠️ نطاق السكري — سكر الصيام مرتفع"}),
        ],
        "advice": {
            "low":  {"en": "Immediate glucose intake needed. Investigate cause: medication, prolonged fasting, insulinoma.", "fr": "Apport immédiat de glucose nécessaire. Investiguer : médicament, jeûne trop long, insulinome.", "ar": "يلزم تناول الجلوكوز فوراً. ابحث عن السبب: دواء، صيام طويل."},
            "high": {"en": "Confirm with HbA1c. Verify fasting duration (min 8h). If confirmed: lifestyle changes + medical follow-up.", "fr": "Confirmer avec HbA1c. Vérifier durée du jeûne (min 8h). Si confirmé : mode de vie + suivi médical.", "ar": "أكّد بـ HbA1c. تحقق من مدة الصيام (8 ساعات). إذا تأكد: تغيير نمط الحياة + متابعة طبية."}
        },
        "reference": {"en": "Normal fasting: 70–99 mg/dL | Pre-diabetes: 100–125 | Diabetes: ≥126", "fr": "Normal à jeun : 0,70–0,99 g/L | Pré-diabète : 1,00–1,25 | Diabète : ≥1,26", "ar": "طبيعي صائم: 70–99 ملغ/دل | قبل السكري: 100–125 | السكري: ≥126"}
    },
    {
        "name": {"en": "HbA1c", "fr": "HbA1c (hémoglobine glyquée)", "ar": "HbA1c"},
        "aliases": ["hba1c", "hemoglobin a1c", "hémoglobine glyquée", "glycated hemoglobin", "a1c"],
        "unit": "%",
        "ranges": [
            (5.7,         "normal", {"en": "✅ Normal — no diabetes risk", "fr": "✅ Normal — pas de risque diabétique", "ar": "✅ طبيعي — لا خطر سكري"}),
            (6.4,         "high",   {"en": "🔶 Pre-diabetic", "fr": "🔶 Pré-diabétique", "ar": "🔶 ما قبل السكري"}),
            (float("inf"),"high",   {"en": "⚠️ Diabetic range — medical follow-up required", "fr": "⚠️ Zone diabétique — suivi médical nécessaire", "ar": "⚠️ نطاق السكري — المتابعة الطبية ضرورية"}),
        ],
        "advice": {
            "high": {"en": "HbA1c reflects average blood sugar over 3 months. If ≥6.5%: diabetes confirmed. Consult endocrinologist.", "fr": "L'HbA1c reflète la glycémie sur 3 mois. Si ≥6,5% : diabète confirmé. Consulter un endocrinologue.", "ar": "HbA1c يعكس متوسط السكر على 3 أشهر. إذا ≥6.5%: السكري مؤكد. استشر طبيب الغدد."}
        },
        "reference": {"en": "Normal: <5.7% | Pre-diabetes: 5.7–6.4% | Diabetes: ≥6.5%", "fr": "Normal : <5,7% | Pré-diabète : 5,7–6,4% | Diabète : ≥6,5%", "ar": "طبيعي: <5.7% | قبل السكري: 5.7–6.4% | السكري: ≥6.5%"}
    },
    {
        "name": {"en": "CRP (Inflammation)", "fr": "CRP (Inflammation)", "ar": "CRP (الالتهاب)"},
        "aliases": ["crp", "c-reactive protein", "protéine c réactive", "proteine c reactive"],
        "unit": "mg/L",
        "ranges": [
            (10,          "normal", {"en": "✅ Normal — no significant inflammation", "fr": "✅ Normale — pas d'inflammation significative", "ar": "✅ طبيعي — لا التهاب ملحوظ"}),
            (40,          "high",   {"en": "🔶 Mildly elevated — possible mild infection", "fr": "🔶 Légèrement élevée — infection légère possible", "ar": "🔶 مرتفع قليلاً — احتمال عدوى خفيفة"}),
            (float("inf"),"high",   {"en": "⚠️ Significantly elevated — active infection or autoimmune flare", "fr": "⚠️ Très élevée — infection active ou poussée auto-immune", "ar": "⚠️ مرتفع بشكل ملحوظ — عدوى نشطة أو انتكاسة مناعية"}),
        ],
        "advice": {
            "high": {"en": "Identify source of inflammation. Complete with CBC, ESR. If infectious cause suspected: blood cultures.", "fr": "Identifier la source. Compléter avec NFS, VS. Si cause infectieuse : hémocultures.", "ar": "حدد مصدر الالتهاب. أكمل بصورة دم وسرعة الترسب. إذا اشتُبه بعدوى: مزارع دم."}
        },
        "reference": {"en": "Normal: <10 mg/L | Mild: 10–40 | Active infection: >40", "fr": "Normal : <10 mg/L | Légère : 10–40 | Infection active : >40", "ar": "طبيعي: <10 | خفيف: 10–40 | عدوى نشطة: >40 ملغ/ل"}
    },
    {
        "name": {"en": "TSH (Thyroid)", "fr": "TSH (Thyroïde)", "ar": "TSH (الغدة الدرقية)"},
        "aliases": ["tsh", "thyroid stimulating hormone"],
        "unit": "mIU/L",
        "ranges": [
            (0.4,         "low",    {"en": "⚠️ Low — possible hyperthyroidism", "fr": "⚠️ Basse — possible hyperthyroïdie", "ar": "⚠️ منخفض — احتمال فرط نشاط الغدة الدرقية"}),
            (4.0,         "normal", {"en": "✅ Normal thyroid function", "fr": "✅ Fonction thyroïdienne normale", "ar": "✅ وظيفة الغدة الدرقية طبيعية"}),
            (float("inf"),"high",   {"en": "⚠️ Elevated — possible hypothyroidism", "fr": "⚠️ Élevée — possible hypothyroïdie", "ar": "⚠️ مرتفع — احتمال قصور الغدة الدرقية"}),
        ],
        "advice": {
            "low":  {"en": "Low TSH = possible hyperthyroidism. Measure FT4 and FT3. Symptoms: rapid heartbeat, weight loss, tremors.", "fr": "TSH basse = possible hyperthyroïdie. Mesurer FT4 et FT3. Symptômes : tachycardie, perte de poids.", "ar": "TSH منخفض = احتمال فرط نشاط الدرقية. قس FT4 وFT3."},
            "high": {"en": "High TSH = possible hypothyroidism. Measure FT4. Symptoms: fatigue, weight gain, cold intolerance.", "fr": "TSH élevée = possible hypothyroïdie. Mesurer FT4. Symptômes : fatigue, prise de poids.", "ar": "TSH مرتفع = احتمال قصور الدرقية. قس FT4. الأعراض: إرهاق، زيادة الوزن."}
        },
        "reference": {"en": "Normal: 0.4–4.0 mIU/L | Low = hyperthyroidism | High = hypothyroidism", "fr": "Normal : 0,4–4,0 mUI/L | Bas = hyperthyroïdie | Élevé = hypothyroïdie", "ar": "طبيعي: 0.4–4.0 | منخفض = فرط نشاط | مرتفع = قصور"}
    },
    {
        "name": {"en": "Creatinine", "fr": "Créatinine", "ar": "الكرياتينين"},
        "aliases": ["creatinine", "créatinine", "creatinine"],
        "unit": "mg/dL",
        "ranges": [
            (0.5,         "low",    {"en": "🔶 Low — possible muscle loss", "fr": "🔶 Basse — perte musculaire possible", "ar": "🔶 منخفض — فقدان عضلي محتمل"}),
            (1.35,        "normal", {"en": "✅ Normal", "fr": "✅ Normal", "ar": "✅ طبيعي"}),
            (float("inf"),"high",   {"en": "⚠️ Elevated — possible kidney dysfunction", "fr": "⚠️ Élevée — possible insuffisance rénale", "ar": "⚠️ مرتفع — احتمال خلل كلوي"}),
        ],
        "advice": {
            "high": {"en": "Calculate eGFR. Check urea and urinalysis. Possible causes: dehydration, kidney disease. Repeat after hydration.", "fr": "Calculer le DFGe. Vérifier urée et analyse urinaire. Causes : déshydratation, maladie rénale.", "ar": "احسب معدل الترشيح الكبيبي. تحقق من اليوريا وتحليل البول."}
        },
        "reference": {"en": "Normal (men): 0.74–1.35 mg/dL | Normal (women): 0.59–1.04 mg/dL", "fr": "Normal (homme) : 7–12 mg/L | Normal (femme) : 5–10 mg/L", "ar": "طبيعي (رجل): 0.74–1.35 | طبيعي (امرأة): 0.59–1.04 ملغ/دل"}
    },
    {
        "name": {"en": "Triglycerides", "fr": "Triglycérides", "ar": "الدهون الثلاثية"},
        "aliases": ["triglycerides", "triglycérides", "triglyceride"],
        "unit": "mg/dL",
        "ranges": [
            (150,         "normal", {"en": "✅ Normal", "fr": "✅ Normal", "ar": "✅ طبيعي"}),
            (199,         "high",   {"en": "🔶 Borderline high", "fr": "🔶 Légèrement élevés", "ar": "🔶 مرتفع قليلاً"}),
            (499,         "high",   {"en": "⚠️ High — increased cardiovascular risk", "fr": "⚠️ Élevés — risque cardiovasculaire accru", "ar": "⚠️ مرتفع — زيادة الخطر القلبي الوعائي"}),
            (float("inf"),"high",   {"en": "🔴 Very high — risk of pancreatitis", "fr": "🔴 Très élevés — risque de pancréatite", "ar": "🔴 مرتفع جداً — خطر التهاب البنكرياس"}),
        ],
        "advice": {
            "high": {"en": "Reduce sugar, refined carbs, alcohol. Increase omega-3. If >500: urgent medical evaluation to prevent pancreatitis.", "fr": "Réduire sucres, glucides raffinés, alcool. Augmenter les oméga-3. Si >500 : évaluation médicale urgente.", "ar": "قلل السكر والكربوهيدرات المكررة والكحول. زد أوميغا-3. إذا >500: تقييم طبي عاجل."}
        },
        "reference": {"en": "Normal: <150 mg/dL | Borderline: 150–199 | High: 200–499 | Very high: ≥500", "fr": "Normal : <1,5 g/L | Limite : 1,5–1,99 | Élevé : 2–4,99 | Très élevé : ≥5", "ar": "طبيعي: <150 | حدي: 150–199 | مرتفع: 200–499 | مرتفع جداً: ≥500 ملغ/دل"}
    },
    {
        "name": {"en": "Cholesterol (total)", "fr": "Cholestérol total", "ar": "الكوليسترول الكلي"},
        "aliases": ["cholesterol", "cholestérol", "total cholesterol"],
        "unit": "mg/dL",
        "ranges": [
            (200,         "normal", {"en": "✅ Normal — desirable", "fr": "✅ Normal — souhaitable", "ar": "✅ طبيعي — مرغوب"}),
            (239,         "high",   {"en": "🔶 Borderline high", "fr": "🔶 Légèrement élevé", "ar": "🔶 مرتفع قليلاً"}),
            (float("inf"),"high",   {"en": "⚠️ High — increased cardiovascular risk", "fr": "⚠️ Élevé — risque cardiovasculaire accru", "ar": "⚠️ مرتفع — زيادة خطر أمراض القلب"}),
        ],
        "advice": {
            "high": {"en": "Check LDL and HDL fractions. Dietary changes: reduce saturated fats. Consider statin therapy if cardiovascular risk is high.", "fr": "Vérifier les fractions LDL et HDL. Alimentation : réduire les graisses saturées. Envisager une statine si risque cardiovasculaire élevé.", "ar": "تحقق من LDL وHDL. قلل الدهون المشبعة في الغذاء. فكر في العلاج بالستاتين إذا كان الخطر القلبي مرتفعاً."}
        },
        "reference": {"en": "Normal: <200 mg/dL | Borderline: 200–239 | High: ≥240", "fr": "Normal : <2 g/L | Limite : 2–2,39 | Élevé : ≥2,4", "ar": "طبيعي: <200 | حدي: 200–239 | مرتفع: ≥240 ملغ/دل"}
    },
    {
        "name": {"en": "Platelets", "fr": "Plaquettes", "ar": "الصفائح الدموية"},
        "aliases": ["platelet", "platelets", "plaquettes", "thrombocytes"],
        "unit": "×10³/µL",
        "ranges": [
            (50,          "low",    {"en": "🔴 Critically low — severe bleeding risk", "fr": "🔴 Critique — risque hémorragique sévère", "ar": "🔴 منخفض بشكل خطير — خطر نزيف شديد"}),
            (150,         "low",    {"en": "⚠️ Low — thrombocytopenia", "fr": "⚠️ Basses — thrombocytopénie", "ar": "⚠️ منخفض — قلة الصفيحات"}),
            (400,         "normal", {"en": "✅ Normal", "fr": "✅ Normales", "ar": "✅ طبيعي"}),
            (float("inf"),"high",   {"en": "⚠️ High — thrombocytosis, possible clot risk", "fr": "⚠️ Élevées — thrombocytose, risque de caillot", "ar": "⚠️ مرتفع — كثرة الصفيحات، خطر تجلط"}),
        ],
        "advice": {
            "low":  {"en": "Identify cause: infection, autoimmune, medication. If <50: risk of spontaneous bleeding, urgent evaluation.", "fr": "Identifier la cause : infection, auto-immune, médicament. Si <50 : risque de saignement spontané, évaluation urgente.", "ar": "حدد السبب: عدوى، مناعة ذاتية، دواء. إذا <50: خطر نزيف تلقائي، تقييم عاجل."},
            "high": {"en": "If >1000: essential thrombocythemia possible. Consult hematologist.", "fr": "Si >1000 : thrombocytémie essentielle possible. Consulter un hématologue.", "ar": "إذا >1000: كثرة الصفيحات الأساسية محتملة. استشر طبيب الدم."}
        },
        "reference": {"en": "Normal: 150–400 ×10³/µL | Low = thrombocytopenia | High = thrombocytosis", "fr": "Normal : 150–400 G/L | Bas = thrombocytopénie | Élevé = thrombocytose", "ar": "طبيعي: 150–400 × 10³/ميكرولتر"}
    },
    {
        "name": {"en": "Vitamin D", "fr": "Vitamine D", "ar": "فيتامين D"},
        "aliases": ["vitamin d", "vitamine d", "25-hydroxyvitamin", "25 oh vitamine d", "vit d"],
        "unit": "ng/mL",
        "ranges": [
            (20,          "low",    {"en": "⚠️ Deficient — vitamin D deficiency", "fr": "⚠️ Carence en vitamine D", "ar": "⚠️ نقص — عوز فيتامين D"}),
            (30,          "low",    {"en": "🔶 Insufficient — suboptimal level", "fr": "🔶 Insuffisant — niveau sous-optimal", "ar": "🔶 غير كافٍ — مستوى دون الأمثل"}),
            (100,         "normal", {"en": "✅ Normal", "fr": "✅ Normal", "ar": "✅ طبيعي"}),
            (float("inf"),"high",   {"en": "⚠️ Toxic level — hypervitaminosis D", "fr": "⚠️ Niveau toxique — hypervitaminose D", "ar": "⚠️ مستوى سام — فرط فيتامين D"}),
        ],
        "advice": {
            "low":  {"en": "Supplement with vitamin D3 (1000–4000 IU/day). Increase sun exposure. Recheck after 3 months.", "fr": "Supplémenter en vitamine D3 (1000–4000 UI/j). Augmenter l'exposition solaire. Recontrôler après 3 mois.", "ar": "تناول مكملات فيتامين D3 (1000–4000 وحدة/يوم). زد التعرض للشمس. أعد الفحص بعد 3 أشهر."},
            "high": {"en": "Stop supplementation. Risk of hypercalcemia. Check calcium levels urgently.", "fr": "Arrêter la supplémentation. Risque d'hypercalcémie. Vérifier le calcium en urgence.", "ar": "أوقف المكملات. خطر ارتفاع الكالسيوم. تحقق من مستوى الكالسيوم بشكل عاجل."}
        },
        "reference": {"en": "Deficient: <20 ng/mL | Insufficient: 20–29 | Normal: 30–100 | Toxic: >100", "fr": "Carence : <50 nmol/L | Insuffisance : 50–75 | Normal : >75 nmol/L", "ar": "نقص: <20 | غير كافٍ: 20–29 | طبيعي: 30–100 | سام: >100 نانوغرام/مل"}
    },
    {
        "name": {"en": "INR (Coagulation)", "fr": "INR (Coagulation)", "ar": "INR (التخثر)"},
        "aliases": ["inr", "international normalized ratio"],
        "unit": "",
        "ranges": [
            (0.8,         "low",    {"en": "🔶 Low — possible hypercoagulability", "fr": "🔶 Bas — possible hypercoagulabilité", "ar": "🔶 منخفض — احتمال فرط التخثر"}),
            (1.2,         "normal", {"en": "✅ Normal coagulation", "fr": "✅ Coagulation normale", "ar": "✅ تخثر طبيعي"}),
            (3.0,         "high",   {"en": "🔶 Elevated — in therapeutic range (anticoagulants)", "fr": "🔶 Élevé — dans la plage thérapeutique (anticoagulants)", "ar": "🔶 مرتفع — ضمن النطاق العلاجي (مضادات التخثر)"}),
            (float("inf"),"high",   {"en": "⚠️ Very high — increased bleeding risk", "fr": "⚠️ Très élevé — risque hémorragique accru", "ar": "⚠️ مرتفع جداً — خطر نزيف متزايد"}),
        ],
        "advice": {
            "high": {"en": "If on anticoagulants (warfarin): dose adjustment needed. If not: investigate liver function and vitamin K.", "fr": "Si sous anticoagulants (warfarine) : ajustement de dose nécessaire. Sinon : explorer la fonction hépatique et la vitamine K.", "ar": "إذا كنت على مضادات التخثر: يلزم تعديل الجرعة. وإلا: افحص وظائف الكبد وفيتامين K."}
        },
        "reference": {"en": "Normal: 0.8–1.2 | Therapeutic (anticoagulants): 2.0–3.0 | High = bleeding risk", "fr": "Normal : 0,8–1,2 | Thérapeutique : 2,0–3,0 | Élevé = risque hémorragique", "ar": "طبيعي: 0.8–1.2 | علاجي: 2.0–3.0 | مرتفع = خطر نزيف"}
    },
    {
        "name": {"en": "Urea", "fr": "Urée", "ar": "اليوريا"},
        "aliases": ["urea", "urée", "bun", "blood urea nitrogen"],
        "unit": "mg/dL",
        "ranges": [
            (7,           "low",    {"en": "🔶 Low — possible malnutrition or low protein intake", "fr": "🔶 Basse — malnutrition ou faible apport protéique", "ar": "🔶 منخفض — سوء التغذية أو نقص البروتين"}),
            (20,          "normal", {"en": "✅ Normal", "fr": "✅ Normale", "ar": "✅ طبيعي"}),
            (float("inf"),"high",   {"en": "⚠️ Elevated — possible kidney dysfunction or dehydration", "fr": "⚠️ Élevée — insuffisance rénale ou déshydratation possible", "ar": "⚠️ مرتفع — احتمال خلل كلوي أو جفاف"}),
        ],
        "advice": {
            "high": {"en": "Correlate with creatinine and eGFR. Check hydration status. High protein diet can also elevate urea.", "fr": "Corréler avec créatinine et DFGe. Vérifier l'hydratation. Une alimentation riche en protéines peut aussi élever l'urée.", "ar": "قارن مع الكرياتينين ومعدل الترشيح. تحقق من حالة الترطيب. النظام الغني بالبروتين قد يرفع اليوريا."}
        },
        "reference": {"en": "Normal: 7–20 mg/dL (BUN) | High = kidney dysfunction or dehydration", "fr": "Normal : 0,15–0,45 g/L | Élevée = insuffisance rénale ou déshydratation", "ar": "طبيعي: 7–20 ملغ/دل | مرتفع = خلل كلوي أو جفاف"}
    },
    {
        "name": {"en": "Sodium", "fr": "Sodium (Natrémie)", "ar": "الصوديوم"},
        "aliases": ["sodium", "natrémie", "natremie", "na+"],
        "unit": "mEq/L",
        "ranges": [
            (135,         "low",    {"en": "⚠️ Low — hyponatremia", "fr": "⚠️ Bas — hyponatrémie", "ar": "⚠️ منخفض — نقص صوديوم الدم"}),
            (145,         "normal", {"en": "✅ Normal", "fr": "✅ Normal", "ar": "✅ طبيعي"}),
            (float("inf"),"high",   {"en": "⚠️ High — hypernatremia, dehydration", "fr": "⚠️ Élevé — hypernatrémie, déshydratation", "ar": "⚠️ مرتفع — فرط صوديوم الدم، جفاف"}),
        ],
        "advice": {
            "low":  {"en": "Causes: excessive water intake, heart failure, SIADH. Severe hyponatremia (<120) is a medical emergency.", "fr": "Causes : apport excessif en eau, insuffisance cardiaque, SIADH. Hyponatrémie sévère (<120) : urgence médicale.", "ar": "الأسباب: زيادة الماء، قصور القلب، SIADH. نقص شديد (<120): طارئ طبي."},
            "high": {"en": "Usually dehydration. Increase water intake. If severe: medical management of fluid replacement.", "fr": "Généralement déshydratation. Augmenter l'apport en eau. Si sévère : rééquilibration hydroélectrolytique médicale.", "ar": "عادةً جفاف. زد تناول الماء. إذا كان شديداً: معالجة طبية لتعويض السوائل."}
        },
        "reference": {"en": "Normal: 136–145 mEq/L | Low = hyponatremia | High = hypernatremia", "fr": "Normal : 136–145 mEq/L | Bas = hyponatrémie | Élevé = hypernatrémie", "ar": "طبيعي: 136–145 ميق/ل"}
    },
    {
        "name": {"en": "Potassium", "fr": "Potassium (Kaliémie)", "ar": "البوتاسيوم"},
        "aliases": ["potassium", "kaliémie", "kalémie", "k+"],
        "unit": "mEq/L",
        "ranges": [
            (3.5,         "low",    {"en": "⚠️ Low — hypokalemia, cardiac risk", "fr": "⚠️ Bas — hypokaliémie, risque cardiaque", "ar": "⚠️ منخفض — نقص بوتاسيوم، خطر قلبي"}),
            (5.0,         "normal", {"en": "✅ Normal", "fr": "✅ Normal", "ar": "✅ طبيعي"}),
            (float("inf"),"high",   {"en": "⚠️ High — hyperkalemia, cardiac arrhythmia risk", "fr": "⚠️ Élevé — hyperkaliémie, risque d'arythmie cardiaque", "ar": "⚠️ مرتفع — فرط بوتاسيوم، خطر اضطراب نظم القلب"}),
        ],
        "advice": {
            "low":  {"en": "Causes: diuretics, vomiting, diarrhea. If <3.0: cardiac monitoring needed. Supplement under medical supervision.", "fr": "Causes : diurétiques, vomissements, diarrhée. Si <3,0 : surveillance cardiaque. Supplémentation sous contrôle médical.", "ar": "الأسباب: مدرات البول، التقيؤ، الإسهال. إذا <3.0: مراقبة قلبية ضرورية."},
            "high": {"en": "Causes: kidney failure, medication (ACE inhibitors, spironolactone). If >6.0: medical emergency — cardiac arrest risk.", "fr": "Causes : insuffisance rénale, médicaments (IEC, spironolactone). Si >6,0 : urgence médicale — risque d'arrêt cardiaque.", "ar": "الأسباب: فشل كلوي، أدوية. إذا >6.0: طارئ طبي — خطر توقف القلب."}
        },
        "reference": {"en": "Normal: 3.5–5.0 mEq/L | Low = hypokalemia | High = hyperkalemia", "fr": "Normal : 3,5–5,0 mEq/L | Bas = hypokaliémie | Élevé = hyperkaliémie", "ar": "طبيعي: 3.5–5.0 ميق/ل"}
    },
]


# Unit conversion table: alias -> factor to multiply to get base unit
UNIT_CONVERSIONS = {
    "glucose":    {"g/l": 100, "mmol/l": 18.0, "mg/dl": 1},
    "glycémie":   {"g/l": 100, "mmol/l": 18.0, "mg/dl": 1},
    "glycemie":   {"g/l": 100, "mmol/l": 18.0, "mg/dl": 1},
    "cholesterol": {"g/l": 100, "mmol/l": 38.67, "mg/dl": 1},
    "cholestérol": {"g/l": 100, "mmol/l": 38.67, "mg/dl": 1},
    "triglycerides": {"g/l": 100, "mmol/l": 88.57, "mg/dl": 1},
    "triglycérides": {"g/l": 100, "mmol/l": 88.57, "mg/dl": 1},
    "creatinine":  {"umol/l": 0.0113, "mg/dl": 1},
    "créatinine":  {"umol/l": 0.0113, "mg/dl": 1},
    "urea":        {"mmol/l": 2.8, "mg/dl": 1},
    "urée":        {"mmol/l": 2.8, "mg/dl": 1},
}

def convert_value(value: float, unit_found: str, alias: str) -> float:
    """Convert value to base unit (mg/dL) if needed."""
    if not unit_found:
        return value
    unit_lower = unit_found.lower().replace(" ", "")
    conversions = UNIT_CONVERSIONS.get(alias.strip(), {})
    factor = conversions.get(unit_lower, 1)
    return round(value * factor, 2)

def extract_value(text: str, aliases: list) -> tuple:
    """
    Returns (value, operator) where operator is None, '<', or '>'
    Handles: 'ferritin 50', 'ferritin < 10', 'glucose 1.05 g/L', 'glucose 7.2 mmol/L'
    """
    text_lower = " " + text.lower() + " "
    unit_pattern = r"(?:ng/ml|g/dl|mg/dl|mmol/l|g/l|umol/l|%|miu/l|u/l|mg/l|meq/l|x10|/ul)?"
    for alias in aliases:
        alias = alias.strip()
        patterns = [
            (rf"(?<!\w){re.escape(alias)}[\s:=\-]*(<\s*)([0-9]+\.?[0-9]*)\s*{unit_pattern}", "<"),
            (rf"(?<!\w){re.escape(alias)}[\s:=\-]*(>\s*)([0-9]+\.?[0-9]*)\s*{unit_pattern}", ">"),
            (rf"(?<!\w){re.escape(alias)}[\s:=\-]*([0-9]+\.?[0-9]*)\s*({unit_pattern})", None),
            (rf"([0-9]+\.?[0-9]*)\s*({unit_pattern})\s*{re.escape(alias)}(?!\w)", None),
        ]
        for pattern, op in patterns:
            match = re.search(pattern, text_lower)
            if match:
                try:
                    if op:
                        val = float(match.group(2))
                        return val, op
                    else:
                        val = float(match.group(1))
                        unit_found = match.group(2) if len(match.groups()) > 1 else ""
                        val = convert_value(val, unit_found, alias)
                        return val, None
                except (ValueError, IndexError):
                    continue
    return None, None


def interpret_value(value: float, operator: str, ranges: list, lang: str) -> tuple:
    """
    Returns (status_label, status_key)
    Handles < and > operators: '<10' means value is below 10
    """
    # If operator is '<', value is below threshold — interpret as lower bound
    if operator == "<":
        threshold, status_key, labels = ranges[0]
        return labels.get(lang, labels["en"]), status_key
    # If operator is '>', value is above threshold — interpret as upper extreme
    if operator == ">":
        threshold, status_key, labels = ranges[-1]
        return labels.get(lang, labels["en"]), status_key

    for threshold, status_key, labels in ranges:
        if value <= threshold:
            return labels.get(lang, labels["en"]), status_key
    last = ranges[-1]
    return last[2].get(lang, last[2]["en"]), last[1]


def analyze_text(text: str, lang: str) -> list:
    results = []
    for param in PARAMETERS:
        value, operator = extract_value(text, param["aliases"])
        if value is not None:
            status_label, status_key = interpret_value(value, operator, param["ranges"], lang)
            advice = ""
            if status_key in param.get("advice", {}):
                advice = param["advice"][status_key].get(lang, param["advice"][status_key]["en"])
            results.append({
                "name": param["name"].get(lang, param["name"]["en"]),
                "value": value,
                "operator": operator,
                "unit": param["unit"],
                "status": status_label,
                "status_key": status_key,
                "advice": advice,
                "reference": param["reference"].get(lang, param["reference"]["en"]),
            })
    return results

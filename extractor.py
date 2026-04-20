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
    # --- Hormones sexuelles ---
    {
        "name": {"en": "FSH", "fr": "FSH (Hormone folliculo-stimulante)", "ar": "FSH (الهرمون المنشط للجريب)"},
        "aliases": ["fsh", "follicle stimulating hormone", "hormone folliculo-stimulante"],
        "unit": "mIU/mL",
        "ranges": [
            (1.5,         "low",    {"en": "🔶 Low — possible pituitary or hypothalamic dysfunction", "fr": "🔶 Basse — possible dysfonction hypophysaire", "ar": "🔶 منخفض — احتمال خلل في الغدة النخامية"}),
            (12.5,        "normal", {"en": "✅ Normal (follicular phase)", "fr": "✅ Normal (phase folliculaire)", "ar": "✅ طبيعي (المرحلة الجريبية)"}),
            (25.8,        "high",   {"en": "🔶 Elevated — possible premature ovarian insufficiency", "fr": "🔶 Élevée — possible insuffisance ovarienne prématurée", "ar": "🔶 مرتفع — احتمال قصور المبيض المبكر"}),
            (float("inf"),"high",   {"en": "⚠️ Very high — menopause or ovarian failure", "fr": "⚠️ Très élevée — ménopause ou insuffisance ovarienne", "ar": "⚠️ مرتفع جداً — انقطاع الطمث أو فشل المبيض"}),
        ],
        "advice": {
            "low":  {"en": "Low FSH may indicate pituitary dysfunction. Measure LH and prolactin. Check for stress or low BMI.", "fr": "FSH basse peut indiquer une dysfonction hypophysaire. Mesurer LH et prolactine.", "ar": "FSH المنخفض قد يشير لخلل في الغدة النخامية. قس LH والبرولاكتين."},
            "high": {"en": "High FSH suggests decreased ovarian reserve. Correlate with AMH and estradiol. Consult gynecologist.", "fr": "FSH élevée suggère une réserve ovarienne diminuée. Corréler avec AMH et estradiol. Consulter un gynécologue.", "ar": "ارتفاع FSH يشير لانخفاض الاحتياطي المبيضي. قارن مع AMH والإستراديول. استشر طبيب النساء."}
        },
        "reference": {"en": "Normal: 1.5–12.5 mIU/mL (follicular) | Menopause: >25.8", "fr": "Normal : 1,5–12,5 mUI/mL (phase folliculaire) | Ménopause : >25,8", "ar": "طبيعي: 1.5–12.5 mIU/mL (جريبية) | انقطاع الطمث: >25.8"}
    },
    {
        "name": {"en": "LH", "fr": "LH (Hormone lutéinisante)", "ar": "LH (الهرمون اللوتيني)"},
        "aliases": ["lh", "luteinizing hormone", "hormone lutéinisante"],
        "unit": "mIU/mL",
        "ranges": [
            (1.7,         "low",    {"en": "🔶 Low — possible pituitary dysfunction", "fr": "🔶 Bas — possible dysfonction hypophysaire", "ar": "🔶 منخفض — احتمال خلل نخامي"}),
            (12.6,        "normal", {"en": "✅ Normal (follicular phase)", "fr": "✅ Normal (phase folliculaire)", "ar": "✅ طبيعي (المرحلة الجريبية)"}),
            (float("inf"),"high",   {"en": "⚠️ Elevated — possible PCOS or menopause", "fr": "⚠️ Élevée — possible SOPK ou ménopause", "ar": "⚠️ مرتفع — احتمال تكيس المبايض أو انقطاع الطمث"}),
        ],
        "advice": {
            "high": {"en": "High LH with high FSH suggests menopause. High LH with normal FSH: consider PCOS. Measure testosterone and estradiol.", "fr": "LH élevée avec FSH élevée = ménopause. LH élevée avec FSH normale : envisager SOPK. Mesurer testostérone et estradiol.", "ar": "ارتفاع LH مع FSH = انقطاع طمث. ارتفاع LH مع FSH طبيعية: فكر في تكيس المبايض."}
        },
        "reference": {"en": "Normal (men): 1.7–8.6 | Women (follicular): 2.4–12.6 | Menopause: >11.3 mIU/mL", "fr": "Normal (homme) : 1,7–8,6 | Femme (folliculaire) : 2,4–12,6 | Ménopause : >11,3", "ar": "طبيعي (رجل): 1.7–8.6 | امرأة (جريبية): 2.4–12.6 | انقطاع طمث: >11.3 mIU/mL"}
    },
    {
        "name": {"en": "Prolactin", "fr": "Prolactine", "ar": "البرولاكتين"},
        "aliases": ["prolactin", "prolactine", "prl"],
        "unit": "ng/mL",
        "ranges": [
            (2,           "low",    {"en": "🔶 Low — rarely clinically significant", "fr": "🔶 Basse — rarement significatif cliniquement", "ar": "🔶 منخفض — نادراً ذو أهمية سريرية"}),
            (25,          "normal", {"en": "✅ Normal (non-pregnant)", "fr": "✅ Normal (hors grossesse)", "ar": "✅ طبيعي (خارج الحمل)"}),
            (100,         "high",   {"en": "⚠️ Elevated — possible stress, medication or microadenoma", "fr": "⚠️ Élevée — stress, médicament ou microadénome possible", "ar": "⚠️ مرتفع — احتمال ضغط نفسي أو دواء أو ورم صغير"}),
            (float("inf"),"high",   {"en": "🔴 Very high — probable prolactinoma", "fr": "🔴 Très élevée — prolactinome probable", "ar": "🔴 مرتفع جداً — ورم البرولاكتين المحتمل"}),
        ],
        "advice": {
            "high": {"en": "Elevated prolactin can cause infertility and galactorrhea. Rule out: hypothyroidism, antipsychotics, stress. If >100: MRI pituitary recommended.", "fr": "Prolactine élevée peut causer infertilité et galactorrhée. Éliminer : hypothyroïdie, antipsychotiques, stress. Si >100 : IRM hypophysaire recommandée.", "ar": "ارتفاع البرولاكتين قد يسبب العقم وإفراز الحليب. استبعد: قصور الدرقية، مضادات الذهان، الضغط النفسي. إذا >100: MRI للغدة النخامية موصى به."}
        },
        "reference": {"en": "Normal (men): 2–18 ng/mL | Women: 2–29 ng/mL | Pregnancy: up to 300", "fr": "Normal (homme) : 2–18 ng/mL | Femme : 2–29 ng/mL | Grossesse : jusqu'à 300", "ar": "طبيعي (رجل): 2–18 | امرأة: 2–29 نانوغرام/مل | حمل: حتى 300"}
    },
    {
        "name": {"en": "Testosterone", "fr": "Testostérone", "ar": "التستوستيرون"},
        "aliases": ["testosterone", "testostérone", "testerone"],
        "unit": "ng/dL",
        "ranges": [
            (300,         "low",    {"en": "⚠️ Low — hypogonadism in men", "fr": "⚠️ Basse — hypogonadisme chez l'homme", "ar": "⚠️ منخفض — قصور الغدد التناسلية عند الرجال"}),
            (1000,        "normal", {"en": "✅ Normal (men)", "fr": "✅ Normal (homme)", "ar": "✅ طبيعي (رجل)"}),
            (float("inf"),"high",   {"en": "⚠️ Elevated — possible PCOS (women) or doping", "fr": "⚠️ Élevée — possible SOPK (femme) ou dopage", "ar": "⚠️ مرتفع — احتمال تكيس المبايض (امرأة) أو منشطات"}),
        ],
        "advice": {
            "low":  {"en": "Low testosterone causes fatigue, low libido, muscle loss. Measure LH and FSH to determine cause. Consider testosterone replacement therapy.", "fr": "Testostérone basse cause fatigue, baisse de libido, perte musculaire. Mesurer LH et FSH pour identifier la cause.", "ar": "انخفاض التستوستيرون يسبب الإرهاق وضعف الرغبة وضمور العضلات. قس LH وFSH لتحديد السبب."},
            "high": {"en": "In women, high testosterone suggests PCOS or adrenal tumor. Measure DHEA-S and 17-OH progesterone.", "fr": "Chez la femme, testostérone élevée suggère SOPK ou tumeur surrénalienne. Mesurer DHEA-S et 17-OH progestérone.", "ar": "عند المرأة، ارتفاع التستوستيرون يشير لتكيس المبايض أو ورم الكظر."}
        },
        "reference": {"en": "Normal (men): 300–1000 ng/dL | Women: 15–70 ng/dL", "fr": "Normal (homme) : 3–10 ng/mL | Femme : 0,15–0,70 ng/mL", "ar": "طبيعي (رجل): 300–1000 | امرأة: 15–70 نانوغرام/دل"}
    },
    {
        "name": {"en": "Progesterone", "fr": "Progestérone", "ar": "البروجستيرون"},
        "aliases": ["progesterone", "progestérone"],
        "unit": "ng/mL",
        "ranges": [
            (1,           "low",    {"en": "🔶 Low — follicular phase or anovulation", "fr": "🔶 Basse — phase folliculaire ou anovulation", "ar": "🔶 منخفض — مرحلة جريبية أو عدم الإباضة"}),
            (25,          "normal", {"en": "✅ Normal (luteal phase)", "fr": "✅ Normal (phase lutéale)", "ar": "✅ طبيعي (المرحلة الأصفرية)"}),
            (float("inf"),"high",   {"en": "⚠️ Elevated — possible pregnancy or luteal cyst", "fr": "⚠️ Élevée — grossesse possible ou kyste lutéal", "ar": "⚠️ مرتفع — احتمال حمل أو كيس أصفري"}),
        ],
        "advice": {
            "low": {"en": "Low progesterone in luteal phase suggests anovulation or luteal phase defect. May cause infertility or early miscarriage. Correlate with cycle day.", "fr": "Progestérone basse en phase lutéale suggère anovulation ou insuffisance lutéale. Peut causer infertilité ou fausse couche précoce.", "ar": "انخفاض البروجستيرون في المرحلة الأصفرية يشير لعدم الإباضة. قد يسبب العقم أو الإجهاض المبكر."}
        },
        "reference": {"en": "Follicular: 0.1–0.9 ng/mL | Luteal: 2–25 ng/mL | Pregnancy: 10–44 (1st trimester)", "fr": "Folliculaire : 0,1–0,9 ng/mL | Lutéale : 2–25 ng/mL | Grossesse : 10–44", "ar": "جريبية: 0.1–0.9 | أصفرية: 2–25 | حمل: 10–44 نانوغرام/مل"}
    },
    {
        "name": {"en": "Estradiol (E2)", "fr": "Œstradiol (E2)", "ar": "الإستراديول (E2)"},
        "aliases": ["estradiol", "oestradiol", "oestradiole", "e2"],
        "unit": "pg/mL",
        "ranges": [
            (20,          "low",    {"en": "⚠️ Low — possible menopause or ovarian failure", "fr": "⚠️ Bas — possible ménopause ou insuffisance ovarienne", "ar": "⚠️ منخفض — احتمال انقطاع الطمث أو قصور المبيض"}),
            (150,         "normal", {"en": "✅ Normal (follicular phase)", "fr": "✅ Normal (phase folliculaire)", "ar": "✅ طبيعي (المرحلة الجريبية)"}),
            (500,         "normal", {"en": "✅ Normal (ovulation peak)", "fr": "✅ Normal (pic d'ovulation)", "ar": "✅ طبيعي (ذروة الإباضة)"}),
            (float("inf"),"high",   {"en": "⚠️ Elevated — possible ovarian cyst or estrogen therapy", "fr": "⚠️ Élevé — kyste ovarien ou traitement aux œstrogènes", "ar": "⚠️ مرتفع — احتمال كيس مبيضي أو علاج بالإستروجين"}),
        ],
        "advice": {
            "low":  {"en": "Low estradiol indicates decreased ovarian function. Common in menopause, anorexia, or excessive exercise. Measure FSH to confirm.", "fr": "Estradiol bas indique une fonction ovarienne diminuée. Commun à la ménopause, anorexie, ou exercice excessif.", "ar": "انخفاض الإستراديول يدل على ضعف وظيفة المبيض. شائع في انقطاع الطمث والأنوريكسيا."},
            "high": {"en": "High estradiol may indicate ovarian cyst, obesity, or estrogen therapy. Measure progesterone and FSH.", "fr": "Estradiol élevé peut indiquer kyste ovarien, obésité ou traitement hormonal.", "ar": "ارتفاع الإستراديول قد يشير لكيس مبيضي أو سمنة أو علاج هرموني."}
        },
        "reference": {"en": "Follicular: 20–150 pg/mL | Ovulation: 100–500 | Menopause: <20", "fr": "Folliculaire : 20–150 pg/mL | Ovulation : 100–500 | Ménopause : <20", "ar": "جريبية: 20–150 | إباضة: 100–500 | انقطاع طمث: <20 بيكوغرام/مل"}
    },
    # --- Bilan hépatique ---
    {
        "name": {"en": "GGT (Gamma-GT)", "fr": "GGT (Gamma-GT)", "ar": "GGT (غاما غلوتاميل ترانسفيراز)"},
        "aliases": ["ggt", "gamma gt", "gamma-gt", "gamma glutamyl"],
        "unit": "U/L",
        "ranges": [
            (55,          "normal", {"en": "✅ Normal", "fr": "✅ Normal", "ar": "✅ طبيعي"}),
            (200,         "high",   {"en": "🔶 Mildly elevated — possible alcohol use or liver stress", "fr": "🔶 Légèrement élevée — consommation d'alcool ou stress hépatique", "ar": "🔶 مرتفع قليلاً — احتمال تناول الكحول أو إجهاد الكبد"}),
            (float("inf"),"high",   {"en": "⚠️ Significantly elevated — liver disease or chronic alcohol use", "fr": "⚠️ Très élevée — maladie hépatique ou alcoolisme chronique", "ar": "⚠️ مرتفع بشكل ملحوظ — مرض كبدي أو إدمان الكحول"}),
        ],
        "advice": {
            "high": {"en": "GGT is sensitive to alcohol and liver disease. Correlate with ALT, AST and clinical history. Abstain from alcohol for 4 weeks and recheck.", "fr": "La GGT est sensible à l'alcool et aux maladies hépatiques. Corréler avec ALAT, ASAT et l'histoire clinique. Abstinence d'alcool 4 semaines puis recontrôle.", "ar": "GGT حساس للكحول وأمراض الكبد. قارن مع ALT وAST والتاريخ السريري. الامتناع عن الكحول 4 أسابيع وإعادة الفحص."}
        },
        "reference": {"en": "Normal: <55 U/L (men), <38 U/L (women) | Elevated = alcohol, liver, bile duct", "fr": "Normal : <55 U/L (homme), <38 U/L (femme) | Élevé = alcool, foie, voies biliaires", "ar": "طبيعي: <55 وحدة/ل (رجل)، <38 (امرأة) | مرتفع = كحول، كبد، قنوات صفراوية"}
    },
    {
        "name": {"en": "AST (SGOT)", "fr": "ASAT (SGOT)", "ar": "AST (ناقلة أمين الأسبارتات)"},
        "aliases": ["ast", "sgot", "asat", "aspartate aminotransferase"],
        "unit": "U/L",
        "ranges": [
            (40,          "normal", {"en": "✅ Normal", "fr": "✅ Normal", "ar": "✅ طبيعي"}),
            (120,         "high",   {"en": "🔶 Mildly elevated — possible liver or muscle damage", "fr": "🔶 Légèrement élevée — possible atteinte hépatique ou musculaire", "ar": "🔶 مرتفع قليلاً — احتمال تلف كبدي أو عضلي"}),
            (float("inf"),"high",   {"en": "⚠️ Significantly elevated — acute liver damage, heart attack or myopathy", "fr": "⚠️ Très élevée — atteinte hépatique aiguë, infarctus ou myopathie", "ar": "⚠️ مرتفع بشكل ملحوظ — تلف كبدي حاد أو احتشاء قلبي أو اعتلال عضلي"}),
        ],
        "advice": {
            "high": {"en": "AST elevated in liver, heart and muscle disease. Correlate with ALT: if AST/ALT >2 consider alcoholic hepatitis. If very high: rule out myocardial infarction.", "fr": "ASAT élevée dans maladies du foie, cœur et muscles. Corréler avec ALAT : si ASAT/ALAT >2 envisager hépatite alcoolique.", "ar": "AST يرتفع في أمراض الكبد والقلب والعضلات. قارن مع ALT: إذا كانت AST/ALT >2 فكر في التهاب الكبد الكحولي."}
        },
        "reference": {"en": "Normal: 10–40 U/L | Elevated = liver disease, myocardial infarction, muscle damage", "fr": "Normal : 10–40 U/L | Élevée = maladie hépatique, infarctus, lésion musculaire", "ar": "طبيعي: 10–40 وحدة/ل | مرتفع = مرض كبدي أو احتشاء قلبي أو تلف عضلي"}
    },
    {
        "name": {"en": "ALT (SGPT)", "fr": "ALAT (SGPT)", "ar": "ALT (ناقلة أمين الألانين)"},
        "aliases": ["alt", "sgpt", "alat", "alanine aminotransferase"],
        "unit": "U/L",
        "ranges": [
            (56,          "normal", {"en": "✅ Normal", "fr": "✅ Normal", "ar": "✅ طبيعي"}),
            (200,         "high",   {"en": "🔶 Mildly elevated — liver inflammation or fatty liver", "fr": "🔶 Légèrement élevée — inflammation hépatique ou stéatose", "ar": "🔶 مرتفع قليلاً — التهاب كبدي أو كبد دهني"}),
            (float("inf"),"high",   {"en": "⚠️ Significantly elevated — acute hepatitis or drug-induced liver injury", "fr": "⚠️ Très élevée — hépatite aiguë ou hépatotoxicité médicamenteuse", "ar": "⚠️ مرتفع بشكل ملحوظ — التهاب كبد حاد أو سُمية دوائية كبدية"}),
        ],
        "advice": {
            "high": {"en": "ALT is the most specific marker for liver damage. Causes: viral hepatitis, fatty liver, medications, alcohol. Repeat after 4 weeks avoiding hepatotoxic drugs.", "fr": "L'ALAT est le marqueur le plus spécifique des lésions hépatiques. Causes : hépatite virale, stéatose, médicaments, alcool.", "ar": "ALT هو المؤشر الأكثر خصوصية لتلف الكبد. الأسباب: التهاب كبد فيروسي، كبد دهني، أدوية، كحول."}
        },
        "reference": {"en": "Normal: 7–56 U/L | Elevated = hepatitis, fatty liver, medication toxicity", "fr": "Normal : 7–56 U/L | Élevée = hépatite, stéatose, toxicité médicamenteuse", "ar": "طبيعي: 7–56 وحدة/ل | مرتفع = التهاب كبد، كبد دهني، سُمية دوائية"}
    },
    {
        "name": {"en": "Total Bilirubin", "fr": "Bilirubine totale", "ar": "البيليروبين الكلي"},
        "aliases": ["bilirubin", "bilirubine", "biliribin", "total bilirubin", "bilirubine totale"],
        "unit": "mg/dL",
        "ranges": [
            (1.2,         "normal", {"en": "✅ Normal", "fr": "✅ Normal", "ar": "✅ طبيعي"}),
            (3.0,         "high",   {"en": "🔶 Mildly elevated — possible Gilbert syndrome or mild hemolysis", "fr": "🔶 Légèrement élevée — possible syndrome de Gilbert ou hémolyse légère", "ar": "🔶 مرتفع قليلاً — احتمال متلازمة جيلبرت أو انحلال دم خفيف"}),
            (float("inf"),"high",   {"en": "⚠️ Elevated — jaundice, liver disease or significant hemolysis", "fr": "⚠️ Élevée — jaunisse, maladie hépatique ou hémolyse significative", "ar": "⚠️ مرتفع — يرقان أو مرض كبدي أو انحلال دم ملحوظ"}),
        ],
        "advice": {
            "high": {"en": "Elevated bilirubin causes jaundice (yellow skin/eyes). Differentiate: if direct (conjugated) high = liver/bile duct issue. If indirect high = hemolysis. Check liver function tests.", "fr": "La bilirubine élevée cause la jaunisse. Différencier : si directe élevée = problème hépatique/biliaire. Si indirecte élevée = hémolyse.", "ar": "ارتفاع البيليروبين يسبب اليرقان (اصفرار الجلد/العينين). فرّق: إذا ارتفع المباشر = مشكلة كبدية. إذا ارتفع غير المباشر = انحلال دم."}
        },
        "reference": {"en": "Normal total: 0.1–1.2 mg/dL | Jaundice visible: >3 mg/dL", "fr": "Normal total : 2–17 µmol/L | Jaunisse visible : >50 µmol/L", "ar": "طبيعي الكلي: 0.1–1.2 ملغ/دل | اليرقان مرئي: >3 ملغ/دل"}
    },
    {
        "name": {"en": "Direct Bilirubin", "fr": "Bilirubine directe (conjuguée)", "ar": "البيليروبين المباشر (المتقارن)"},
        "aliases": ["direct bilirubin", "bilirubine directe", "bilirubin direct", "biliribin direct", "conjugated bilirubin"],
        "unit": "mg/dL",
        "ranges": [
            (0.3,         "normal", {"en": "✅ Normal", "fr": "✅ Normal", "ar": "✅ طبيعي"}),
            (float("inf"),"high",   {"en": "⚠️ Elevated — liver disease, bile duct obstruction or cholestasis", "fr": "⚠️ Élevée — maladie hépatique, obstruction biliaire ou cholestase", "ar": "⚠️ مرتفع — مرض كبدي أو انسداد القناة الصفراوية أو ركود صفراوي"}),
        ],
        "advice": {
            "high": {"en": "Elevated direct bilirubin indicates liver or bile duct problem. Check GGT, alkaline phosphatase, ALT. Abdominal ultrasound recommended.", "fr": "Bilirubine directe élevée indique un problème hépatique ou biliaire. Vérifier GGT, phosphatases alcalines, ALAT. Échographie abdominale recommandée.", "ar": "ارتفاع البيليروبين المباشر يدل على مشكلة كبدية أو في القنوات الصفراوية. تحقق من GGT وALT. الإيكوغرافيا البطنية موصى بها."}
        },
        "reference": {"en": "Normal: 0–0.3 mg/dL | Elevated = cholestasis, hepatitis, bile duct obstruction", "fr": "Normal : 0–5 µmol/L | Élevée = cholestase, hépatite, obstruction biliaire", "ar": "طبيعي: 0–0.3 ملغ/دل | مرتفع = ركود صفراوي أو التهاب كبد أو انسداد"}
    },
    # --- Enzymes pancréatiques ---
    {
        "name": {"en": "Lipase", "fr": "Lipase", "ar": "الليباز"},
        "aliases": ["lipase"],
        "unit": "U/L",
        "ranges": [
            (160,         "normal", {"en": "✅ Normal", "fr": "✅ Normal", "ar": "✅ طبيعي"}),
            (480,         "high",   {"en": "🔶 Mildly elevated (1–3x) — possible pancreatic inflammation", "fr": "🔶 Légèrement élevée (1–3x) — possible inflammation pancréatique", "ar": "🔶 مرتفع قليلاً (1–3 أضعاف) — احتمال التهاب بنكرياسي"}),
            (float("inf"),"high",   {"en": "⚠️ Significantly elevated (>3x) — acute pancreatitis", "fr": "⚠️ Très élevée (>3x) — pancréatite aiguë", "ar": "⚠️ مرتفع بشكل ملحوظ (>3 أضعاف) — التهاب البنكرياس الحاد"}),
        ],
        "advice": {
            "high": {"en": "Lipase >3x upper limit strongly suggests acute pancreatitis. Causes: alcohol, gallstones, hypertriglyceridemia. Urgent evaluation if >480 U/L with abdominal pain.", "fr": "Lipase >3x la limite supérieure suggère fortement une pancréatite aiguë. Causes : alcool, calculs biliaires, hypertriglycéridémie. Évaluation urgente si >480 avec douleur abdominale.", "ar": "الليباز >3 أضعاف الحد الأعلى يشير بقوة لالتهاب البنكرياس الحاد. الأسباب: كحول، حصى مرارة، ارتفاع الدهون الثلاثية. تقييم عاجل إذا >480 مع ألم بطني."}
        },
        "reference": {"en": "Normal: 0–160 U/L | Mild elevation: 160–480 | Acute pancreatitis: >480", "fr": "Normal : 0–160 U/L | Élévation légère : 160–480 | Pancréatite aiguë : >480", "ar": "طبيعي: 0–160 | ارتفاع خفيف: 160–480 | التهاب بنكرياس حاد: >480 وحدة/ل"}
    },
    {
        "name": {"en": "Amylase", "fr": "Amylase", "ar": "الأميلاز"},
        "aliases": ["amylase"],
        "unit": "U/L",
        "ranges": [
            (110,         "normal", {"en": "✅ Normal", "fr": "✅ Normal", "ar": "✅ طبيعي"}),
            (330,         "high",   {"en": "🔶 Mildly elevated — possible pancreatic or salivary gland issue", "fr": "🔶 Légèrement élevée — possible problème pancréatique ou salivaire", "ar": "🔶 مرتفع قليلاً — احتمال مشكلة بنكرياسية أو لعابية"}),
            (float("inf"),"high",   {"en": "⚠️ Significantly elevated — acute pancreatitis or parotitis", "fr": "⚠️ Très élevée — pancréatite aiguë ou parotidite", "ar": "⚠️ مرتفع بشكل ملحوظ — التهاب البنكرياس الحاد أو التهاب النكفة"}),
        ],
        "advice": {
            "high": {"en": "Amylase rises in pancreatitis and parotitis. Less specific than lipase. Correlate with lipase and clinical symptoms.", "fr": "L'amylase monte dans la pancréatite et la parotidite. Moins spécifique que la lipase. Corréler avec lipase et symptômes.", "ar": "الأميلاز يرتفع في التهاب البنكرياس والنكفة. أقل خصوصية من الليباز. قارن مع الليباز والأعراض."}
        },
        "reference": {"en": "Normal: 30–110 U/L | Elevated = pancreatitis, parotitis, intestinal ischemia", "fr": "Normal : 30–110 U/L | Élevée = pancréatite, parotidite, ischémie intestinale", "ar": "طبيعي: 30–110 وحدة/ل | مرتفع = التهاب بنكرياس أو نكفة أو نقص تروية معوية"}
    },
    # --- Minéraux ---
    {
        "name": {"en": "Magnesium", "fr": "Magnésium", "ar": "المغنيسيوم"},
        "aliases": ["magnesium", "magnésium", "magnesium", "mg2+"],
        "unit": "mg/dL",
        "ranges": [
            (1.7,         "low",    {"en": "⚠️ Low — hypomagnesemia", "fr": "⚠️ Bas — hypomagnésémie", "ar": "⚠️ منخفض — نقص المغنيسيوم"}),
            (2.2,         "normal", {"en": "✅ Normal", "fr": "✅ Normal", "ar": "✅ طبيعي"}),
            (float("inf"),"high",   {"en": "⚠️ Elevated — hypermagnesemia, usually from renal failure", "fr": "⚠️ Élevé — hypermagnésémie, généralement insuffisance rénale", "ar": "⚠️ مرتفع — فرط المغنيسيوم، عادةً من الفشل الكلوي"}),
        ],
        "advice": {
            "low":  {"en": "Low magnesium causes muscle cramps, arrhythmia, fatigue. Common causes: poor diet, diuretics, alcohol. Supplement with magnesium glycinate or citrate.", "fr": "Magnésium bas cause crampes, arythmie, fatigue. Causes : alimentation pauvre, diurétiques, alcool. Supplémenter en glycinate ou citrate de magnésium.", "ar": "انخفاض المغنيسيوم يسبب تشنجات عضلية وعدم انتظام القلب والإرهاق. الأسباب: غذاء فقير، مدرات البول، الكحول."},
            "high": {"en": "High magnesium is rare — usually from excessive supplementation or renal failure. Symptoms: weakness, low blood pressure.", "fr": "Magnésium élevé rare — généralement supplémentation excessive ou insuffisance rénale.", "ar": "ارتفاع المغنيسيوم نادر — عادةً من مكملات مفرطة أو فشل كلوي."}
        },
        "reference": {"en": "Normal: 1.7–2.2 mg/dL | Low = hypomagnesemia | High = hypermagnesemia", "fr": "Normal : 0,75–1,05 mmol/L | Bas = hypomagnésémie | Élevé = hypermagnésémie", "ar": "طبيعي: 1.7–2.2 ملغ/دل | منخفض = نقص مغنيسيوم | مرتفع = فرط مغنيسيوم"}
    },
    {
        "name": {"en": "Phosphorus", "fr": "Phosphore", "ar": "الفوسفور"},
        "aliases": ["phosphorus", "phosphore", "phosphate", "inorganic phosphate"],
        "unit": "mg/dL",
        "ranges": [
            (2.5,         "low",    {"en": "⚠️ Low — hypophosphatemia", "fr": "⚠️ Bas — hypophosphatémie", "ar": "⚠️ منخفض — نقص فوسفات الدم"}),
            (4.5,         "normal", {"en": "✅ Normal", "fr": "✅ Normal", "ar": "✅ طبيعي"}),
            (float("inf"),"high",   {"en": "⚠️ Elevated — hyperphosphatemia, usually kidney disease", "fr": "⚠️ Élevé — hyperphosphatémie, généralement maladie rénale", "ar": "⚠️ مرتفع — فرط فوسفات الدم، عادةً مرض كلوي"}),
        ],
        "advice": {
            "low":  {"en": "Low phosphorus causes muscle weakness and bone pain. Causes: malnutrition, antacids (aluminum), hyperparathyroidism. Supplement under medical supervision.", "fr": "Phosphore bas cause faiblesse musculaire et douleurs osseuses. Causes : malnutrition, antiacides, hyperparathyroïdie.", "ar": "انخفاض الفوسفور يسبب ضعف العضلات وآلام العظام. الأسباب: سوء تغذية، مضادات الحموضة، فرط نشاط الغدة جارية الدرقية."},
            "high": {"en": "High phosphorus is common in kidney disease. Correlate with creatinine and PTH. Dietary phosphorus restriction may be needed.", "fr": "Phosphore élevé commun dans la maladie rénale. Corréler avec créatinine et PTH. Restriction alimentaire possible.", "ar": "ارتفاع الفوسفور شائع في أمراض الكلى. قارن مع الكرياتينين وPTH."}
        },
        "reference": {"en": "Normal: 2.5–4.5 mg/dL | Low = malnutrition | High = kidney disease", "fr": "Normal : 0,81–1,45 mmol/L | Bas = malnutrition | Élevé = maladie rénale", "ar": "طبيعي: 2.5–4.5 ملغ/دل | منخفض = سوء تغذية | مرتفع = مرض كلوي"}
    },
    # --- Marqueurs cardiaques ---
    {
        "name": {"en": "CPK (Creatine Kinase)", "fr": "CPK (Créatine Kinase)", "ar": "CPK (كيناز الكرياتين)"},
        "aliases": ["cpk", "ck", "creatine kinase", "créatine kinase"],
        "unit": "U/L",
        "ranges": [
            (200,         "normal", {"en": "✅ Normal", "fr": "✅ Normal", "ar": "✅ طبيعي"}),
            (1000,        "high",   {"en": "🔶 Elevated — possible muscle injury, strenuous exercise or medication", "fr": "🔶 Élevée — possible lésion musculaire, exercice intense ou médicament", "ar": "🔶 مرتفع — احتمال إصابة عضلية أو تمرين مكثف أو دواء"}),
            (float("inf"),"high",   {"en": "⚠️ Significantly elevated — rhabdomyolysis or myocardial infarction", "fr": "⚠️ Très élevée — rhabdomyolyse ou infarctus du myocarde", "ar": "⚠️ مرتفع بشكل ملحوظ — انحلال العضلات أو احتشاء عضلة القلب"}),
        ],
        "advice": {
            "high": {"en": "CPK elevated after intense exercise (normal), but persistently high suggests muscle damage. If very high + chest pain: rule out myocardial infarction (check troponin). Statins can elevate CPK.", "fr": "CPK élevée après exercice intense (normal). Si très élevée + douleur thoracique : éliminer infarctus (vérifier troponine). Les statines peuvent élever la CPK.", "ar": "CPK يرتفع بعد التمرين المكثف (طبيعي)، لكن ارتفاعه المستمر يشير لتلف عضلي. إذا كان مرتفعاً جداً + ألم صدري: استبعد الاحتشاء (تحقق من التروبونين)."}
        },
        "reference": {"en": "Normal (men): 30–200 U/L | Women: 25–170 U/L | Very high = rhabdomyolysis", "fr": "Normal (homme) : 30–200 U/L | Femme : 25–170 U/L | Très élevée = rhabdomyolyse", "ar": "طبيعي (رجل): 30–200 | امرأة: 25–170 وحدة/ل | مرتفع جداً = انحلال العضلات"}
    },
    {
        "name": {"en": "LDH (Lactate Dehydrogenase)", "fr": "LDH (Lactate Déshydrogénase)", "ar": "LDH (لاكتات ديهيدروجيناز)"},
        "aliases": ["ldh", "lactate dehydrogenase", "lactate déshydrogénase"],
        "unit": "U/L",
        "ranges": [
            (250,         "normal", {"en": "✅ Normal", "fr": "✅ Normal", "ar": "✅ طبيعي"}),
            (500,         "high",   {"en": "🔶 Mildly elevated — possible tissue damage", "fr": "🔶 Légèrement élevée — possible lésion tissulaire", "ar": "🔶 مرتفع قليلاً — احتمال تلف نسيجي"}),
            (float("inf"),"high",   {"en": "⚠️ Significantly elevated — hemolysis, liver disease, myocardial infarction or cancer", "fr": "⚠️ Très élevée — hémolyse, maladie hépatique, infarctus ou cancer", "ar": "⚠️ مرتفع بشكل ملحوظ — انحلال دم أو مرض كبدي أو احتشاء أو سرطان"}),
        ],
        "advice": {
            "high": {"en": "LDH is a non-specific marker of tissue damage. Very high LDH: rule out hemolysis, liver disease, myocardial infarction, lymphoma. Correlate with clinical picture.", "fr": "LDH est un marqueur non spécifique de lésion tissulaire. Très élevée : éliminer hémolyse, maladie hépatique, infarctus, lymphome.", "ar": "LDH مؤشر غير نوعي لتلف الأنسجة. مرتفع جداً: استبعد انحلال الدم ومرض الكبد والاحتشاء والليمفوما."}
        },
        "reference": {"en": "Normal: 140–250 U/L | Elevated = tissue damage (non-specific)", "fr": "Normal : 140–250 U/L | Élevée = lésion tissulaire (non spécifique)", "ar": "طبيعي: 140–250 وحدة/ل | مرتفع = تلف نسيجي (غير نوعي)"}
    },
    {
        "name": {"en": "Troponin", "fr": "Troponine", "ar": "التروبونين"},
        "aliases": ["troponin", "troponine", "troponin i", "troponin t", "tnl", "tnt"],
        "unit": "ng/mL",
        "ranges": [
            (0.04,        "normal", {"en": "✅ Normal — no cardiac damage", "fr": "✅ Normal — pas de lésion cardiaque", "ar": "✅ طبيعي — لا تلف قلبي"}),
            (0.4,         "high",   {"en": "⚠️ Elevated — possible myocardial injury", "fr": "⚠️ Élevée — possible lésion myocardique", "ar": "⚠️ مرتفع — احتمال إصابة عضلة القلب"}),
            (float("inf"),"high",   {"en": "🔴 Significantly elevated — myocardial infarction (STEMI/NSTEMI)", "fr": "🔴 Très élevée — infarctus du myocarde (STEMI/NSTEMI)", "ar": "🔴 مرتفع بشكل ملحوظ — احتشاء عضلة القلب (STEMI/NSTEMI)"}),
        ],
        "advice": {
            "high": {"en": "Elevated troponin = myocardial damage. If chest pain present: MEDICAL EMERGENCY — call 15/112 immediately. Serial troponins every 3-6h needed. ECG urgently.", "fr": "Troponine élevée = lésion myocardique. Si douleur thoracique : URGENCE MÉDICALE — appeler le 15 immédiatement. Troponines sériées toutes les 3-6h. ECG en urgence.", "ar": "ارتفاع التروبونين = تلف عضلة القلب. إذا كان هناك ألم صدري: طارئ طبي — اتصل بالإسعاف فوراً. تروبونين متسلسل كل 3-6 ساعات. رسم قلب عاجل."}
        },
        "reference": {"en": "Normal: <0.04 ng/mL | Elevated = myocardial injury | Very high = heart attack", "fr": "Normal : <0,04 ng/mL | Élevée = lésion myocardique | Très élevée = infarctus", "ar": "طبيعي: <0.04 نانوغرام/مل | مرتفع = إصابة قلبية | مرتفع جداً = احتشاء"}
    },
    {
        "name": {"en": "D-Dimer", "fr": "D-Dimères", "ar": "D-Dimère (د-داي مر)"},
        "aliases": ["d-dimer", "d dimer", "ddimer", "d-dimère", "d dimère", "ddimere"],
        "unit": "µg/mL",
        "ranges": [
            (0.5,         "normal", {"en": "✅ Normal — no significant clotting activity", "fr": "✅ Normal — pas d'activité de coagulation significative", "ar": "✅ طبيعي — لا نشاط تخثري ملحوظ"}),
            (1.0,         "high",   {"en": "🔶 Mildly elevated — possible infection, inflammation or minor clot", "fr": "🔶 Légèrement élevés — infection, inflammation ou caillot mineur", "ar": "🔶 مرتفع قليلاً — احتمال عدوى أو التهاب أو جلطة صغيرة"}),
            (float("inf"),"high",   {"en": "⚠️ Significantly elevated — DVT or pulmonary embolism suspected", "fr": "⚠️ Très élevés — TVP ou embolie pulmonaire suspectée", "ar": "⚠️ مرتفع بشكل ملحوظ — اشتباه بتجلط وريدي عميق أو انصمام رئوي"}),
        ],
        "advice": {
            "high": {"en": "High D-dimer is sensitive but not specific for thrombosis. Causes: DVT, PE, DIC, infection, cancer, post-surgery. If DVT/PE suspected: urgent Doppler ultrasound or CT pulmonary angiography.", "fr": "D-dimères élevés : sensibles mais non spécifiques. Causes : TVP, EP, CIVD, infection, cancer, post-op. Si TVP/EP suspectée : écho-Doppler ou angio-TDM pulmonaire en urgence.", "ar": "D-Dimère المرتفع حساس لكن غير نوعي للجلطات. الأسباب: تجلط وريدي، انصمام رئوي، عدوى، سرطان. إذا اشتُبه بجلطة: إيكو دوبلر أو أنجيو CT رئوي عاجل."}
        },
        "reference": {"en": "Normal: <0.5 µg/mL (FEU) | Elevated = clotting activity (non-specific)", "fr": "Normal : <0,5 µg/mL | Élevés = activité de coagulation (non spécifique)", "ar": "طبيعي: <0.5 ميكروغرام/مل | مرتفع = نشاط تخثري (غير نوعي)"}
    },
    # --- Sérologie infectieuse ---
    {
        "name": {"en": "HBs Antigen (Hepatitis B)", "fr": "Antigène HBs (Hépatite B)", "ar": "مستضد HBs (التهاب الكبد B)"},
        "aliases": ["antigene hbs", "hbs antigen", "hbsag", "hepatitis b surface antigen", "antigène hbs"],
        "unit": "",
        "ranges": [
            (0.9,         "normal", {"en": "✅ Negative — no active Hepatitis B infection", "fr": "✅ Négatif — pas d'infection active à l'hépatite B", "ar": "✅ سلبي — لا عدوى نشطة بالتهاب الكبد B"}),
            (float("inf"),"high",   {"en": "⚠️ Positive — active Hepatitis B infection detected", "fr": "⚠️ Positif — infection active à l'hépatite B détectée", "ar": "⚠️ إيجابي — عدوى نشطة بالتهاب الكبد B"}),
        ],
        "advice": {
            "high": {"en": "Positive HBsAg confirms active Hepatitis B. Measure: HBe Ag, Anti-HBe, HBV DNA viral load, liver function tests. Consult hepatologist. Check close contacts for vaccination.", "fr": "HBsAg positif confirme une hépatite B active. Mesurer : HBe Ag, Anti-HBe, charge virale HBV ADN, bilan hépatique. Consulter un hépatologue.", "ar": "إيجابية HBsAg تؤكد التهاب الكبد B النشط. قس: HBe Ag، Anti-HBe، الحمل الفيروسي HBV DNA، وظائف الكبد. استشر طبيب أمراض الكبد."}
        },
        "reference": {"en": "Result: Negative (normal) or Positive | Positive = active infection or chronic carrier", "fr": "Résultat : Négatif (normal) ou Positif | Positif = infection active ou porteur chronique", "ar": "النتيجة: سلبي (طبيعي) أو إيجابي | إيجابي = عدوى نشطة أو حامل مزمن"}
    },
    {
        "name": {"en": "Anti-HBs Antibodies", "fr": "Anticorps Anti-HBs", "ar": "أجسام مضادة Anti-HBs"},
        "aliases": ["anti-hbs", "anti hbs", "antibody hbs", "anticorps anti-hbs", "anti hbs antibody"],
        "unit": "IU/L",
        "ranges": [
            (10,          "low",    {"en": "⚠️ Low / Negative — no immunity against Hepatitis B", "fr": "⚠️ Bas / Négatif — pas d'immunité contre l'hépatite B", "ar": "⚠️ منخفض / سلبي — لا مناعة ضد التهاب الكبد B"}),
            (100,         "normal", {"en": "✅ Positive — adequate immunity (vaccination or recovery)", "fr": "✅ Positif — immunité adéquate (vaccination ou guérison)", "ar": "✅ إيجابي — مناعة كافية (تطعيم أو شفاء)"}),
            (float("inf"),"normal", {"en": "✅ Strong immunity against Hepatitis B", "fr": "✅ Immunité forte contre l'hépatite B", "ar": "✅ مناعة قوية ضد التهاب الكبد B"}),
        ],
        "advice": {
            "low": {"en": "Anti-HBs <10 IU/L means no immunity. If not vaccinated: start Hepatitis B vaccine series (3 doses). If previously vaccinated: booster dose recommended.", "fr": "Anti-HBs <10 UI/L = pas d'immunité. Si non vacciné : démarrer le vaccin hépatite B (3 doses). Si déjà vacciné : rappel recommandé.", "ar": "Anti-HBs <10 يعني عدم وجود مناعة. إذا لم تتطعم: ابدأ سلسلة لقاح التهاب الكبد B (3 جرعات). إذا تطعمت سابقاً: جرعة تعزيزية موصى بها."}
        },
        "reference": {"en": "<10 IU/L: no immunity | 10–100: adequate | >100: strong immunity", "fr": "<10 UI/L : pas d'immunité | 10–100 : adéquate | >100 : forte immunité", "ar": "<10: لا مناعة | 10–100: كافية | >100: مناعة قوية IU/L"}
    },
    # --- Sérologie bactérienne ---
    {
        "name": {"en": "ASLO (Anti-Streptolysin O)", "fr": "ASLO (Antistreptolysine O)", "ar": "ASLO (مضاد ستربتوليزين O)"},
        "aliases": ["aslo", "anti-streptolysin", "antistreptolysine", "asto"],
        "unit": "IU/mL",
        "ranges": [
            (200,         "normal", {"en": "✅ Normal — no recent Group A Strep infection", "fr": "✅ Normal — pas d'infection streptococcique récente", "ar": "✅ طبيعي — لا عدوى عقدية حديثة"}),
            (400,         "high",   {"en": "🔶 Mildly elevated — possible recent strep infection", "fr": "🔶 Légèrement élevé — possible infection streptococcique récente", "ar": "🔶 مرتفع قليلاً — احتمال عدوى عقدية حديثة"}),
            (float("inf"),"high",   {"en": "⚠️ Significantly elevated — active strep infection or rheumatic fever", "fr": "⚠️ Très élevé — infection streptococcique active ou rhumatisme articulaire", "ar": "⚠️ مرتفع بشكل ملحوظ — عدوى عقدية نشطة أو الحمى الروماتيزمية"}),
        ],
        "advice": {
            "high": {"en": "High ASLO indicates recent Group A Streptococcus infection. Risk of rheumatic fever and glomerulonephritis. Check ECG and urine analysis. Antibiotic treatment if active infection confirmed.", "fr": "ASLO élevé indique une infection récente à Streptocoque A. Risque de rhumatisme articulaire et glomérulonéphrite. Vérifier ECG et analyse urinaire.", "ar": "ارتفاع ASLO يدل على عدوى حديثة بالمكورات العقدية A. خطر الحمى الروماتيزمية والتهاب الكبيبات. تحقق من رسم القلب وتحليل البول."}
        },
        "reference": {"en": "Normal: <200 IU/mL | Elevated = recent strep infection, rheumatic fever risk", "fr": "Normal : <200 UI/mL | Élevé = infection streptococcique récente, risque RAA", "ar": "طبيعي: <200 وحدة/مل | مرتفع = عدوى عقدية حديثة، خطر الحمى الروماتيزمية"}
    },
    {
        "name": {"en": "Rheumatoid Factor (RF)", "fr": "Facteur Rhumatoïde (FR)", "ar": "العامل الروماتويدي (RF)"},
        "aliases": ["rheumatoid factor", "facteur rhumatoide", "facteur rhumatoïde", "rf", "fr"],
        "unit": "IU/mL",
        "ranges": [
            (14,          "normal", {"en": "✅ Negative — no rheumatoid factor detected", "fr": "✅ Négatif — pas de facteur rhumatoïde détecté", "ar": "✅ سلبي — لا عامل روماتويدي مكتشف"}),
            (60,          "high",   {"en": "🔶 Weakly positive — possible early rheumatoid arthritis or other condition", "fr": "🔶 Faiblement positif — possible polyarthrite rhumatoïde débutante", "ar": "🔶 إيجابي ضعيف — احتمال التهاب مفاصل روماتويدي مبكر"}),
            (float("inf"),"high",   {"en": "⚠️ Strongly positive — rheumatoid arthritis, Sjögren's or lupus", "fr": "⚠️ Fortement positif — polyarthrite rhumatoïde, Sjögren ou lupus", "ar": "⚠️ إيجابي قوي — التهاب مفاصل روماتويدي أو متلازمة شوغرن أو ذئبة"}),
        ],
        "advice": {
            "high": {"en": "Positive RF is not specific for rheumatoid arthritis. Correlate with anti-CCP antibodies, clinical symptoms (joint pain, morning stiffness). Consult rheumatologist.", "fr": "FR positif n'est pas spécifique de la polyarthrite rhumatoïde. Corréler avec anti-CCP, symptômes cliniques. Consulter un rhumatologue.", "ar": "إيجابية RF ليست نوعية لالتهاب المفاصل الروماتويدي. قارن مع anti-CCP والأعراض السريرية. استشر طبيب الروماتيزم."}
        },
        "reference": {"en": "Normal: <14 IU/mL | Positive = rheumatoid arthritis, Sjögren's, lupus, infections", "fr": "Normal : <14 UI/mL | Positif = polyarthrite rhumatoïde, Sjögren, lupus, infections", "ar": "طبيعي: <14 وحدة/مل | إيجابي = التهاب مفاصل روماتويدي أو شوغرن أو ذئبة أو عدوى"}
    },
    {
        "name": {"en": "Wright Test (Brucellosis)", "fr": "Test de Wright (Brucellose)", "ar": "اختبار رايت (البروسيلا)"},
        "aliases": ["wright", "brucella wright", "brucellose wright", "test de wright"],
        "unit": "titer",
        "ranges": [
            (79,          "normal", {"en": "✅ Negative — no Brucellosis", "fr": "✅ Négatif — pas de brucellose", "ar": "✅ سلبي — لا إصابة بالبروسيلا"}),
            (160,         "high",   {"en": "🔶 Borderline — possible early Brucellosis, repeat test", "fr": "🔶 Limite — possible brucellose débutante, répéter le test", "ar": "🔶 حدي — احتمال بروسيلا مبكرة، أعد الاختبار"}),
            (float("inf"),"high",   {"en": "⚠️ Positive — Brucellosis confirmed (1/160 or higher)", "fr": "⚠️ Positif — brucellose confirmée (1/160 ou plus)", "ar": "⚠️ إيجابي — تأكيد البروسيلا (1/160 أو أعلى)"}),
        ],
        "advice": {
            "high": {"en": "Brucellosis is transmitted via unpasteurized dairy or contact with infected animals. Treatment: doxycycline + rifampicin for 6 weeks. Notify public health if confirmed.", "fr": "La brucellose se transmet par les produits laitiers non pasteurisés ou le contact animal. Traitement : doxycycline + rifampicine 6 semaines.", "ar": "تنتقل البروسيلا عبر الألبان غير المبسترة أو التلامس مع الحيوانات. العلاج: دوكسيسيكلين + ريفامبيسين 6 أسابيع."}
        },
        "reference": {"en": "Negative: <1/80 | Borderline: 1/80 | Positive: ≥1/160", "fr": "Négatif : <1/80 | Limite : 1/80 | Positif : ≥1/160", "ar": "سلبي: <1/80 | حدي: 1/80 | إيجابي: ≥1/160"}
    },
    {
        "name": {"en": "Widal Test (Typhoid)", "fr": "Test de Widal (Typhoïde)", "ar": "اختبار ويدال (التيفوئيد)"},
        "aliases": ["widal", "widal test", "test de widal", "typhoid widal"],
        "unit": "titer",
        "ranges": [
            (79,          "normal", {"en": "✅ Negative — no Typhoid fever", "fr": "✅ Négatif — pas de fièvre typhoïde", "ar": "✅ سلبي — لا حمى تيفية"}),
            (160,         "high",   {"en": "🔶 Borderline — possible recent exposure or early infection", "fr": "🔶 Limite — possible exposition récente ou infection débutante", "ar": "🔶 حدي — احتمال تعرض حديث أو عدوى مبكرة"}),
            (float("inf"),"high",   {"en": "⚠️ Positive — Typhoid fever suspected (≥1/160)", "fr": "⚠️ Positif — fièvre typhoïde suspectée (≥1/160)", "ar": "⚠️ إيجابي — اشتباه حمى التيفوئيد (≥1/160)"}),
        ],
        "advice": {
            "high": {"en": "Positive Widal suggests typhoid fever (Salmonella typhi). Confirm with blood culture. Treatment: ciprofloxacin or azithromycin. Isolate patient and notify public health.", "fr": "Widal positif suggère une fièvre typhoïde (Salmonella typhi). Confirmer par hémoculture. Traitement : ciprofloxacine ou azithromycine.", "ar": "إيجابية ويدال تشير لحمى التيفوئيد (السالمونيلا). أكّد بزرع الدم. العلاج: سيبروفلوكساسين أو أزيثروميسين."}
        },
        "reference": {"en": "Negative: <1/80 | Borderline: 1/80 | Positive (typhoid suspected): ≥1/160", "fr": "Négatif : <1/80 | Limite : 1/80 | Positif (typhoïde suspectée) : ≥1/160", "ar": "سلبي: <1/80 | حدي: 1/80 | إيجابي (اشتباه تيفوئيد): ≥1/160"}
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
    Also handles comma decimals: 'glucose 1,05 g/L' -> 'glucose 1.05 g/L'
    """
    # Normalize comma decimals: 1,05 -> 1.05 (but not 1,000 style thousands)
    text = re.sub(r'(\d),(\d)', r'\1.\2', text)
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

import re

# Each range entry is now: (max_value, status_key, labels_dict)
# status_key: "low" | "normal" | "high" — explicit, no inference

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
            "low":  {"en": "Consider iron supplementation. Check transferrin saturation and CBC. Possible causes: poor diet, chronic bleeding, malabsorption.", "fr": "Envisager une supplémentation en fer. Vérifier la saturation en transferrine et la NFS. Causes possibles : alimentation pauvre en fer, saignement chronique, malabsorption.", "ar": "فكر في مكملات الحديد. تحقق من تشبع الترانسفيرين وصورة الدم الكاملة. الأسباب: نظام غذائي فقير بالحديد، نزيف مزمن، سوء الامتصاص."},
            "high": {"en": "High ferritin may indicate inflammation, liver disease or hemochromatosis. Repeat fasting. Correlate with CRP.", "fr": "Ferritine élevée = possible inflammation, maladie du foie ou hémochromatose. Refaire à jeun. Corréler avec la CRP.", "ar": "ارتفاع الفيريتين قد يدل على التهاب أو مرض كبدي. أعد الفحص صائماً وقارنه بـ CRP."}
        },
        "reference": {"en": "Normal: 12–200 ng/mL (women), 30–300 ng/mL (men)", "fr": "Normal : 12–200 ng/mL (femme), 30–300 ng/mL (homme)", "ar": "طبيعي: 12–200 نانوغرام/مل (امرأة)، 30–300 (رجل)"}
    },
    {
        "name": {"en": "Hemoglobin", "fr": "Hémoglobine", "ar": "الهيموغلوبين"},
        "aliases": ["hemoglobin", "hémoglobine", "haemoglobin", " hb "],
        "unit": "g/dL",
        "ranges": [
            (7,           "low",    {"en": "🔴 Critically low — severe anemia, transfusion may be needed", "fr": "🔴 Critique — anémie sévère, transfusion possible", "ar": "🔴 منخفض بشكل خطير — فقر دم شديد، قد يلزم نقل دم"}),
            (10,          "low",    {"en": "⚠️ Low — moderate anemia", "fr": "⚠️ Basse — anémie modérée", "ar": "⚠️ منخفض — فقر دم متوسط"}),
            (12,          "low",    {"en": "🔶 Borderline — mild anemia (women threshold)", "fr": "🔶 Légèrement basse — anémie légère (seuil femme)", "ar": "🔶 منخفض قليلاً — فقر دم خفيف (حد المرأة)"}),
            (17.5,        "normal", {"en": "✅ Normal", "fr": "✅ Normal", "ar": "✅ طبيعي"}),
            (float("inf"),"high",   {"en": "⚠️ Elevated — possible dehydration or polycythemia", "fr": "⚠️ Élevée — déshydratation ou polyglobulie possible", "ar": "⚠️ مرتفع — احتمال جفاف أو كثرة الكريات الحمراء"}),
        ],
        "advice": {
            "low":  {"en": "Check ferritin, B12, folate to identify cause. Dietary review recommended. If <8 g/dL, urgent medical evaluation needed.", "fr": "Vérifier ferritine, B12, folate pour identifier la cause. Bilan alimentaire recommandé. Si <8 g/dL : évaluation médicale urgente.", "ar": "تحقق من الفيريتين وB12 وحمض الفوليك لتحديد السبب. مراجعة النظام الغذائي. إذا كان <8: تقييم طبي عاجل."},
            "high": {"en": "Evaluate hydration. If persistent, check for polycythemia vera (JAK2 mutation).", "fr": "Évaluer l'hydratation. Si persistant, rechercher une polyglobulie de Vaquez (mutation JAK2).", "ar": "تقييم حالة الترطيب. إذا استمر، تحقق من كثرة الحمر الحقيقية."}
        },
        "reference": {"en": "Normal: 12–15.5 g/dL (women), 13.5–17.5 g/dL (men)", "fr": "Normal : 12–15,5 g/dL (femme), 13,5–17,5 g/dL (homme)", "ar": "طبيعي: 12–15.5 غ/دل (امرأة)، 13.5–17.5 (رجل)"}
    },
    {
        "name": {"en": "Glucose (fasting)", "fr": "Glycémie (à jeun)", "ar": "سكر الدم (صائم)"},
        "aliases": ["glucose", "glycémie", "glycemie", "blood sugar"],
        "unit": "mg/dL",
        "ranges": [
            (60,          "low",    {"en": "🔴 Critically low — hypoglycemia, emergency", "fr": "🔴 Critique — hypoglycémie, urgence", "ar": "🔴 منخفض جداً — نقص سكر حاد، طارئ"}),
            (99,          "normal", {"en": "✅ Normal fasting glucose", "fr": "✅ Glycémie à jeun normale", "ar": "✅ سكر الدم الصائم طبيعي"}),
            (125,         "high",   {"en": "🔶 Pre-diabetic range — impaired fasting glucose", "fr": "🔶 Zone pré-diabétique — hyperglycémie modérée", "ar": "🔶 نطاق ما قبل السكري — ارتفاع طفيف في سكر الصيام"}),
            (float("inf"),"high",   {"en": "⚠️ Diabetic range — high fasting glucose", "fr": "⚠️ Zone diabétique — glycémie à jeun élevée", "ar": "⚠️ نطاق السكري — سكر الصيام مرتفع"}),
        ],
        "advice": {
            "low":  {"en": "Immediate glucose intake needed. Investigate cause: medication, prolonged fasting, insulinoma.", "fr": "Apport immédiat de glucose nécessaire. Investiguer : médicament, jeûne trop long, insulinome.", "ar": "يلزم تناول الجلوكوز فوراً. ابحث عن السبب: دواء، صيام طويل، ورم أنسولين."},
            "high": {"en": "Confirm with HbA1c. Verify fasting duration (min 8h) and last meal content (avoid sugary food). If confirmed: lifestyle changes + medical follow-up. Consider HbA1c test.", "fr": "Confirmer avec HbA1c. Vérifier la durée du jeûne (min 8h) et le dernier repas (sucré ?). Si confirmé : mode de vie + suivi médical. Prescrire une HbA1c.", "ar": "أكّد بـ HbA1c. تحقق من مدة الصيام (8 ساعات) وآخر وجبة (هل كانت محلاة؟). إذا تأكد: تغيير نمط الحياة + متابعة طبية. اطلب فحص HbA1c."}
        },
        "reference": {"en": "Normal fasting: 70–99 mg/dL | Pre-diabetes: 100–125 | Diabetes: ≥126", "fr": "Normal à jeun : 0,70–0,99 g/L | Pré-diabète : 1,00–1,25 | Diabète : ≥1,26", "ar": "طبيعي صائم: 70–99 ملغ/دل | قبل السكري: 100–125 | السكري: ≥126"}
    },
    {
        "name": {"en": "HbA1c", "fr": "HbA1c (hémoglobine glyquée)", "ar": "HbA1c (الهيموغلوبين الغليكوزيلاتي)"},
        "aliases": ["hba1c", "hemoglobin a1c", "hémoglobine glyquée", "glycated hemoglobin"],
        "unit": "%",
        "ranges": [
            (5.7,         "normal", {"en": "✅ Normal — no diabetes risk", "fr": "✅ Normal — pas de risque diabétique", "ar": "✅ طبيعي — لا خطر سكري"}),
            (6.4,         "high",   {"en": "🔶 Pre-diabetic — lifestyle changes recommended", "fr": "🔶 Pré-diabétique — changement de mode de vie recommandé", "ar": "🔶 ما قبل السكري — يُنصح بتغيير نمط الحياة"}),
            (float("inf"),"high",   {"en": "⚠️ Diabetic range — medical follow-up required", "fr": "⚠️ Zone diabétique — suivi médical nécessaire", "ar": "⚠️ نطاق السكري — المتابعة الطبية ضرورية"}),
        ],
        "advice": {
            "high": {"en": "HbA1c reflects average blood sugar over 3 months. If ≥6.5%: diabetes confirmed. Consult endocrinologist. Consider diet changes, physical activity, and medication.", "fr": "L'HbA1c reflète la glycémie moyenne sur 3 mois. Si ≥6,5% : diabète confirmé. Consulter un endocrinologue. Revoir alimentation, activité physique, traitement.", "ar": "HbA1c يعكس متوسط السكر على 3 أشهر. إذا ≥6.5%: السكري مؤكد. استشر طبيب الغدد. راجع النظام الغذائي والرياضة والعلاج."}
        },
        "reference": {"en": "Normal: <5.7% | Pre-diabetes: 5.7–6.4% | Diabetes: ≥6.5%", "fr": "Normal : <5,7% | Pré-diabète : 5,7–6,4% | Diabète : ≥6,5%", "ar": "طبيعي: <5.7% | قبل السكري: 5.7–6.4% | السكري: ≥6.5%"}
    },
    {
        "name": {"en": "CRP (Inflammation)", "fr": "CRP (Inflammation)", "ar": "CRP (الالتهاب)"},
        "aliases": ["crp", "c-reactive protein", "protéine c réactive"],
        "unit": "mg/L",
        "ranges": [
            (10,          "normal", {"en": "✅ Normal — no significant inflammation", "fr": "✅ Normale — pas d'inflammation significative", "ar": "✅ طبيعي — لا التهاب ملحوظ"}),
            (40,          "high",   {"en": "🔶 Mildly elevated — possible mild infection or inflammation", "fr": "🔶 Légèrement élevée — infection ou inflammation légère", "ar": "🔶 مرتفع قليلاً — احتمال عدوى أو التهاب خفيف"}),
            (float("inf"),"high",   {"en": "⚠️ Significantly elevated — active infection, autoimmune flare or tissue damage", "fr": "⚠️ Très élevée — infection active, poussée auto-immune ou lésion tissulaire", "ar": "⚠️ مرتفع بشكل ملحوظ — عدوى نشطة أو انتكاسة مناعية أو تلف نسيجي"}),
        ],
        "advice": {
            "high": {"en": "Identify source of inflammation. Complete with CBC, ESR, blood cultures if infectious cause suspected. Monitor over time.", "fr": "Identifier la source. Compléter avec NFS, VS, hémocultures si cause infectieuse suspectée. Surveiller l'évolution.", "ar": "حدد مصدر الالتهاب. أكمل بصورة دم، سرعة ترسب، مزارع إذا اشتُبه بعدوى. راقب التطور."}
        },
        "reference": {"en": "Normal: <10 mg/L | Mild: 10–40 | Active infection: >40", "fr": "Normal : <10 mg/L | Légère : 10–40 | Infection active : >40", "ar": "طبيعي: <10 ملغ/ل | خفيف: 10–40 | عدوى نشطة: >40"}
    },
    {
        "name": {"en": "TSH (Thyroid)", "fr": "TSH (Thyroïde)", "ar": "TSH (الغدة الدرقية)"},
        "aliases": ["tsh", "thyroid stimulating"],
        "unit": "mIU/L",
        "ranges": [
            (0.4,         "low",    {"en": "⚠️ Low — possible hyperthyroidism", "fr": "⚠️ Basse — possible hyperthyroïdie", "ar": "⚠️ منخفض — احتمال فرط نشاط الغدة الدرقية"}),
            (4.0,         "normal", {"en": "✅ Normal thyroid function", "fr": "✅ Fonction thyroïdienne normale", "ar": "✅ وظيفة الغدة الدرقية طبيعية"}),
            (float("inf"),"high",   {"en": "⚠️ Elevated — possible hypothyroidism", "fr": "⚠️ Élevée — possible hypothyroïdie", "ar": "⚠️ مرتفع — احتمال قصور الغدة الدرقية"}),
        ],
        "advice": {
            "low":  {"en": "Low TSH = possible overactive thyroid. Measure FT4 and FT3. Symptoms: rapid heartbeat, weight loss, tremors. Consult endocrinologist.", "fr": "TSH basse = possible hyperthyroïdie. Mesurer FT4 et FT3. Symptômes : tachycardie, perte de poids, tremblements. Consulter un endocrinologue.", "ar": "TSH منخفض = احتمال فرط نشاط الدرقية. قس FT4 وFT3. الأعراض: تسارع القلب، فقدان الوزن، رعشة. استشر طبيب الغدد."},
            "high": {"en": "High TSH = possible underactive thyroid. Measure FT4. Symptoms: fatigue, weight gain, cold intolerance. Levothyroxine may be needed.", "fr": "TSH élevée = possible hypothyroïdie. Mesurer FT4. Symptômes : fatigue, prise de poids, intolérance au froid. Lévothyroxine possible.", "ar": "TSH مرتفع = احتمال قصور الدرقية. قس FT4. الأعراض: إرهاق، زيادة الوزن، عدم تحمل البرد. قد يلزم ليفوثيروكسين."}
        },
        "reference": {"en": "Normal: 0.4–4.0 mIU/L | Low = hyperthyroidism | High = hypothyroidism", "fr": "Normal : 0,4–4,0 mUI/L | Bas = hyperthyroïdie | Élevé = hypothyroïdie", "ar": "طبيعي: 0.4–4.0 | منخفض = فرط نشاط | مرتفع = قصور"}
    },
    {
        "name": {"en": "Creatinine", "fr": "Créatinine", "ar": "الكرياتينين"},
        "aliases": ["creatinine", "créatinine"],
        "unit": "mg/dL",
        "ranges": [
            (0.5,         "low",    {"en": "🔶 Low — possible muscle loss or low protein intake", "fr": "🔶 Basse — perte musculaire ou faible apport protéique", "ar": "🔶 منخفض — فقدان عضلي أو نقص البروتين"}),
            (1.35,        "normal", {"en": "✅ Normal", "fr": "✅ Normal", "ar": "✅ طبيعي"}),
            (float("inf"),"high",   {"en": "⚠️ Elevated — possible kidney dysfunction", "fr": "⚠️ Élevée — possible insuffisance rénale", "ar": "⚠️ مرتفع — احتمال خلل كلوي"}),
        ],
        "advice": {
            "high": {"en": "Calculate eGFR. Check urea and urinalysis. Possible causes: dehydration, kidney disease, high protein diet. Repeat after adequate hydration.", "fr": "Calculer le DFGe. Vérifier urée et analyse urinaire. Causes : déshydratation, maladie rénale, alimentation riche en protéines. Refaire après hydratation.", "ar": "احسب معدل الترشيح الكبيبي. تحقق من اليوريا وتحليل البول. الأسباب: جفاف، مرض كلوي، نظام غني بالبروتين."}
        },
        "reference": {"en": "Normal (men): 0.74–1.35 mg/dL | Normal (women): 0.59–1.04 mg/dL", "fr": "Normal (homme) : 7–12 mg/L | Normal (femme) : 5–10 mg/L", "ar": "طبيعي (رجل): 0.74–1.35 | طبيعي (امرأة): 0.59–1.04 ملغ/دل"}
    },
]


def extract_value(text: str, aliases: list) -> float | None:
    text_lower = text.lower()
    for alias in aliases:
        alias = alias.strip()
        patterns = [
            rf"{re.escape(alias)}[\s:=\-]*([0-9]+\.?[0-9]*)",
            rf"([0-9]+\.?[0-9]*)[\s]*(?:ng/ml|g/dl|mg/dl|mmol/l|%|miu/l|u/l|mg/l)?[\s]*{re.escape(alias)}",
        ]
        for pattern in patterns:
            match = re.search(pattern, text_lower)
            if match:
                try:
                    return float(match.group(1))
                except (ValueError, IndexError):
                    continue
    return None


def interpret_value(value: float, ranges: list, lang: str) -> tuple[str, str]:
    for threshold, status_key, labels in ranges:
        if value <= threshold:
            label = labels.get(lang, labels["en"])
            return label, status_key
    last = ranges[-1]
    return last[2].get(lang, last[2]["en"]), last[1]


def analyze_text(text: str, lang: str) -> list[dict]:
    results = []
    for param in PARAMETERS:
        value = extract_value(text, param["aliases"])
        if value is not None:
            status_label, status_key = interpret_value(value, param["ranges"], lang)
            advice = ""
            if status_key in param.get("advice", {}):
                advice = param["advice"][status_key].get(lang, param["advice"][status_key]["en"])
            results.append({
                "name": param["name"].get(lang, param["name"]["en"]),
                "value": value,
                "unit": param["unit"],
                "status": status_label,
                "status_key": status_key,
                "advice": advice,
                "reference": param["reference"].get(lang, param["reference"]["en"]),
            })
    return results

import sys
sys.path.insert(0, ".")

from extractor import extract_value, analyze_text, PARAMETERS

# -----------------------------------------------
# extract_value tests
# -----------------------------------------------

def test_extract_simple():
    val, op = extract_value("Ferritin 50 ng/mL", ["ferritin"])
    assert val == 50.0 and op is None

def test_extract_with_colon():
    val, op = extract_value("ferritin: 8.5", ["ferritin"])
    assert val == 8.5 and op is None

def test_extract_alias_french():
    val, op = extract_value("Ferritine 120 ng/mL", ["ferritin", "ferritine"])
    assert val == 120.0

def test_extract_operator_less_than():
    val, op = extract_value("CRP < 5 mg/L", ["crp"])
    assert val == 5.0 and op == "<"

def test_extract_operator_greater_than():
    val, op = extract_value("Glucose > 200 mg/dL", ["glucose"])
    assert val == 200.0 and op == ">"

def test_extract_not_found():
    val, op = extract_value("nothing here", ["ferritin"])
    assert val is None and op is None

def test_extract_decimal():
    val, op = extract_value("TSH 0.25 mIU/L", ["tsh"])
    assert val == 0.25

# -----------------------------------------------
# analyze_text tests
# -----------------------------------------------

def test_ferritin_very_low():
    results = analyze_text("Ferritin 6 ng/mL", "en")
    r = next(r for r in results if "Ferritin" in r["name"])
    assert r["status_key"] == "low"
    assert "iron deficiency" in r["status"].lower() or "low" in r["status_key"]

def test_ferritin_normal():
    results = analyze_text("Ferritin 85 ng/mL", "en")
    r = next(r for r in results if "Ferritin" in r["name"])
    assert r["status_key"] == "normal"

def test_hemoglobin_moderate_anemia():
    results = analyze_text("Hemoglobin 9.8 g/dL", "en")
    r = next(r for r in results if "Hemoglobin" in r["name"])
    assert r["status_key"] == "low"

def test_glucose_diabetic():
    results = analyze_text("Glucose 187 mg/dL", "en")
    r = next(r for r in results if "Glucose" in r["name"])
    assert r["status_key"] == "high"

def test_glucose_normal():
    results = analyze_text("Glucose 88 mg/dL", "en")
    r = next(r for r in results if "Glucose" in r["name"])
    assert r["status_key"] == "normal"

def test_tsh_hypothyroidism():
    results = analyze_text("TSH 8.5 mIU/L", "en")
    r = next(r for r in results if "TSH" in r["name"])
    assert r["status_key"] == "high"

def test_operator_less_than_crp():
    results = analyze_text("CRP < 5 mg/L", "en")
    r = next(r for r in results if "CRP" in r["name"])
    assert r["status_key"] == "normal"  # <5 is low = normal CRP

def test_all_normal():
    text = "Ferritin 85 ng/mL, Hemoglobin 14.2 g/dL, Glucose 88 mg/dL, CRP 3 mg/L"
    results = analyze_text(text, "en")
    assert all(r["status_key"] == "normal" for r in results)

def test_multilingual_french():
    results = analyze_text("Ferritine 8 ng/mL, Hémoglobine 9.8 g/dL", "fr")
    assert len(results) == 2
    assert all(r["status_key"] == "low" for r in results)

def test_multilingual_arabic():
    results = analyze_text("Ferritin 8 ng/mL, Glucose 187 mg/dL", "ar")
    assert len(results) == 2

def test_advice_present_when_abnormal():
    results = analyze_text("Ferritin 6 ng/mL", "en")
    r = results[0]
    assert r["advice"] != ""

def test_no_advice_when_normal():
    results = analyze_text("Ferritin 85 ng/mL", "en")
    r = results[0]
    assert r["advice"] == ""

# -----------------------------------------------
# Run
# -----------------------------------------------

if __name__ == "__main__":
    tests = [
        test_extract_simple, test_extract_with_colon, test_extract_alias_french,
        test_extract_operator_less_than, test_extract_operator_greater_than,
        test_extract_not_found, test_extract_decimal,
        test_ferritin_very_low, test_ferritin_normal,
        test_hemoglobin_moderate_anemia, test_glucose_diabetic,
        test_glucose_normal, test_tsh_hypothyroidism,
        test_operator_less_than_crp, test_all_normal,
        test_multilingual_french, test_multilingual_arabic,
        test_advice_present_when_abnormal, test_no_advice_when_normal,
    ]
    passed = 0
    for t in tests:
        try:
            t()
            print(f"  ✅ {t.__name__}")
            passed += 1
        except AssertionError as e:
            print(f"  ❌ {t.__name__} — {e}")
        except Exception as e:
            print(f"  💥 {t.__name__} — {e}")
    print(f"\n{passed}/{len(tests)} tests passed")

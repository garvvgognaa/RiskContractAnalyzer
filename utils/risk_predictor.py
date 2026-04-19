   

import re
import os
import joblib
import numpy as np
from typing import Dict, List

from app_config import (
    RISK_KEYWORDS,
    RISK_KEYWORD_THRESHOLD,
    BASE_RISKY_CONFIDENCE,
    SAFE_CONFIDENCE,
)

                                                                             
                                                                  
                                                                             
_MODEL_PATH      = os.path.join("models", "best_model.joblib")
_VECTORIZER_PATH = os.path.join("models", "vectorizer.joblib")

                                                                             
                                       
                                                                             
_model      = None
_vectorizer = None
_use_ml     = False                                              


def _load_model() -> None:
                                                                             
    global _model, _vectorizer, _use_ml
    if _use_ml:                          
        return
    if os.path.exists(_MODEL_PATH) and os.path.exists(_VECTORIZER_PATH):
        try:
            _model      = joblib.load(_MODEL_PATH)
            _vectorizer = joblib.load(_VECTORIZER_PATH)
            _use_ml     = True
            print("[RiskPredictor] Loaded trained ML model from disk.")
        except Exception as exc:
            print(f"[RiskPredictor] Failed to load model — falling back to rule-based. ({exc})")
    else:
        print("[RiskPredictor] No saved model found — using rule-based keyword predictor.")


                                                                             
                                             
                                                                             
_CATEGORY_MAP: Dict[str, str] = {
    "indemnify":           "Indemnity",
    "indemnification":     "Indemnity",
    "indemnified":         "Indemnity",
    "hold harmless":       "Indemnity",
    "liability":           "Liability",
    "unlimited liability": "Liability",
    "gross negligence":    "Liability",
    "terminate":           "Termination",
    "termination":         "Termination",
    "penalty":             "Penalties",
    "penalties":           "Penalties",
    "liquidated damages":  "Penalties",
    "forfeiture":          "Penalties",
    "default":             "Default",
    "arbitration":         "Dispute Resolution",
    "arbitral":            "Dispute Resolution",
    "waive":               "Waiver",
    "waiver":              "Waiver",
    "waived":              "Waiver",
    "jurisdiction":        "Jurisdiction",
    "governing law":       "Jurisdiction",
    "irrevocable":         "IP / Rights",
    "perpetual":           "IP / Rights",
    "royalty-free":        "IP / Rights",
    "sublicense":          "IP / Rights",
    "assign":              "IP / Rights",
    "assignment":          "IP / Rights",
    "transfer of rights":  "IP / Rights",
    "non-disclosure":      "Confidentiality",
    "proprietary":         "Confidentiality",
    "trade secret":        "Confidentiality",
    "confidential information": "Confidentiality",
    "interest rate":       "Financial",
    "compound interest":   "Financial",
    "late payment":        "Financial",
    "surcharge":           "Financial",
    "deduct":              "Financial",
    "withhold":            "Financial",
    "escrow":              "Financial",
    "non-compete":         "Non-Compete",
    "non-solicitation":    "Non-Compete",
    "garden leave":        "Non-Compete",
    "restraint of trade":  "Non-Compete",
}


                                                                             
                                                                          
                                                                             

def _extract_keywords(text: str) -> List[str]:
                                                            
    text_lower = text.lower()
    matched = []
    for keyword in RISK_KEYWORDS:
        pattern = r"\b" + re.escape(keyword) + r"\b"
        if re.search(pattern, text_lower):
            matched.append(keyword)
    return matched


def _keywords_to_categories(matched: List[str]) -> List[str]:
                                                                           
    return list(dict.fromkeys(
        _CATEGORY_MAP.get(kw, "General Risk") for kw in matched
    ))


                                                                             
                          
                                                                             

def predict_clause_risk(clause: Dict) -> Dict:
           
    _load_model()                           

    text = clause["text"]
    matched   = _extract_keywords(text)
    categories = _keywords_to_categories(matched)

                                                                             
                               
                                                                             
    if _use_ml and _model is not None and _vectorizer is not None:
        try:
            X_vec = _vectorizer.transform([text])
            pred  = int(_model.predict(X_vec)[0])                       

                                                                             
            if hasattr(_model, "predict_proba"):
                proba      = _model.predict_proba(X_vec)[0]
                confidence = float(np.max(proba))
            else:
                confidence = BASE_RISKY_CONFIDENCE if pred == 1 else SAFE_CONFIDENCE

            label = "Risky" if pred == 1 else "Safe"
            return {
                **clause,
                "label":             label,
                "confidence":        round(confidence, 3),
                "matched_keywords":  matched,
                "categories":        categories,
                "predictor":         "ML Model",
            }
        except Exception as exc:
            print(f"[RiskPredictor] ML prediction failed, falling back: {exc}")

                                                                             
                                                    
                                                                             
    is_risky = len(matched) >= RISK_KEYWORD_THRESHOLD
    if is_risky:
        bonus      = min(0.10, len(matched) * 0.02)
        confidence = round(BASE_RISKY_CONFIDENCE + bonus, 3)
        label      = "Risky"
    else:
        confidence = SAFE_CONFIDENCE
        label      = "Safe"

    return {
        **clause,
        "label":             label,
        "confidence":        confidence,
        "matched_keywords":  matched,
        "categories":        categories,
        "predictor":         "Rule-Based",
    }


def analyze_clauses(clauses: List[Dict]) -> List[Dict]:
           
    return [predict_clause_risk(c) for c in clauses]


def compute_summary_stats(analyzed_clauses: List[Dict]) -> Dict:
           
    total  = len(analyzed_clauses)
    risky  = sum(1 for c in analyzed_clauses if c["label"] == "Risky")
    safe   = total - risky
    risk_pct = round((risky / total * 100) if total > 0 else 0.0, 1)

                                                            
    predictors = [c.get("predictor", "Rule-Based") for c in analyzed_clauses]
    predictor  = max(set(predictors), key=predictors.count) if predictors else "Rule-Based"

    return {
        "total":          total,
        "risky_count":    risky,
        "safe_count":     safe,
        "risk_percentage": risk_pct,
        "predictor":      predictor,
    }

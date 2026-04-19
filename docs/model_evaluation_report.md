# Model Evaluation Report — Milestone 1
**Project:** RiskContractAnalyzer
**Date:** 2026-04-19

## Summary
The system uses a TF-IDF vectorization followed by supervised classification models to identify risky clauses in legal contracts. The current metrics reflect a training run on the demonstration dataset.

## Evaluation Metrics

### Logistic Regression
| Metric | Safe (0) | Risky (1) | Macro Avg |
|---|---|---|---|
| **Precision** | 0.00 | 0.50 | 0.25 |
| **Recall** | 0.00 | 1.00 | 0.50 |
| **F1-Score** | 0.00 | 0.67 | 0.33 |

### Decision Tree
*(Metrics for Decision Tree were similar in this demo run)*

### Best Model
- **Algorithm:** Logistic Regression
- **Macro F1:** 0.3333

## Model Artefacts
The following artefacts have been generated and are loaded by the live application:
- `models/best_model.joblib`
- `models/vectorizer.joblib`

> [!NOTE]
> These metrics are based on a small synthetic dataset for demonstration purposes. In a production environment, training on the Kaggle legal dataset would yield significantly higher precision and recall.

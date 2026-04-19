   
from sklearn.metrics import classification_report, f1_score


def evaluate_models(models: dict, X_test_vec, y_test) -> str:
           
    best_name, best_f1 = None, -1.0
    labels = ["Safe (0)", "Risky (1)"]

    for name, model in models.items():
        y_pred = model.predict(X_test_vec)
        print(f"\n{'='*50}")
        print(f"  {name}")
        print('='*50)
        print(classification_report(y_test, y_pred, target_names=labels))
        macro_f1 = f1_score(y_test, y_pred, average="macro")
        if macro_f1 > best_f1:
            best_f1, best_name = macro_f1, name

    print(f"\nBest model: {best_name}  (macro F1 = {best_f1:.4f})")
    return best_name

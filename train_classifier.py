   
import pandas as pd

from src.model_training.data_loader import load_and_split
from src.model_training.feature_extractor import build_vectorizer, fit_and_transform
from src.model_training.trainer import train_models
from src.model_training.evaluator import evaluate_models
from src.model_training.model_saver import save_best


def build_demo_dataframe() -> pd.DataFrame:
                                                                            
    data = {
        "clause_text": [
            "The party may terminate this agreement without notice at any time.",
            "Either party shall provide 30 days written notice before termination.",
            "Liability is limited to the total fees paid in the preceding month.",
            "The vendor assumes no liability for indirect or consequential damages.",
            "Confidential information must not be disclosed to any third parties.",
            "All disputes shall be resolved through binding arbitration.",
            "Payment is due within 30 days of invoice date.",
            "The client retains full intellectual property rights over deliverables.",
            "The contractor may subcontract work without prior written consent.",
            "Governing law shall be the laws of the State of New York.",
        ],
        "is_risky": [1, 0, 1, 1, 0, 1, 0, 0, 1, 0],
    }
    return pd.DataFrame(data)


def main():
    print("=== Risk Contract Classifier Pipeline ===\n")

                     
    df = build_demo_dataframe()
    print(f"Dataset size: {len(df)} samples")
    X_train, X_test, y_train, y_test = load_and_split(df)
    print(f"Train: {len(X_train)}  |  Test: {len(X_test)}\n")

                                  
    vectorizer = build_vectorizer()
    X_train_vec, X_test_vec = fit_and_transform(vectorizer, X_train, X_test)

                     
    models = train_models(X_train_vec, y_train)

                             
    best_name = evaluate_models(models, X_test_vec, y_test)

                                     
    save_best(models, best_name, vectorizer)

    print("\nPipeline complete.")


if __name__ == "__main__":
    main()

import os
import pandas as pd

def process_kaggle_dataset(input_csv_path: str, output_csv_path: str):
           
    if not os.path.exists(input_csv_path):
        raise FileNotFoundError(f"Input dataset not found at {input_csv_path}. Please download it first.")

    print(f"Loading Kaggle dataset from {input_csv_path}...")
    df = pd.read_csv(input_csv_path)

                                                        
                                
                                                                                       
    
    if 'clause_text' not in df.columns or 'clause_status' not in df.columns:
        raise ValueError("The dataset does not contain required 'clause_text' or 'clause_status' columns.")

                
    df = df.dropna(subset=['clause_text', 'clause_status'])

                                          
    df['clause_status'] = df['clause_status'].astype(int)

                                                                                   
                                           
    cleaned_df = df[['clause_text', 'clause_status']].rename(columns={
        'clause_status': 'is_risky'
    })

    print(f"Processed dataset: {len(cleaned_df)} rows.")
    print(f"Class distribution:\n{cleaned_df['is_risky'].value_counts()}")

                              
    os.makedirs(os.path.dirname(output_csv_path), exist_ok=True)
    cleaned_df.to_csv(output_csv_path, index=False)
    print(f"Saved processed dataset to {output_csv_path}.")

if __name__ == "__main__":
    input_file = "data/raw/legal_docs_modified.csv"
    output_file = "data/processed/kaggle_training_data.csv"
    process_kaggle_dataset(input_file, output_file)

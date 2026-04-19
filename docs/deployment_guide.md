# Deployment Guide: RiskContractAnalyzer
**Host Your Legal AI App Publicly (Streamlit Community Cloud)**

To meet project requirements, your application must be publicly accessible.

## Prerequisites
1.  **GitHub Account**: Your code must be pushed to a public GitHub repository.
2.  **Groq API Key**: Ensure you have a valid `GROQ_API_KEY`.

---

## Step 1: Prepare Your Repository
Ensure your project structure includes these essential files:
- `app.py` (Main entry point)
- `requirements.txt` (All dependencies including `groq` and `scikit-learn`)
- `models/best_model.joblib` & `models/vectorizer.joblib` (Pre-trained models)
- `data/knowledge_base/` (JSON files for RAG)

> [!WARNING]  
> Do **NOT** commit `.streamlit/secrets.toml` to GitHub. The API key should be set via the Streamlit Dashboard secrets.

---

## Step 2: Deploy to Streamlit Community Cloud
1.  Go to [share.streamlit.io](https://share.streamlit.io/).
2.  Connect your GitHub account.
3.  Click **"New app"**.
4.  Select your repository, branch (`main`), and main file path (`app.py`).
5.  **Critial Step: Set Secrets**
    - Click **"Advanced settings..."** before deploying.
    - In the **Secrets** section, paste the following:
      ```toml
      GROQ_API_KEY = "your_actual_groq_api_key_here"
      ```
6.  Click **"Deploy!"**.

---

## Step 3: Verify the Deployment
1.  Once the app is live, test the file upload.
2.  Check if the "ML Model" predictor is active.
3.  Verify that the **"AI Deep Analysis"** tab works (this confirms your API key and RAG system are working).

---

## Alternative: Hugging Face Spaces
1. Create a new **Space** on [huggingface.co](https://huggingface.co/).
2. Select **Streamlit** as the SDK.
3. Upload your files or sync with GitHub.
4. Set `GROQ_API_KEY` in the **Settings > Variables and secrets** tab of your Space.

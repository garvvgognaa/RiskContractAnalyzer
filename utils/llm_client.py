import google.generativeai as genai
import streamlit as st
import os
from dotenv import load_dotenv

# Load environment variables if running locally without streamlit secrets
load_dotenv()

class LLMClient:
    """
    Client for interacting with Google Gemini API.
    Handles configuration and model initialization.
    """
    def __init__(self, model_name="gemini-1.5-flash"):
        self.api_key = self._get_api_key()
        if not self.api_key:
            st.error("GEMINI_API_KEY not found. Please set it in .streamlit/secrets.toml or as an environment variable.")
            return

        genai.configure(api_key=self.api_key)
        self.model = genai.GenerativeModel(model_name)

    def _get_api_key(self):
        # Try Streamlit secrets first
        try:
            return st.secrets["GEMINI_API_KEY"]
        except (KeyError, FileNotFoundError, AttributeError):
            # Fallback to environment variable
            return os.getenv("GEMINI_API_KEY")

    def generate_response(self, prompt: str, system_instruction: str = None) -> str:
        """
        Generates a response from the LLM based on the given prompt.
        """
        if not self.model:
            return "LLM not initialized properly."

        try:
            # Use chat session for better context or just generate_content
            if system_instruction:
                # Some versions of genai support system_instruction in initialization
                # For simplicity, we prepend it to the prompt here if not supported
                full_prompt = f"System: {system_instruction}\n\nUser: {prompt}"
            else:
                full_prompt = prompt

            response = self.model.generate_content(full_prompt)
            return response.text
        except Exception as e:
            return f"Error generating LLM response: {str(e)}"

# Smoke test
if __name__ == "__main__":
    client = LLMClient()
    if client.model:
        print("Testing LLM Client...")
        # response = client.generate_response("Say 'Hello, AI Legal Assistant!'")
        # print(f"Response: {response}")
        print("LLM Client initialized successfully.")

   

import os
import streamlit as st
from dotenv import load_dotenv

load_dotenv()


class LLMClient:
           

    def __init__(self, model_name: str = "llama-3.1-8b-instant"):
        self.model_name = model_name
        self.client = None
        self._init_client()

    def _get_api_key(self) -> str | None:
                                                                     
        try:
            return st.secrets["GROQ_API_KEY"]
        except Exception:
            return os.getenv("GROQ_API_KEY")

    def _init_client(self) -> None:
        api_key = self._get_api_key()
        if not api_key:
            print("[LLMClient] WARNING: GROQ_API_KEY not found. AI analysis will be disabled.")
            return
        try:
            from groq import Groq
            self.client = Groq(api_key=api_key)
        except ImportError:
            print("[LLMClient] ERROR: groq package not installed. Run: pip install groq")

    @property
    def is_available(self) -> bool:
        return self.client is not None

    def generate_response(self, prompt: str, system_instruction: str = None) -> str:
                   
        if not self.client:
            return "LLM not available — GROQ_API_KEY missing or groq package not installed."

        messages = []
        if system_instruction:
            messages.append({"role": "system", "content": system_instruction})
        messages.append({"role": "user", "content": prompt})

        try:
            completion = self.client.chat.completions.create(
                model=self.model_name,
                messages=messages,
                temperature=0.3,                                                           
                max_tokens=2048,
            )
            return completion.choices[0].message.content
        except Exception as e:
            return f"Error generating LLM response: {str(e)}"


            
if __name__ == "__main__":
    client = LLMClient()
    if client.is_available:
        print("Testing Groq LLM Client...")
        resp = client.generate_response("Say 'Hello, AI Legal Assistant!' and nothing else.")
        print(f"Response: {resp}")
    else:
        print("LLM Client not initialized — check GROQ_API_KEY.")

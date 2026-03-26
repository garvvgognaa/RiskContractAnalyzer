import enum
import json
import os
from typing import List, Dict, Any, Optional
from utils.llm_client import LLMClient
from utils.retriever import get_relevant_guidelines
from src.agents.prompts import SYSTEM_PROMPT, ANALYSIS_TEMPLATE, REPORT_SUMMARY_TEMPLATE

class AgentState(enum.Enum):
    IDLE = "Idle"
    INITIALIZING = "Initializing"
    ANALYZING = "Analyzing Risks"
    RETRIEVING = "Retrieving Knowledge"
    REPORTING = "Generating Report"
    COMPLETED = "Completed"
    ERROR = "Error"

class LegalAgent:
    def __init__(self):
        self.state = AgentState.IDLE
        self.llm = LLMClient()
        self.history: List[Dict[str, str]] = []
        self.state_callback = None
        self.report = {}

    def set_state(self, state: AgentState):
        self.state = state
        if self.state_callback:
            self.state_callback(state)
        print(f"[Agent Status]: {state.value}")

    def run_analysis(self, document_text: str, clauses: List[Dict[str, Any]]):
        try:
            self.set_state(AgentState.INITIALIZING)
            self.set_state(AgentState.RETRIEVING)
            for clause in clauses:
                if 'text' in clause:
                    guidelines = get_relevant_guidelines(clause['text'])
                    clause['relevant_guidelines'] = [g.get('content', '') for g in guidelines]
                    self.history.append({
                        "action": "retrieve_guidelines",
                        "clause_id": clause.get('id', 'unknown'),
                        "guidelines_found": len(guidelines)
                    })
            
            self.set_state(AgentState.ANALYZING)
            for clause in clauses:
                prompt = ANALYSIS_TEMPLATE.format(
                    clause_text=clause['text'],
                    guidelines="\n".join(clause['relevant_guidelines'])
                )
                response_text = self.llm.generate_response(prompt, system_instruction=SYSTEM_PROMPT)
                try:
                    cleaned_response = response_text.strip().strip('`').strip('json').strip()
                    clause.update(json.loads(cleaned_response))
                except:
                    clause.update({"risk_severity": "Unknown", "explanation": "Failed analysis."})
            
            self.set_state(AgentState.REPORTING)
            self.report = self.generate_report(clauses)
            self.set_state(AgentState.COMPLETED)
            return self.report
        except Exception as e:
            self.set_state(AgentState.ERROR)
            return None

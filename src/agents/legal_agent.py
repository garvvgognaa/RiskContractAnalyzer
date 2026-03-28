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
                except Exception as e:
                    clause.update({
                        "risk_severity": "Unknown",
                        "explanation": "Failed to analyze clause.",
                        "mitigation": "Manual review recommended."
                    })

            self.set_state(AgentState.REPORTING)
            self.report = self.generate_report(clauses)
            self.set_state(AgentState.COMPLETED)
            return self.report
        except Exception as e:
            self.set_state(AgentState.ERROR)
            return None

    def generate_report(self, clauses: List[Dict[str, Any]]) -> Dict[str, Any]:
        clauses_data = json.dumps([{
            "text": c.get('text'),
            "risk_severity": c.get('risk_severity'),
            "explanation": c.get('explanation')
        } for c in clauses], indent=2)
        
        prompt = REPORT_SUMMARY_TEMPLATE.format(clauses_data=clauses_data)
        response_text = self.llm.generate_response(prompt, system_instruction=SYSTEM_PROMPT)
        
        try:
            cleaned_response = response_text.strip().strip('`').strip('json').strip()
            report_meta = json.loads(cleaned_response)
        except Exception as e:
            report_meta = {
                "contract_summary": "Error generating summary.",
                "legal_disclaimer": "AI usage disclaimer: Manual review required."
            }
            
        final_report = {
            "report_metadata": report_meta,
            "risky_clauses": clauses,
            "analysis_history": self.history
        }
        
        os.makedirs("data/reports", exist_ok=True)
        report_path = "data/reports/analysis_report.json"
        with open(report_path, "w") as f:
            json.dump(final_report, f, indent=4)
        
        return final_report

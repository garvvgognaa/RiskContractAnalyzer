import enum
from typing import List, Dict, Any, Optional
from utils.llm_client import LLMClient
from utils.retriever import get_relevant_guidelines

class AgentState(enum.Enum):
    IDLE = "Idle"
    INITIALIZING = "Initializing"
    ANALYZING = "Analyzing Risks"
    RETRIEVING = "Retrieving Knowledge"
    REPORTING = "Generating Report"
    COMPLETED = "Completed"
    ERROR = "Error"

class LegalAgent:
    """
    Main Agentic controller for the Legal Contract Risk Analyzer.
    Maintains state and orchestrates LLM, Retrieval, and Tool usage.
    """
    def __init__(self):
        self.state = AgentState.IDLE
        self.llm = LLMClient()
        self.history: List[Dict[str, str]] = []
        self.state_callback = None # Optional callback to update UI

    def set_state(self, state: AgentState):
        """Update agent state and trigger callback."""
        self.state = state
        if self.state_callback:
            self.state_callback(state)
        print(f"[Agent Status]: {state.value}")

    def run_analysis(self, document_text: str, clauses: List[Dict[str, Any]]):
        """
        Main entry point for running the agentic analysis pipeline.
        This is where the 'reasoning loop' happens.
        """
        try:
            self.set_state(AgentState.INITIALIZING)
            # Placeholder for initial setup or preprocessing
            
            self.set_state(AgentState.ANALYZING)
            # 1. Analyze identified contract risks and patterns
            # (To be implemented by Member 3)
            
            self.set_state(AgentState.RETRIEVING)
            # 2. Retrieve relevant legal guidelines
            for clause in clauses:
                if 'text' in clause:
                    guidelines = get_relevant_guidelines(clause['text'])
                    clause['relevant_guidelines'] = guidelines
                    self.history.append({
                        "action": "retrieve_guidelines",
                        "clause_id": clause.get('id', 'unknown'),
                        "guidelines_found": len(guidelines)
                    })
            
            self.set_state(AgentState.REPORTING)
            # 3. Generate structured contract risk reports
            # (To be implemented by Member 3)
            
            self.set_state(AgentState.COMPLETED)
            
        except Exception as e:
            print(f"Error in Agent reasoning loop: {e}")
            self.set_state(AgentState.ERROR)

# Mock Runner for testing
if __name__ == "__main__":
    agent = LegalAgent()
    agent.run_analysis("Sample contract text", [{"text": "Sample clause", "id": 1}])

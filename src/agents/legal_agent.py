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

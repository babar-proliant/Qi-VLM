# case_context.py

from typing import List, Dict, Optional
from dataclasses import dataclass, field
import threading

_lock = threading.RLock()

@dataclass
class CaseContext:

    patient_id: str = "Unknown"
    symptoms: str = ""
    current_meds: str = ""
    findings: List[Dict] = field(default_factory=list)
    synthesis: str = ""
    case_summary: str = ""
    coherence_level: int = 2
    clinical_scenario: str = "standard_clinical"
    active_specialists: List[str] = field(default_factory=list)
    has_data: bool = False
    
    def clear(self):
        self.patient_id = "Unknown"
        self.symptoms = ""
        self.current_meds = ""
        self.findings = []
        self.synthesis = ""
        self.case_summary = ""
        self.coherence_level = 2
        self.clinical_scenario = "standard_clinical"
        self.active_specialists = []
        self.has_data = False
    
    def build_context_string(self) -> str:
        if not self.has_data:
            return ""
        context_parts = []
        context_parts.append("### CURRENT CASE CONTEXT ###")
        context_parts.append(f"Patient ID: {self.patient_id}")
        context_parts.append(f"Symptoms: {self.symptoms or 'Not provided'}")
        context_parts.append(f"Current Medications: {self.current_meds or 'Not provided'}")
        context_parts.append(f"Case Complexity: Level {self.coherence_level}")
        context_parts.append("")

        if self.findings:
            context_parts.append("### ANALYSIS FINDINGS ###")
            for i, finding in enumerate(self.findings, 1):
                context_parts.append(f"\n--- Finding {i}: {finding.get('file', 'Unknown')} ({finding.get('type', 'Unknown')}) ---")
                context_parts.append(finding.get('result', 'No result'))
            context_parts.append("")
        
        if self.synthesis:
            context_parts.append("### CLINICAL SYNTHESIS ###")
            context_parts.append(self.synthesis)
        
        return "\n".join(context_parts)

_case_context = CaseContext()

def get_case_context() -> CaseContext:
    with _lock:
        return _case_context

def clear_case_context():
    with _lock:
        _case_context.clear()
        print("📋 Case context cleared")


def update_case_context(
    patient_id: str = None,
    symptoms: str = None,
    current_meds: str = None,
    findings: List[Dict] = None,
    synthesis: str = None,
    coherence_level: int = None,
    clinical_scenario: str = None,
    active_specialists: List[str] = None
):
    with _lock:
        if patient_id is not None:
            _case_context.patient_id = patient_id
        if symptoms is not None:
            _case_context.symptoms = symptoms
        if current_meds is not None:
            _case_context.current_meds = current_meds
        if findings is not None:
            _case_context.findings = findings
        if synthesis is not None:
            _case_context.synthesis = synthesis
        if coherence_level is not None:
            _case_context.coherence_level = coherence_level
        if clinical_scenario is not None:
            _case_context.clinical_scenario = clinical_scenario
        if active_specialists is not None:
            _case_context.active_specialists = active_specialists
        
        _case_context.has_data = True
        _case_context.case_summary = _case_context.build_context_string()
        
def has_case_context() -> bool:
    with _lock:
        return _case_context.has_data

def get_case_summary_for_llm() -> str:
    with _lock:
        return _case_context.case_summary

def get_coherence_level() -> int:
    with _lock:
        return _case_context.coherence_level

def get_active_specialists() -> List[str]:
    with _lock:
        return _case_context.active_specialists
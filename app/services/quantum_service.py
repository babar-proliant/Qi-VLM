# quantum_service.py

import json
from typing import Dict, List, Any, Optional, Generator
from .. import config as cfg

try:
    from .quantum_diagnostic_system import (
        QuantumDiagnosticSystem,
        BayesianCollapseEngine,
        CrossModalTensionDetector,
        EvidenceType,
        TensionSeverity,
        DiagnosticHypothesis,
        CrossModalTension
    )
except ImportError:
    from quantum_diagnostic_system import (
        QuantumDiagnosticSystem,
        BayesianCollapseEngine,
        CrossModalTensionDetector,
        EvidenceType,
        TensionSeverity,
        DiagnosticHypothesis,
        CrossModalTension
    )


class QuantumDiagnosticService:
  
    def __init__(self, show_quantum_reasoning: bool = cfg.SHOW_QUANTUM_REASONING):
        self.bayesian_engine = BayesianCollapseEngine()
        self.tension_detector = CrossModalTensionDetector()
        self.diagnostic_system = QuantumDiagnosticSystem()
        self.show_quantum_reasoning = cfg.SHOW_QUANTUM_REASONING
    
    def analyze_case(
        self,
        vision_results: List[Dict[str, Any]],
        patient_data: Dict[str, Any],
        show_quantum_reasoning: bool = cfg.SHOW_QUANTUM_REASONING
    ) -> Dict[str, Any]:

        show_quantum = show_quantum_reasoning if show_quantum_reasoning is not None else self.show_quantum_reasoning
        
        combined_vision = self._combine_vision_results(vision_results)
        
        result = self.diagnostic_system.run_diagnostic_cycle(
            vision_result=combined_vision,
            patient_data=patient_data
        )
        
        return result
    
    def _combine_vision_results(self, results: List[Dict]) -> str:
        combined = []
        for r in results:
            filename = r.get('filename', 'Unknown file')
            result_text = r.get('result', '')
            combined.append(f"--- {filename} ---\n{result_text}")
        return "\n\n".join(combined)
    
    def get_quantum_diagnostic_prompt(
        self,
        vision_results: List[Dict[str, Any]],
        patient_data: Dict[str, Any],
        show_quantum_reasoning: bool = cfg.SHOW_QUANTUM_REASONING
    ) -> str:
        show_quantum = show_quantum_reasoning if show_quantum_reasoning is not None else self.show_quantum_reasoning
        combined_vision = self._combine_vision_results(vision_results)
        
        symptoms = patient_data.get('symptoms', 'Not provided')
        history = patient_data.get('history', patient_data.get('med_history', 'Not provided'))
        medications = patient_data.get('medications', patient_data.get('current_meds', 'Not provided'))
        
        clinical_context = f"""
Patient Symptoms: {symptoms}
Medical History: {history}
Current Medications: {medications}
"""
        
        tensions = self.tension_detector.detect_tension(combined_vision, clinical_context)
        tension_section = self._format_tension_section(tensions)
        
        common_diagnoses = self._infer_common_diagnoses(combined_vision, clinical_context)
        rare_diagnoses = self._infer_rare_diagnoses(combined_vision, clinical_context)
        
        prompt = self._build_professional_prompt(
            combined_vision=combined_vision,
            clinical_context=clinical_context,
            tension_section=tension_section,
            common_diagnoses=common_diagnoses,
            rare_diagnoses=rare_diagnoses,
            tensions=tensions,
            show_quantum_reasoning=cfg.SHOW_QUANTUM_REASONING
        )
        
        return prompt
    
    def _format_tension_section(self, tensions: List[CrossModalTension]) -> str:
        if not tensions:
            return "No significant cross-modal tensions detected. Imaging and clinical findings are consistent."
        
        sections = []
        for t in tensions:
            sections.append(f"""
**{t.tension_type.upper()}** (Severity: {t.severity.value})
- Vision: {t.vision_finding}
- Clinical: {t.clinical_finding}
- Possible Explanations: {', '.join(t.possible_explanations[:2])}
- Recommendation: {t.resolution_recommendation}
""")
        return "\n".join(sections)
    
    def _infer_common_diagnoses(self, vision: str, clinical: str) -> List[str]:
        common = []
        vision_lower = vision.lower()
        clinical_lower = clinical.lower()
        
        if "consolidation" in vision_lower or "opacity" in vision_lower:
            if "fever" in clinical_lower:
                common.append("Bacterial pneumonia")
            common.append("Pneumonia")
        
        if "effusion" in vision_lower:
            if "fever" in clinical_lower:
                common.append("Parapneumonic effusion")
            if "dyspnea" in clinical_lower or "breath" in clinical_lower:
                common.append("Heart failure")
        
        if "cardiomegaly" in vision_lower or "enlarged heart" in vision_lower:
            common.append("Heart failure")
            common.append("Cardiomyopathy")
        
        if "interstitial" in vision_lower or "hazy" in vision_lower:
            common.append("Interstitial Lung Disease")
            common.append("Pulmonary Fibrosis")
        
        if "fracture" in vision_lower:
            common.append("Traumatic fracture")
        
        if "nodule" in vision_lower:
            common.append("Pulmonary nodule (benign or malignant)")
        
        if "ground glass" in vision_lower:
            if "fever" in clinical_lower:
                common.append("Viral pneumonia")
            common.append("Interstitial lung disease")
        
        if not common:
            if "chest pain" in clinical_lower:
                common.extend(["Musculoskeletal pain", "Gastroesophageal reflux"])
            elif "dyspnea" in clinical_lower or "breath" in clinical_lower:
                common.extend(["Asthma", "COPD exacerbation"])
            else:
                common.append("Non-specific findings")
        
        return common[:4]
    
    def _infer_rare_diagnoses(self, vision: str, clinical: str) -> List[str]:
        rare = []
        vision_lower = vision.lower()
        clinical_lower = clinical.lower()
        
        if "consolidation" in vision_lower:
            rare.append("Pulmonary embolism with infarction")
            rare.append("Lung malignancy")
        
        if "effusion" in vision_lower:
            rare.append("Malignant effusion")
        
        if "nodule" in vision_lower or "mass" in vision_lower:
            rare.append("Primary lung cancer")
            rare.append("Metastatic disease")
        
        if "chest pain" in clinical_lower:
            rare.append("Pulmonary embolism")
            rare.append("Aortic dissection")
        
        return rare[:2]
    
    def _build_professional_prompt(
        self,
        combined_vision: str,
        clinical_context: str,
        tension_section: str,
        common_diagnoses: List[str],
        rare_diagnoses: List[str],
        tensions: List[CrossModalTension],
        show_quantum_reasoning: bool = False
    ) -> str:
        quantum_section = ""
        if show_quantum_reasoning:
            quantum_section = self._build_quantum_visible_section(
                common_diagnoses, rare_diagnoses, tensions, combined_vision
            )
        hypotheses_table = "| Rank | Diagnosis | Category | Initial Probability |\n"
        hypotheses_table += "|------|-----------|----------|--------------------|\n"
        
        for i, diag in enumerate(common_diagnoses, 1):
            prob = 0.35 - (i - 1) * 0.05
            hypotheses_table += f"| {i} | {diag} | COMMON | {prob:.0%} |\n"
        
        for i, diag in enumerate(rare_diagnoses, len(common_diagnoses) + 1):
            prob = 0.15 - (i - len(common_diagnoses) - 1) * 0.03
            hypotheses_table += f"| {i} | {diag} | RARE | {prob:.0%} |\n"
        tension_impact = ""
        if tensions:
            tension_impact = """
**IMPORTANT: Cross-Modal Tensions Detected**
The following tensions have been identified and must be addressed:
""" + tension_section
        
        return f"""
You are a BOARD-CERTIFIED PHYSICIAN performing systematic clinical reasoning.
{quantum_section}
════════════════════════════════════════════════════════════════
CLINICAL CASE DATA
════════════════════════════════════════════════════════════════

**Patient Context**: {clinical_context}

**Imaging/Findings**: {combined_vision}

════════════════════════════════════════════════════════════════
CROSS-MODAL ANALYSIS
════════════════════════════════════════════════════════════════
{tension_impact if tension_impact else "Imaging and clinical findings are internally consistent."}

════════════════════════════════════════════════════════════════
DIAGNOSTIC HYPOTHESIS INITIALIZATION
════════════════════════════════════════════════════════════════

{hypotheses_table}

════════════════════════════════════════════════════════════════
REASONING PROCESS
════════════════════════════════════════════════════════════════

**PHASE 1: Evidence Assessment**
For each hypothesis, evaluate supporting and contradicting findings.

**PHASE 2: Probability Update**
Update probabilities based on evidence strength.

**PHASE 3: Cross-Modal Correlation**
Check anatomical and severity correlation.

**PHASE 4: Differential Ranking**
Rank diagnoses by updated probability.

**PHASE 5: Collapse to Final Assessment**
Present primary diagnosis or differential.

════════════════════════════════════════════════════════════════
OUTPUT FORMAT (Professional Clinical Report)
════════════════════════════════════════════════════════════════

**Clinical Assessment**

**Executive Summary**:
[One paragraph: Most likely diagnosis with confidence level]

**Primary Diagnosis**:
**[Diagnosis name]**
- Confidence: [High/Moderate/Low]
- Key supporting evidence: [List 2-3 main findings]

**Differential Diagnosis**:
| Rank | Diagnosis | Probability | Reasoning |
|------|-----------|-------------|-----------|
[Table of alternative diagnoses]

**Evidence Synthesis**:
[How findings combine to support the diagnosis]

**Cross-Modal Considerations**:
[Address any tensions between imaging and clinical data]

**Recommended Workup**:
[List additional tests that would increase diagnostic certainty]

**Clinical Recommendations**:
[Immediate management recommendations]

---

Now generate the complete clinical assessment:

"""
    
    def _build_quantum_visible_section(
        self,
        common_diagnoses: List[str],
        rare_diagnoses: List[str],
        tensions: List[CrossModalTension],
        vision_text: str
    ) -> str:
        all_diagnoses = common_diagnoses + rare_diagnoses
        n_diagnoses = len(all_diagnoses)
        state_vector = "|Ψ₀⟩ = "
        for i, diag in enumerate(all_diagnoses[:4]):
            coef = chr(945 + i)  # α, β, γ, δ
            if i < n_diagnoses - 1:
                state_vector += f"{coef}|{diag}⟩ + "
            else:
                state_vector += f"{coef}|{diag}⟩"
        entanglement_section = ""
        if tensions:
            for t in tensions[:2]:
                entanglement_section += f"""
[{t.vision_finding[:30]}...] ────[ENTANGLED: r=0.{7 if t.severity.value == "high" else 5}]────► [{t.clinical_finding[:30]}...]
"""
        
        return f"""
════════════════════════════════════════════════════════════════
🔬 QUANTUM DIAGNOSTIC ANALYSIS (VISIBLE REASONING)
════════════════════════════════════════════════════════════════

## Phase 0: State Vector Initialization
```
{state_vector}
```
Initial amplitude distribution represents prior probabilities based on prevalence.

## Phase 1: Evidence as Measurement Operators
Each imaging finding acts as a measurement operator M̂ on the state vector.

### Interference Pattern
| Evidence | Effect | Amplitude Change |
|----------|--------|------------------|
| [From imaging] | ↑ constructive / ↓ destructive | Modify α, β, γ, δ |

## Phase 2: Entanglement Mapping
{entanglement_section if entanglement_section else "No strong entanglements detected between findings."}

Explain: "When findings are entangled, a collapse in uncertainty of one will logically affect the other."

## Phase 3: Vacuum States
Identify missing data:
```
|Laboratory⟩ = |∅⟩ (VACUUM STATE)
Impact: Cannot rule out metabolic/infectious etiologies
```

## Phase 4: State Vector Evolution
Show amplitude changes through analysis:
```
Initial:  |Ψ₀⟩ = α|D₁⟩ + β|D₂⟩ + γ|D₃⟩ + δ|D₄⟩
After evidence: |Ψ₁⟩ = α'|D₁⟩ + β'|D₂⟩ + γ'|D₃⟩ + δ'|D₄⟩
```

## Phase 5: Required Collapse Measurements
Tests that would collapse remaining uncertainty:
```
M̂_test → collapses |D₁⟩ vs |D₂⟩
```

---

THEN provide the professional clinical report.

"""

_quantum_service: Optional[QuantumDiagnosticService] = None

def get_quantum_service(show_quantum_reasoning: bool = False) -> QuantumDiagnosticService:
    global _quantum_service
    if _quantum_service is None:
        _quantum_service = QuantumDiagnosticService(show_quantum_reasoning=show_quantum_reasoning)
    return _quantum_service

def get_quantum_synthesis_prompt(
    vision_results: List[Dict[str, Any]],
    symptoms: str = "",
    med_history: str = "",
    current_meds: str = "",
    show_quantum_reasoning: bool = cfg.SHOW_QUANTUM_REASONING
) -> str:
    service = get_quantum_service(show_quantum_reasoning=cfg.SHOW_QUANTUM_REASONING)
    patient_data = {
        "symptoms": symptoms,
        "history": med_history,
        "medications": current_meds
    }
    
    return service.get_quantum_diagnostic_prompt(
        vision_results, 
        patient_data, 
        show_quantum_reasoning=cfg.SHOW_QUANTUM_REASONING
    )


def analyze_with_quantum_reasoning(
    vision_results: List[Dict[str, Any]],
    patient_data: Dict[str, Any],
    show_quantum_reasoning: bool = cfg.SHOW_QUANTUM_REASONING
) -> Dict[str, Any]:
    service = get_quantum_service(show_quantum_reasoning=cfg.SHOW_QUANTUM_REASONING)
    return service.analyze_case(vision_results, patient_data, show_quantum_reasoning)


if __name__ == "__main__":
    
    vision_results = [
        {
            "filename": "chest_xray.png",
            "result": """
Chest X-ray PA and Lateral views:

Findings:
- Right lower lobe consolidation with air bronchograms present
- No pleural effusion identified
- Cardiac silhouette is normal in size and contour
- Lungs otherwise clear bilaterally
- No pneumothorax
- No acute bony abnormality

Impression: Right lower lobe consolidation consistent with pneumonia.
""",
            "confidence": 0.92
        }
    ]
    
    patient_data = {
        "symptoms": "Cough, fever 102°F, right-sided chest pain, shortness of breath x 3 days",
        "history": "Type 2 Diabetes, Hypertension",
        "medications": "Metformin 1000mg BID, Lisinopril 20mg daily"
    }
    
    prompt = get_quantum_synthesis_prompt(
        vision_results=vision_results,
        symptoms=patient_data["symptoms"],
        med_history=patient_data["history"],
        current_meds=patient_data["medications"],
        show_quantum_reasoning=cfg.SHOW_QUANTUM_REASONING
    )
    
    print("="*60)
    print("QUANTUM DIAGNOSTIC PROMPT (WITH VISIBLE REASONING)")
    print("="*60)
    print(prompt[:3000])
    print("\n... [truncated for display] ...")

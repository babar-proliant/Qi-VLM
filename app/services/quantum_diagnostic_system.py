# quantum_diagnostic_system.py

from dataclasses import dataclass, field
from typing import Dict, List, Optional, Tuple, Any
from enum import Enum
import json
import re


class EvidenceType(Enum):
    IMAGING = "imaging"
    LABORATORY = "laboratory"
    SYMPTOMS = "symptoms"
    HISTORY = "history"
    MEDICATIONS = "medications"
    PHYSICAL_EXAM = "physical_exam"

class TensionSeverity(Enum):
    NONE = "none"
    LOW = "low"
    MODERATE = "moderate"
    HIGH = "high"
    CRITICAL = "critical"


@dataclass
class DiagnosticHypothesis:
    name: str
    category: str  # COMMON, RARE, ATYPICAL
    prior_probability: float = 0.0
    posterior_probability: float = 0.0
    supporting_evidence: List[str] = field(default_factory=list)
    contradicting_evidence: List[str] = field(default_factory=list)
    likelihood_ratio: float = 1.0
    clinical_reasoning: str = ""
    
    def to_dict(self) -> dict:
        return {
            "name": self.name,
            "category": self.category,
            "prior_probability": round(self.prior_probability, 3),
            "posterior_probability": round(self.posterior_probability, 3),
            "supporting_evidence": self.supporting_evidence,
            "contradicting_evidence": self.contradicting_evidence,
            "likelihood_ratio": round(self.likelihood_ratio, 3),
            "clinical_reasoning": self.clinical_reasoning
        }


@dataclass
class CrossModalTension:
    vision_finding: str
    clinical_finding: str
    tension_type: str  # "contradiction", "asymmetry", "inconsistency"
    severity: TensionSeverity
    possible_explanations: List[str] = field(default_factory=list)
    resolution_recommendation: str = ""
    
    def to_dict(self) -> dict:
        return {
            "vision_finding": self.vision_finding,
            "clinical_finding": self.clinical_finding,
            "tension_type": self.tension_type,
            "severity": self.severity.value,
            "possible_explanations": self.possible_explanations,
            "resolution_recommendation": self.resolution_recommendation
        }


@dataclass
class DiagnosticState:
    hypotheses: List[DiagnosticHypothesis] = field(default_factory=list)
    collapsed: bool = False
    collapsed_diagnosis: Optional[str] = None
    confidence: float = 0.0
    residual_uncertainty: List[str] = field(default_factory=list)
    
    def to_dict(self) -> dict:
        return {
            "hypotheses": [h.to_dict() for h in self.hypotheses],
            "collapsed": self.collapsed,
            "collapsed_diagnosis": self.collapsed_diagnosis,
            "confidence": round(self.confidence, 3),
            "residual_uncertainty": self.residual_uncertainty
        }

class BayesianCollapseEngine:
  
    def __init__(self, initial_amplitude_range: Tuple[float, float] = (0.15, 0.35)):
        self.initial_amplitude_range = initial_amplitude_range
        self.hypotheses: List[DiagnosticHypothesis] = []
        self.evidence_history: List[Dict] = []
    
    def initialize_hypotheses(
        self, 
        common_diagnoses: List[str],
        rare_diagnoses: List[str] = None,
        atypical_diagnoses: List[str] = None
    ) -> DiagnosticState:
        self.hypotheses = []
        total_hypotheses = len(common_diagnoses) + len(rare_diagnoses or []) + len(atypical_diagnoses or [])
        for diag in common_diagnoses:
            prior = 0.30 + (0.05 * (1 - common_diagnoses.index(diag) / max(len(common_diagnoses), 1)))
            self.hypotheses.append(DiagnosticHypothesis(
                name=diag,
                category="COMMON",
                prior_probability=min(prior, 0.40),
                posterior_probability=min(prior, 0.40)
            ))
        for diag in (rare_diagnoses or []):
            prior = 0.15 + (0.05 * (1 - (rare_diagnoses or []).index(diag) / max(len(rare_diagnoses or []), 1)))
            self.hypotheses.append(DiagnosticHypothesis(
                name=diag,
                category="RARE",
                prior_probability=min(prior, 0.20),
                posterior_probability=min(prior, 0.20)
            ))
        for diag in (atypical_diagnoses or []):
            prior = 0.08 + (0.04 * (1 - (atypical_diagnoses or []).index(diag) / max(len(atypical_diagnoses or []), 1)))
            self.hypotheses.append(DiagnosticHypothesis(
                name=diag,
                category="ATYPICAL",
                prior_probability=min(prior, 0.15),
                posterior_probability=min(prior, 0.15)
            ))
        self._normalize_probabilities()
        return DiagnosticState(hypotheses=self.hypotheses.copy())
    
    def _normalize_probabilities(self):
        total = sum(h.posterior_probability for h in self.hypotheses)
        if total > 0:
            for h in self.hypotheses:
                h.posterior_probability = h.posterior_probability / total
                h.prior_probability = h.prior_probability / total
    
    def apply_evidence(
        self,
        evidence: str,
        evidence_type: EvidenceType,
        constructive_for: List[str] = None,
        destructive_for: List[str] = None,
        likelihood_ratio: float = 1.5
    ) -> DiagnosticState:

        constructive_for = constructive_for or []
        destructive_for = destructive_for or []
        
        self.evidence_history.append({
            "evidence": evidence,
            "type": evidence_type.value if evidence_type else "general",
            "constructive_for": constructive_for,
            "destructive_for": destructive_for,
            "likelihood_ratio": likelihood_ratio
        })
        
        for hypothesis in self.hypotheses:
            if hypothesis.name in constructive_for:
                boost = likelihood_ratio * 0.05
                hypothesis.posterior_probability *= (1 + boost)
                hypothesis.supporting_evidence.append(evidence)
                hypothesis.likelihood_ratio *= likelihood_ratio
            
            if hypothesis.name in destructive_for:
                reduction = likelihood_ratio * 0.03
                hypothesis.posterior_probability *= (1 - min(reduction, 0.5))
                hypothesis.contradicting_evidence.append(evidence)
                hypothesis.likelihood_ratio /= likelihood_ratio
        self._normalize_probabilities()
        return DiagnosticState(hypotheses=self.hypotheses.copy())
    
    def collapse(self, threshold: float = 0.55) -> DiagnosticState:
        if not self.hypotheses:
            return DiagnosticState(collapsed=False)
        sorted_hypotheses = sorted(
            self.hypotheses, 
            key=lambda h: h.posterior_probability, 
            reverse=True
        )
        top_hypothesis = sorted_hypotheses[0]
        can_collapse = (
            top_hypothesis.posterior_probability >= threshold or
            len(self.evidence_history) >= 5  
        )
        
        if can_collapse:
            second_prob = sorted_hypotheses[1].posterior_probability if len(sorted_hypotheses) > 1 else 0
            confidence_gap = top_hypothesis.posterior_probability - second_prob

            residual = [
                h.name for h in sorted_hypotheses[1:]
                if h.posterior_probability > 0.10
            ]
            
            return DiagnosticState(
                hypotheses=sorted_hypotheses,
                collapsed=True,
                collapsed_diagnosis=top_hypothesis.name,
                confidence=min(top_hypothesis.posterior_probability + confidence_gap, 0.95),
                residual_uncertainty=residual
            )
        
        return DiagnosticState(
            hypotheses=sorted_hypotheses,
            collapsed=False,
            residual_uncertainty=[h.name for h in sorted_hypotheses[:3]]
        )
    
    def get_bayesian_collapse_prompt(
        self,
        initial_hypotheses: str,
        new_evidence: str
    ) -> str:

        return f"""
[PHASE: BAYESIAN COLLAPSE]

PRIOR HYPOTHESES (Superposition State):
{initial_hypotheses}

NEW CLINICAL EVIDENCE:
{new_evidence}

BAYESIAN UPDATE INSTRUCTIONS:

1. LIKELIHOOD RATIO CALCULATION:
   For each hypothesis, assess: "How likely is this evidence IF this diagnosis were true?"
   - High likelihood: Evidence strongly supports the diagnosis
   - Low likelihood: Evidence is unusual given the diagnosis
   
2. DESTRUCTIVE INTERFERENCE IDENTIFICATION:
   Which hypothesis becomes mathematically LESS likely due to this evidence?
   - Evidence that contradicts a diagnosis should reduce its probability
   - Example: Normal troponin DESTRUCTS acute MI hypothesis
   
3. PROBABILITY REDISTRIBUTION:
   When one hypothesis loses probability, where does it go?
   - Calculate the posterior probability for each remaining hypothesis
   
4. COLLAPSE DECISION:
   Can we collapse to a single diagnosis?
   - Threshold: >60% probability with clear evidence gap
   - If not, maintain superposition and recommend additional tests

OUTPUT FORMAT:
| Diagnosis | Prior P | Likelihood Ratio | Posterior P | Evidence Impact |
|-----------|---------|------------------|-------------|-----------------|
[Table with all hypotheses]

COLLAPSED DIAGNOSIS: [If threshold reached]
RESIDUAL UNCERTAINTY: [What remains to be ruled out]

EXECUTE THE COLLAPSE.
"""


class CrossModalTensionDetector:

    ASYMMETRY_PATTERNS = {
        "left_right": ["left", "right", "bilateral", "unilateral"],
        "upper_lower": ["upper", "lower", "supra", "infra"],
        "anterior_posterior": ["anterior", "posterior", "front", "back"]
    }
    
    SEVERITY_INDICATORS = {
        "mild": ["mild", "minimal", "slight", "subtle", "early"],
        "moderate": ["moderate", "moderate-severe", "significant"],
        "severe": ["severe", "critical", "extensive", "advanced", "acute"]
    }
    
    def __init__(self):
        self.detected_tensions: List[CrossModalTension] = []
    
    def detect_tension(
        self,
        vision_observations: str,
        clinical_context: str
    ) -> List[CrossModalTension]:

        self.detected_tensions = []
        
        vision_lower = vision_observations.lower()
        clinical_lower = clinical_context.lower()
        
        self._check_lateralization_tension(vision_lower, clinical_lower)
        self._check_severity_tension(vision_lower, clinical_lower)
        self._check_temporal_tension(vision_lower, clinical_lower)
        self._check_presence_tension(vision_lower, clinical_lower)

        return self.detected_tensions
    
    def _check_lateralization_tension(self, vision: str, clinical: str):
        vision_left = "left" in vision
        vision_right = "right" in vision
        clinical_left = "left" in clinical
        clinical_right = "right" in clinical
        
        if vision_left and not vision_right and clinical_right and not clinical_left:
            self.detected_tensions.append(CrossModalTension(
                vision_finding="Left-sided findings on imaging",
                clinical_finding="Right-sided symptoms reported",
                tension_type="asymmetry",
                severity=TensionSeverity.HIGH,
                possible_explanations=[
                    "Data entry error (wrong side documented)",
                    "Referred pain syndrome",
                    "Bilateral process with asymmetric presentation",
                    "Incidental finding on imaging (symptoms from other cause)"
                ],
                resolution_recommendation="Verify symptom laterality with patient. Consider if imaging finding is incidental."
            ))
        
        elif vision_right and not vision_left and clinical_left and not clinical_right:
            self.detected_tensions.append(CrossModalTension(
                vision_finding="Right-sided findings on imaging",
                clinical_finding="Left-sided symptoms reported",
                tension_type="asymmetry",
                severity=TensionSeverity.HIGH,
                possible_explanations=[
                    "Data entry error (wrong side documented)",
                    "Referred pain syndrome",
                    "Bilateral process with asymmetric presentation",
                    "Incidental finding on imaging"
                ],
                resolution_recommendation="Verify symptom laterality with patient. Cross-reference with prior imaging."
            ))
    
    def _check_severity_tension(self, vision: str, clinical: str):
        vision_severity = self._extract_severity(vision)
        clinical_severity = self._extract_severity(clinical)
        
        severity_order = ["mild", "moderate", "severe"]
        
        if vision_severity == "severe" and clinical_severity == "mild":
            self.detected_tensions.append(CrossModalTension(
                vision_finding="Severe imaging findings",
                clinical_finding="Mild/minimal symptoms reported",
                tension_type="severity_mismatch",
                severity=TensionSeverity.MODERATE,
                possible_explanations=[
                    "Chronic condition with patient adaptation",
                    "Early in disease course (imaging precedes symptoms)",
                    "Silent/asymptomatic pathology",
                    "Incidental chronic finding"
                ],
                resolution_recommendation="Consider chronicity of findings. Assess functional status more thoroughly."
            ))
        
        elif vision_severity == "mild" and clinical_severity == "severe":
            self.detected_tensions.append(CrossModalTension(
                vision_finding="Mild imaging findings",
                clinical_finding="Severe symptoms reported",
                tension_type="severity_mismatch",
                severity=TensionSeverity.HIGH,
                possible_explanations=[
                    "Non-imaging diagnosis (functional/metabolic)",
                    "Timing issue (early imaging before radiographic changes)",
                    "Different underlying cause for symptoms",
                    "Pain amplification syndrome"
                ],
                resolution_recommendation="Consider alternative diagnoses not visible on imaging. May need additional workup."
            ))
    
    def _check_temporal_tension(self, vision: str, clinical: str):
        acute_vision = any(term in vision for term in ["acute", "new", "recent", "fresh"])
        chronic_vision = any(term in vision for term in ["chronic", "old", "remote", "healed"])
        acute_clinical = any(term in clinical for term in ["acute", "sudden", "hours", "days"])
        chronic_clinical = any(term in clinical for term in ["chronic", "months", "years", "longstanding"])
        
        if chronic_vision and acute_clinical:
            self.detected_tensions.append(CrossModalTension(
                vision_finding="Chronic imaging findings",
                clinical_finding="Acute symptom presentation",
                tension_type="temporal_mismatch",
                severity=TensionSeverity.MODERATE,
                possible_explanations=[
                    "Acute exacerbation of chronic condition",
                    "New superimposed process not visible yet",
                    "Chronic incidental finding with new unrelated symptoms"
                ],
                resolution_recommendation="Compare with prior imaging. Consider acute-on-chronic presentation."
            ))
    
    def _check_presence_tension(self, vision: str, clinical: str):

        contradictions = [
            ("no effusion", "effusion", "fluid"),
            ("no fracture", "fracture", "fracture"),
            ("no mass", "mass", "mass"),
            ("normal heart size", "cardiomegaly", "heart size"),
            ("clear lungs", "consolidation", "lung opacity"),
        ]
        
        for vision_neg, clinical_pos, finding_name in contradictions:
            if vision_neg in vision and clinical_pos in clinical:
                self.detected_tensions.append(CrossModalTension(
                    vision_finding=f"Imaging shows: {vision_neg}",
                    clinical_finding=f"Clinical context mentions: {clinical_pos}",
                    tension_type="contradiction",
                    severity=TensionSeverity.CRITICAL,
                    possible_explanations=[
                        "Documentation error",
                        "Finding missed on initial imaging review",
                        "Clinical finding from different study/exam",
                        "Terminology mismatch"
                    ],
                    resolution_recommendation=f"Re-review imaging specifically for {finding_name}. Verify clinical documentation."
                ))
    
    def _extract_severity(self, text: str) -> str:
        for level, indicators in self.SEVERITY_INDICATORS.items():
            if any(ind in text for ind in indicators):
                return level
        return "moderate"  
    
    def get_tension_analysis_prompt(
        self,
        vision_observations: str,
        clinical_context: str
    ) -> str:

        detected = self.detect_tension(vision_observations, clinical_context)
        tension_summary = "\n".join([
            f"- {t.tension_type}: {t.vision_finding} vs {t.clinical_finding} [{t.severity.value}]"
            for t in detected
        ]) if detected else "No significant tensions detected."
        
        return f"""
[PHASE: CROSS-MODAL TENSION ANALYSIS]

IMAGE/VISION DATA:
{vision_observations}

CLINICAL CONTEXT:
{clinical_context}

PRE-DETECTED TENSIONS:
{tension_summary}

ANALYSIS INSTRUCTIONS:

1. CLINICAL ASYMMETRY SEARCH:
   - Does imaging laterality match symptom laterality?
   - Example: "Left pain" in chart but "Right opacity" in image = ASYMMETRY
   
2. SEVERITY CALIBRATION:
   - Does imaging severity match clinical severity?
   - Severe symptoms with mild imaging = SUSPECT FUNCTIONAL/ALTERNATIVE CAUSE
   
3. TEMPORAL COHERENCE:
   - Acute symptoms with chronic imaging findings?
   - Chronic symptoms with acute imaging findings?
   
4. PRESENCE/ABSENCE VERIFICATION:
   - Does "no X" in imaging match "X" in clinical notes?
   - This is a CRITICAL contradiction requiring immediate verification

OUTPUT FORMAT:

| Tension Type | Vision Finding | Clinical Finding | Severity | Possible Explanation |
|--------------|----------------|------------------|----------|---------------------|

RESOLUTION RECOMMENDATIONS:
[List specific actions to resolve each tension]

IS THIS A DATA ENTRY ERROR OR COMPLEX PRESENTATION?
[Provide assessment with confidence level]

EXECUTE TENSION ANALYSIS.
"""


class QuantumDiagnosticSystem:
    
    def __init__(self, vision_service=None, llm_service=None):

        self.vision_service = vision_service
        self.llm_service = llm_service
        self.bayesian_engine = BayesianCollapseEngine()
        self.tension_detector = CrossModalTensionDetector()
        self.current_state: Optional[DiagnosticState] = None
        self.tensions: List[CrossModalTension] = []
        self.processing_log: List[str] = []
    
    def run_diagnostic_cycle(
        self,
        image_path: str = None,
        vision_result: str = None,
        patient_data: Dict[str, Any] = None,
        return_prompt_only: bool = False
    ) -> Dict[str, Any]:

        self.processing_log = []
        patient_data = patient_data or {}
        self._log("📸 PHASE 1: OBSERVATION")
        if vision_result:
            self._log("   Using pre-computed vision result")
            vision_observations = vision_result
        elif image_path and self.vision_service:
            self._log("   Running vision model analysis...")
            vision_observations = self._analyze_image(image_path)
        else:
            self._log("   No vision input provided")
            vision_observations = "No imaging data available"
        self._log("🔍 PHASE 2: CROSS-MODAL TENSION")
        clinical_context = self._build_clinical_context(patient_data)
        self.tensions = self.tension_detector.detect_tension(
            vision_observations, 
            clinical_context
        )
        if self.tensions:
            self._log(f"   Detected {len(self.tensions)} tension(s)")
            for t in self.tensions:
                self._log(f"   - {t.tension_type}: {t.severity.value}")
        else:
            self._log("   No significant tensions detected")
        self._log("🌀 PHASE 3: HYPOTHESIS SUPERPOSITION")
        common_diagnoses = self._generate_common_diagnoses(
            vision_observations, 
            patient_data
        )
        rare_diagnoses = self._generate_rare_diagnoses(
            vision_observations, 
            patient_data
        )
        self.current_state = self.bayesian_engine.initialize_hypotheses(
            common_diagnoses=common_diagnoses,
            rare_diagnoses=rare_diagnoses
        )
        self._log(f"   Initialized {len(self.current_state.hypotheses)} hypotheses")
        self._log("📊 PHASE 4: EVIDENCE INTEGRATION")

        self.current_state = self.bayesian_engine.apply_evidence(
            evidence=f"Imaging findings: {vision_observations[:500]}",
            evidence_type=EvidenceType.IMAGING,
            constructive_for=self._get_supported_diagnoses(vision_observations),
            destructive_for=self._get_excluded_diagnoses(vision_observations)
        )
        
        if patient_data.get('symptoms'):
            self.current_state = self.bayesian_engine.apply_evidence(
                evidence=f"Symptoms: {patient_data['symptoms']}",
                evidence_type=EvidenceType.SYMPTOMS,
                constructive_for=self._get_symptom_supported(patient_data['symptoms'])
            )
        
        for tension in self.tensions:
            if tension.severity in [TensionSeverity.HIGH, TensionSeverity.CRITICAL]:
                self.current_state = self.bayesian_engine.apply_evidence(
                    evidence=f"Tension detected: {tension.tension_type}",
                    evidence_type=EvidenceType.PHYSICAL_EXAM,
                    likelihood_ratio=0.7  # Reduces confidence
                )
        
        self._log(f"   Applied {len(self.bayesian_engine.evidence_history)} evidence items")
        self._log("⚡ PHASE 5: BAYESIAN COLLAPSE")
        
        self.current_state = self.bayesian_engine.collapse(threshold=0.55)
        
        if self.current_state.collapsed:
            self._log(f"   Collapsed to: {self.current_state.collapsed_diagnosis}")
            self._log(f"   Confidence: {self.current_state.confidence:.1%}")
        else:
            self._log("   Superposition maintained - insufficient evidence for collapse")
        
        if return_prompt_only:
            return {
                "prompt": self._generate_final_prompt(
                    vision_observations, 
                    clinical_context
                )
            }
        
        return {
            "vision_observations": vision_observations,
            "clinical_context": clinical_context,
            "tensions": [t.to_dict() for t in self.tensions],
            "diagnostic_state": self.current_state.to_dict(),
            "processing_log": self.processing_log,
            "final_report": self._generate_report()
        }
    
    def _log(self, message: str):
        self.processing_log.append(message)
        print(message)
    
    def _analyze_image(self, image_path: str) -> str:
        if self.vision_service:
            return self.vision_service.analyze(image_path)
        return "Vision analysis not available"
    
    def _build_clinical_context(self, patient_data: Dict) -> str:
        parts = []
        if patient_data.get('symptoms'):
            parts.append(f"Symptoms: {patient_data['symptoms']}")
        if patient_data.get('history'):
            parts.append(f"History: {patient_data['history']}")
        if patient_data.get('medications'):
            parts.append(f"Medications: {patient_data['medications']}")
        return "\n".join(parts) if parts else "No clinical context provided"
    
    def _generate_common_diagnoses(
        self, 
        vision: str, 
        patient_data: Dict
    ) -> List[str]:

        common = []
        
        vision_lower = vision.lower()
        
        if "consolidation" in vision_lower or "opacity" in vision_lower:
            common.extend(["Bacterial pneumonia", "Viral pneumonia"])
        if "effusion" in vision_lower:
            common.extend(["Parapneumonic effusion", "Heart failure"])
        if "cardiomegaly" in vision_lower or "enlarged heart" in vision_lower:
            common.extend(["Dilated cardiomyopathy", "Heart failure"])
        if "fracture" in vision_lower:
            common.extend(["Traumatic fracture", "Pathological fracture"])
        if "nodule" in vision_lower or "mass" in vision_lower:
            common.extend(["Pulmonary nodule", "Neoplasm"])
        
        if not common:
            common = ["Normal variant", "Inflammatory process", "Degenerative change"]
        
        return common[:4]
    
    def _generate_rare_diagnoses(
        self, 
        vision: str, 
        patient_data: Dict
    ) -> List[str]:

        rare = []
        
        vision_lower = vision.lower()
        
        if "consolidation" in vision_lower:
            rare.extend(["Pulmonary embolism with infarction", "Lung malignancy"])
        if "effusion" in vision_lower:
            rare.extend(["Malignant effusion", "Tuberculosis"])
        if "cardiomegaly" in vision_lower:
            rare.extend(["Pericardial effusion", "Infiltrative disease"])
        
        return rare[:2]
    
    def _get_supported_diagnoses(self, vision: str) -> List[str]:

        supported = []
        vision_lower = vision.lower()
        
        if "consolidation" in vision_lower:
            supported.append("Bacterial pneumonia")
        if "effusion" in vision_lower:
            supported.append("Parapneumonic effusion")
        if "cardiomegaly" in vision_lower:
            supported.append("Heart failure")
        
        return supported
    
    def _get_excluded_diagnoses(self, vision: str) -> List[str]:

        excluded = []
        vision_lower = vision.lower()
        
        if "no acute" in vision_lower or "normal" in vision_lower:
            excluded.append("Acute pathology")
        if "no effusion" in vision_lower:
            excluded.append("Pleural effusion")
        
        return excluded
    
    def _get_symptom_supported(self, symptoms: str) -> List[str]:

        supported = []
        symptoms_lower = symptoms.lower()
        
        if "fever" in symptoms_lower or "cough" in symptoms_lower:
            supported.append("Bacterial pneumonia")
        if "dyspnea" in symptoms_lower or "shortness of breath" in symptoms_lower:
            supported.append("Heart failure")
        if "chest pain" in symptoms_lower:
            supported.extend(["Pulmonary embolism", "Acute coronary syndrome"])
        
        return supported
    
    def _generate_final_prompt(
        self, 
        vision: str, 
        clinical: str
    ) -> str:
        
        tension_prompt = self.tension_detector.get_tension_analysis_prompt(
            vision, clinical
        )
        
        bayesian_prompt = self.bayesian_engine.get_bayesian_collapse_prompt(
            initial_hypotheses=json.dumps(
                [h.to_dict() for h in self.current_state.hypotheses], 
                indent=2
            ),
            new_evidence=f"{vision}\n\n{clinical}"
        )
        
        return f"""
{'='*60}
QUANTUM DIAGNOSTIC SYNTHESIS
{'='*60}

{tension_prompt}

{'='*60}

{bayesian_prompt}

{'='*60}
PROFESSIONAL OUTPUT REQUIREMENTS:
- Use standard clinical terminology
- Do NOT use quantum/physics terminology in final report
- Provide evidence-based reasoning
- State confidence level explicitly
- List recommended additional tests if uncertainty remains
{'='*60}
"""
    
    def _generate_report(self) -> str:

        if not self.current_state:
            return "No diagnostic analysis performed."
        
        if self.current_state.collapsed:
            report = f"""
**Clinical Assessment**:

**Primary Diagnosis**:
**{self.current_state.collapsed_diagnosis}**
Confidence: {self.current_state.confidence:.0%}

**Diagnostic Reasoning**:
Based on the available clinical and imaging evidence, the most likely diagnosis 
is {self.current_state.collapsed_diagnosis} with {self.current_state.confidence:.0%} confidence.

**Evidence Summary**:
"""
            for h in self.current_state.hypotheses[:3]:
                report += f"\n**{h.name}** ({h.category})\n"
                if h.supporting_evidence:
                    report += f"- Supporting: {', '.join(h.supporting_evidence[:2])}\n"
                if h.contradicting_evidence:
                    report += f"- Contradicting: {', '.join(h.contradicting_evidence[:2])}\n"
            
            if self.current_state.residual_uncertainty:
                report += f"\n**Residual Uncertainty**:\n"
                report += f"Conditions not yet excluded: {', '.join(self.current_state.residual_uncertainty)}\n"
            
            if self.tensions:
                report += f"\n**Cross-Modal Considerations**:\n"
                for t in self.tensions:
                    report += f"- {t.tension_type}: {t.resolution_recommendation}\n"
        
        else:
            report = f"""
**Clinical Assessment**:

**Differential Diagnosis (Superposition State)**:
Unable to collapse to single diagnosis. Multiple hypotheses remain viable:

"""
            for h in self.current_state.hypotheses[:4]:
                report += f"**{h.name}** - Probability: {h.posterior_probability:.1%}\n"
            
            report += f"\n**Recommended Additional Testing**\n"
            report += "Additional evidence needed to resolve diagnostic uncertainty.\n"
        
        return report


def create_quantum_diagnostic_system(vision_service=None, llm_service=None) -> QuantumDiagnosticSystem:
    return QuantumDiagnosticSystem(
        vision_service=vision_service,
        llm_service=llm_service
    )

def analyze_case_quantum(
    vision_result: str,
    patient_data: Dict[str, Any]
) -> Dict[str, Any]:

    system = QuantumDiagnosticSystem()
    return system.run_diagnostic_cycle(
        vision_result=vision_result,
        patient_data=patient_data
    )


if __name__ == "__main__":
    print("="*60)
    print("QUANTUM DIAGNOSTIC SYSTEM - INITIALIZED")
    print("="*60)
    
    result = analyze_case_quantum(
        vision_result="Chest X-ray shows right lower lobe consolidation.",
        patient_data={
            "symptoms": "Cough, fever, right-sided chest pain",
            "history": "Diabetes"
        }
    )
    
    print("\nDiagnostic State:")
    print(json.dumps(result["diagnostic_state"], indent=2))

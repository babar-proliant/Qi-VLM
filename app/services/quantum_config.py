#quantum_config.py

from dataclasses import dataclass, field
from typing import Dict, List, Optional
from enum import Enum


class CoherenceLevel(Enum):
    """Case complexity levels for quantum reasoning."""
    SINGLE_SYSTEM = 1      
    MULTI_SYSTEM = 2       # 2-3 states, moderate uncertainty
    COMPLEX = 3            # 4+ states, extensive entanglement
    CRITICAL = 4           # Maximum uncertainty, vacuum states prevalent


class VerbosityLevel(Enum):
    """Output verbosity levels."""
    MINIMAL = "minimal"       # Key findings only
    STANDARD = "standard"     # Standard clinical output
    DETAILED = "detailed"     # Include reasoning steps
    FULL_QUANTUM = "full"     # Show all quantum phases


@dataclass
class QuantumAmplitudeConfig:
    """Configuration for probability amplitude calculations."""
    
    common_initial_min: float = 0.25
    common_initial_max: float = 0.35
    
    rare_initial_min: float = 0.15
    rare_initial_max: float = 0.25
    
    atypical_initial_min: float = 0.15
    atypical_initial_max: float = 0.25
    
    max_pre_collapse_amplitude: float = 0.60
    
    dampening_threshold: float = 0.10
    
    collapse_threshold: float = 0.05
    
    constructive_boost: float = 0.05
    
    destructive_reduction: float = 0.03

@dataclass
class QuantumPromptConfig:
    
    verbosity: VerbosityLevel = VerbosityLevel.STANDARD
    
    include_phase_0: bool = True   # Wavefunction initialization
    include_phase_1: bool = True   # Data decomposition
    include_phase_2: bool = True   # Entanglement mapping
    include_phase_3: bool = True   # Interference analysis
    include_phase_4: bool = True   # Differential matrix
    include_phase_5: bool = True   # Measurement strategy
    include_phase_6: bool = True   # Educational synthesis
    
    include_modality_guidance: bool = True
    include_specialist_list: bool = True
    require_spectrum_language: bool = True
    max_vision_prompt_tokens: int = 2000
    max_diagnostic_prompt_tokens: int = 3000


@dataclass
class EntanglementPattern:
    name: str
    organs: List[str]
    pathway: str
    hidden_links: List[str]
    clinical_significance: str

DEFAULT_ENTANGLEMENT_PATTERNS: Dict[str, EntanglementPattern] = {
    
    "cardiopulmonary": EntanglementPattern(
        name="Cardiopulmonary Entanglement",
        organs=["Heart", "Lungs", "Pulmonary Vasculature"],
        pathway="Cardiac output → Pulmonary circulation → Gas exchange → Systemic perfusion",
        hidden_links=[
            "Left heart dysfunction → Pulmonary congestion",
            "Pulmonary embolism → Right heart strain",
            "COPD → Cor pulmonale"
        ],
        clinical_significance="Distinguishes cardiac vs pulmonary cause of dyspnea"
    ),
    
    "cardiorenal": EntanglementPattern(
        name="Cardiorenal Entanglement",
        organs=["Heart", "Kidneys", "Vasculature"],
        pathway="Cardiac output → Renal perfusion → Fluid balance → Cardiac preload",
        hidden_links=[
            "Heart failure → Renal hypoperfusion → CKD",
            "CKD → Fluid overload → Heart failure exacerbation",
            "RAAS activation → Combined organ damage"
        ],
        clinical_significance="Explains dual organ dysfunction in cardiorenal syndrome"
    ),
    
    "hepatorenal": EntanglementPattern(
        name="Hepatorenal Entanglement",
        organs=["Liver", "Kidneys", "Portal System"],
        pathway="Liver function → Portal pressure → Renal perfusion → Filtration",
        hidden_links=[
            "Cirrhosis → Portal hypertension → Ascites → Renal hypoperfusion",
            "Hepatorenal syndrome → Functional renal failure",
            "Bilirubin → Nephrotoxicity"
        ],
        clinical_significance="Identifies reversible vs irreversible renal dysfunction"
    ),
    
    "neurocardiac": EntanglementPattern(
        name="Neurocardiac Entanglement",
        organs=["Brain", "Heart", "Autonomic System"],
        pathway="CNS → Autonomic tone → Cardiac rhythm/contractility",
        hidden_links=[
            "Stroke → Arrhythmia (neurogenic stunning)",
            "Seizure → Takotsubo cardiomyopathy",
            "Brainstem lesion → Cardiac conduction defects"
        ],
        clinical_significance="Explains cardiac findings in neurological emergencies"
    ),
    
    "paraneoplastic": EntanglementPattern(
        name="Paraneoplastic Entanglement",
        organs=["Tumor", "Immune System", "Multiple Organs"],
        pathway="Neoplasm → Immune response → Cross-reactivity → Organ damage",
        hidden_links=[
            "Small cell lung cancer → Lambert-Eaton → Neuromuscular",
            "Ovarian cancer → Anti-NMDA → Encephalitis",
            "Lymphoma → Autoimmune hemolysis"
        ],
        clinical_significance="Connects malignancy to unexpected multi-organ findings"
    ),
    
    "sepsis_multiorgan": EntanglementPattern(
        name="Sepsis Multi-Organ Entanglement",
        organs=["Infection Source", "Circulation", "Lungs", "Kidneys", "Liver"],
        pathway="Infection → SIRS → Endothelial dysfunction → Multi-organ failure",
        hidden_links=[
            "Pneumonia → ARDS → Renal hypoxia",
            "UTI → Urosepsis → Cardiac depression",
            "Peritonitis → Third spacing → Hypotension → AKI"
        ],
        clinical_significance="Prioritizes source control and organ support"
    )
}


@dataclass
class VacuumStateConfig:
    vacuum_categories: List[str] = field(default_factory=lambda: [
        "demographics",
        "symptoms",
        "medical_history",
        "medications",
        "imaging",
        "laboratory",
        "vital_signs",
        "physical_exam"
    ])

    vacuum_entropy_multiplier: float = 1.5  # Increases uncertainty when vacuum present
    vacuum_min_amplitude: float = 0.10
    report_vacuum_states: bool = True

@dataclass 
class QuantumConfig:
    amplitude: QuantumAmplitudeConfig = field(default_factory=QuantumAmplitudeConfig)
    prompt: QuantumPromptConfig = field(default_factory=QuantumPromptConfig)
    vacuum: VacuumStateConfig = field(default_factory=VacuumStateConfig)
    
    default_coherence_level: CoherenceLevel = CoherenceLevel.MULTI_SYSTEM
    default_verbosity: VerbosityLevel = VerbosityLevel.STANDARD

    entanglement_patterns: Dict[str, EntanglementPattern] = field(
        default_factory=lambda: DEFAULT_ENTANGLEMENT_PATTERNS
    )
    
    enable_resurrection_analysis: bool = True
    enable_hidden_entanglement_search: bool = True
    enable_specialist_activation: bool = True
    
    max_states_to_maintain: int = 5
    min_states_to_maintain: int = 3

_config: Optional[QuantumConfig] = None

def get_config() -> QuantumConfig:
    global _config
    if _config is None:
        _config = QuantumConfig()
    return _config

def set_config(config: QuantumConfig) -> None:
    global _config
    _config = config

def configure(
    coherence_level: int = 2,
    verbosity: str = "standard",
    max_states: int = 5,
    enable_all_features: bool = True
) -> QuantumConfig:
    
    config = QuantumConfig(
        default_coherence_level=CoherenceLevel(coherence_level),
        default_verbosity=VerbosityLevel(verbosity),
        max_states_to_maintain=max_states,
        enable_resurrection_analysis=enable_all_features,
        enable_hidden_entanglement_search=enable_all_features,
        enable_specialist_activation=enable_all_features
    )
    
    set_config(config)
    return config


PRESET_CONFIGS = {
    "fast_triage": configure(
        coherence_level=1,
        verbosity="minimal",
        max_states=3,
        enable_all_features=False
    ),
    
    "standard_clinical": configure(
        coherence_level=2,
        verbosity="standard",
        max_states=5,
        enable_all_features=True
    ),
    
    "complex_case": configure(
        coherence_level=3,
        verbosity="detailed",
        max_states=5,
        enable_all_features=True
    ),
    
    "teaching_case": configure(
        coherence_level=3,
        verbosity="full",
        max_states=5,
        enable_all_features=True
    ),
    
    "critical_care": configure(
        coherence_level=4,
        verbosity="standard",
        max_states=5,
        enable_all_features=True
    )
}


import json
from pathlib import Path

def load_config_from_file(config_path: str) -> QuantumConfig:
   
    path = Path(config_path)
    if not path.exists():
        return get_config()
    
    with open(path, 'r') as f:
        data = json.load(f)
    
    config = QuantumConfig()
    
    if "default_coherence_level" in data:
        config.default_coherence_level = CoherenceLevel(data["default_coherence_level"])
    
    if "verbosity" in data:
        config.default_verbosity = VerbosityLevel(data["verbosity"])
    
    if "max_states_to_maintain" in data:
        config.max_states_to_maintain = data["max_states_to_maintain"]
    
    if "amplitude" in data:
        for key, value in data["amplitude"].items():
            if hasattr(config.amplitude, key):
                setattr(config.amplitude, key, value)
    
    set_config(config)
    return config

def save_config_to_file(config_path: str) -> None:
    
    config = get_config()
    
    data = {
        "default_coherence_level": config.default_coherence_level.value,
        "verbosity": config.default_verbosity.value,
        "max_states_to_maintain": config.max_states_to_maintain,
        "enable_resurrection_analysis": config.enable_resurrection_analysis,
        "enable_hidden_entanglement_search": config.enable_hidden_entanglement_search,
        "amplitude": {
            "max_pre_collapse_amplitude": config.amplitude.max_pre_collapse_amplitude,
            "constructive_boost": config.amplitude.constructive_boost,
            "destructive_reduction": config.amplitude.destructive_reduction
        }
    }
    
    with open(config_path, 'w') as f:
        json.dump(data, f, indent=2)


if __name__ == "__main__":
    
    print("=" * 60)
    print("QUANTUM DIAGNOSTIC CONFIGURATION")
    print("=" * 60)
    
    config = configure(coherence_level=2, verbosity="standard")
    print(f"\nDefault coherence level: {config.default_coherence_level.name}")
    print(f"Max states: {config.max_states_to_maintain}")
    
    print(f"\nMax pre-collapse amplitude: {config.amplitude.max_pre_collapse_amplitude}")
    print(f"Constructive boost per finding: {config.amplitude.constructive_boost}")
    
    print(f"\nAvailable entanglement patterns: {list(config.entanglement_patterns.keys())}")
    
    cardio = config.entanglement_patterns["cardiopulmonary"]
    print(f"\nCardiopulmonary pathway: {cardio.pathway}")
    print(f"Hidden links: {cardio.hidden_links}")
    
    print("\n" + "=" * 60)
    print("Available presets:", list(PRESET_CONFIGS.keys()))

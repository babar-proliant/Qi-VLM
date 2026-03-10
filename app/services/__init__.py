# services/__init__.py

QUANTUM_SERVICE_AVAILABLE = False
QUANTUM_VISION_PROMPT_AVAILABLE = False
QUANTUM_DIAGNOSTIC_PROMPT_AVAILABLE = False
QUANTUM_CONFIG_AVAILABLE = False
QUANTUM_SYSTEM_AVAILABLE = False

try:
    from .quantum_service import (
        QuantumDiagnosticService,
        get_quantum_service,
        get_quantum_synthesis_prompt,
        analyze_with_quantum_reasoning
    )
    QUANTUM_SERVICE_AVAILABLE = True
except ImportError:
    pass

try:
    from .quantum_vision_prompt import (
        get_vision_prompt,
        get_modality_specific_guidance,
        PRESET_PROMPTS
    )
    QUANTUM_VISION_PROMPT_AVAILABLE = True
except ImportError:
    pass

try:
    from .quantum_diagnostic_prompt import (
        get_diagnostic_prompt,
        get_synthesis_prompt,
        get_chat_followup_prompt,
        get_scenario_prompt,
        CLINICAL_SCENARIOS
    )
    QUANTUM_DIAGNOSTIC_PROMPT_AVAILABLE = True
except ImportError:
    pass

try:
    from .quantum_config import (
        get_config,
        set_config,
        configure,
        QuantumConfig,
        CoherenceLevel,
        VerbosityLevel,
        PRESET_CONFIGS
    )
    QUANTUM_CONFIG_AVAILABLE = True
except ImportError:
    pass

try:
    from .quantum_diagnostic_system import (
        QuantumDiagnosticSystem,
        BayesianCollapseEngine,
        CrossModalTensionDetector,
        create_quantum_diagnostic_system,
        analyze_case_quantum
    )
    QUANTUM_SYSTEM_AVAILABLE = True
except ImportError:
    pass

try:
    from .llm_service import (
        get_llm,
        unload_llm,
        is_llm_loaded
    )
except ImportError:
    pass

try:
    from .vision_service import (
        unload_vision_model,
        is_vision_available,
        is_model_loaded
    )
except ImportError:
    pass


__all__ = [
    "QUANTUM_SERVICE_AVAILABLE",
    "QUANTUM_VISION_PROMPT_AVAILABLE",
    "QUANTUM_DIAGNOSTIC_PROMPT_AVAILABLE",
    "QUANTUM_CONFIG_AVAILABLE",
    "QUANTUM_SYSTEM_AVAILABLE",
]

if QUANTUM_SERVICE_AVAILABLE:
    __all__.extend([
        "QuantumDiagnosticService",
        "get_quantum_service",
        "get_quantum_synthesis_prompt",
        "analyze_with_quantum_reasoning",
    ])

if QUANTUM_VISION_PROMPT_AVAILABLE:
    __all__.extend([
        "get_vision_prompt",
        "get_modality_specific_guidance",
        "PRESET_PROMPTS",
    ])

if QUANTUM_DIAGNOSTIC_PROMPT_AVAILABLE:
    __all__.extend([
        "get_diagnostic_prompt",
        "get_synthesis_prompt",
        "get_chat_followup_prompt",
        "get_scenario_prompt",
        "CLINICAL_SCENARIOS",
    ])

if QUANTUM_CONFIG_AVAILABLE:
    __all__.extend([
        "get_config",
        "set_config",
        "configure",
        "QuantumConfig",
        "CoherenceLevel",
        "VerbosityLevel",
        "PRESET_CONFIGS",
    ])

if QUANTUM_SYSTEM_AVAILABLE:
    __all__.extend([
        "QuantumDiagnosticSystem",
        "BayesianCollapseEngine",
        "CrossModalTensionDetector",
        "create_quantum_diagnostic_system",
        "analyze_case_quantum",
    ])

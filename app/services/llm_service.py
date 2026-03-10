# llm_service.py

import os
from typing import Generator
from llama_cpp import Llama

from .. import config as cfg

try:
    from .quantum_diagnostic_prompt import get_diagnostic_prompt
    QUANTUM_PROMPT_AVAILABLE = True
except ImportError:
    QUANTUM_PROMPT_AVAILABLE = False
    print("⚠️ Warning: quantum_diagnostic_prompt not found. Using fallback logic.")

_llm = None


def get_llm():
    global _llm
    if _llm is None:
        model_path = cfg.LLM_MODEL_PATH

        if not os.path.exists(model_path):
            raise FileNotFoundError(
                f"BioMistral model not found at: {model_path}\n"
                f"Please download it and place it in the models/ directory."
            )

        print(f"Loading BioMistral model from: {model_path}")
        _llm = Llama(
            model_path=model_path,
            n_ctx=8192,
            n_gpu_layers=cfg.GPU_LAYERS,
            verbose=False
        )
        print("✅ BioMistral model loaded successfully.")
    return _llm


def unload_llm():
    global _llm
    if _llm is not None:
        del _llm
        _llm = None
        import gc
        gc.collect()
        print("✅ LLM model unloaded and memory freed")


def _determine_coherence_level(findings: list, symptoms: str = "") -> int:
    num_findings = len(findings) if findings else 0
    symptom_words = len(symptoms.split()) if symptoms else 0
    
    if num_findings <= 1 and symptom_words < 10:
        return 1
    elif num_findings <= 2 and symptom_words < 20:
        return 2
    elif num_findings <= 3 and symptom_words < 30:
        return 3
    else:
        return 4


def analyze_text_or_labs(text, symptoms=""):
    llm = get_llm()

    prompt = f"""[INST]Analyze this clinical text and provide findings:

{text}

Patient Symptoms: {symptoms if symptoms else 'Not provided'}

Provide:
1. SUMMARY
2. ABNORMALITIES  
3. DIFFERENTIALS
4. RECOMMENDATIONS[/INST]"""

    output = llm(prompt, max_tokens=500, temperature=0.2)
    return {
        "summary": output['choices'][0]['text'].strip(),
        "confidence": 0.90
    }


def analyze_text_or_labs_streaming(text: str, symptoms: str = "") -> Generator[str, None, None]:

    yield "__STATUS__:🤖 Loading LLM model..."
    
    try:
        llm = get_llm()
    except Exception as e:
        yield f"__ERROR__:{str(e)}"
        return
    
    yield "__STATUS__:📝 Analyzing document..."
    
    prompt = f"""[INST]You are an expert physician analyzing medical text/document.

TEXT TO ANALYZE:
{text}

PATIENT SYMPTOMS: {symptoms if symptoms else 'Not provided'}

Provide a detailed medical analysis. Extract key findings, interpret values,
and provide clinical recommendations.

OUTPUT FORMAT:

1. SUMMARY: Brief overview of the document
2. KEY FINDINGS: Important observations extracted
3. ABNORMAL VALUES: Any values outside normal range
4. CLINICAL SIGNIFICANCE: What these findings mean
5. RECOMMENDATIONS: Next steps or actions

[/INST]"""
    
    try:
        full_response = ""
        for chunk in llm(
            prompt,
            max_tokens=1024,
            temperature=0.3,
            repeat_penalty=1.1,
            stream=True
        ):
            token = chunk['choices'][0].get('text', '')
            if token:
                full_response += token
                yield token
        
        yield f"__COMPLETE__:{full_response}"
        
    except Exception as e:
        yield f"__ERROR__:{str(e)}"


def chat_with_llm(user_message, history=[]):
    llm = get_llm()

    conversation = "[INST]You are a medical AI assistant.\n"
    for msg in history[-6:]:
        if msg.get('role') == 'user':
            conversation += f"{msg.get('content', '')} [/INST] "
        else:
            conversation += f"{msg.get('content', '')} [INST] "
    conversation += f"{user_message} [/INST]"

    output = llm(conversation, max_tokens=500, temperature=0.3)
    return output['choices'][0]['text'].strip()


def chat_with_llm_streaming(user_message: str, history: list) -> Generator[str, None, None]:

    try:
        llm = get_llm()
    except Exception as e:
        yield f"__ERROR__:{str(e)}"
        return
    
    conversation = "[INST]You are a helpful medical AI assistant. "
    conversation += "You provide accurate, evidence-based medical information. "
    conversation += "Always recommend consulting healthcare professionals for specific medical advice.\n\n"
    
    for msg in history[-5:]:
        role = msg.get('role', 'user')
        content = msg.get('content', '')
        if role == 'user':
            conversation += f"User: {content}\n"
        else:
            conversation += f"Assistant: {content}\n"
    
    conversation += f"User: {user_message}\nAssistant: [/INST]"
    
    try:
        full_response = ""
        for chunk in llm(
            conversation,
            max_tokens=512,
            temperature=0.4,
            repeat_penalty=1.1,
            stream=True
        ):
            token = chunk['choices'][0].get('text', '')
            if token:
                full_response += token
                yield token
        
        yield f"__COMPLETE__:{full_response}"
        
    except Exception as e:
        yield f"__ERROR__:{str(e)}"


def synthesize_case(symptoms, current_meds, findings, show_quantum_reasoning=cfg.SHOW_QUANTUM_REASONING):
    llm = get_llm()
    findings_text = ""
    for f in (findings or []):
        findings_text += f"File: {f.get('file', 'Unknown')} ({f.get('type', 'Unknown')})\n"
        findings_text += f"Finding: {f.get('result', 'No result')}\n"
        findings_text += f"Confidence: {f.get('confidence', 0)*100:.0f}%\n\n"
    if not findings_text.strip():
        return "No clinical findings available."
    coherence_level = _determine_coherence_level(findings, symptoms)
    prompt = _build_synthesis_prompt(
        findings_text=findings_text,
        symptoms=symptoms,
        current_meds=current_meds,
        coherence_level=coherence_level,
        show_quantum_reasoning=show_quantum_reasoning
    )

    print(f"\n{'='*60}")
    print(f"🤖 SYNTHESIZE - Generating clinical summary...")
    print(f"🔬 show_quantum_reasoning = {show_quantum_reasoning}")
    print(f"{'='*60}\n")

    full_response = ""
    for chunk in llm(
        prompt,
        max_tokens=4096,  
        temperature=0.4,
        top_p=0.9,
        repeat_penalty=1.0,
        stream=True
    ):
        token = chunk['choices'][0].get('text', '')
        full_response += token
        print(token, end='', flush=True)
    
    print("\n")
    print(f"\n✅ Generated {len(full_response)} characters")

    return full_response.strip()


def synthesize_case_streaming(
    symptoms: str, 
    current_meds: str, 
    findings: list,
    show_quantum_reasoning: bool = cfg.SHOW_QUANTUM_REASONING
) -> Generator[str, None, None]:
    yield "__STATUS__:🤖 Loading LLM model..."
    
    try:
        llm = get_llm()
    except Exception as e:
        yield f"__ERROR__:{str(e)}"
        return
    
    findings_text = ""
    for f in (findings or []):
        findings_text += f"File: {f.get('file', 'Unknown')} ({f.get('type', 'Unknown')})\n"
        findings_text += f"Finding: {f.get('result', 'No result')}\n"
        findings_text += f"Confidence: {f.get('confidence', 0)*100:.0f}%\n\n"

    if not findings_text.strip():
        yield "__COMPLETE__:No clinical findings available."
        return
    
    yield f"__STATUS__:📝 Generating clinical summary (quantum_reasoning={show_quantum_reasoning})..."
    
    coherence_level = _determine_coherence_level(findings, symptoms)
    
    prompt = _build_synthesis_prompt(
        findings_text=findings_text,
        symptoms=symptoms,
        current_meds=current_meds,
        coherence_level=coherence_level,
        show_quantum_reasoning=show_quantum_reasoning
    )
    
    try:
        print(f"\n{'='*60}")
        print(f"🤖 SYNTHESIZE STREAMING - Generating clinical summary...")
        print(f"🔬 show_quantum_reasoning = {show_quantum_reasoning}")
        print(f"{'='*60}\n")
        
        full_response = ""
        for chunk in llm(
            prompt,
            max_tokens=4096,  
            temperature=0.4,
            top_p=0.9,
            repeat_penalty=1.0,
            stream=True
        ):
            token = chunk['choices'][0].get('text', '')
            if token:
                full_response += token
                yield token
                print(token, end='', flush=True)
        
        print(f"\n\n✅ Generated {len(full_response)} characters")
        yield f"__COMPLETE__:{full_response}"
        
    except Exception as e:
        yield f"__ERROR__:{str(e)}"


def _build_synthesis_prompt(
    findings_text: str,
    symptoms: str,
    current_meds: str,
    coherence_level: int = 2,
    show_quantum_reasoning: bool = cfg.SHOW_QUANTUM_REASONING
) -> str:

    if QUANTUM_PROMPT_AVAILABLE:
        print("🔬 Using quantum_diagnostic_prompt module for LLM prompt generation.")
        return get_diagnostic_prompt(
            age_gender="Unknown",  
            med_history="Not provided", 
            symptoms=symptoms,
            current_meds=current_meds,
            findings_text=findings_text,
            coherence_level=coherence_level,
            show_quantum_reasoning=show_quantum_reasoning
        )
    
    print("⚠️ Quantum prompt module missing, using fallback.")
    
    quantum_section = ""
    if show_quantum_reasoning:
        quantum_section = """
# 🔬 QUANTUM DIAGNOSTIC ANALYSIS (VISIBLE REASONING)

You MUST show your quantum reasoning process using mathematical notation:

## Phase 0: State Vector Initialization
Initialize diagnostic superposition with multiple hypotheses:
|Ψ₀⟩ = α|Diagnosis₁⟩ + β|Diagnosis₂⟩ + γ|Diagnosis₃⟩ + δ|Diagnosis₄⟩

## Phase 1: Evidence as Measurement Operators
Show interference tables for findings.

## Phase 2: Entanglement Mapping
Show correlations between findings.

## Phase 3: Vacuum State Handling
Identify missing data.

## Phase 4: State Vector Evolution
Show amplitude changes.

## Phase 5: Collapse to Probability
Convert amplitudes to probabilities.

---
AFTER showing quantum reasoning, provide the professional clinical report.

"""
    
    prompt = f"""[INST]You are **MEDICAL POLYMATH — QUANTUM DIAGNOSTIC REASONING ENGINE**.
{quantum_section}

# PATIENT DATA

Symptoms: {symptoms}
Current Medications: {current_meds}

Findings:
{findings_text}

Provide a comprehensive clinical analysis.
[/INST]
"""
    
    return prompt



def synthesize_with_quantum_service(
    vision_results: list,
    symptoms: str = "",
    med_history: str = "",
    current_meds: str = "",
    show_quantum_reasoning: bool = cfg.SHOW_QUANTUM_REASONING
) -> Generator[str, None, None]:

    yield "__STATUS__:🔄 Using Quantum Diagnostic Service..."
    
    try:
        from .quantum_service import get_quantum_synthesis_prompt
    except ImportError:
        from quantum_service import get_quantum_synthesis_prompt

    prompt = get_quantum_synthesis_prompt(
        vision_results=vision_results,
        symptoms=symptoms,
        med_history=med_history,
        current_meds=current_meds,
        show_quantum_reasoning=cfg.SHOW_QUANTUM_REASONING
    )
    
    llm_prompt = f"[INST]{prompt}[/INST]"
    
    try:
        llm = get_llm()
    except Exception as e:
        yield f"__ERROR__:{str(e)}"
        return
    
    try:
        print(f"\n{'='*60}")
        print(f"🔬 QUANTUM SERVICE - Generating clinical summary...")
        print(f"🔬 show_quantum_reasoning = {cfg.SHOW_QUANTUM_REASONING}")
        print(f"{'='*60}\n")
        
        full_response = ""
        for chunk in llm(
            llm_prompt,
            max_tokens=4096,
            temperature=0.4,
            top_p=0.9,
            repeat_penalty=1.0,
            stream=True
        ):
            token = chunk['choices'][0].get('text', '')
            if token:
                full_response += token
                yield token
                print(token, end='', flush=True)
        
        print(f"\n\n✅ Generated {len(full_response)} characters")
        yield f"__COMPLETE__:{full_response}"
        
    except Exception as e:
        yield f"__ERROR__:{str(e)}"
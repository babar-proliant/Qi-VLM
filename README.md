<div align="center">

<img src="https://img.shields.io/badge/Python-3.10+-3776AB?style=for-the-badge&logo=python&logoColor=white" alt="Python"/>
<img src="https://img.shields.io/badge/FastAPI-0.100+-009688?style=for-the-badge&logo=fastapi&logoColor=white" alt="FastAPI"/>
<img src="https://img.shields.io/badge/Streamlit-1.28+-FF4B4B?style=for-the-badge&logo=streamlit&logoColor=white" alt="Streamlit"/>
<img src="https://img.shields.io/badge/CUDA-11.8+-76B900?style=for-the-badge&logo=nvidia&logoColor=white" alt="CUDA"/>
<img src="https://img.shields.io/badge/License-MIT-F7DF1E?style=for-the-badge" alt="License"/>


## ⚠️ I feel a need to enhance, it is hidden for sometime, will public full code soon



# Qi-VLM 

### Quantum-Informed Vision-Language Model for Clinical Diagnostics

**A novel medical AI system that combines Quantum State Mechanics with Vision-Language Models for transparent, uncertainty-aware clinical reasoning.**

[Features](#-key-features) • [Architecture](#-architecture) • [Installation](#-installation) • [Usage](#-usage) • [Documentation](#-documentation)

</div>

<img width="1899" height="940" alt="Screenshot 2026-03-11 122937" src="https://github.com/user-attachments/assets/97d43f83-b6f8-467a-afb3-02bfccb84100" />


---

## 🎯 The Problem with Medical AI Today

Standard AI models in medical imaging face critical limitations that hinder clinical adoption:

| Challenge | Impact on Clinical Practice |
|-----------|----------------------------|
| **Black Box Reasoning** | Clinicians cannot verify or trust AI conclusions |
| **Uncertainty Blindness** | Models produce overconfident predictions on ambiguous cases |
| **Artifact Hallucination** | X-rays with wires, tubes, or noise trigger false positives |
| **Context Isolation** | Each image analyzed independently, ignoring clinical context |
| **Missing Data Handling** | Absence of laboratory data treated as "normal" rather than unknown |

> *"A chest X-ray showing a pacemaker shouldn't just say 'foreign object detected'—it should understand the entanglement between cardiac pathology and medical devices."*

---

## 💡 The Quantum-Informed Solution

Qi-VLM introduces a **Bayesian Collapse Engine** that treats medical diagnosis as a quantum measurement problem—where multiple diagnostic hypotheses exist in superposition until clinical evidence forces collapse to a definitive conclusion.

### The Quantum Analogy

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                     QUANTUM DIAGNOSTIC REASONING                            │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                             │
│   State Vector Initialization                                               │
│   ┌─────────────────────────────────────────────────────────────────────┐   │
│   │  |Ψ₀⟩ = 0.35|Pneumonia⟩ + 0.25|Heart Failure⟩ + 0.20|COPD⟩            │   │
│   │        + 0.12|Pulmonary Embolism⟩ + 0.08|Malignancy⟩                 │   │
│   └─────────────────────────────────────────────────────────────────────┘   │
│                              ↓ Evidence Applied                             │
│   ┌─────────────────────────────────────────────────────────────────────┐   │
│   │  Measurement Operator M̂ (e.g., "Right Lower Lobe Consolidation")    │   │
│   │  • Constructive Interference: ↑ Pneumonia amplitude                 │   │
│   │  • Destructive Interference: ↓ Heart Failure amplitude              │   │
│   └─────────────────────────────────────────────────────────────────────┘   │
│                              ↓ State Collapse                               │
│   ┌─────────────────────────────────────────────────────────────────────┐   │
│   │  COLLAPSED STATE: |Ψ_final⟩ = |Bacterial Pneumonia⟩                  │   │
│   │  Confidence: 62%    Residual Uncertainty: 28% Viral                 │   │
│   └─────────────────────────────────────────────────────────────────────┘   │
│                                                                             │
└─────────────────────────────────────────────────────────────────────────────┘
```

### Key Innovations

| Quantum Concept | Medical Application | Clinical Benefit |
|-----------------|--------------------|------------------|
| **Superposition** | Multiple diagnoses held simultaneously | Avoids premature diagnostic closure |
| **Entanglement** | Cross-organ correlation modeling | "Cardiomegaly predicts pulmonary congestion" |
| **Measurement Operators** | Clinical evidence as amplitude modifiers | Transparent evidence-to-diagnosis mapping |
| **Vacuum States** | Missing data = high entropy, not "normal" | Explicit uncertainty quantification |
| **Wave Function Collapse** | Bayesian probability redistribution | Confidence-calibrated final diagnosis |

---

## 🚀 Key Features

### Core Capabilities

- **Multi-Modal Medical Image Analysis** — X-rays, CT scans, MRIs, ECGs, and more
- **Streaming Inference** — Real-time token-by-token output with progress indicators
- **Multi-File Case Synthesis** — Upload multiple images for comprehensive case analysis
- **Interactive Consultation** — Chat with AI about analyzed cases

### Quantum Reasoning Features

- **Visible State Evolution** — Watch diagnostic hypotheses evolve in real-time
- **Cross-Modal Tension Detection** — Identifies contradictions between imaging and clinical data
- **Bayesian Probability Updates** — Evidence-based probability redistribution
- **Vacuum State Reporting** — Explicit acknowledgment of missing data impact

### Production Features

- **Edge AI Optimized** — Runs entirely on local hardware (patient data never leaves your machine)
- **GPU Memory Management** — Dynamic model loading/unloading for resource efficiency
- **Streaming API** — Server-Sent Events for responsive user experience

---

## 🏗️ Architecture

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                           Qi-VLM Architecture                               │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                             │
│   ┌──────────────┐      ┌──────────────────┐      ┌─────────────────┐       │
│   │   Streamlit  │─────►│   FastAPI Backend │────►│   Vision Model  │       │
│   │   Frontend   │      │   (Streaming)     │     │  Qwen2.5-VL-7B  │       │
│   └──────────────┘      └────────┬─────────┘      └─────────────────┘       │
│                                   │                                         │
│                                   ▼                                         │
│   ┌─────────────────────────────────────────────────────────────────────┐   │
│   │                     QUANTUM DIAGNOSTIC ENGINE                       │   │
│   │  ┌────────────────────────┐  ┌────────────────────────────────────┐ │   │
│   │  │  Bayesian Collapse     │  │   Cross-Modal Tension Detector     │ │   │
│   │  │       Engine           │  │                                    │ │   │
│   │  │                        │  │   • Lateralization Tension         │ │   │
│   │  │  • State Vectors       │  │   • Severity Mismatch              │ │   │
│   │  │  • Evidence Operators  │  │   • Temporal Inconsistency         │ │   │
│   │  │  • Collapse Logic      │  │   • Presence Contradiction         │ │   │
│   │  └────────────────────────┘  └────────────────────────────────────┘ │   │
│   └─────────────────────────────────────────────────────────────────────┘   │
│                                   │                                         │
│                                   ▼                                         │
│   ┌─────────────────────────────────────────────────────────────────────┐   │
│   │                       LLM Synthesis Layer                           │   │
│   │                     Mistral-7B-Instruct (GGUF)                      │   │
│   │              Clinical Report Generation + Consultation              │   │
│   └─────────────────────────────────────────────────────────────────────┘   │
│                                                                             │
└─────────────────────────────────────────────────────────────────────────────┘
```

---

## 📊 Quantum vs Classical Output Comparison

### Classical AI Output (Black Box)

```
════════════════════════════════════════════════════════════════
IMAGING ANALYSIS REPORT
════════════════════════════════════════════════════════════════

Findings:
- Right lower lobe consolidation with air bronchograms
- Cardiac silhouette within normal limits
- No pleural effusion

Impression: Right lower lobe consolidation, most likely pneumonia.
Confidence: Moderate
════════════════════════════════════════════════════════════════
```

### Qi-VLM Output (Transparent Reasoning)

```
════════════════════════════════════════════════════════════════
🔬 QUANTUM DIAGNOSTIC ANALYSIS (VISIBLE REASONING)
════════════════════════════════════════════════════════════════

## Phase 0: State Vector Initialization
|Ψ₀⟩ = 0.35|Bacterial Pneumonia⟩ + 0.25|Viral Pneumonia⟩ + 
       0.20|Heart Failure⟩ + 0.12|Pulmonary Embolism⟩ + 0.08|Malignancy⟩

## Phase 1: Evidence as Measurement Operators

| Evidence                 | Operator | Affected States         | Amplitude Change  |
|--------------------------|----------|-------------------------|-------------------|
| "RLL consolidation"      | M̂₁       | Bacterial Pneumonia⟩    | α: 0.35 → 0.48 ↑  |
|                          |          | Heart Failure⟩          | γ: 0.20 → 0.08 ↓  |
| "Fever 102°F"            | M̂₂       | Bacterial Pneumonia⟩    | α: 0.48 → 0.56 ↑  |
| "No pleural effusion"    | M̂₄       | Heart Failure⟩          | γ: 0.04 → 0.02 ↓  |

## Phase 3: Vacuum State Handling
|Laboratory: WBC⟩ = |∅⟩ (VACUUM STATE)
Impact: Cannot differentiate bacterial vs viral etiology
Uncertainty bound: ±12%

## Phase 5: Collapse to Probability
COLLAPSED DIAGNOSIS: Bacterial Pneumonia
CONFIDENCE: 62% (Moderate-High)
RESIDUAL UNCERTAINTY: 28% Viral Pneumonia

════════════════════════════════════════════════════════════════
```

### Comparison Summary

| Feature | Classical AI | Qi-VLM Quantum-Informed |
|---------|--------------|-------------------------|
| **Diagnosis** | Single output | Ranked with probabilities |
| **Reasoning** | Hidden | Fully visible 6-phase process |
| **Uncertainty** | Ignored | Quantified explicitly |
| **Missing Data** | Assumed normal | Treated as vacuum states |
| **Alternatives** | Not discussed | Full differential retained |
| **Confidence** | Qualitative ("Moderate") | Quantified (62%) |

---

## 🔬 Diagnostic Phase Evolution

Qi-VLM processes clinical cases through **6 distinct phases**, each producing transparent, verifiable outputs:

```
┌──────────────────────────────────────────────────────────────────────────────┐
│                        DIAGNOSTIC PHASE EVOLUTION                            │
├──────────────────────────────────────────────────────────────────────────────┤
│                                                                              │
│  PHASE 0: State Vector Initialization                                        │
│  ┌────────────────────────────────────────────────────────────────────-────┐ │
│  │ Initialize diagnostic superposition based on imaging findings           │ │
│  │ |Ψ₀⟩ = Σᵢ αᵢ|Diagnosisᵢ⟩  where Σ|αᵢ|² = 1                               │ │
│  └────────────────────────────────────────────────────────────────────────-┘ │
│                              ↓                                               │
│  PHASE 1: Evidence as Measurement Operators                                  │
│  ┌───────────────────────────────────────────────────────────────────────-─┐ │
│  │ Each clinical finding acts as operator M̂ on state vector                │ │
│  │ M̂ₖ |ψ⟩ → Updated amplitudes via constructive/destructive interference    │ │
│  └───────────────────────────────────────────────────────────────────────-─┘ │
│                              ↓                                               │
│  PHASE 2: Entanglement Mapping                                               │
│  ┌────────────────────────────────────────────────────────────────────────-┐ │
│  │ Cross-correlations between findings (e.g., Cardiomegaly ↔ Congestion)   │ │
│  │ [Finding A] ────[ENTANGLED: r=0.89]────► [Finding B]                    │ │
│  └────────────────────────────────────────────────────────────────────────-┘ │
│                              ↓                                               │
│  PHASE 3: Vacuum State Handling                                              │
│  ┌───────────────────────────────────────────────────────────────────────-─┐ │
│  │ Missing data = |∅⟩ (not "normal")                                       │ │
│  │ Shannon entropy: H(vacuum) = -Σpᵢ log₂(pᵢ) × λ_vacuum                   │ │
│  └────────────────────────────────────────────────────────────────────────-┘ │
│                              ↓                                               │
│  PHASE 4: State Vector Evolution                                             │
│  ┌────────────────────────────────────────────────────────────────────-────┐ │
│  │ Track probability redistribution:                                       │ │
│  │ T₀ → T₁ → T₂ → ... → T_final (e.g., P(Bacterial): 35% → 62%)            │ │
│  └───────────────────────────────────────────────────────────────────────-─┘ │
│                              ↓                                               │
│  PHASE 5: Bayesian Collapse                                                  │
│  ┌───────────────────────────────────────────────────────────────────────-─┐ │
│  │ Collapse triggered when: P(top hypothesis) > threshold (default 55%)    │ │
│  │ Output: Final diagnosis + confidence + residual uncertainty             │ │
│  └───────────────────────────────────────────────────────────────────────-─┘ │
│                                                                              │
└──────────────────────────────────────────────────────────────────────────────┘
```

---

## 🖥️ Hardware Requirements

Qi-VLM is optimized for **local workstation inference**, ensuring patient data privacy:

| Component | Minimum Specification | Recommended | Purpose |
|-----------|----------------------|-------------|---------|
| **CPU** | Intel Xeon E-2286M or equivalent | AMD Threadripper | DICOM processing, OCR |
| **GPU** | NVIDIA Quadro RTX 5000 (16GB) | RTX 4090 (24GB) | Vision + LLM inference |
| **RAM** | 32GB DDR4 | 64GB DDR4 | Model loading, multi-file cases |
| **Storage** | 50GB SSD | 100GB NVMe | Model weights (~25GB total) |

### Performance Benchmarks

| Operation | Time (RTX 5000) | Time (RTX 4090) |
|-----------|-----------------|-----------------|
| Single X-ray Analysis | 8-15 seconds | 4-8 seconds |
| Multi-file Case (3 images) | 45-90 seconds | 25-50 seconds |
| Full Diagnostic Reasoning | < 4 minutes | < 2 minutes |
| Chat Response | 2-5 seconds | 1-3 seconds |

---

## 📦 Installation

### Prerequisites

- Python 3.10+
- CUDA 11.8+ (for GPU inference)
- Tesseract OCR (for PDF processing)
- Poppler (for PDF to image conversion)

### Quick Start

```bash
# 1. Clone repository
git clone https://github.com/YOUR_USERNAME/qi-vlm.git
cd qi-vlm

# 2. Create virtual environment
python -m venv venv
source venv/bin/activate  # Linux/Mac
# or: venv\Scripts\activate  # Windows

# 3. Install dependencies
pip install -r requirements.txt

# 4. Start backend server
cd app
python -m uvicorn main:app --host 0.0.0.0 --port 8000

# 5. Start frontend (new terminal)
streamlit run streamlit_app.py
```

### Model Downloads

Models are automatically downloaded from Hugging Face on first run:

| Model | Size | Purpose |
|-------|------|---------|
| Qwen/Qwen2.5-VL-7B-Instruct | ~15GB | Vision-language understanding |
| Mistral-7B-Instruct-v0.2.Q4_K_M.gguf | ~4GB | Clinical report synthesis |

Manual placement:
```
models/
├── qwen2.5-vl-7b-instruct/
│   ├── config.json
│   ├── model.safetensors
│   └── ...
└── mistral-7b-instruct-v0.2.Q4_K_M.gguf
```

---

## 🎮 Usage

### Web Interface

1. Open browser to `http://localhost:8501`
2. Upload medical image (X-ray, CT, MRI, ECG, etc.)
3. Enter clinical context (symptoms, history, medications)
4. Watch real-time quantum reasoning unfold
5. Review comprehensive diagnostic report

### API Usage

#### Streaming Analysis Endpoint

```python
import requests

# Single file analysis with streaming
files = {"file": open("chest_xray.png", "rb")}
data = {"symptoms": "Cough, fever, chest pain"}

response = requests.post(
    "http://localhost:8000/analyze_stream",
    files=files,
    data=data,
    stream=True
)

for line in response.iter_lines(decode_unicode=True):
    if line.startswith('data:'):
        print(line[5:])  # Real-time tokens
```

#### Multi-File Case Analysis

```python
# Upload multiple files for comprehensive case synthesis
files = [
    ("files", open("xray_pa.png", "rb")),
    ("files", open("xray_lateral.png", "rb")),
]
data = {"symptoms": "Progressive dyspnea, orthopnea"}

response = requests.post(
    "http://localhost:8000/analyze_case_stream",
    files=files,
    data=data,
    stream=True
)
```

### API Endpoints

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/analyze` | POST | Single file analysis |
| `/analyze_stream` | POST | Single file with streaming response |
| `/analyze_case_stream` | POST | Multi-file case analysis |
| `/chat` | POST | Standard chat interaction |
| `/chat_stream` | POST | Streaming chat |
| `/health` | GET | System health status |
| `/context/status` | GET | Current case context |
| `/context/clear` | POST | Clear case context |
| `/quantum/status` | GET | Quantum reasoning status |

---

## 📁 Project Structure

```
qi-vlm/
├── app/
│   ├── main.py                      # FastAPI application entry point
│   ├── config.py                    # Configuration constants
│   ├── case_context.py              # Multi-turn case management
│   ├── file_types.py                # Medical file type definitions
│   ├── streaming_service.py         # Streaming utilities
│   └── services/
│       ├── __init__.py              # Service exports
│       ├── model_downloader.py      # Hugging Face model download
│       ├── model_manager.py         # GPU memory management
│       ├── image_service.py         # Medical image analysis
│       ├── vision_service.py        # Vision model wrapper
│       ├── llm_service.py           # LLM model wrapper
│       ├── ocr_service.py           # PDF/image OCR
│       ├── ct_mri_service.py        # DICOM processing
│       ├── ecg_service.py           # ECG/Echo analysis
│       ├── quantum_config.py        # Quantum reasoning config
│       ├── quantum_service.py       # Quantum diagnostic service
│       ├── quantum_vision_prompt.py # Vision prompts
│       ├── quantum_diagnostic_prompt.py  # LLM prompts
│       └── quantum_diagnostic_system.py  # Core reasoning engine
├── streamlit_app.py                 # Web UI
├── models/                          # Model weights (gitignored)
├── docs/
│   ├── TECHNICAL_DETAILS.md         # Deep technical documentation
│   ├── PHASE_EVOLUTION.md           # Visual phase evolution examples
│   └── QUANTUM_VS_CLASSICAL.md      # Output comparison examples
├── examples/                        # Example inputs/outputs
├── requirements.txt
├── .gitignore
└── README.md
```

---

## 🔬 Technical Highlights

### Cross-Modal Tension Detection

Qi-VLM detects four types of data conflicts between imaging and clinical context:

| Tension Type | Definition | Severity | Example |
|--------------|------------|----------|---------|
| **Lateralization** | Left/right mismatch | HIGH | Left lung opacity, right chest pain |
| **Severity Mismatch** | Imaging ≠ clinical severity | MODERATE-HIGH | Severe effusion, mild dyspnea |
| **Temporal Inconsistency** | Acute imaging, chronic symptoms | MODERATE | Chronic fracture, acute pain |
| **Presence Contradiction** | "No X" vs "X" in notes | CRITICAL | "No effusion" vs "effusion noted" |

### Entanglement Patterns

Predefined cross-organ correlation patterns:

| Pattern | Organs | Clinical Significance |
|---------|--------|----------------------|
| **Cardiopulmonary** | Heart, Lungs | Distinguishes cardiac vs pulmonary dyspnea |
| **Cardiorenal** | Heart, Kidneys | Cardiorenal syndrome diagnosis |
| **Hepatorenal** | Liver, Kidneys | HRS identification |
| **Neurocardiac** | Brain, Heart | Neurogenic cardiac injury |
| **Paraneoplastic** | Tumor, Immune | Occult malignancy detection |

---

## 📚 Documentation

| Document | Description |
|----------|-------------|
| **[Technical Details](docs/TECHNICAL_DETAILS.md)** | Deep dive into quantum mechanics concepts, Bayesian inference, and implementation |
| **[Phase Evolution](docs/PHASE_EVOLUTION.md)** | Visual examples of state vector evolution |
| **[Quantum vs Classical](docs/QUANTUM_VS_CLASSICAL.md)** | Side-by-side output comparison |
| **[Examples](examples/)** | Sample inputs and outputs |

---

## ⚠️ Clinical Disclaimer

> **This system is for Clinical Decision Support ONLY.**
>
> Qi-VLM is designed to **assist** healthcare professionals, not replace them. All outputs should be reviewed by qualified medical personnel. This tool:
> - Does NOT provide definitive diagnoses
> - Should NOT be used as the sole basis for treatment decisions
> - Is intended for educational and research purposes only
> - Must comply with local healthcare AI regulations

---

## 🤝 Contributing

We welcome contributions! Please see our [Contributing Guidelines](CONTRIBUTING.md) for details on:

- Code of Conduct
- Development setup
- Pull request process
- Coding standards

---

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

---

## 🙏 Acknowledgments

- **Qwen Team** — Qwen2.5-VL vision-language model
- **Mistral AI** — Mistral-7B foundation model
- **Hugging Face** — Model hosting and transformers library
- **FastAPI** & **Streamlit** — Excellent tooling for AI applications

---

## 📊 Citation

If you use Qi-VLM in your research, please cite:

```bibtex
@software{qi_vlm_2026,
  title = {Qi-VLM: Quantum-Informed Vision-Language Model for Clinical Diagnostics},
  author = {Babar Ali},
  year = {2026},
  url = {https://github.com/babar-proliant/Qi-VLM}
}
```

---

<div align="center">

### Built with ❤️ for the future of transparent medical AI

**[⬆ Back to Top](#qi-vlm)**

</div>

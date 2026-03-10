# Qi-VLM
Next-generation Medical VLM using Quantum State Mechanics to bridge the gap between Computer Vision and Clinical Logic.


my LLM made below readme, check and polish it further:

# Qi-VLM: Quantum-Informed Vision-Language Model for Clinical Diagnostics

<div align="center">

![Python](https://img.shields.io/badge/Python-3.10+-blue.svg)
![FastAPI](https://img.shields.io/badge/FastAPI-0.100+-green.svg)
![Streamlit](https://img.shields.io/badge/Streamlit-1.28+-red.svg)
![License](https://img.shields.io/badge/License-MIT-yellow.svg)
![CUDA](https://img.shields.io/badge/CUDA-11.8+-brightgreen.svg)

**A novel medical AI system that combines Quantum State Mechanics with Vision-Language Models for transparent, uncertainty-aware clinical reasoning.**

[Features](#-key-features) • [Architecture](#-architecture) • [Installation](#-installation) • [Usage](#-usage) • [Technical Details](docs/TECHNICAL_DETAILS.md)

</div>

---

## 🎯 The Problem

Standard AI models in medical imaging face critical limitations:

| Challenge | Impact |
|-----------|--------|
| **Black Box Reasoning** | Clinicians cannot verify AI conclusions |
| **Uncertainty Blindness** | Models produce overconfident predictions on ambiguous data |
| **Artifact Hallucination** | X-rays with wires, tubes, or noise trigger false positives |
| **Context Isolation** | Each image analyzed independently, ignoring clinical context |

> *"A chest X-ray showing a pacemaker shouldn't just say 'foreign object detected'—it should understand the entanglement between cardiac pathology and medical devices."*

---

## 💡 The Solution: Quantum-Informed Reasoning

Qi-VLM introduces a **Bayesian Collapse Engine** that treats medical diagnosis as a quantum measurement problem:

### State Vector Initialization
```
|Ψ₀⟩ = α|Pneumonia⟩ + β|Heart Failure⟩ + γ|COPD⟩ + δ|PE⟩
```
Multiple diagnostic hypotheses are maintained in superposition until evidence forces collapse.

### Entanglement Mapping
```
[Cardiomegaly] ────[ENTANGLED: r=0.89]────► [Pulmonary Congestion]
```
Cross-modal correlations between imaging findings are explicitly modeled.

### Vacuum State Handling
```
|Laboratory Data⟩ = |∅⟩ (VACUUM STATE)
```
Missing information is treated as uncertainty, not assumption of normality.

---

## 🚀 Key Features

### Core Capabilities
- **Multi-Modal Medical Image Analysis**: X-rays, CT scans, MRIs, ECGs, and more
- **Streaming Inference**: Real-time token-by-token output with progress indicators
- **Multi-File Case Synthesis**: Upload multiple images for comprehensive case analysis
- **Interactive Consultation**: Chat with AI about analyzed cases

### Quantum Reasoning Features
- **Visible State Evolution**: Watch diagnostic hypotheses evolve in real-time
- **Cross-Modal Tension Detection**: Identifies contradictions between imaging and clinical data
- **Bayesian Probability Updates**: Evidence-based probability redistribution

### Production Features
- **Edge AI Optimized**: Runs entirely on local hardware (patient data never leaves your machine)
- **GPU Memory Management**: Dynamic model loading/unloading for resource efficiency
- **Streaming API**: Server-Sent Events for responsive user experience

---

## 🏗️ Architecture

```
┌─────────────────────────────────────────────────────────────────────┐
│                         Qi-VLM Architecture                         │
├─────────────────────────────────────────────────────────────────────┤
│                                                                     │
│  ┌─────────────┐    ┌──────────────────┐    ┌─────────────────┐   │
│  │   Streamlit │───►│   FastAPI Backend │───►│  Vision Model   │   │
│  │   Frontend  │    │   (Streaming)     │    │ Qwen2.5-VL-7B   │   │
│  └─────────────┘    └────────┬─────────┘    └─────────────────┘   │
│                              │                                      │
│                              ▼                                      │
│  ┌─────────────────────────────────────────────────────────────┐   │
│  │              QUANTUM DIAGNOSTIC ENGINE                       │   │
│  │  ┌────────────────────┐  ┌────────────────────────────────┐ │   │
│  │  │ Bayesian Collapse  │  │  Cross-Modal Tension Detector  │ │   │
│  │  │     Engine         │  │                                │ │   │
│  │  │                    │  │  • Lateralization Tension      │ │   │
│  │  │ • State Vectors    │  │  • Severity Mismatch           │ │   │
│  │  │ • Evidence Ops     │  │  • Temporal Inconsistency      │ │   │
│  │  │ • Collapse Logic   │  │  • Presence Contradiction      │ │   │
│  │  └────────────────────┘  └────────────────────────────────┘ │   │
│  └─────────────────────────────────────────────────────────────┘   │
│                              │                                      │
│                              ▼                                      │
│  ┌─────────────────────────────────────────────────────────────┐   │
│  │                    LLM Synthesis Layer                       │   │
│  │                   BioMistral-7B (GGUF)                       │   │
│  │           Clinical Report Generation + Consultation          │   │
│  └─────────────────────────────────────────────────────────────┘   │
│                                                                     │
└─────────────────────────────────────────────────────────────────────┘
```

---

## 🖥️ Hardware Optimization

Qi-VLM is optimized for **local workstation inference**, ensuring patient data privacy:

| Component | Specification | Purpose |
|-----------|---------------|---------|
| **CPU** | Intel Xeon E-2286M | DICOM processing, OCR |
| **GPU** | NVIDIA Quadro RTX 5000 (16GB) | Vision + LLM inference |
| **RAM** | 32GB+ DDR4 | Model loading, multi-file cases |
| **Storage** | 50GB+ SSD | Model weights (~25GB total) |

### Performance Benchmarks
| Operation | Time |
|-----------|------|
| Single X-ray Analysis | 8-15 seconds |
| Multi-file Case (3 images) | 45-90 seconds |
| Full Diagnostic Reasoning | < 4 minutes end-to-end |
| Chat Response | 2-5 seconds |

---

## 📦 Installation

### Prerequisites
- Python 3.10+
- CUDA 11.8+ (for GPU inference)
- Tesseract OCR (for PDF processing)
- Poppler (for PDF to image conversion)

### 1. Clone Repository
```bash
git clone https://github.com/YOUR_USERNAME/qi-vlm.git
cd qi-vlm
```

### 2. Create Virtual Environment
```bash
python -m venv venv
source venv/bin/activate  # Linux/Mac
# or
venv\Scripts\activate  # Windows
```

### 3. Install Dependencies
```bash
pip install -r requirements.txt
```

### 4. Download Models

The application will automatically download models on first run, or manually:

```python
# Models are downloaded from Hugging Face
# Vision: Qwen/Qwen2.5-VL-7B-Instruct
# LLM: Mistral-7B-Instruct-v0.2 (GGUF format)
```

Place models in:
```
models/
├── qwen2.5-vl-7b-instruct/    # Vision model (~15GB)
│   ├── config.json
│   ├── model.safetensors
│   └── ...
└── mistral-7b-instruct-v0.2.Q4_K_M.gguf  # LLM (~4GB)
```

---

## 🎮 Usage

### Start Backend Server
```bash
cd app
python -m uvicorn main:app --host 0.0.0.0 --port 8000
```

### Start Frontend
```bash
streamlit run streamlit_app.py
```

### Access Application
Open browser to `http://localhost:8501`

---

## 📊 API Endpoints

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

### Example: Streaming Analysis
```python
import requests

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
        print(line[5:])
```

---

## 📁 Project Structure

```
qi-vlm/
├── app/
│   ├── main.py                    # FastAPI application entry point
│   ├── config.py                  # Configuration constants
│   ├── case_context.py            # Multi-turn case management
│   ├── file_types.py              # Medical file type definitions
│   ├── streaming_service.py       # Streaming utilities
│   └── services/
│       ├── __init__.py            # Service exports
│       ├── model_downloader.py    # Hugging Face model download
│       ├── model_manager.py       # GPU memory management
│       ├── image_service.py       # Medical image analysis
│       ├── vision_service.py      # Vision model wrapper
│       ├── llm_service.py         # LLM model wrapper
│       ├── ocr_service.py         # PDF/image OCR
│       ├── ct_mri_service.py      # DICOM processing
│       ├── ecg_service.py         # ECG/Echo analysis
│       ├── quantum_config.py      # Quantum reasoning config
│       ├── quantum_service.py     # Quantum diagnostic service
│       ├── quantum_vision_prompt.py    # Vision prompts
│       ├── quantum_diagnostic_prompt.py # LLM prompts
│       └── quantum_diagnostic_system.py # Core reasoning engine
├── streamlit_app.py               # Web UI
├── models/                        # Model weights (gitignored)
├── docs/
│   └── TECHNICAL_DETAILS.md       # Deep technical documentation
├── examples/                      # Example inputs/outputs
├── requirements.txt
├── .gitignore
└── README.md
```

---

## 🔬 Technical Highlights

### Quantum Diagnostic Phases

| Phase | Operation | Output |
|-------|-----------|--------|
| **Phase 0** | State Vector Initialization | \|Ψ₀⟩ = Σᵢ αᵢ\|Diagnosisᵢ⟩ |
| **Phase 1** | Evidence as Measurement Operators | M̂ₖ \|ψ⟩ → Updated amplitudes |
| **Phase 2** | Entanglement Mapping | Cross-correlation matrix |
| **Phase 3** | Vacuum State Handling | Uncertainty quantification |
| **Phase 4** | State Vector Evolution | \|Ψₜ⟩ progression |
| **Phase 5** | Bayesian Collapse | Final probability distribution |
| **Phase 6** | Clinical Synthesis | Professional report |

### Cross-Modal Tension Detection

The system detects four types of data conflicts:

1. **Lateralization Tension**: Left-sided imaging vs right-sided symptoms
2. **Severity Mismatch**: Mild imaging vs severe symptoms (or vice versa)
3. **Temporal Inconsistency**: Acute imaging vs chronic presentation
4. **Presence Contradiction**: "No effusion" in report vs "effusion" in clinical notes

---

## 📚 Documentation

- **[Technical Details](docs/TECHNICAL_DETAILS.md)**: Deep dive into quantum mechanics concepts, Bayesian inference, and implementation details
- **[API Reference](docs/API_REFERENCE.md)**: Complete API documentation
- **[Examples](examples/)**: Sample inputs and outputs demonstrating quantum reasoning

---

## ⚠️ Disclaimer

> **This system is for Clinical Decision Support ONLY.**
> 
> Qi-VLM is designed to assist healthcare professionals, not replace them. All outputs should be reviewed by qualified medical personnel. This tool:
> - Does NOT provide definitive diagnoses
> - Should NOT be used as the sole basis for treatment decisions
> - Is intended for educational and research purposes
> - Must comply with local healthcare AI regulations

---

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

---

## 🙏 Acknowledgments

- **Qwen Team** for the Qwen2.5-VL vision-language model
- **Mistral AI** for the Mistral-7B foundation model
- **Hugging Face** for model hosting and transformers library
- **FastAPI** and **Streamlit** communities for excellent tooling

---

<div align="center">

**Built with ❤️ for the future of transparent medical AI**

[⬆ Back to Top](#qi-vlm-quantum-informed-vision-language-model-for-clinical-diagnostics)

</div>

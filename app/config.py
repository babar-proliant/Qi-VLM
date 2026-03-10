# config.py

import os

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
MODELS_DIR = os.path.join(BASE_DIR, "models")
VISION_MODEL_PATH = os.path.join(MODELS_DIR, "qwen2.5-vl-7b-instruct")
LLM_MODEL_PATH = os.path.join(MODELS_DIR, "mistral-7b-instruct-v0.2.Q4_K_M.gguf")
TESSERACT_PATH = os.path.join(MODELS_DIR, r"tesseract\tesseract.exe")
POPPLER_PATH = os.path.join(MODELS_DIR, r"poppler\Library\bin")
UPLOAD_DIR = os.environ.get("UPLOAD_DIR", "temp_uploads")

try:
    import torch
    TORCH_DEVICE = "cuda" if torch.cuda.is_available() else "cpu"
    GPU_LAYERS = 35 if TORCH_DEVICE == "cuda" else 0
except ImportError:
    TORCH_DEVICE = "cpu"
    GPU_LAYERS = 0

KEEP_MODELS_LOADED = True
SHOW_QUANTUM_REASONING = True

VISION_MAX_TOKENS = 1000
VISION_MIN_TOKENS = 80

LLM_CONTEXT_SIZE = 8192
LLM_MAX_TOKENS_ANALYSIS = 1024
LLM_MAX_TOKENS_SYNTHESIS = 2048
LLM_MAX_TOKENS_CHAT = 512

API_HOST = "0.0.0.0"
API_PORT = 8000

MAX_FILE_SIZE = 50 * 1024 * 1024  

STREAM_TIMEOUT_SECONDS = 3600  

class StatusMessages:
    VISION_LOADING = "🧠 Loading vision model..."
    VISION_ANALYZING = "📸 Analyzing image with Vision LLM..."
    LLM_LOADING = "🤖 Loading LLM model..."
    LLM_ANALYZING = "📝 Analyzing document..."
    LLM_SYNTHESIZING = "📝 Generating clinical summary..."
    PDF_EXTRACTING = "📄 Extracting text from PDF..."
    FILE_SAVING = "📁 Saving uploaded file..."
    COMPLETE = "✅ Analysis complete!"
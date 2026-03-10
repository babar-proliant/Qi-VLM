# model_manager.py

import os
import gc
import threading
import logging
from typing import Optional, Tuple, Any
from concurrent.futures import ThreadPoolExecutor

from .config import MODELS_DIR, GPU_LAYERS, LLM_MODEL_PATH, VISION_MODEL_PATH

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

_model_lock = threading.RLock()

_vision_processor = None
_vision_model = None
_vision_loaded = False

_llm = None
_llm_loaded = False

_executor = ThreadPoolExecutor(max_workers=2, thread_name_prefix="model_loader")


def get_vision_model_paths() -> Tuple[str, str]:
    model_path = os.environ.get(
        "VISION_MODEL_PATH",
        os.path.join(MODELS_DIR, VISION_MODEL_PATH)
    )
    lora_path = os.path.join(model_path, "lora_adapter")
    return model_path, lora_path

def _load_vision_model_internal() -> Tuple[Any, Any]:
    global _vision_processor, _vision_model, _vision_loaded

    if _vision_loaded and _vision_model is not None:
        logger.info("♻️ Reusing loaded vision model")
        return _vision_processor, _vision_model

    try:
        import torch
        from transformers import AutoProcessor, BitsAndBytesConfig

        model_path, lora_path = get_vision_model_paths()
        has_lora = os.path.exists(lora_path)

        if not os.path.exists(model_path):
            raise FileNotFoundError(f"Vision model not found at: {model_path}")

        logger.info(f"Loading Qwen2.5-VL Medical from: {model_path}")

        try:
            from transformers import Qwen2_5_VLForConditionalGeneration
            model_class = Qwen2_5_VLForConditionalGeneration
        except ImportError:
            try:
                from transformers import Qwen2VLForConditionalGeneration
                model_class = Qwen2VLForConditionalGeneration
            except ImportError:
                from transformers import AutoModelForVision2Seq
                model_class = AutoModelForVision2Seq

        bnb_config = BitsAndBytesConfig(
            load_in_4bit=True,
            bnb_4bit_compute_dtype=torch.float16,
            bnb_4bit_use_double_quant=True,
            bnb_4bit_quant_type="nf4",
        )

        device = "cuda" if torch.cuda.is_available() else "cpu"
        device_map = {"": 0} if device == "cuda" else "auto"

        _vision_model = model_class.from_pretrained(
            model_path,
            quantization_config=bnb_config,
            torch_dtype=torch.float16,
            device_map=device_map,
            trust_remote_code=True,
        )

        if has_lora:
            try:
                from peft import PeftModel
                _vision_model = PeftModel.from_pretrained(
                    _vision_model,
                    lora_path,
                    device_map=device_map,
                )
                logger.info("✅ LoRA adapter loaded")
            except Exception as e:
                logger.warning(f"LoRA loading failed: {e}")

        _vision_processor = AutoProcessor.from_pretrained(
            model_path,
            trust_remote_code=True,
        )

        _vision_model.eval()
        _vision_loaded = True

        if torch.cuda.is_available():
            vram_gb = torch.cuda.memory_allocated(0) / (1024**3)
            logger.info(f"✅ Vision model loaded (VRAM: {vram_gb:.1f}GB)")
        else:
            logger.info("✅ Vision model loaded (CPU mode)")

        return _vision_processor, _vision_model

    except Exception as e:
        logger.error(f"Vision model load failed: {e}")
        _vision_loaded = False
        raise


def get_vision_model() -> Tuple[Any, Any]:
    with _model_lock:
        return _load_vision_model_internal()

def unload_vision_model():

    global _vision_processor, _vision_model, _vision_loaded

    with _model_lock:
        if _vision_model is None and _vision_processor is None:
            logger.info("ℹ️ Vision model already unloaded")
            return

        logger.info("🔄 Unloading vision model to free VRAM...")

        if _vision_model is not None:
            try:
                import torch
                if hasattr(_vision_model, 'to'):
                    _vision_model.to('cpu')
            except Exception:
                pass

            if hasattr(_vision_model, 'free'):
                try:
                    _vision_model.free()
                except Exception:
                    pass
            del _vision_model
            _vision_model = None

        if _vision_processor is not None:
            del _vision_processor
            _vision_processor = None

        _vision_loaded = False

        gc.collect()

        try:
            import torch
            if torch.cuda.is_available():
                torch.cuda.empty_cache()
                torch.cuda.ipc_collect()
                vram_gb = torch.cuda.memory_allocated(0) / (1024**3)
                logger.info(f"✅ Vision model unloaded (VRAM now: {vram_gb:.1f}GB)")
        except ImportError:
            logger.info("✅ Vision model unloaded")


def is_vision_loaded() -> bool:
    with _model_lock:
        return _vision_loaded and _vision_model is not None


def get_llm_model_path() -> str:
    return os.environ.get(
        "LLM_MODEL_PATH",
        os.path.join(MODELS_DIR, LLM_MODEL_PATH)
    )

def _load_llm_internal() -> Any:

    global _llm, _llm_loaded

    if _llm_loaded and _llm is not None:
        logger.info("♻️ Reusing loaded LLM model")
        return _llm

    try:
        from llama_cpp import Llama

        model_path = get_llm_model_path()

        if not os.path.exists(model_path):
            raise FileNotFoundError(f"LLM model not found at: {model_path}")

        logger.info(f"Loading Mistral from: {model_path}")

        n_gpu_layers = GPU_LAYERS

        _llm = Llama(
            model_path=model_path,
            n_ctx=8192,
            n_gpu_layers=n_gpu_layers,
            verbose=False
        )

        _llm_loaded = True
        logger.info("✅ LLM model loaded (will stay loaded)")

        return _llm

    except Exception as e:
        logger.error(f"LLM model load failed: {e}")
        _llm_loaded = False
        raise


def get_llm() -> Any:
    with _model_lock:
        return _load_llm_internal()

def is_llm_loaded() -> bool:
    with _model_lock:
        return _llm_loaded and _llm is not None

def preload_llm_only():
    logger.info("=" * 60)
    logger.info("🚀 PRELOADING LLM MODEL (Vision loads on demand)...")
    logger.info("=" * 60)

    try:
        get_llm()
    except Exception as e:
        logger.warning(f"LLM model preload failed: {e}")

    logger.info("=" * 60)
    logger.info("✅ LLM PRELOADED - Ready for requests")
    logger.info("=" * 60)

def get_model_status() -> dict:
    with _model_lock:
        cuda_available = False
        vram_used = 0
        try:
            import torch
            cuda_available = torch.cuda.is_available()
            if cuda_available:
                vram_used = torch.cuda.memory_allocated(0) / (1024**3)
        except ImportError:
            pass

        return {
            "vision_loaded": _vision_loaded,
            "llm_loaded": _llm_loaded,
            "cuda_available": cuda_available,
            "vram_used_gb": round(vram_used, 2),
        }
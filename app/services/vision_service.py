# vision_service.py

import os
import gc
import base64
import io
import logging
import re
from typing import Dict, Optional, Generator
from PIL import Image
import numpy as np

from .. import config as cfg

try:
    from .quantum_vision_prompt import get_vision_prompt, get_modality_specific_guidance, PRESET_PROMPTS
    QUANTUM_PROMPTS_AVAILABLE = True
except ImportError:
    QUANTUM_PROMPTS_AVAILABLE = False

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

_VISION_PROCESSOR = None
_VISION_MODEL = None
_VISION_AVAILABLE = None

DEVICE = "cuda" if cfg.TORCH_DEVICE == "cuda" else "cpu"


def is_vision_available() -> bool:
    global _VISION_AVAILABLE
    if _VISION_AVAILABLE is None:
        model_path = cfg.VISION_MODEL_PATH
        if os.path.exists(model_path):
            _VISION_AVAILABLE = True
            logger.info(f"✅ Qwen2.5-VL Medical vision model found at: {model_path}")
        else:
            _VISION_AVAILABLE = False
            logger.warning(f"⚠️ Vision model not found at: {model_path}")
    return _VISION_AVAILABLE


def get_vision_model():
    global _VISION_PROCESSOR, _VISION_MODEL
    
    if _VISION_MODEL is not None and _VISION_PROCESSOR is not None:
        logger.info("♻️ Reusing loaded vision model")
        return _VISION_PROCESSOR, _VISION_MODEL
    
    if not is_vision_available():
        return None, None
    
    try:
        import torch
        from transformers import AutoProcessor, BitsAndBytesConfig
        
        model_path = cfg.VISION_MODEL_PATH
        logger.info(f"Loading Qwen2.5-VL Medical from: {model_path}")
        
        try:
            from transformers import Qwen2_5_VLForConditionalGeneration
            model_class = Qwen2_5_VLForConditionalGeneration
        except:
            try:
                from transformers import Qwen2VLForConditionalGeneration
                model_class = Qwen2VLForConditionalGeneration
            except:
                from transformers import AutoModelForVision2Seq
                model_class = AutoModelForVision2Seq
        
        lora_path = os.path.join(model_path, "lora_adapter")
        has_lora = os.path.exists(lora_path)
        
        bnb_config = BitsAndBytesConfig(
            load_in_4bit=True,
            bnb_4bit_compute_dtype=torch.float16,
            bnb_4bit_use_double_quant=True,
            bnb_4bit_quant_type="nf4",
        )
        
        _VISION_MODEL = model_class.from_pretrained(
            model_path,
            quantization_config=bnb_config,
            torch_dtype=torch.float16,
            device_map={"": 0},
            trust_remote_code=True,
        )
        
        if has_lora:
            try:
                from peft import PeftModel
                _VISION_MODEL = PeftModel.from_pretrained(
                    _VISION_MODEL,
                    lora_path,
                    device_map={"": 0},
                )
                logger.info("✅ LoRA adapter loaded")
            except Exception as e:
                logger.warning(f"LoRA loading failed: {e}")
        
        _VISION_PROCESSOR = AutoProcessor.from_pretrained(
            model_path,
            trust_remote_code=True,
        )
        
        _VISION_MODEL.eval()
        
        vram_gb = torch.cuda.memory_allocated(0) / (1024**3)
        logger.info(f"✅ Vision model loaded (VRAM {vram_gb:.1f}GB)")
        
        return _VISION_PROCESSOR, _VISION_MODEL
    
    except Exception as e:
        logger.error(f"Vision model load failed: {e}")
        return None, None


def unload_vision_model():
    global _VISION_PROCESSOR, _VISION_MODEL
    
    if _VISION_MODEL is None and _VISION_PROCESSOR is None:
        logger.info("ℹ️ Vision model already unloaded")
        return
    
    if _VISION_MODEL is not None:
        if hasattr(_VISION_MODEL, 'free'):
            _VISION_MODEL.free()
        del _VISION_MODEL
        _VISION_MODEL = None
    
    if _VISION_PROCESSOR is not None:
        del _VISION_PROCESSOR
        _VISION_PROCESSOR = None
    
    gc.collect()
    
    if DEVICE == "cuda":
        import torch
        torch.cuda.empty_cache()
        torch.cuda.ipc_collect()
    
    logger.info("✅ Vision model unloaded and VRAM cleared")


def is_model_loaded() -> bool:
    return _VISION_MODEL is not None and _VISION_PROCESSOR is not None

def _clean_repetition(text: str) -> str:
    lines = text.split('\n')
    seen = set()
    unique = []
    for line in lines:
        s = line.strip()
        if not s:
            unique.append(line)
            continue
        if s not in seen:
            seen.add(s)
            unique.append(line)
    return '\n'.join(unique)


def _normalize_output(text: str) -> str:
    return text.strip()


def analyze_with_vision(
    image_path: str,
    analysis_type: str,
    body_part: str = None,
    extra_context: str = None,
    max_tokens: int = 1000,
    keep_loaded: bool = False,
    show_quantum_reasoning: bool = cfg.SHOW_QUANTUM_REASONING
) -> Dict:
    processor, model = get_vision_model()
    
    if processor is not None and model is not None:
        result = _analyze_with_qwen(
            processor, model, image_path,
            analysis_type, body_part, extra_context, max_tokens,
            show_quantum_reasoning
        )
        if not keep_loaded:
            unload_vision_model()
        return result
    
    return _analyze_with_ocr_llm(image_path, analysis_type, body_part, extra_context)


def analyze_with_vision_streaming(
    image_path: str,
    analysis_type: str,
    body_part: str = None,
    extra_context: str = None,
    max_tokens: int = 1000,
    keep_loaded: bool = False,
    show_quantum_reasoning: bool = cfg.SHOW_QUANTUM_REASONING
) -> Generator[str, None, None]:

    yield "__STATUS__:🧠 Loading vision model..."
    
    processor, model = get_vision_model()
    
    if processor is None or model is None:
        yield "__ERROR__:Failed to load vision model"
        return
    
    mode_str = "quantum reasoning" if show_quantum_reasoning else "professional analysis"
    yield f"__STATUS__:📸 Analyzing image with Vision LLM ({mode_str})..."
    
    try:
        import torch
        from transformers import TextIteratorStreamer
        from threading import Thread
        
        image = _load_image(image_path)
        if image is None:
            yield "__ERROR__:Failed to load image"
            if not keep_loaded:
                unload_vision_model()
            return
        
        prompt = _get_medical_prompt(
            analysis_type, body_part, extra_context,
            show_quantum_reasoning=cfg.SHOW_QUANTUM_REASONING
        )
        
        messages = [
            {
                "role": "user",
                "content": [
                    {"type": "text", "text": prompt},
                    {"type": "image", "image": image},
                ],
            }
        ]
        
        text = processor.apply_chat_template(
            messages,
            tokenize=False,
            add_generation_prompt=True
        )
        
        inputs = processor(
            text=[text],
            images=[image],
            return_tensors="pt",
            padding=True
        )
        
        inputs = {k: v.cuda() if hasattr(v, 'cuda') else v for k, v in inputs.items()}
        
        tokenizer = processor.tokenizer if hasattr(processor, "tokenizer") else processor
        
        streamer = TextIteratorStreamer(
            tokenizer,
            skip_prompt=True,
            skip_special_tokens=True,
            decode_kwargs={"clean_up_tokenization_spaces": True}
        )
        
        generation_kwargs = dict(
            **inputs,
            max_new_tokens=max_tokens,
            min_new_tokens=80,
            do_sample=True,
            repetition_penalty=1.2,
            no_repeat_ngram_size=5,
            pad_token_id=tokenizer.pad_token_id if hasattr(tokenizer, "pad_token_id") else tokenizer.eos_token_id,
            streamer=streamer,
        )
        
        thread = Thread(target=model.generate, kwargs=generation_kwargs)
        thread.start()
        
        full_response = ""
        for token in streamer:
            full_response += token
            yield token
        
        thread.join()
        
        full_response = _clean_repetition(full_response)
        full_response = _normalize_output(full_response)
        
        yield f"__COMPLETE__:{full_response}"
        
        if not keep_loaded:
            unload_vision_model()
    
    except Exception as e:
        logger.error(f"Streaming vision analysis failed: {e}")
        yield f"__ERROR__:{str(e)}"
        if not keep_loaded:
            unload_vision_model()


def _analyze_with_qwen(
    processor,
    model,
    image_path: str,
    analysis_type: str,
    body_part: str,
    extra_context: str,
    max_tokens: int,
    show_quantum_reasoning: bool = False
) -> Dict:
    
    try:
        import torch
        
        image = _load_image(image_path)
        if image is None:
            return _analyze_with_ocr_llm(image_path, analysis_type, body_part, extra_context)
        
        prompt = _get_medical_prompt(
            analysis_type, body_part, extra_context,
            show_quantum_reasoning=cfg.SHOW_QUANTUM_REASONING
        )
        
        messages = [
            {
                "role": "user",
                "content": [
                    {"type": "text", "text": prompt},
                    {"type": "image", "image": image},
                ],
            }
        ]
        
        text = processor.apply_chat_template(
            messages,
            tokenize=False,
            add_generation_prompt=True
        )
        
        inputs = processor(
            text=[text],
            images=[image],
            return_tensors="pt",
            padding=True
        )
        
        inputs = {k: v.cuda() if hasattr(v, 'cuda') else v for k, v in inputs.items()}
        
        tokenizer = processor.tokenizer if hasattr(processor, "tokenizer") else processor
        
        with torch.no_grad():
            outputs = model.generate(
                **inputs,
                max_new_tokens=max_tokens,
                min_new_tokens=80,
                do_sample=True,
                repetition_penalty=1.2,
                no_repeat_ngram_size=5,
                pad_token_id=tokenizer.pad_token_id if hasattr(tokenizer, "pad_token_id") else tokenizer.eos_token_id,
            )
        
        input_len = inputs["input_ids"].shape[1]
        generated_ids = outputs[0][input_len:]
        
        response = processor.decode(
            generated_ids,
            skip_special_tokens=True,
            clean_up_tokenization_spaces=True
        )
        
        response = response.strip()
        response = _clean_repetition(response)
        response = _normalize_output(response)
        
        return {
            "summary": response,
            "confidence": 0.90,
            "model": "qwen2.5-vl-7b-medical",
            "method": "vision",
            "quantum_reasoning_used": cfg.SHOW_QUANTUM_REASONING
        }
    
    except Exception as e:
        logger.error(f"Vision analysis failed: {e}")
        return _analyze_with_ocr_llm(image_path, analysis_type, body_part, extra_context)


def _load_image(image_path: str) -> Optional[Image.Image]:
    try:
        ext = image_path.lower().split('.')[-1]
        
        if ext in ['dcm', 'dicom']:
            import pydicom
            ds = pydicom.dcmread(image_path)
            img_array = ds.pixel_array.astype(np.float32)
            img_array = ((img_array - img_array.min()) /
                         (img_array.max() - img_array.min()) * 255).astype(np.uint8)
            
            if img_array.ndim == 2:
                image = Image.fromarray(img_array, mode='L').convert('RGB')
            else:
                image = Image.fromarray(img_array)
        else:
            image = Image.open(image_path)
            if image.mode != 'RGB':
                image = image.convert('RGB')
        
        image = image.resize((1024, 1024), Image.Resampling.LANCZOS)
        from PIL import ImageEnhance
        
        enhancer = ImageEnhance.Contrast(image)
        image = enhancer.enhance(1.6)
        
        return image
    
    except Exception as e:
        logger.error(f"Image load failed: {e}")
        return None


def _get_medical_prompt(
    analysis_type: str,
    body_part: str,
    context: str,
    show_quantum_reasoning: bool = cfg.SHOW_QUANTUM_REASONING
) -> str:
    
    if QUANTUM_PROMPTS_AVAILABLE:
        try:
            logger.info(f"✅ Using quantum vision prompt (show_reasoning={cfg.SHOW_QUANTUM_REASONING})")
            
            analysis_mode = "comprehensive"
            if analysis_type:
                analysis_mode = "focused"
            
            context_str = context if context else ""
            if body_part:
                context_str = f"Body region of interest: {body_part}\n{context_str}"
            
            prompt = get_vision_prompt(
                analysis_type=analysis_mode,
                body_part=body_part or "unspecified",
                context=context_str,
                show_quantum_reasoning=cfg.SHOW_QUANTUM_REASONING
            )
            
            return prompt
        
        except Exception as e:
            logger.warning(f"Quantum prompt failed, using fallback: {e}")
    
    body = body_part or "the visible anatomy"
    ctx = f"\nPatient context: {context}" if context else ""
    
    prompt = f"""You are a BOARD-CERTIFIED RADIOLOGIST analyzing medical images.

Provide a comprehensive professional radiology report.

PATIENT CONTEXT: {ctx}
BODY REGION: {body}

OUTPUT FORMAT:

**Imaging Analysis Report**

**Examination**
- **Modality:** [Imaging type]
- **Body Region:** [Anatomical area]

**Technical Quality**
- **Image Quality:** [Adequate/Limited/Suboptimal]
- **Limiting Factors:** [None/Motion/Exposure/Artifacts]

**Findings**

Describe ALL observations systematically:
- General Description of image contents
- Anatomical structures with assessment (Definite/Probable/Possible)
- Any foreign objects/devices (identify if possible)

**Abnormal Findings Summary**
[List significant abnormal findings]

**Normal Structures Confirmed**
[List important normal structures]

**Areas of Limited Assessment**
[List regions that could not be fully evaluated]

**Overall Assessment**
- **Primary Findings:** [Summary]
- **Confidence Level:** [High/Moderate/Low]
- **Recommended Additional Imaging:** [If applicable]
"""
    
    return prompt


def _analyze_with_ocr_llm(image_path, analysis_type, body_part, extra_context):
    """Fallback to OCR + LLM when vision model is not available."""
    from .ocr_service import extract_text_from_image
    from .llm_service import analyze_text_or_labs
    
    extracted_text = extract_text_from_image(image_path)
    
    prompt = f"""
A medical image text was extracted:

{extracted_text}

Interpret medically.
"""
    
    result = analyze_text_or_labs(prompt)
    
    return {
        "summary": result.get('summary', ''),
        "confidence": 0.70,
        "model": "biomistral-7b",
        "method": "ocr+llm",
    }


def encode_image_to_base64(image_path: str) -> str:
    image = _load_image(image_path)
    buffer = io.BytesIO()
    image.save(buffer, format='JPEG', quality=85)
    return base64.b64encode(buffer.getvalue()).decode('utf-8')

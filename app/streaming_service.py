# streaming_service.py

import os
import logging
import re
from typing import Generator, Optional, List, Dict, Any
from PIL import Image
import numpy as np

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class StreamMarkers:
    STATUS = "__STATUS__:"
    COMPLETE = "__COMPLETE__:"
    ERROR = "__ERROR__:"


def _yield_status(msg: str) -> str:
    return f"{StreamMarkers.STATUS}{msg}"


def _yield_complete(text: str) -> str:
    return f"{StreamMarkers.COMPLETE}{text}"


def _yield_error(msg: str) -> str:
    return f"{StreamMarkers.ERROR}{msg}"


def load_image_for_vision(image_path: str) -> Optional[Image.Image]:

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

        image.thumbnail((1024, 1024), Image.Resampling.LANCZOS)
        return image

    except Exception as e:
        logger.error(f"Image load failed: {e}")
        return None


def _clean_repetition(text: str) -> str:

    lines = text.split('\n')
    seen = set()
    unique = []
    for line in lines:
        stripped = line.strip()
        if not stripped:
            unique.append(line)
            continue
        if stripped not in seen:
            seen.add(stripped)
            unique.append(line)
    return '\n'.join(unique)


VISION_PROMPT = """You are MEDICAL VISION ANALYST. Analyze this medical image.

OUTPUT FORMAT:
### Medical Image Analysis:
### Modality:
- Type:
- Body Region:

### Image Quality:
- Orientation:
- Exposure:
- Artifacts:

### Anatomical Coverage:
Describe visible anatomical regions.

### Observed Findings:
For each finding:
- Location:
- Observation:
- Confidence: Definite / Probable / Uncertain

### Important Negative Observations:
Normal-appearing structures.

### Technical Limitations:
Factors affecting interpretation.

### Confidence: High / Moderate / Low
"""

SYNTHESIS_PROMPT = """[INST]You are MEDICAL POLYMATH — DIAGNOSTIC REASONING ENGINE.
- Maintain multiple diagnostic hypotheses simultaneously
- Missing data = VACUUM STATE (uncertain evidence)
- Separate supporting from contradicting evidence

# OUTPUT FORMAT

### Executive Summary
Most likely diagnosis and why.

### Case Overview
Patient context. Note missing information.

### Key Findings
Symptoms:
Imaging observations:
Laboratory information:

### Pathophysiologic Reasoning
How findings may be connected.

### Evidence Analysis
For each hypothesis:
Diagnosis:
Supporting evidence:
Contradicting evidence:
Likelihood estimate:

### Differential Diagnosis
Rank possibilities.

### Diagnostic Strategy
Tests to clarify diagnosis.

### Final Confidence
Estimated confidence and remaining uncertainty.

# PATIENT DATA
Symptoms: {symptoms}
Medications: {current_meds}

Findings: {findings_text}

[/INST]
"""


def stream_vision_analysis(
    image_path: str,
    analysis_type: str = None,
    body_part: str = None,
    extra_context: str = None,
    max_tokens: int = 1000
) -> Generator[str, None, None]:

    try:
        from .model_manager import get_vision_model
        yield _yield_status("🧠 Loading vision model...")
        
        processor, model = get_vision_model()
        
        yield _yield_status("📸 Analyzing image...")
        
        import torch
        from transformers import TextIteratorStreamer
        from threading import Thread

        image = load_image_for_vision(image_path)
        if image is None:
            yield _yield_error("Failed to load image")
            return

        prompt = VISION_PROMPT
        if extra_context:
            prompt += f"\nPatient context: {extra_context}"

        messages = [{
            "role": "user",
            "content": [
                {"type": "text", "text": prompt},
                {"type": "image", "image": image},
            ],
        }]

        text = processor.apply_chat_template(messages, tokenize=False, add_generation_prompt=True)
        inputs = processor(text=[text], images=[image], return_tensors="pt", padding=True)

        if torch.cuda.is_available():
            inputs = {k: v.cuda() for k, v in inputs.items()}

        tokenizer = processor.tokenizer if hasattr(processor, "tokenizer") else processor
        streamer = TextIteratorStreamer(tokenizer, skip_prompt=True, skip_special_tokens=True)

        thread = Thread(target=model.generate, kwargs={
            **inputs,
            "max_new_tokens": max_tokens,
            "min_new_tokens": 80,
            "do_sample": True,
            "repetition_penalty": 1.2,
            "pad_token_id": tokenizer.pad_token_id if hasattr(tokenizer, "pad_token_id") else tokenizer.eos_token_id,
            "streamer": streamer,
        }, daemon=True)
        thread.start()

        full_response = ""
        for token in streamer:
            full_response += token
            yield token

        thread.join(timeout=30)
        yield _yield_complete(_clean_repetition(full_response.strip()))
        return

    except ImportError as e:
        logger.info(f"Model manager not available: {e}, using z-ai-sdk fallback")
        yield from _stream_vision_zai(image_path, extra_context)
    except Exception as e:
        logger.warning(f"Local vision model failed: {e}")
        yield from _stream_vision_zai(image_path, extra_context)


def _stream_vision_zai(image_path: str, context: str = None) -> Generator[str, None, None]:
    yield _yield_status("🧠 Analyzing with cloud vision...")
    
    try:
        import asyncio
        from z_ai_web_dev_sdk import ZAI
        
        image = load_image_for_vision(image_path)
        if image is None:
            yield _yield_error("Failed to load image")
            return

        import io
        import base64
        buffer = io.BytesIO()
        image.save(buffer, format='JPEG')
        image_base64 = base64.b64encode(buffer.getvalue()).decode('utf-8')

        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        
        async def analyze():
            zai = await ZAI.create()
            
            completion = await zai.chat.completions.create(
                messages=[{
                    "role": "user",
                    "content": [
                        {"type": "text", "text": VISION_PROMPT + (f"\nPatient context: {context}" if context else "")},
                        {"type": "image_url", "image_url": {"url": f"data:image/jpeg;base64,{image_base64}"}}
                    ]
                }],
                stream=False
            )
            return completion.choices[0].message.content

        full_response = loop.run_until_complete(analyze())
        loop.close()
        
        yield full_response
        yield _yield_complete(full_response)

    except Exception as e:
        yield _yield_error(f"Vision analysis failed: {str(e)}")


def stream_llm_analysis(text: str, symptoms: str = "", max_tokens: int = 1024) -> Generator[str, None, None]:
    yield _yield_status("🤖 Analyzing document...")

    prompt = f"""[INST]Analyze this medical text:

{text}

Patient Symptoms: {symptoms if symptoms else 'Not provided'}

Provide:
1. SUMMARY
2. KEY FINDINGS  
3. ABNORMAL VALUES
4. CLINICAL SIGNIFICANCE
5. RECOMMENDATIONS
[/INST]"""

    try:
        from .model_manager import get_llm
        llm = get_llm()
        
        full_response = ""
        for chunk in llm(prompt, max_tokens=max_tokens, temperature=0.3, stream=True):
            token = chunk['choices'][0].get('text', '')
            if token:
                full_response += token
                yield token
        
        yield _yield_complete(full_response)
        
    except Exception as e:
        yield _yield_error(f"LLM analysis failed: {str(e)}")


def stream_llm_synthesis(
    symptoms: str,
    current_meds: str,
    findings: List[Dict]
) -> Generator[str, None, None]:

    yield _yield_status("🤖 Generating clinical summary...")
    
    findings_text = ""
    for f in (findings or []):
        findings_text += f"File: {f.get('file', 'Unknown')} ({f.get('type', 'Unknown')})\n"
        findings_text += f"Finding: {f.get('result', 'No result')}\n"
        findings_text += f"Confidence: {f.get('confidence', 0)*100:.0f}%\n\n"

    if not findings_text.strip():
        yield _yield_complete("No clinical findings available.")
        return

    prompt = SYNTHESIS_PROMPT.format(
        symptoms=symptoms or "Not provided",
        current_meds=current_meds or "Not provided", 
        findings_text=findings_text
    )

    try:
        from .model_manager import get_llm
        llm = get_llm()
        
        full_response = ""
        for chunk in llm(prompt, max_tokens=2048, temperature=0.4, stream=True):
            token = chunk['choices'][0].get('text', '')
            if token:
                full_response += token
                yield token
        
        yield _yield_complete(full_response)
        
    except Exception as e:
        yield _yield_error(f"Synthesis failed: {str(e)}")


def stream_llm_chat(user_message: str, history: List[Dict]) -> Generator[str, None, None]:

    try:
        from .model_manager import get_llm
        llm = get_llm()
        
        conversation = "[INST]You are a helpful medical AI assistant. Always recommend consulting healthcare professionals.\n\n"
        
        for msg in history[-5:]:
            role = msg.get('role', 'user')
            content = msg.get('content', '')
            if role == 'user':
                conversation += f"User: {content}\n"
            else:
                conversation += f"Assistant: {content}\n"
        
        conversation += f"User: {user_message}\nAssistant: [/INST]"

        full_response = ""
        for chunk in llm(conversation, max_tokens=512, temperature=0.4, stream=True):
            token = chunk['choices'][0].get('text', '')
            if token:
                full_response += token
                yield token
        
        yield _yield_complete(full_response)
        
    except Exception as e:
        yield _yield_error(f"Chat failed: {str(e)}")

def stream_ocr_analysis(file_path: str, symptoms: str = "") -> Generator[str, None, None]:

    yield _yield_status("📄 Extracting text from PDF...")
    
    try:
        from pdf2image import convert_from_path
        import pytesseract

        pages = convert_from_path(file_path)
        
        full_text = ""
        for page in pages:
            full_text += pytesseract.image_to_string(page) + "\n"

        if not full_text.strip():
            yield _yield_error("No text extracted from PDF")
            return

        yield _yield_status(f"📄 Extracted {len(full_text)} characters")
        
        yield from stream_llm_analysis(full_text, symptoms)

    except Exception as e:
        yield _yield_error(f"OCR failed: {str(e)}")

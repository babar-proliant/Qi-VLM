# image_service.py

from typing import Dict, Optional, Generator
import torch
import base64
from PIL import Image
from io import BytesIO
import numpy as np
import cv2
import pydicom

def load_image(path: str):
    try:
        ds = pydicom.dcmread(path)
        img = ds.pixel_array.astype(np.float32)

        if hasattr(ds, "RescaleSlope") and hasattr(ds, "RescaleIntercept"):
            img = img * ds.RescaleSlope + ds.RescaleIntercept

        return img

    except Exception:
        img = Image.open(path).convert("RGB")
        return np.array(img)

def render_basic_overlay_b64(img_np):
    if img_np.ndim == 2:
        img_np = cv2.cvtColor(img_np, cv2.COLOR_GRAY2BGR)
    img_np = img_np.astype(np.uint8)
    pil_img = Image.fromarray(img_np)
    buff = BytesIO()
    pil_img.save(buff, format="PNG")
    return base64.b64encode(buff.getvalue()).decode("ascii")

def analyze_medical_image(
    path: str,
    modality: str = None,       
    body_part: str = None,      
    symptoms: Optional[str] = None,
    keep_loaded: bool = False
) -> Dict:

    from .vision_service import analyze_with_vision
    print(f"🧠 Analyzing image with Qwen2.5-VL-Medical (Auto-detect mode)...")
    context = None
    if symptoms:
        context = f"Patient symptoms: {symptoms}"
    result = analyze_with_vision(
        image_path=path,
        analysis_type=modality,     
        body_part=body_part,        
        extra_context=context,
        keep_loaded=keep_loaded
    )
    img = load_image(path)
    preview_b64 = render_basic_overlay_b64(img)

    body_part_names = {
        "chest": "Chest",
        "hand": "Hand/Wrist",
        "foot": "Foot/Ankle",
        "spine": "Spine",
        "skull": "Skull/Facial",
        "pelvis": "Pelvis/Hip",
        "knee": "Knee",
        "shoulder": "Shoulder",
        "abdomen": "Abdomen",
        "brain": "Brain",
        "other": "Body Part"
    }

    if body_part:
        result["body_part"] = body_part_names.get(body_part.lower(), body_part)
    else:
        result["body_part"] = "Auto-detected"
    
    result["modality"] = modality if modality else "Medical Image"
    result["preview_b64"] = preview_b64
    result["model"] = "Qwen2.5-VL-7B-Medical"

    return result

def analyze_medical_image_streaming(
    path: str,
    modality: str = None,       
    body_part: str = None,      
    symptoms: Optional[str] = None,
    keep_loaded: bool = False
) -> Generator[str, None, None]:

    from .vision_service import analyze_with_vision_streaming
    print(f"🧠 Analyzing image(s)...")

    context = None
    if symptoms:
        context = f"Patient symptoms: {symptoms}"

    yield from analyze_with_vision_streaming(
        image_path=path,
        analysis_type=modality,
        body_part=body_part,
        extra_context=context,
        keep_loaded=keep_loaded
    )

def analyze_xray(
    path: str,
    body_part: str = None,
    symptoms: Optional[str] = None,
    keep_loaded: bool = False
) -> Dict:
    return analyze_medical_image(
        path=path,
        modality="xray",
        body_part=body_part,
        symptoms=symptoms,
        keep_loaded=keep_loaded
    )

def analyze_xray_streaming(
    path: str,
    body_part: str = None,
    symptoms: Optional[str] = None,
    keep_loaded: bool = False
) -> Generator[str, None, None]:

    yield from analyze_medical_image_streaming(
        path=path,
        modality="xray",
        body_part=body_part,
        symptoms=symptoms,
        keep_loaded=keep_loaded
    )
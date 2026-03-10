# ecg_service.py

import os
from typing import Dict, Optional


def analyze_ecg(path: str, symptoms: str = None) -> Dict:
    from .vision_service import analyze_with_vision

    print(f"\n📊 ECG Analysis for: {path}")

    context = f"Patient symptoms: {symptoms}" if symptoms else None
    result = analyze_with_vision(
        image_path=path,
        analysis_type="ecg",
        body_part="heart",
        extra_context=context,
        max_tokens=700  
    )
    result["modality"] = "ECG/EKG"
    result["body_part"] = "Cardiac"

    return result


def analyze_echo(path: str, symptoms: str = None) -> Dict:
    from .vision_service import analyze_with_vision
    print(f"\n📊 Echocardiogram Analysis for: {path}")
    context = f"Patient symptoms: {symptoms}" if symptoms else None
    result = analyze_with_vision(
        image_path=path,
        analysis_type="xray",  
        body_part="heart",
        extra_context=f"Echocardiogram image. {context}" if context else "Echocardiogram image",
        max_tokens=600
    )

    result["modality"] = "Echocardiogram"
    result["body_part"] = "Cardiac"

    return result

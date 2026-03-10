# ct_mri_service.py

import pydicom
import numpy as np
from PIL import Image
import os
import tempfile
from typing import Optional, Dict, List


def extract_key_slices(dicom_path: str, num_slices: int = 5) -> List[str]:
    try:
        ds = pydicom.dcmread(dicom_path, force=True)
        pixel_array = ds.pixel_array.astype(np.float32)
        if pixel_array.ndim == 3:
            num_total_slices = pixel_array.shape[0]
            if num_total_slices <= 1:
                return [_save_slice_as_image(pixel_array, dicom_path, 0)]
            if num_total_slices <= num_slices:
                slice_indices = list(range(num_total_slices))
            else:
                slice_indices = []
                slice_indices.append(0)  
                slice_indices.append(num_total_slices // 2)  
                slice_indices.append(num_total_slices - 1)  
                step = num_total_slices // (num_slices - 1)
                for i in range(1, num_slices - 1):
                    idx = i * step
                    if idx not in slice_indices and 0 < idx < num_total_slices:
                        slice_indices.append(idx)
                slice_indices = sorted(set(slice_indices))[:num_slices]
            slice_paths = []
            for i, idx in enumerate(slice_indices):
                slice_img = pixel_array[idx]
                path = _save_slice_as_image(slice_img, dicom_path, idx)
                slice_paths.append(path)
            return slice_paths
        elif pixel_array.ndim == 2:
            return [_save_slice_as_image(pixel_array, dicom_path, 0)]
        else:
            print(f"Unexpected array dimensions: {pixel_array.ndim}")
            return []
    except Exception as e:
        print(f"Error extracting DICOM slices: {e}")
        return []


def _save_slice_as_image(slice_array: np.ndarray, original_path: str, slice_idx: int) -> str:
    slice_float = slice_array.astype(np.float32)
    p2, p98 = np.percentile(slice_float, [2, 98])
    slice_windowed = np.clip(slice_float, p2, p98)
    slice_normalized = ((slice_windowed - slice_windowed.min()) /
                        (slice_windowed.max() - slice_windowed.min()) * 255).astype(np.uint8)
    img = Image.fromarray(slice_normalized, mode='L')
    temp_dir = tempfile.gettempdir()
    base_name = os.path.splitext(os.path.basename(original_path))[0]
    temp_path = os.path.join(temp_dir, f"{base_name}_slice_{slice_idx}.png")
    img.save(temp_path)
    return temp_path

def analyze_3d_scan(path: str, body_part: str = None, symptoms: str = None) -> Dict:
    from .vision_service import analyze_with_vision
    print(f"\n📊 CT/MRI Analysis for: {path}")
    print(f"   Body part: {body_part or 'Auto-detect'}")
    try:
        ds = pydicom.dcmread(path, force=True)
        modality = getattr(ds, 'Modality', 'Unknown')
        dicom_body_part = getattr(ds, 'BodyPartExamined', None)
        study_desc = getattr(ds, 'StudyDescription', 'N/A')
        if not body_part and dicom_body_part:
            body_part = dicom_body_part.lower()
        print(f"   Modality: {modality}")
        print(f"   Study: {study_desc}")
    except Exception as e:
        print(f"   ⚠️ Could not read DICOM metadata: {e}")
        modality = "CT/MRI"
    analysis_type = "ct" if modality == "CT" else "mri" if modality in ["MR", "MRI"] else "ct"
    print(f"   Extracting key slices...")

    slice_paths = extract_key_slices(path, num_slices=3)
    if not slice_paths:
        slice_paths = [path]
    print(f"   Extracted {len(slice_paths)} slices")

    context_parts = []
    if symptoms:
        context_parts.append(f"Symptoms: {symptoms}")
    if study_desc and study_desc != 'N/A':
        context_parts.append(f"Study: {study_desc}")
    context = " | ".join(context_parts) if context_parts else None

    all_findings = []
    for i, slice_path in enumerate(slice_paths):
        print(f"   Analyzing slice {i+1}/{len(slice_paths)}...")

        result = analyze_with_vision(
            image_path=slice_path,
            analysis_type=analysis_type,
            body_part=body_part,
            extra_context=context,
            max_tokens=500
        )

        if result.get("summary") and not result.get("error"):
            all_findings.append(result["summary"])

        if slice_path != path and os.path.exists(slice_path):
            try:
                os.remove(slice_path)
            except:
                pass

    if all_findings:
        if len(all_findings) == 1:
            combined_summary = all_findings[0]
        else:
            combined_summary = f"**Multi-Slice Analysis ({modality} Scan):**\n\n"
            for i, finding in enumerate(all_findings):
                combined_summary += f"**Slice {i+1}:**\n{finding}\n\n"
    else:
        combined_summary = f"{modality} scan analysis completed. No significant findings detected or analysis unavailable."

    body_part_names = {
        "head": "Head/Brain",
        "brain": "Brain",
        "chest": "Chest/Thorax",
        "abdomen": "Abdomen/Pelvis",
        "spine": "Spine",
        "joint": "Joint/MSK",
        "pelvis": "Pelvis",
        "neck": "Neck"
    }

    return {
        "summary": combined_summary,
        "confidence": 0.80,
        "modality": f"{modality} Scan",
        "body_part": body_part_names.get(body_part.lower() if body_part else None, body_part or "Unspecified"),
        "model": "qwen2.5-vl-7b-medical",
        "slices_analyzed": len(slice_paths)
    }

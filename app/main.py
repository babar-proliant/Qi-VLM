# main.py

import os
import json
import asyncio
import uvicorn
import aiofiles
from fastapi import FastAPI, UploadFile, File, Form, HTTPException, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import StreamingResponse
from pydantic import BaseModel
from typing import List, Optional
import traceback

from .services.model_downloader import check_and_download_models
check_and_download_models()

from .services.image_service import analyze_medical_image, analyze_medical_image_streaming

from .services.llm_service import (
    analyze_text_or_labs, 
    analyze_text_or_labs_streaming,
    synthesize_case, 
    synthesize_case_streaming,
    chat_with_llm,
    chat_with_llm_streaming,
    unload_llm,
    _determine_coherence_level  # For passing coherence to context
)

from .services.ocr_service import extract_text_from_image, extract_text_from_pdf
from .services.vision_service import unload_vision_model
from .services.ct_mri_service import analyze_3d_scan
from .services.ecg_service import analyze_ecg, analyze_echo

from .case_context import (
    clear_case_context,
    update_case_context,
    get_case_summary_for_llm,
    has_case_context,
    get_coherence_level
)

app = FastAPI(title="Medical AI Assistant")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

UPLOAD_DIR = "temp_uploads"
os.makedirs(UPLOAD_DIR, exist_ok=True)

class ChatMessage(BaseModel):
    role: str
    content: str

class ChatRequest(BaseModel):
    message: str
    history: List[ChatMessage] = []

def detect_file_type(file_name: str) -> dict:
    ext = file_name.lower().split('.')[-1] if '.' in file_name else ''
    
    if ext == 'pdf':
        return {
            "service": "ocr_then_llm",
            "label": "PDF Document"
        }
    
    if ext in ['txt', 'csv']:
        return {
            "service": "llm_direct",
            "label": "Text Document"
        }
    
    return {
        "service": "vision_model",
        "label": "Medical Image"
    }


def route_analysis(
    file_path: str, 
    file_name: str, 
    symptoms: str = "", 
    current_meds: str = "",
    keep_loaded: bool = False
):
    detected = detect_file_type(file_name)
    service = detected["service"]
    label = detected["label"]
    
    print(f"\n🚀 Routing: {file_name}")
    print(f"   Service: {service}")

    result = None

    try:
        if service == "vision_model":
            print(f"   📸 Activating Vision Model (Auto-detect)...")
            
            result = analyze_medical_image(
                path=file_path,
                modality=None,
                body_part=None,
                symptoms=symptoms,
                keep_loaded=keep_loaded
            )

        elif service == "ocr_then_llm":
            print(f"   📄 Extracting text from PDF via OCR...")
            extracted_text = extract_text_from_pdf(file_path)
            
            if extracted_text.strip():
                print(f"   📝 OCR extracted {len(extracted_text)} characters")
                result = analyze_text_or_labs(extracted_text, symptoms=symptoms)
            else:
                result = {
                    "summary": "Could not extract text from PDF.",
                    "confidence": 0.3
                }
        
        elif service == "llm_direct":
            print(f"   📝 Processing text file...")
            with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                text_content = f.read()
            
            if text_content.strip():
                result = analyze_text_or_labs(text_content, symptoms=symptoms)
            else:
                result = {
                    "summary": "The text file appears to be empty.",
                    "confidence": 0.3
                }

        if result and "modality" not in result:
            result["modality"] = label

        print(f"   ✅ Analysis complete.")

    except Exception as e:
        print(f"   ❌ ERROR: {e}")
        traceback.print_exc()
        result = {
            "summary": f"Analysis error: {str(e)}",
            "confidence": 0.0,
            "modality": "Error"
        }

    return result, label


@app.post("/analyze")
async def analyze_endpoint(
    patient_id: str = Form(default="Unknown"),
    symptoms: str = Form(default=""),
    current_meds: str = Form(default=""),
    file: UploadFile = File(...)
):
    file_path = os.path.join(UPLOAD_DIR, file.filename)

    async with aiofiles.open(file_path, "wb") as out:
        content = await file.read()
        await out.write(content)

    try:
        result, modality = route_analysis(
            file_path=file_path,
            file_name=file.filename,
            symptoms=symptoms,
            current_meds=current_meds,
            keep_loaded=False
        )

        finding_for_llm = [{
            "file": file.filename,
            "type": modality,
            "result": result["summary"],
            "confidence": result.get("confidence", 0.0)
        }]

        synthesis = synthesize_case(symptoms, current_meds, finding_for_llm)

        return {
            "modality": modality,
            "summary": result["summary"],
            "confidence": result["confidence"],
            "raw_output": result,
            "synthesis": synthesis,
        }

    except Exception as e:
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        if os.path.exists(file_path):
            os.remove(file_path)


@app.post("/chat")
async def chat_endpoint(request: ChatRequest):
    history_dicts = [msg.dict() for msg in request.history]
    response_text = chat_with_llm(request.message, history_dicts)
    return {"response": response_text}


@app.post("/analyze_case_v2")
async def analyze_case_v2_endpoint(request: Request):
    form = await request.form()

    patient_id = form.get("patient_id", "Unknown")
    symptoms = form.get("symptoms", "")
    current_meds = form.get("current_meds", "")

    files_list = form.getlist("files")
    files_data = {}
    for f in files_list:
        if hasattr(f, 'filename') and f.filename:
            files_data[f.filename] = f

    total_files = len(files_data)
    print(f"\n📊 Processing {total_files} files in batch mode...")

    collected_findings = []

    try:
        for idx, (filename, upload_file) in enumerate(files_data.items()):
            is_last_file = (idx == total_files - 1)
            file_path = os.path.join(UPLOAD_DIR, filename)

            async with aiofiles.open(file_path, "wb") as out:
                content = await upload_file.read()
                await out.write(content)

            try:
                result, modality = route_analysis(
                    file_path=file_path,
                    file_name=filename,
                    symptoms=symptoms,
                    current_meds=current_meds,
                    keep_loaded=not is_last_file
                )

                collected_findings.append({
                    "file": filename,
                    "type": modality,
                    "result": result["summary"],
                    "confidence": result.get("confidence", 0.0)
                })

            except Exception as e:
                traceback.print_exc()
                collected_findings.append({
                    "file": filename,
                    "type": "Error",
                    "result": str(e),
                    "confidence": 0.0
                })
            finally:
                if os.path.exists(file_path):
                    os.remove(file_path)

        unload_vision_model()

    except Exception as e:
        print(f"   ❌ Batch processing error: {e}")
        unload_vision_model()
        traceback.print_exc()

    synthesis = synthesize_case(symptoms, current_meds, collected_findings)

    return {
        "patient_id": patient_id,
        "findings": collected_findings,
        "synthesis": synthesis
    }

@app.post("/analyze_stream")
async def analyze_stream_endpoint(
    patient_id: str = Form(default="Unknown"),
    symptoms: str = Form(default=""),
    current_meds: str = Form(default=""),
    file: UploadFile = File(...)
):
    async def event_generator():
        file_path = None
        try:
            file_path = os.path.join(UPLOAD_DIR, file.filename)
            
            yield 'event: status\ndata: {"message": "📁 Saving uploaded file..."}\n\n'
            
            async with aiofiles.open(file_path, "wb") as out:
                content = await file.read()
                await out.write(content)
            
            detected = detect_file_type(file.filename)
            service = detected["service"]
            detected_label = detected["label"]
            
            status_msg = f"🔍 Detected: {detected_label}"
            yield f'event: status\ndata: {json.dumps({"message": status_msg})}\n\n'
            
            vision_result = ""
            
            if service == "vision_model":
                for token in analyze_medical_image_streaming(file_path, None, None, symptoms):
                    if token.startswith("__STATUS__:"):
                        msg = token.replace("__STATUS__:", "")
                        yield f'event: status\ndata: {json.dumps({"message": msg})}\n\n'
                    elif token.startswith("__COMPLETE__:"):
                        vision_result = token.replace("__COMPLETE__:", "")
                    elif token.startswith("__ERROR__:"):
                        msg = token.replace("__ERROR__:", "")
                        yield f'event: error\ndata: {json.dumps({"message": msg})}\n\n'
                        return
                    else:
                        yield f'event: vision\ndata: {json.dumps({"token": token})}\n\n'
                
                yield f'event: vision_complete\ndata: {json.dumps({"result": vision_result[:500]})}\n\n'
                
                yield 'event: status\ndata: {"message": "🤖 Generating clinical summary..."}\n\n'
                
                finding = [{"file": file.filename, "type": "Vision", "result": vision_result, "confidence": 0.90}]
                
                for token in synthesize_case_streaming(symptoms, current_meds, finding):
                    if token.startswith("__STATUS__:"):
                        msg = token.replace("__STATUS__:", "")
                        yield f'event: status\ndata: {json.dumps({"message": msg})}\n\n'
                    elif token.startswith("__COMPLETE__:"):
                        res = token.replace("__COMPLETE__:", "")
                        yield f'event: complete\ndata: {json.dumps({"synthesis": res})}\n\n'
                    elif token.startswith("__ERROR__:"):
                        msg = token.replace("__ERROR__:", "")
                        yield f'event: error\ndata: {json.dumps({"message": msg})}\n\n'
                    else:
                        yield f'event: llm\ndata: {json.dumps({"token": token})}\n\n'
            
            elif service == "ocr_then_llm":
                yield 'event: status\ndata: {"message": "📄 Extracting text from PDF..."}\n\n'
                
                extracted_text = extract_text_from_pdf(file_path)
                
                if not extracted_text.strip():
                    yield 'event: error\ndata: {"message": "Could not extract text from PDF"}\n\n'
                    return
                
                for token in analyze_text_or_labs_streaming(extracted_text, symptoms):
                    if token.startswith("__STATUS__:"):
                        msg = token.replace("__STATUS__:", "")
                        yield f'event: status\ndata: {json.dumps({"message": msg})}\n\n'
                    elif token.startswith("__COMPLETE__:"):
                        res = token.replace("__COMPLETE__:", "")
                        yield f'event: complete\ndata: {json.dumps({"synthesis": res})}\n\n'
                    elif token.startswith("__ERROR__:"):
                        msg = token.replace("__ERROR__:", "")
                        yield f'event: error\ndata: {json.dumps({"message": msg})}\n\n'
                    else:
                        yield f'event: llm\ndata: {json.dumps({"token": token})}\n\n'
            
            elif service == "llm_direct":
                with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                    text_content = f.read()
                
                for token in analyze_text_or_labs_streaming(text_content, symptoms):
                    if token.startswith("__STATUS__:"):
                        msg = token.replace("__STATUS__:", "")
                        yield f'event: status\ndata: {json.dumps({"message": msg})}\n\n'
                    elif token.startswith("__COMPLETE__:"):
                        res = token.replace("__COMPLETE__:", "")
                        yield f'event: complete\ndata: {json.dumps({"synthesis": res})}\n\n'
                    elif token.startswith("__ERROR__:"):
                        msg = token.replace("__ERROR__:", "")
                        yield f'event: error\ndata: {json.dumps({"message": msg})}\n\n'
                    else:
                        yield f'event: llm\ndata: {json.dumps({"token": token})}\n\n'
                
        except Exception as e:
            traceback.print_exc()
            yield f'event: error\ndata: {json.dumps({"message": str(e)})}\n\n'
        finally:
            if file_path and os.path.exists(file_path):
                os.remove(file_path)
    
    return StreamingResponse(
        event_generator(),
        media_type="text/event-stream",
        headers={"Cache-Control": "no-cache", "Connection": "keep-alive", "X-Accel-Buffering": "no"}
    )


@app.post("/analyze_case_stream")
async def analyze_case_stream_endpoint(request: Request):

    print("\n" + "="*60)
    print("🔄 NEW CASE ANALYSIS - Clearing previous context")
    print("="*60)
    unload_llm()
    clear_case_context()
    
    form = await request.form()
    
    patient_id = form.get("patient_id", "Unknown")
    symptoms = form.get("symptoms", "")
    current_meds = form.get("current_meds", "")
    
    files_list = form.getlist("files")
    
    files_data = {}
    for f in files_list:
        if hasattr(f, 'filename') and f.filename:
            file_path = os.path.join(UPLOAD_DIR, f.filename)
            content = await f.read()
            async with aiofiles.open(file_path, "wb") as out:
                await out.write(content)
            files_data[f.filename] = file_path
    
    total_files = len(files_data)
    print(f"📁 Files to process: {total_files}")
    
    async def event_generator():
        
        try:
            init_msg = f"📊 Processing {total_files} files..."
            print(f"📤 Yielding initial status: {init_msg}")
            yield f'event: status\ndata: {json.dumps({"message": init_msg})}\n\n'
            
            collected_findings = []
            synthesis_result = ""
            
            for idx, (filename, file_path) in enumerate(files_data.items()):
                is_last = (idx == total_files - 1)
                
                detected = detect_file_type(filename)
                service = detected["service"]
                print(f"   Processing {filename} -> {service}")
                
                if service == "vision_model":
                    vision_result = ""
                    
                    for token in analyze_medical_image_streaming(file_path, None, None, symptoms, keep_loaded=not is_last):
                        if token.startswith("__STATUS__:"):
                            msg_content = token.replace("__STATUS__:", "")
                            status_msg = f"[{idx+1}/{total_files}] {msg_content}"
                            yield f'event: status\ndata: {json.dumps({"message": status_msg})}\n\n'
                        elif token.startswith("__COMPLETE__:"):
                            vision_result = token.replace("__COMPLETE__:", "")
                        elif token.startswith("__ERROR__:"):
                            err_msg = token.replace("__ERROR__:", "")
                            yield f'event: error\ndata: {json.dumps({"message": err_msg})}\n\n'
                        else:
                            yield f'event: vision\ndata: {json.dumps({"file_num": idx+1, "filename": filename, "token": token})}\n\n'
                    
                    res_preview = vision_result[:200]
                    yield f'event: file_complete\ndata: {json.dumps({"file_num": idx+1, "filename": filename, "result": res_preview})}\n\n'
                    collected_findings.append({"file": filename, "type": "Vision", "result": vision_result, "confidence": 0.90})
                
                elif service == "ocr_then_llm":
                    proc_msg = f"[{idx+1}/{total_files}] Processing PDF..."
                    yield f'event: status\ndata: {json.dumps({"message": proc_msg})}\n\n'
                    
                    extracted_text = extract_text_from_pdf(file_path)
                    doc_result = ""
                    
                    if extracted_text.strip():
                        for token in analyze_text_or_labs_streaming(extracted_text, symptoms):
                            if token.startswith("__STATUS__:"):
                                msg_content = token.replace("__STATUS__:", "")
                                status_msg = f"[{idx+1}/{total_files}] {msg_content}"
                                yield f'event: status\ndata: {json.dumps({"message": status_msg})}\n\n'
                            elif token.startswith("__COMPLETE__:"):
                                doc_result = token.replace("__COMPLETE__:", "")
                            elif token.startswith("__ERROR__:"):
                                err_msg = token.replace("__ERROR__:", "")
                                yield f'event: error\ndata: {json.dumps({"message": err_msg})}\n\n'
                            else:
                                yield f'event: llm\ndata: {json.dumps({"file_num": idx+1, "token": token})}\n\n'
                    
                    collected_findings.append({"file": filename, "type": "PDF", "result": doc_result, "confidence": 0.90})
                
                else:
                    with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                        text_content = f.read()
                    
                    text_result = ""
                    for token in analyze_text_or_labs_streaming(text_content, symptoms):
                        if token.startswith("__STATUS__:"):
                            pass
                        elif token.startswith("__COMPLETE__:"):
                            text_result = token.replace("__COMPLETE__:", "")
                        elif token.startswith("__ERROR__:"):
                            err_msg = token.replace("__ERROR__:", "")
                            yield f'event: error\ndata: {json.dumps({"message": err_msg})}\n\n'
                        else:
                            yield f'event: llm\ndata: {json.dumps({"file_num": idx+1, "token": token})}\n\n'
                    
                    collected_findings.append({"file": filename, "type": "Text", "result": text_result, "confidence": 0.90})
                
                if os.path.exists(file_path):
                    os.remove(file_path)
            
            print("📷 Unloading Vision model...")
            unload_vision_model()
            
            print("🤖 Loading LLM to study the case...")
            yield 'event: status\ndata: {"message": "🤖 Generating comprehensive clinical summary..."}\n\n'
            
            for token in synthesize_case_streaming(symptoms, current_meds, collected_findings):
                if token.startswith("__STATUS__:"):
                    msg = token.replace("__STATUS__:", "")
                    yield f'event: status\ndata: {json.dumps({"message": msg})}\n\n'
                elif token.startswith("__COMPLETE__:"):
                    synthesis_result = token.replace("__COMPLETE__:", "")
                    yield f'event: synthesis_complete\ndata: {json.dumps({"synthesis": synthesis_result})}\n\n'
                elif token.startswith("__ERROR__:"):
                    err = token.replace("__ERROR__:", "")
                    yield f'event: error\ndata: {json.dumps({"message": err})}\n\n'
                else:
                    yield f'event: llm\ndata: {json.dumps({"token": token})}\n\n'
            
            update_case_context(
                patient_id=patient_id,
                symptoms=symptoms,
                current_meds=current_meds,
                findings=collected_findings,
                synthesis=synthesis_result
            )
            print("✅ Case context stored - AI will remember this for chat")
            
            yield 'event: complete\ndata: {"message": "Analysis complete! You can now ask questions about this case."}\n\n'
            print("\n✅ ANALYSIS COMPLETE - Use consultation tab to discuss the case with AI.")
            
        except Exception as e:
            print(f"❌ GENERATOR ERROR: {e}")
            traceback.print_exc()
            yield f'event: error\ndata: {json.dumps({"message": str(e)})}\n\n'
    
    print("📤 Returning StreamingResponse...")
    return StreamingResponse(
        event_generator(),
        media_type="text/event-stream",
        headers={"Cache-Control": "no-cache", "Connection": "keep-alive", "X-Accel-Buffering": "no"}
    )


@app.post("/chat_stream")
async def chat_stream_endpoint(request: ChatRequest):
    async def event_generator():
        history_dicts = [msg.dict() for msg in request.history]
        
        for token in chat_with_llm_streaming(request.message, history_dicts):
            if token.startswith("__ERROR__:"):
                err = token.replace("__ERROR__:", "")
                yield f'event: error\ndata: {json.dumps({"message": err})}\n\n'
            elif token.startswith("__COMPLETE__:"):
                pass
            else:
                yield f'event: token\ndata: {json.dumps({"token": token})}\n\n'
        
        yield 'event: complete\ndata: {"message": "done"}\n\n'
    
    return StreamingResponse(
        event_generator(),
        media_type="text/event-stream",
        headers={"Cache-Control": "no-cache", "Connection": "keep-alive", "X-Accel-Buffering": "no"}
    )


@app.get("/health")
async def health_check():
    return {
        "status": "healthy",
        "has_case_context": has_case_context(),
        "coherence_level": get_coherence_level()
    }


@app.get("/context/status")
async def context_status():
    from .case_context import get_case_context
    ctx = get_case_context()
    return {
        "has_context": ctx.has_data,
        "patient_id": ctx.patient_id if ctx.has_data else None,
        "findings_count": len(ctx.findings) if ctx.has_data else 0,
        "has_symptoms": bool(ctx.symptoms) if ctx.has_data else False,
        "has_medications": bool(ctx.current_meds) if ctx.has_data else False,
        "has_synthesis": bool(ctx.synthesis) if ctx.has_data else False,
        "coherence_level": ctx.coherence_level if ctx.has_data else None,
        "clinical_scenario": ctx.clinical_scenario if ctx.has_data else None,
        "active_specialists": ctx.active_specialists if ctx.has_data else []
    }


@app.get("/quantum/status")
async def quantum_status():
    try:
        from .services.quantum_vision_prompt import PRESET_PROMPTS, get_modality_specific_guidance
        vision_presets = list(PRESET_PROMPTS.keys())
        vision_available = True
    except ImportError:
        vision_presets = []
        vision_available = False
    
    try:
        from .services.quantum_diagnostic_prompt import CLINICAL_SCENARIOS
        clinical_scenarios = list(CLINICAL_SCENARIOS.keys())
        diagnostic_available = True
    except ImportError:
        clinical_scenarios = []
        diagnostic_available = False
    
    return {
        "quantum_vision_prompts": vision_available,
        "quantum_diagnostic_prompts": diagnostic_available,
        "vision_presets": vision_presets,
        "clinical_scenarios": clinical_scenarios,
        "coherence_levels": {
            "1": "Single system, minimal superposition",
            "2": "Multi-system, moderate uncertainty",
            "3": "Complex case, extensive entanglement",
            "4": "Critical/maximum uncertainty"
        }
    }


@app.post("/context/clear")
async def clear_context():
    clear_case_context()
    return {"status": "cleared"}


if __name__ == "__main__":
    uvicorn.run("app.main:app", host="0.0.0.0", port=8000, reload=True)
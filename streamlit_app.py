# streamlit_app.py

import streamlit as st
import requests
import base64
import json
import html
import re
from PIL import Image
from io import BytesIO
import time
import markdown

API_URL = "http://localhost:8000"

st.set_page_config(page_title="Qi-VLM: Quantum-Informed Vision-Language Model for Clinical Diagnostics", layout="wide", initial_sidebar_state="collapsed")

st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=DM+Sans:wght@400;500;600;700&display=swap');
    
    * { font-family: 'DM Sans', sans-serif; }
    
    /* Hide Elements */
    [data-testid="stSidebar"], #MainMenu, footer, header { visibility: hidden; }
    
    /* Tabs */
    .stTabs [data-baseweb="tabs-list"] { background: #f0f7ff !important; gap: 0; border-radius: 12px; padding: 4px; }
    .stTabs [data-baseweb="tab"] {
        font-size: 0.8rem !important;
        padding: 5px 10px !important;
        font-weight: 500;
        background: #0284c7 !important;
        color: white !important;
        border-radius: 8px !important;
    }
    .stTabs [aria-selected="true"] { 
        background: #027d29 !important; 
        color: white !important; 
        box-shadow: 0 2px 8px rgba(2, 132, 199, 0.3);
    }
    .stTabs [data-baseweb="tab-highlight"] { display: none; }
    
    /* Header */
    .clinical-header {
        display: flex;
        align-items: center;
        justify-content: space-between;
        padding: 12px 20px;
        background: linear-gradient(135deg, #0284c7 0%, #0369a1 100%);
        border-radius: 0 0 20px 20px;
        margin: -8px -24px 16px -24px;
        box-shadow: 0 4px 20px rgba(2, 132, 199, 0.3);
    }
    .header-left { display: flex; align-items: center; gap: 12px; }
    .header-icon { font-size: 1.8rem; }
    .header-title { color: white; font-size: 1.3rem; font-weight: 700; }
    .header-sub { color: rgba(255,255,255,0.8); font-size: 0.75rem; }
    .header-badge {
        background: rgba(255,255,255,0.2);
        color: white;
        padding: 6px 14px;
        border-radius: 20px;
        font-size: 0.75rem;
        font-weight: 500;
    }
    
    /* Cards */
    .clinical-card {
        background: white;
        border-radius: 12px;
        border: 1px solid #e0f2fe;
        padding: 14px;
        margin-bottom: 10px;
        box-shadow: 0 2px 8px rgba(2, 132, 199, 0.08);
    }
    .card-label {
        font-size: 0.7rem;
        font-weight: 700;
        color: #0284c7;
        text-transform: uppercase;
        letter-spacing: 1px;
        margin-bottom: 10px;
        display: flex;
        align-items: center;
        gap: 6px;
    }
    
    /* File Items */
    .file-clinical {
        display: flex;
        align-items: center;
        gap: 10px;
        padding: 8px 12px;
        background: #f0f7ff;
        border-radius: 8px;
        margin-bottom: 6px;
        border: 1px solid #e0f2fe;
    }
    .file-icon { font-size: 1rem; }
    .file-name { font-size: 0.8rem; color: #0369a1; font-weight: 600; }
    
    /* Form Elements */
    .stTextInput>div>div>input, .stTextArea>div>textarea {
        background: #f8fbff !important;
        border: 1px solid #e0f2fe !important;
        font-size: 0.85rem !important;
        border-radius: 8px !important;
    }
    .stTextInput>div>div>input:focus, .stTextArea>div>textarea:focus { border-color: #0284c7 !important; }
    .stSelectbox>div>div { border-color: #e0f2fe !important; }
    
    /* Result Cards */
    .result-clinical {
        background: linear-gradient(135deg, #f0f7ff, #ffffff);
        border-left: 4px solid #0284c7;
        padding: 12px 16px;
        border-radius: 0 10px 10px 0;
        margin-bottom: 8px;
        border: 1px solid #e0f2fe;
    }
    .result-file { font-weight: 700; color: #0369a1; font-size: 0.85rem; margin-bottom: 6px; }
    .result-text { font-size: 0.8rem; color: #475569; line-height: 1.4; white-space: pre-wrap; }
    
    /* Report text styling */
    .report-text {
        font-size: 0.85rem;
        color: #475569;
        line-height: 1.5;
        white-space: pre-wrap;
        word-wrap: break-word;
    }
    
    /* Reports Container */
    .reports-container {
        margin-bottom: 12px;
    }
    .reports-label {
        font-size: 0.7rem;
        font-weight: 600;
        color: #64748b;
        margin-bottom: 8px;
        text-transform: uppercase;
        letter-spacing: 0.5px;
    }
    
    /* Synthesis */
    .synthesis-clinical {
        background: linear-gradient(135deg, #f0f7ff, #e0f2fe);
        border: 1px solid #bae6fd;
        border-radius: 10px;
        padding: 16px;
        font-size: 0.85rem;
        color: #334155;
        line-height: 1.5;
    }
    .synthesis-clinical strong { color: #0369a1; }
    
    /* Streaming Container */
    .streaming-container {
        background: linear-gradient(135deg, #f0f7ff, #ffffff);
        border-left: 4px solid #0284c7;
        padding: 12px 16px;
        border-radius: 0 10px 10px 0;
        margin-bottom: 8px;
        border: 1px solid #e0f2fe;
        min-height: 80px;
    }
    
    .streaming-label {
        font-size: 0.75rem;
        font-weight: 600;
        color: #0284c7;
        margin-bottom: 6px;
    }
    
    .streaming-text {
        font-size: 0.85rem;
        color: #334155;
        line-height: 1.5;
        white-space: pre-wrap;
        word-wrap: break-word;
    }
    
    /* Typing cursor */
    .typing-cursor {
        display: inline-block;
        animation: blink 1s infinite;
        color: #0284c7;
        font-weight: bold;
        margin-left: 2px;
    }
    
    @keyframes blink {
        0%, 50% { opacity: 1; }
        51%, 100% { opacity: 0; }
    }
    
    /* Status badge */
    .status-badge {
        display: inline-flex;
        align-items: center;
        gap: 8px;
        background: linear-gradient(135deg, #f0f7ff, #e0f2fe);
        border: 1px solid #bae6fd;
        padding: 8px 14px;
        border-radius: 20px;
        font-size: 0.8rem;
        color: #0369a1;
        margin-bottom: 10px;
        font-weight: 500;
    }
    
    .status-spinner {
        width: 14px;
        height: 14px;
        border: 2px solid #bae6fd;
        border-top-color: #0284c7;
        border-radius: 50%;
        animation: spin 0.8s linear infinite;
    }
    
    @keyframes spin {
        to { transform: rotate(360deg); }
    }
    
    /* Button */
    .stButton>button {
        background: linear-gradient(135deg, #0284c7, #0369a1) !important;
        color: white !important;
        font-weight: 600 !important;
        border-radius: 10px !important;
        padding: 10px 20px !important;
        font-size: 0.85rem !important;
        border: none !important;
        box-shadow: 0 4px 12px rgba(2, 132, 199, 0.3) !important;
    }
    .stButton>button:hover { box-shadow: 0 6px 16px rgba(2, 132, 199, 0.4) !important; }
    
    /* Footer */
    .clinical-footer {
        position: fixed;
        bottom: 0;
        left: 0;
        width: 100%;
        background: linear-gradient(180deg, rgba(255,245,245,0.98) 0%, rgba(255,235,235,1) 100%);
        border-top: 2px solid #e74c3c;
        padding: 10px 16px;
        text-align: center;
        color: #e74c3c;
        font-weight: 700;
        font-size: 0.75rem;
        z-index: 9999;
        box-shadow: 0 -2px 10px rgba(231, 76, 60, 0.15);
        display: flex;
        align-items: center;
        justify-content: center;
        gap: 8px;
    }
    
    .footer-icon { font-size: 1rem; animation: pulse 2s infinite; }
    .footer-text { color: #e74c3c; font-weight: 700; letter-spacing: 0.3px; }
    
    @keyframes pulse {
        0%, 100% { opacity: 1; }
        50% { opacity: 0.6; }
    }
    
    @media screen and (max-width: 480px) {
        .clinical-footer { padding: 6px 10px; font-size: 0.65rem; }
    }
    
    @media screen and (min-width: 481px) and (max-width: 768px) {
        .clinical-footer { padding: 7px 12px; font-size: 0.7rem; }
    }
    
    @media screen and (min-width: 769px) and (max-width: 1024px) {
        .clinical-footer { padding: 8px 14px; font-size: 0.72rem; }
    }
    
    @media screen and (min-width: 1025px) and (max-width: 1440px) {
        .clinical-footer { padding: 10px 16px; font-size: 0.75rem; }
    }
    
    @media screen and (min-width: 1441px) {
        .clinical-footer { padding: 12px 20px; font-size: 0.8rem; }
    }
    
    @media screen and (max-height: 500px) and (orientation: landscape) {
        .clinical-footer { padding: 4px 10px; font-size: 0.6rem; }
    }
    
    @supports (padding-bottom: env(safe-area-inset-bottom)) {
        .clinical-footer { padding-bottom: calc(10px + env(safe-area-inset-bottom)); }
    }
    
    /* Content Padding */
    .block-container { padding: 0.5rem 1.5rem 4rem 1.5rem !important; }
    .stTabs [data-baseweb="tab-panel"] { padding-bottom: 50px !important; }
    div[data-testid="stChatInput"] { padding-bottom: 45px !important; }
    
    /* Chat */
    .stChatMessage { background: #f8fbff !important; border-radius: 10px; padding: 8px 12px !important; border: 1px solid #e0f2fe !important; }
    div[data-testid="stChatInput"] textarea { border-color: #e0f2fe !important; }
    
    /* Compact Columns */
    [data-testid="column"] { padding: 0 8px !important; }
    
    /* Hide uploader label */
    .stFileUploader>label { display: none; }
    
    /* Section titles */
    .section-title { font-size: 0.75rem; font-weight: 600; color: #64748b; margin: 8px 0 6px 0; }
</style>
""", unsafe_allow_html=True)

import re
import html

def _split_camel_case(text: str) -> str:
    text = re.sub(r'([a-z])([A-Z])', r'\1 \2', text)
    return text
    
def _fix_inline_lists(text: str) -> str:
    text = re.sub(r'(?<!\n)(\s)(\d+\.)\s+', r'\n\2 ', text)
    text = re.sub(r'(?<!\n)\s-\s+', r'\n- ', text)
    text = re.sub(r'^\s*\*\s+', '- ', text, flags=re.MULTILINE)
    return text

def _normalize_heading_case(text: str) -> str:
    text = text.lower().title()
    acronyms = ["CT", "MRI", "PET", "COPD", "CHF", "ILD", "ECG", "EKG", "ICU", "IV", "PA", "AP"]
    for a in acronyms:
        text = re.sub(rf'\b{a.title()}\b', a, text)
    return text
    
def _detect_headings(text: str) -> str:
    lines = text.split("\n")
    processed = []
    for line in lines:
        stripped = line.strip()
        is_heading = (
            len(stripped) > 3
            and len(stripped) < 80
            and not stripped.endswith(".")
            and not stripped.startswith("-")
            and not re.match(r'^\d+\.', stripped)
            and (
                stripped.isupper()
                or stripped.endswith(":")
                or stripped.istitle()
            )
        )

        if is_heading:
            stripped = _split_camel_case(stripped)
            normalized = _normalize_heading_case(stripped.rstrip(":"))
            processed.append(f"## {normalized}")
        else:
            processed.append(line)

    return "\n".join(processed)

def _clean_spacing(text: str) -> str:
    text = re.sub(r'\s+[:：]', ':', text)
    text = re.sub(r'^\s*[-:]{3,}(\s+[-:]{3,})+\s*$', '', text, flags=re.MULTILINE)
    text = text.replace("\r\n", "\n")
    text = re.sub(r'\n\s*\n\s*\n+', '\n\n', text)
    return text

def _remove_markdown_headings(text: str) -> str:
    return re.sub(
        r'^\s*#{1,}\s*',
        '',
        text,
        flags=re.MULTILINE
    )

def format_vision_text(text: str):
    if not text:
        return ""
    text = _remove_markdown_headings(text)
    text = _split_camel_case(text)
    text = _fix_inline_lists(text)
    text = _detect_headings(text)
    text = _clean_spacing(text)
    text = html.escape(text)
    text = re.sub(r'\*\*([^*]+)\*\*', r'<BOLD>\1</BOLD>', text)
    text = re.sub(r'^\s*##\s*(.+)$', r'<h5>\1</h5>', text, flags=re.MULTILINE)
    text = re.sub(r'\n{1,}', '', text)
    text = re.sub(r'\n{2,}', '\n', text)
    text = re.sub(r'\n{3,}', '\n', text)
    text = text.replace("\r\n", "\n")
    text = re.sub(r'\n\s*\n\s*\n+', '\n\n', text)
    return text

def format_llm_text(text: str):
    if not text:
        return ""
    text = _fix_inline_lists(text)
    text = _detect_headings(text)
    text = _clean_spacing(text)
    text = html.escape(text)
    text = re.sub(r'\*\*([^*]+)\*\*', r'<BOLD>\1</BOLD>', text)
    text = re.sub(r'^\s*##\s*(.+)$', r'<h5>\1</h5>', text, flags=re.MULTILINE)
    return text

def parse_sse_stream(response):
    event_type = "message"
    for line in response.iter_lines(decode_unicode=True):
        if not line:
            continue
        if line.startswith('event:'):
            event_type = line[6:].strip()
        elif line.startswith('data:'):
            data_str = line[5:].strip()
            try:
                data = json.loads(data_str)
                yield event_type, data
            except json.JSONDecodeError:
                yield event_type, {"raw": data_str}


def stream_single_file(file, patient_id, symptoms):
    files = {"file": (file.name, file.getvalue())}
    data = {
        "patient_id": patient_id or "Unknown",
        "symptoms": symptoms or ""
    }
    
    try:
        response = requests.post(
            f"{API_URL}/analyze_stream",
            files=files,
            data=data,
            stream=True,
            timeout=300
        )
        for event_type, data in parse_sse_stream(response):
            yield event_type, data
    except Exception as e:
        yield "error", {"message": str(e)}


def stream_case_analysis(files_list, patient_id, symptoms, current_meds):
    files = [("files", (f.name, f.getvalue())) for f in files_list]
    data = {
        "patient_id": patient_id or "Unknown",
        "symptoms": symptoms or "",
        "current_meds": current_meds or ""
    }
    
    try:
        response = requests.post(
            f"{API_URL}/analyze_case_stream",
            files=files,
            data=data,
            stream=True,
            timeout=600
        )
        for event_type, data in parse_sse_stream(response):
            yield event_type, data
        
    except Exception as e:
        yield "error", {"message": str(e)}


def stream_chat(message, history):
    payload = {"message": message, "history": history}
    
    try:
        response = requests.post(
            f"{API_URL}/chat_stream",
            json=payload,
            stream=True,
            timeout=120
        )
        for event_type, data in parse_sse_stream(response):
            yield event_type, data
    except Exception as e:
        yield "error", {"message": str(e)}

if "messages" not in st.session_state:
    st.session_state.messages = []
if "case_result" not in st.session_state:
    st.session_state.case_result = None
if "single_result" not in st.session_state:
    st.session_state.single_result = None
if "vision_reports" not in st.session_state:
    st.session_state.vision_reports = {}  
if "expanded_reports" not in st.session_state:
    st.session_state.expanded_reports = {}  


st.markdown("""
<div class="clinical-header">
    <div class="header-left">
        <span class="header-icon">🩺</span>
        <div>
            <div class="header-title">Qi-VLM: Quantum-Informed Vision-Language Model</div>
            <div class="header-sub">for Clinical Decision Support Only. Not for diagnostic use.</div>
        </div>
    </div>
</div>
""", unsafe_allow_html=True)

tab1, tab2, tab3 = st.tabs(["Assessment", "Report Analysis", "Consultation"])

with tab1:
    col_input, col_output = st.columns([0.35, 0.65], gap="small")

    with col_input:
        st.markdown('<div class="clinical-card">', unsafe_allow_html=True)
        st.markdown('<div class="card-label">📁 Upload Medical Files</div>', unsafe_allow_html=True)
        
        uploaded_files = st.file_uploader(
            "Upload", accept_multiple_files=True,
            type=['png', 'jpg', 'jpeg', 'dcm', 'pdf', 'txt', 'csv', 'bmp', 'dicom'],
            key="comp_up", label_visibility="collapsed"
        )

        if uploaded_files:
            st.markdown('<div class="section-title">Uploaded Files</div>', unsafe_allow_html=True)
            for file in uploaded_files:
                ext = file.name.lower().split('.')[-1] if '.' in file.name else ''
                icon = "📄" if ext == 'pdf' else "📋" if ext in ['txt', 'csv'] else "🩻" if ext in ['dcm', 'dicom'] else "🖼️"
                st.markdown(f'<div class="file-clinical"><span class="file-icon">{icon}</span><span class="file-name">{file.name}</span></div>', unsafe_allow_html=True)
        
        st.markdown('</div>', unsafe_allow_html=True)
        
        st.markdown('<div class="clinical-card">', unsafe_allow_html=True)
        st.markdown('<div class="card-label">👤 Patient Information</div>', unsafe_allow_html=True)
        patient_id = st.text_input("Patient ID", placeholder="PAT-001", label_visibility="collapsed")
        symptoms = st.text_area("Symptoms", height=40, placeholder="Enter symptoms...", label_visibility="collapsed")
        meds = st.text_area("Medications", height=40, placeholder="Current medications...", label_visibility="collapsed")
        st.markdown('</div>', unsafe_allow_html=True)

        analyze_btn = st.button("🔬 Analyze Case", use_container_width=True, type="primary")

    with col_output:
        if analyze_btn:
            if not uploaded_files:
                st.warning("Upload at least one file.")
            else:
                st.session_state.vision_reports = {}
                st.session_state.case_result = None
                
                status_placeholder = st.empty()
                completed_placeholder = st.empty()  
                current_vision_placeholder = st.empty()  
                llm_placeholder = st.empty()
                
                vision_text = ""
                current_filename = ""
                llm_text = ""
                
                try:
                    for event_type, data in stream_case_analysis(uploaded_files, patient_id, symptoms, meds):
                        if event_type == "status":
                            msg = data.get('message', '')
                            status_placeholder.markdown(f'<div class="status-badge"><div class="status-spinner"></div>{msg}</div>', unsafe_allow_html=True)
                        
                        elif event_type == "vision":
                            token = data.get('token', '')
                            current_filename = data.get('filename', '')
                            vision_text += token
                            formatted_text = format_vision_text(vision_text)
                            # Show streaming output for current file
                            current_vision_placeholder.markdown(f"""
                            <div class="streaming-container">
                                <div class="streaming-label">📷 Analyzing: {current_filename}</div>
                                <div class="streaming-text">{formatted_text}<span class="typing-cursor">▌</span></div>
                            </div>
                            """, unsafe_allow_html=True)
                        
                        elif event_type == "file_complete":
                            filename = data.get('filename', '')
                            st.session_state.vision_reports[filename] = {
                                'text': vision_text,
                                'type': 'Vision'
                            }
                            
                            current_vision_placeholder.empty()
                            
                            completed_count = len(st.session_state.vision_reports)
                            completed_placeholder.info(f"✅ {completed_count} file(s) analyzed - Reports available below")
                            
                            vision_text = ""
                            current_filename = ""
                        
                        elif event_type == "llm":
                            token = data.get('token', '')
                            llm_text += token
                            formatted_text = format_llm_text(llm_text)
                            llm_placeholder.markdown(f"""
                            <div class="synthesis-clinical">
                                <div class="card-label">💡 AI Clinical Summary</div>
                                {formatted_text}<span class="typing-cursor">▌</span>
                            </div>
                            """, unsafe_allow_html=True)
                        
                        elif event_type == "synthesis_complete":
                            synthesis = data.get('synthesis', llm_text)
                            status_placeholder.success("✅ Analysis Complete!")
                            formatted_text = format_llm_text(synthesis)
                            llm_placeholder.markdown(f"""
                            <div class="synthesis-clinical">
                                <div class="card-label">💡 AI Clinical Summary</div>
                                {formatted_text}
                            </div>
                            """, unsafe_allow_html=True)
                            st.session_state['case_result'] = {
                                'findings': list(st.session_state.vision_reports.keys()),
                                'synthesis': synthesis
                            }
                        
                        elif event_type == "complete":
                            status_placeholder.success("✅ All analysis complete!")
                        
                        elif event_type == "error":
                            status_placeholder.error(f"❌ {data.get('message', 'Error')}")
                    
                    time.sleep(1)
                    status_placeholder.empty()
                    completed_placeholder.empty()
                    
                    if st.session_state.get('vision_reports'):
                        st.markdown('<div class="reports-label">📁 Analysis Reports (Click to expand)</div>', unsafe_allow_html=True)
                        for filename, report_data in st.session_state.vision_reports.items():
                            report_text = report_data.get('text', '') if isinstance(report_data, dict) else report_data
                            file_type = report_data.get('type', 'Vision') if isinstance(report_data, dict) else 'Vision'
                            icon = "📷" if file_type == "Vision" else "📄" if file_type == "PDF" else "📋"
                            formatted_text = format_vision_text(report_text) if file_type == "Vision" else format_llm_text(report_text)
                            
                            with st.expander(f"{icon} {filename}", expanded=False):
                                st.markdown(f"<div class='report-text'>{formatted_text}</div>", unsafe_allow_html=True)
                    
                except Exception as e:
                    st.error(f"Streaming error: {e}")
        
        elif st.session_state.get('case_result'):
            res = st.session_state['case_result']
            
            if st.session_state.get('vision_reports'):
                st.markdown('<div class="reports-label">📁 Analysis Reports (Click to expand)</div>', unsafe_allow_html=True)
                for filename, report_data in st.session_state.vision_reports.items():
                    report_text = report_data.get('text', '') if isinstance(report_data, dict) else report_data
                    file_type = report_data.get('type', 'Vision') if isinstance(report_data, dict) else 'Vision'
                    icon = "📷" if file_type == "Vision" else "📄" if file_type == "PDF" else "📋"
                    formatted_text = format_vision_text(report_text) if file_type == "Vision" else format_llm_text(report_text)
                    
                    with st.expander(f"{icon} {filename}", expanded=False):
                        st.markdown(f"<div class='report-text'>{formatted_text}</div>", unsafe_allow_html=True)
            
            formatted_text = format_llm_text(res["synthesis"])
            st.success("✅ Analysis Complete")
            st.markdown(f"""
            <div class="synthesis-clinical">
                <div class="card-label">💡 AI Clinical Summary</div>
                {formatted_text}
            </div>
            """, unsafe_allow_html=True)
        else:
            st.info("Upload files and analyze to see results.")

with tab2:
    col_input, col_output = st.columns([0.35, 0.65], gap="small")

    with col_input:
        st.markdown('<div class="clinical-card">', unsafe_allow_html=True)
        st.markdown('<div class="card-label">📁 Upload File</div>', unsafe_allow_html=True)
        
        single_file = st.file_uploader(
            "Upload", type=["png", "jpg", "jpeg", "dcm", "txt", "pdf", "csv", "bmp", "dicom"],
            key="single_up", label_visibility="collapsed"
        )

        st.markdown('<div class="section-title">Patient ID</div>', unsafe_allow_html=True)
        spid = st.text_input("ID", placeholder="Optional", label_visibility="collapsed")
        symptoms_single = st.text_area("Symptoms", placeholder="Optional symptoms...", height=40, label_visibility="collapsed")

        analyze_single = st.button("🔍 Analyze", use_container_width=True, type="primary")
        st.markdown('</div>', unsafe_allow_html=True)

    with col_output:
        if analyze_single and single_file:
            status_placeholder = st.empty()
            vision_placeholder = st.empty()
            llm_placeholder = st.empty()
            
            vision_text = ""
            llm_text = ""
            
            try:
                for event_type, data in stream_single_file(single_file, spid, symptoms_single):
                    if event_type == "status":
                        msg = data.get('message', '')
                        status_placeholder.markdown(f'<div class="status-badge"><div class="status-spinner"></div>{msg}</div>', unsafe_allow_html=True)
                    
                    elif event_type == "vision":
                        token = data.get('token', '')
                        vision_text += token
                        formatted_text = format_vision_text(vision_text)
                        vision_placeholder.markdown(f"""
                        <div class="streaming-container">
                            <div class="streaming-label">📷 Vision Analysis</div>
                            <div class="streaming-text">{formatted_text}<span class="typing-cursor">▌</span></div>
                        </div>
                        """, unsafe_allow_html=True)
                    
                    elif event_type == "vision_complete":
                        formatted_text = format_vision_text(vision_text)
                        vision_placeholder.markdown(f"""
                        <div class="result-clinical">
                            <div class="result-file">📷 Vision Analysis</div>
                            <div class="result-text">{formatted_text}</div>
                        </div>
                        """, unsafe_allow_html=True)
                    
                    elif event_type == "llm":
                        token = data.get('token', '')
                        llm_text += token
                        formatted_text = format_llm_text(llm_text)
                        llm_placeholder.markdown(f"""
                        <div class="synthesis-clinical">
                            <div class="card-label">💡 Clinical Summary</div>
                            {formatted_text}<span class="typing-cursor">▌</span>
                        </div>
                        """, unsafe_allow_html=True)
                    
                    elif event_type == "complete":
                        status_placeholder.success("✅ Analysis Complete!")
                        formatted_text = format_llm_text(llm_text)
                        llm_placeholder.markdown(f"""
                        <div class="synthesis-clinical">
                            <div class="card-label">💡 Clinical Summary</div>
                            {formatted_text}
                        </div>
                        """, unsafe_allow_html=True)
                        st.session_state['single_result'] = {'synthesis': llm_text, 'vision': vision_text}
                    
                    elif event_type == "error":
                        status_placeholder.error(f"❌ {data.get('message', 'Error')}")
                
                time.sleep(1)
                status_placeholder.empty()
                        
            except Exception as e:
                st.error(f"Streaming error: {e}")
        
        elif st.session_state.get('single_result'):
            res = st.session_state['single_result']
            formatted_text = format_llm_text(res["synthesis"])
            st.success("✅ Analysis Complete")
            st.markdown(f'<div class="synthesis-clinical">{formatted_text}</div>', unsafe_allow_html=True)
        else:
            st.info("Upload a file to analyze.")

with tab3:
    chat_container = st.container(height=480)
    
    with chat_container:
        for msg in st.session_state.messages:
            with st.chat_message(msg["role"]):
                st.markdown(msg["content"])
    
    prompt = st.chat_input("Ask a medical question...")
    
    if prompt:
        st.session_state.messages.append({"role": "user", "content": prompt})
        
        with chat_container:
            with st.chat_message("user"):
                st.markdown(prompt)
            
            with st.chat_message("assistant"):
                response_placeholder = st.empty()
                full_response = ""
                
                for event_type, data in stream_chat(prompt, st.session_state.messages[-5:]):
                    if event_type == "token":
                        token = data.get('token', '')
                        full_response += token
                        response_placeholder.markdown(full_response + "▌")
                    elif event_type == "complete":
                        response_placeholder.markdown(full_response)
                    elif event_type == "error":
                        response_placeholder.error(f"Error: {data.get('message', 'Unknown error')}")
                        full_response = f"Error: {data.get('message', 'Unknown error')}"
                
                st.session_state.messages.append({"role": "assistant", "content": full_response})

st.markdown('''
<div class="clinical-footer">
    <span class="footer-icon">⚠️</span>
    <span class="footer-text">Clinical Decision Support Only. Not for diagnostic use.</span>
</div>
''', unsafe_allow_html=True)
# API Reference: Qi-VLM

Complete REST API documentation for the Qi-VLM backend service.

---

## Base URL

```
http://localhost:8000
```

---

## Endpoints Overview

| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/analyze` | Single file analysis (sync) |
| POST | `/analyze_stream` | Single file analysis (streaming) |
| POST | `/analyze_case_stream` | Multi-file case analysis |
| POST | `/chat` | Chat interaction (sync) |
| POST | `/chat_stream` | Chat interaction (streaming) |
| GET | `/health` | System health check |
| GET | `/context/status` | Case context status |
| POST | `/context/clear` | Clear case context |
| GET | `/quantum/status` | Quantum reasoning status |

---

## Detailed Endpoints

### `POST /analyze`

Analyze a single medical file synchronously.

**Request**:
- Content-Type: `multipart/form-data`

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `file` | File | Yes | Medical file (image, PDF, text) |
| `patient_id` | string | No | Patient identifier |
| `symptoms` | string | No | Patient symptoms |
| `current_meds` | string | No | Current medications |

**Response**:
```json
{
  "modality": "Medical Image",
  "summary": "Analysis findings...",
  "confidence": 0.90,
  "raw_output": {
    "summary": "...",
    "confidence": 0.90,
    "model": "qwen2.5-vl-7b-medical"
  },
  "synthesis": "Clinical summary..."
}
```

**Example**:
```bash
curl -X POST "http://localhost:8000/analyze" \
  -F "file=@chest_xray.png" \
  -F "symptoms=Cough, fever"
```

---

### `POST /analyze_stream`

Analyze a single medical file with streaming response.

**Request**: Same as `/analyze`

**Response**: Server-Sent Events (SSE)

| Event | Data | Description |
|-------|------|-------------|
| `status` | `{"message": "..."}` | Status update |
| `vision` | `{"token": "..."}` | Vision analysis token |
| `vision_complete` | `{"result": "..."}` | Vision analysis complete |
| `llm` | `{"token": "..."}` | LLM synthesis token |
| `complete` | `{"synthesis": "..."}` | Analysis complete |
| `error` | `{"message": "..."}` | Error occurred |

**Example**:
```javascript
const eventSource = new EventSource('/analyze_stream');
eventSource.onmessage = (event) => {
  const data = JSON.parse(event.data);
  console.log(data);
};
```

---

### `POST /analyze_case_stream`

Analyze multiple medical files as a unified case.

**Request**:
- Content-Type: `multipart/form-data`

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `files` | File[] | Yes | Multiple medical files |
| `patient_id` | string | No | Patient identifier |
| `symptoms` | string | No | Patient symptoms |
| `current_meds` | string | No | Current medications |

**Response**: Server-Sent Events (SSE)

| Event | Data | Description |
|-------|------|-------------|
| `status` | `{"message": "..."}` | Processing status |
| `vision` | `{"file_num": 1, "filename": "...", "token": "..."}` | Vision token |
| `file_complete` | `{"file_num": 1, "filename": "...", "result": "..."}` | File complete |
| `llm` | `{"token": "..."}` | Synthesis token |
| `synthesis_complete` | `{"synthesis": "..."}` | Synthesis done |
| `complete` | `{"message": "..."}` | All analysis complete |
| `error` | `{"message": "..."}` | Error occurred |

**Example**:
```python
import requests

files = [
    ("files", ("xray.png", open("xray.png", "rb"))),
    ("files", ("ecg.pdf", open("ecg.pdf", "rb")))
]
data = {"symptoms": "Chest pain", "current_meds": "Aspirin"}

response = requests.post(
    "http://localhost:8000/analyze_case_stream",
    files=files,
    data=data,
    stream=True
)

for line in response.iter_lines(decode_unicode=True):
    if line.startswith('data:'):
        print(line[5:])
```

---

### `POST /chat`

Chat with the AI about a previously analyzed case.

**Request**:
- Content-Type: `application/json`

```json
{
  "message": "What are the key findings?",
  "history": [
    {"role": "user", "content": "Previous question"},
    {"role": "assistant", "content": "Previous response"}
  ]
}
```

**Response**:
```json
{
  "response": "Based on the analysis..."
}
```

---

### `POST /chat_stream`

Chat with streaming response.

**Request**: Same as `/chat`

**Response**: Server-Sent Events (SSE)

| Event | Data | Description |
|-------|------|-------------|
| `token` | `{"token": "..."}` | Response token |
| `complete` | `{"message": "done"}` | Response complete |
| `error` | `{"message": "..."}` | Error occurred |

---

### `GET /health`

Check system health and model status.

**Response**:
```json
{
  "status": "healthy",
  "has_case_context": true,
  "coherence_level": 2
}
```

---

### `GET /context/status`

Get detailed case context status.

**Response**:
```json
{
  "has_context": true,
  "patient_id": "PAT-001",
  "findings_count": 3,
  "has_symptoms": true,
  "has_medications": false,
  "has_synthesis": true,
  "coherence_level": 2,
  "clinical_scenario": "chest_pain",
  "active_specialists": ["Cardiologist", "Pulmonologist"]
}
```

---

### `POST /context/clear`

Clear the current case context.

**Response**:
```json
{
  "status": "cleared"
}
```

---

### `GET /quantum/status`

Get quantum reasoning configuration status.

**Response**:
```json
{
  "quantum_vision_prompts": true,
  "quantum_diagnostic_prompts": true,
  "vision_presets": ["chest_xray", "ct_chest", "mri_brain", "ecg"],
  "clinical_scenarios": ["chest_pain", "abdominal_pain", "neurological"],
  "coherence_levels": {
    "1": "Single system, minimal superposition",
    "2": "Multi-system, moderate uncertainty",
    "3": "Complex case, extensive entanglement",
    "4": "Critical/maximum uncertainty"
  }
}
```

---

## Error Handling

All endpoints return errors in the following format:

```json
{
  "detail": "Error description"
}
```

### HTTP Status Codes

| Code | Description |
|------|-------------|
| 200 | Success |
| 400 | Bad Request |
| 404 | Not Found |
| 500 | Internal Server Error |

---

## Supported File Types

### Images
- PNG, JPEG, BMP
- DICOM (.dcm, .dicom)

### Documents
- PDF (text extraction via OCR)
- TXT (plain text)
- CSV (lab data)

---

## Rate Limiting

Currently no rate limiting is implemented. For production deployment, consider adding:
- Request rate limits per IP
- File size limits (default: 50MB)
- Concurrent request limits

---

## CORS Configuration

CORS is currently configured to allow all origins:

```python
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
```

For production, restrict to specific domains:

```python
allow_origins=["https://your-domain.com"]
```

---

## WebSocket Support

Currently not implemented. Future versions may add WebSocket support for real-time streaming.

---

<div align="center">

**[⬆ Back to README](../README.md)**

</div>

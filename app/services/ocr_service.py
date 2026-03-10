# ocr_service.py

import pytesseract
from PIL import Image
import os
import sys

from .. import config as cfg

TESSERACT_PATH = cfg.TESSERACT_PATH
POPPLER_PATH = cfg.POPPLER_PATH

if os.path.exists(TESSERACT_PATH):
    pytesseract.pytesseract.tesseract_cmd = TESSERACT_PATH
else:
    common_paths = [
        r"C:\Program Files\Tesseract-OCR\tesseract.exe",
        r"C:\Program Files (x86)\Tesseract-OCR\tesseract.exe",
        "/usr/bin/tesseract",
        "/usr/local/bin/tesseract"
    ]
    for path in common_paths:
        if os.path.exists(path):
            pytesseract.pytesseract.tesseract_cmd = path
            print(f"✅ Tesseract found at: {path}")
            break
    else:
        print(f"⚠️ Tesseract NOT found. OCR will use system default.")

if os.path.exists(POPPLER_PATH):
    os.environ['PATH'] += os.pathsep + POPPLER_PATH
else:
    print(f"⚠️ Poppler NOT found. PDF processing may fail.")


def extract_text_from_image(image_path):
    try:
        img = Image.open(image_path)
        img = img.convert('L')
        text = pytesseract.image_to_string(img)
        return text
    except Exception as e:
        print(f"OCR Error: {e}")
        return ""

def extract_text_from_pdf(pdf_path):
    try:
        from pdf2image import convert_from_path
        try:
            pages = convert_from_path(pdf_path, poppler_path=POPPLER_PATH)
        except:
            pages = convert_from_path(pdf_path)

        full_text = ""
        for page in pages:
            text = pytesseract.image_to_string(page)
            full_text += text + "\n"
        return full_text
    except Exception as e:
        print(f"PDF OCR Error: {e}")
        return ""

# app/services/model_downloader.py

import os
import sys
from huggingface_hub import hf_hub_download, snapshot_download

from .. import config as cfg

def check_and_download_models():
    print("\n" + "="*60)
    print("CHECKING MODELS AVAILABILITY")
    print("="*60)

    llm_path = cfg.LLM_MODEL_PATH
    if not os.path.exists(llm_path):
        print(f"\nLLM not found.")
        print(f"   Downloading from Hugging Face: {cfg.LLM_HF_REPO} ...")
        try:
            hf_hub_download(
                repo_id=cfg.LLM_HF_REPO,
                filename=cfg.LLM_HF_FILE,
                local_dir=cfg.MODEL_DIR,
                local_dir_use_symlinks=False,  
                resume_download=True
            )
            print(f"LLM Download Complete: {cfg.LLM_HF_FILE}")
        except Exception as e:
            print(f"❌ LLM Download Failed: {e}")
            print("   Please ensure you have internet access and disk space.")
            sys.exit(1)
    else:
        print(f"LLM Model - OK")

    vision_path = cfg.VISION_MODEL_PATH
    config_file = os.path.join(vision_path, "config.json")
    
    if not os.path.exists(vision_path) or not os.path.exists(config_file):
        print(f"\nVision Model not found.")
        print(f"   Downloading from Hugging Face: {cfg.VISION_HF_REPO} ...")
        print("   ⚠️ This is a large model (~15-30GB). This may take a while...")
        
        try:
            snapshot_download(
                repo_id=cfg.VISION_HF_REPO,
                local_dir=vision_path,
                local_dir_use_symlinks=False,  
                resume_download=True,
            )
            print(f"Vision Model Download Complete.")
        except Exception as e:
            print(f"Vision Model Download Failed: {e}")
            print("   Please ensure you have internet access and disk space.")
            sys.exit(1)
    else:
        print(f"Vision Model - OK")

    print("="*60 + "\n")
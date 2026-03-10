@echo off
echo Checking Virtual Environment...
if not exist "venv" (
    echo Creating venv...
    python -m venv venv
)

echo Activating venv...
call venv\Scripts\activate.bat

echo Upgrading Pip...
python -m pip install --upgrade pip

echo Installing Dependencies from requirements.txt...
pip install -r requirements.txt

echo Installing PyTorch with CUDA 12.4 Support...
pip install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cu124

echo Installing llama-cpp-python...
pip install llama-cpp-python

echo Starting Backend...
start "MedAssist-API" cmd /k "venv\Scripts\activate.bat && python -m uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload"

timeout /t 5 /nobreak > NUL

echo Starting Frontend...
start "MedAssist-UI" cmd /k "venv\Scripts\activate.bat && streamlit run streamlit_app.py"

echo System Running. Close windows to stop.

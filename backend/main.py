from fastapi import FastAPI, UploadFile, File, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pathlib import Path
import shutil
import math

# Import our backend modules
from backend.modules.data_loader import load_dataset
from backend.modules.data_cleaner import clean_dataset
from backend.modules.analyzer import dataset_statistics
from backend.modules.visualizer import generate_charts
from backend.modules.model_trainer import auto_train_model
from backend.modules.chat import chat_with_data
from pydantic import BaseModel
from typing import Optional

app = FastAPI(title="AI Autonomous Data Analyst", version="1.0")

class ChatRequest(BaseModel):
    query: str
    file_path: str
    api_key: Optional[str] = None


app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

UPLOAD_FOLDER = Path("backend/uploads")

@app.get("/")
def home():
    return {"message": "AI Autonomous Data Analyst API running"}

# Clean infinite and NaN values which break JSON serialization
def sanitize_stats(stats):
    import numpy as np
    sanitized = {}
    for key, value in stats.items():
        if isinstance(value, dict):
            sanitized[key] = sanitize_stats(value)
        elif isinstance(value, (int, float)):
            if np.isnan(value) or np.isinf(value):
                sanitized[key] = None
            else:
                sanitized[key] = value
        else:
            sanitized[key] = value
    return sanitized

@app.post("/upload")
async def upload_dataset(file: UploadFile = File(...)):
    if not file.filename:
        raise HTTPException(status_code=400, detail="Missing filename.")

    safe_name = Path(file.filename).name
    UPLOAD_FOLDER.mkdir(parents=True, exist_ok=True)
    file_path = UPLOAD_FOLDER / safe_name

    with file_path.open("wb") as buffer:
        shutil.copyfileobj(file.file, buffer)

    try:
        # Process the file
        df = load_dataset(str(file_path))
        df_cleaned = clean_dataset(df)
        raw_stats = dataset_statistics(df_cleaned)
        
        # Additional Capabilities
        charts_json = generate_charts(df_cleaned)
        ml_prediction = auto_train_model(df_cleaned)
        
        # Make it JSON serializable
        stats = sanitize_stats(raw_stats)
        
        return {
            "status": "success", 
            "file_path": str(file_path),
            "analysis": stats,
            "charts": charts_json,
            "ml_prediction": ml_prediction
        }
    except Exception as e:
        return {"status": "error", "message": f"Data processing failed: {str(e)}"}

@app.get("/analysis")
def get_analysis():
    return {"message": "Analysis endpoint"}

@app.post("/chat")
def data_chat(request: ChatRequest):
    if not request.file_path or not request.query:
        raise HTTPException(status_code=400, detail="Missing query or file_path")
    
    # Optional logic: ensure file exists
    if not Path(request.file_path).exists():
        raise HTTPException(status_code=404, detail="Dataset file not found. Please re-upload.")
        
    response_text = chat_with_data(request.file_path, request.query, request.api_key)
    return {"status": "success", "response": response_text}
import os
from contextlib import asynccontextmanager
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from app.redactor import Redactor

@asynccontextmanager
async def lifespan(app: FastAPI):
    print("\n[INFO] Booting up Engine Room: Loading model...")
    current_dir = os.path.dirname(os.path.abspath(__file__))
    model_path = os.path.join(current_dir,"..", "models", "quantized_gguf", "pii-redactor-qwen-q4_k_m.gguf") 
    
    app.redactor = Redactor(model_path)
    
    yield 
    
    app.redactor = None

app = FastAPI(lifespan=lifespan)

class RedactionRequest(BaseModel):
    text: str

@app.post("/redact")
def redact(request: RedactionRequest):
    try:
        result = app.redactor.process_text(request.text)
        return {"original": request.text, "redacted": result}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
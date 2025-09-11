from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List, Optional, Dict, Any
import os
import hashlib
import psycopg2
from psycopg2.extras import RealDictCursor
from cryptography.fernet import Fernet
from dotenv import load_dotenv
import json

load_dotenv()

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Database connection
def get_db_connection():
    url = os.getenv("SUPABASE_URL", "https://wxqhercmwmyhihfcuwti.supabase.co")
    host = url.replace("https://", "").replace(".supabase.co", "")
    return psycopg2.connect(
        host=f"db.{host}.supabase.co",
        database="postgres",
        user="postgres",
        password=os.getenv("SUPABASE_PASSWORD", ""),
        port=5432
    )

# Encryption setup
encryption_key = os.getenv("ENCRYPTION_KEY", Fernet.generate_key())
cipher = Fernet(encryption_key)

def text_to_vector(text: str) -> List[float]:
    """Convert text to 192-dim vector using MD5 hash"""
    hash_obj = hashlib.md5(text.encode())
    hash_bytes = hash_obj.digest()
    # Extend to 192 dimensions by repeating and padding
    extended = (hash_bytes * 12)[:24]  # 24 bytes = 192 bits
    return [float(b) / 255.0 for b in extended]

from memory import db, inner_voice, learn, ask_back, budget
import asyncio

class QueryRequest(BaseModel):
    q: str
    kind: Optional[str] = None
    top_k: int = 3

class SpendRequest(BaseModel):
    tokens: int

class DocumentResponse(BaseModel):
    score: float
    doc: Dict[str, Any]

@app.post("/query", response_model=List[DocumentResponse])
async def query_documents(request: QueryRequest):
    try:
        query_vector = text_to_vector(request.q)
        
        # Using SQLite for now, not Supabase for documents table
        # This part needs to be updated if documents are moved to SQLite
        raise HTTPException(status_code=501, detail="/query endpoint not yet implemented for SQLite documents.")
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/spend")
async def spend_tokens(request: SpendRequest):
    try:
        if budget.spend_with_plan("API_Spend", request.tokens):
            return {"ok": True, "bal": db.token_balance()}
        else:
            return {"ok": False, "bal": db.token_balance()}
            
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/chat")
async def chat(msg: str):
    # Store user turn
    db.add_turn(role="user", text=msg)

    # Maybe ask back
    question = ask_back.should_ask_back({"text": msg})
    if question:
        db.add_turn(role="assistant", text=question)
        return {"reply": question}
    else:
        # Normal RAG reply (placeholder for now)
        reply = f"Echo: {msg}"
        # In a real scenario, this would involve RAG logic

        db.add_turn(role="assistant", text=reply)

        # Reflect & learn in background
        asyncio.create_task(inner_voice.reflect({"text": reply}))
        asyncio.create_task(learn.learn_from_turn({"text": msg}))
        
        return {"reply": reply}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)



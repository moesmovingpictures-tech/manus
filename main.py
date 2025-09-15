from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List, Optional, Dict, Any
import os
import hashlib
import asyncio
import json # Keep json for meta handling
from memory.deepseek_utils import deepseek_chat_completion
from memory.task_queue import background_task_queue

from memory import db, inner_voice, learn, ask_back, budget, monitor

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

def text_to_vector(text: str) -> List[float]:
    """Convert text to 192-dim vector using MD5 hash"""
    hash_obj = hashlib.md5(text.encode())
    hash_bytes = hash_obj.digest()
    # Extend to 192 dimensions by repeating and padding
    extended = (hash_bytes * 12)[:24]  # 24 bytes = 192 bits
    return [float(b) / 255.0 for b in extended]

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
        
        pool = await db.get_db_pool()
        
        # Build query for SQLite
        # Note: SQLite does not have a native vector type or cosine similarity operator.
        # The 'embedding - ?' is a placeholder. For actual vector similarity, 
        # a custom function or a dedicated vector search library would be needed.
        # For now, it will perform a subtraction, which is not a true similarity metric.
        base_query = """
        SELECT id, text, kind, meta, 
               (SELECT SUM(ABS(CAST(json_extract(T1.value, '$') AS REAL) - CAST(json_extract(T2.value, '$') AS REAL))) 
                FROM json_each(conv_turn.embedding) AS T1, json_each(?) AS T2 
                WHERE T1.key = T2.key) as score -- Placeholder for L1 distance
        FROM conv_turn 
        WHERE embedding IS NOT NULL
        """
        params = [json.dumps(query_vector)]
        
        if request.kind:
            base_query += " AND kind = ?"
            params.append(request.kind)
            
        base_query += " ORDER BY score ASC LIMIT ?" # ASC for distance (lower is better)
        params.append(request.top_k)
        
        cursor = await pool.execute(base_query, params)
        results = await cursor.fetchall()
        
        response = []
        for row in results:
            response.append(DocumentResponse(
                score=float(row["score"]),
                doc={
                    "id": row["id"],
                    "text": row["text"],
                    "kind": row["kind"],
                    "meta": json.loads(row["meta"]) if row["meta"] else None
                }
            ))
        
        return response
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/spend")
async def spend_tokens(request: SpendRequest):
    try:
        if await budget.spend_with_plan("API_Spend", request.tokens):
            return {"ok": True, "bal": await db.token_balance()}
        else:
            return {"ok": False, "bal": await db.token_balance()}
            
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/chat")
async def chat(msg: str):
    # Store user turn
    await db.add_turn(role="user", text=msg, embedding=text_to_vector(msg))

    # Maybe ask back
    question = ask_back.should_ask_back({"text": msg})
    if question:
        await db.add_turn(role="assistant", text=question)
        return {"reply": question}
    else:
        # Normal RAG reply (placeholder for now)
        reply = f"Echo: {msg}"
        # In a real scenario, this would involve RAG logic

        await db.add_turn(role="assistant", text=reply)

        # Reflect & learn in background
        await background_task_queue.add_task(inner_voice.reflect, {"text": reply})
        await background_task_queue.add_task(learn.learn_from_turn, {"text": msg})
        
        return {"reply": reply}

@app.on_event("startup")
async def startup_event():
    asyncio.create_task(monitor.start_monitoring())

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)




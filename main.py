from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List, Optional, Dict, Any
import os
import hashlib
import asyncio
import json # Keep json for meta handling
import time
from memory.deepseek_utils import deepseek_chat_completion
from memory.task_queue import background_task_queue

from memory import db, inner_voice, learn, ask_back, budget, monitor, orchestrator, manifest
from memory.inter_manus_sync import inter_manus_sync

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

class ChatRequest(BaseModel):
    msg: str

@app.post("/chat")
async def chat(request: ChatRequest):
    # Route all requests through the orchestrator
    orchestration_result = await orchestrator.orchestrate_request(request.msg)
    
    if orchestration_result["error"]:
        raise HTTPException(status_code=500, detail=orchestration_result["error"])

    # Store user turn
    await db.add_turn(role="user", text=request.msg, embedding=text_to_vector(request.msg))

    # Store assistant turn from orchestrator
    reply = orchestration_result["response"]
    await db.add_turn(role="assistant", text=reply)

    # Reflect & learn in background
    await background_task_queue.add_task(inner_voice.reflect, {"text": reply})
    await background_task_queue.add_task(learn.learn_from_turn, {"text": request.msg})
    
    return {"reply": reply}

@app.on_event("startup")
async def startup_event():
    asyncio.create_task(monitor.start_monitoring())
    await inter_manus_sync.start_sync_service()
    await manifest.update_manifest()

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)




# Inter-Manus Communication Endpoints

@app.get("/sync/status")
async def get_sync_status():
    """Get current synchronization status"""
    try:
        pool = await db.get_db_pool()
        cursor = await pool.execute("SELECT * FROM sync_status WHERE id = 1")
        status = await cursor.fetchone()
        
        # Get recent activity
        cursor = await pool.execute("SELECT * FROM recent_sync_activity")
        activity = await cursor.fetchall()
        
        return {
            "sync_enabled": bool(status["sync_enabled"]) if status else False,
            "last_sync": status["last_sync_timestamp"] if status else 0,
            "last_successful_sync": status["last_successful_sync"] if status else 0,
            "sync_errors": status["sync_errors"] if status else 0,
            "brother_manus_url": status["brother_manus_url"] if status else None,
            "recent_activity": [dict(row) for row in activity] if activity else []
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/sync/trigger")
async def trigger_sync():
    """Manually trigger a synchronization cycle"""
    try:
        await inter_manus_sync.perform_sync()
        return {"status": "sync_triggered", "timestamp": int(time.time())}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/sync/concepts")
async def get_synced_concepts():
    """Get concepts received from brother Manus"""
    try:
        pool = await db.get_db_pool()
        cursor = await pool.execute("""
            SELECT * FROM concepts 
            WHERE source LIKE 'sync_%' 
            ORDER BY created_at DESC 
            LIMIT 50
        """)
        concepts = await cursor.fetchall()
        
        return {
            "concepts": [dict(row) for row in concepts],
            "count": len(concepts)
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/sync/metrics")
async def get_brother_metrics():
    """Get performance metrics from brother Manus"""
    try:
        pool = await db.get_db_pool()
        cursor = await pool.execute("""
            SELECT * FROM brother_metrics 
            ORDER BY timestamp DESC 
            LIMIT 10
        """)
        metrics = await cursor.fetchall()
        
        return {
            "metrics": [dict(row) for row in metrics],
            "count": len(metrics)
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/sync/receive")
async def receive_sync_message(message: dict):
    """Receive a synchronization message from brother Manus"""
    try:
        # Store incoming message for processing
        await inter_manus_sync.store_sync_log("incoming", message)
        
        return {"status": "message_received", "timestamp": int(time.time())}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


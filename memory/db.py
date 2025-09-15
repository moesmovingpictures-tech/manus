import aiosqlite
import json
import os
import asyncio

_DB_PATH = "memory/db.sqlite"
_POOL = None

async def get_db_pool():
    global _POOL
    if _POOL is None:
        _POOL = await aiosqlite.connect(_DB_PATH)
        _POOL.row_factory = aiosqlite.Row # To access columns by name
    return _POOL

async def add(txt):
    pool = await get_db_pool()
    await pool.execute("INSERT INTO lessons(txt,ts) VALUES(?,?)",(txt,int(os.time())))
    await pool.commit()

async def fetch(n=5):
    pool = await get_db_pool()
    cursor = await pool.execute("SELECT txt FROM lessons ORDER BY ts DESC LIMIT ?", (n,))
    rows = await cursor.fetchall()
    return [r["txt"] for r in rows]

async def token_balance():
    balance_file = "token_balance.txt"
    if os.path.exists(balance_file):
        with open(balance_file, 'r') as f:
            return int(f.read().strip())
    return 300000 # Default daily limit if file not found

async def add_turn(role, text, meta=None, embedding=None):
    pool = await get_db_pool()
    await pool.execute("INSERT INTO conv_turn(role,text,meta,embedding,ts) VALUES (?,?,?,?,?)",
                (role, text, json.dumps(meta) if meta else None, json.dumps(embedding) if embedding else None, int(os.time())))
    await pool.commit()

async def spend(tokens: int):
    balance_file = "token_balance.txt"
    current_balance = 300000 # Default if file not found
    if os.path.exists(balance_file):
        with open(balance_file, 'r') as f:
            current_balance = int(f.read().strip())
    new_balance = current_balance - tokens
    with open(balance_file, 'w') as f:
        f.write(str(new_balance))
    print(f"Spent {tokens} tokens. New balance: {new_balance}")



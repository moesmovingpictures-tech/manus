import sys; sys.path.insert(0,"memory"); import db
import asyncio
import os, time

async def self_patch(txt):
    await db.add(txt)                      # persist to SQLite
    latest = await db.fetch(5)             # last 5 lessons
    print("===== MEMORY-RELOAD =======")
    for l in latest:
        print(l)

# This part needs to be called from an async context if self_patch is to be used directly.
# For now, it's assumed to be called from a context that manages the event loop.



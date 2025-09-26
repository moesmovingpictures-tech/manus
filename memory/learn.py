import aiosqlite, itertools, json, time
import asyncio
from memory import db

async def extract_nouns(text):
    # Placeholder for actual implementation (e.g., using spaCy or regex)
    # For now, a simple split and filter for capitalized words
    return [word for word in text.split() if len(word) > 1 and word[0].isupper()]

async def learn_from_turn(turn: dict):
    pool = await db.get_db_pool()
    txt = turn["text"]

    # 4.1 Extract & canonicalise concepts
    nouns = await extract_nouns(txt)
    for noun in nouns:
        await pool.execute("""INSERT INTO concept(name,summary,ts)
        VALUES (?,?,?) ON CONFLICT(name) DO UPDATE
        SET summary=excluded.summary""",
        (noun, f"First seen: {txt[:80]}", int(time.time())))

    # 4.2 Build edges (co-occurrence within same sentence)
    for pair in itertools.combinations(nouns, 2):
        # Ensure the order for consistency, though not strictly necessary for \'related\'
        sorted_pair = tuple(sorted(pair))
        cursor = await pool.execute("""
            SELECT c1.id, c2.id FROM concept c1, concept c2
            WHERE c1.name=? AND c2.name=?
        """, sorted_pair)
        ids = await cursor.fetchone()
        if ids:
            src_id, dst_id = ids
            await pool.execute("""
                INSERT INTO concept_link(src_id,dst_id,rel)
                VALUES (?,?,?)
                ON CONFLICT DO NOTHING""", (src_id, dst_id, 'related'))

    # 4.3 Summarise conversation every N turns
    # This part requires an LLM call, which is outside the current scope of this file
    # and will be handled by the main application logic or a separate module.
    # For now, we\'ll just track the turn count.
    # count = await pool.execute("SELECT COUNT(*) FROM conv_turn WHERE role=\'user\'").fetchone()[0]
    # if count % 10 == 0:
    #     summary = "# TODO: Summarize last 10 turns using LLM"
    #     await pool.execute("INSERT INTO concept(name,summary,meta,ts)
    #     VALUES (?,?,?,?)",
    #     (f"session-{count//10}", summary, json.dumps({"type": "session"}), int(time.time())))

    await pool.commit()



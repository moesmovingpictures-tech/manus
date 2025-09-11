import sqlite3, itertools, json, time
from memory import db

def extract_nouns(text):
    # Placeholder for actual implementation (e.g., using spaCy or regex)
    # For now, a simple split and filter for capitalized words
    return [word for word in text.split() if len(word) > 1 and word[0].isupper()]

def learn_from_turn(turn: dict):
    con = sqlite3.connect("memory/db.sqlite")
    txt = turn["text"]

    # 4.1 Extract & canonicalise concepts
    nouns = extract_nouns(txt)
    for noun in nouns:
        con.execute("""INSERT INTO concept(name,summary,ts)
        VALUES (?,?,?) ON CONFLICT(name) DO UPDATE
        SET summary=excluded.summary""",
        (noun, f"First seen: {txt[:80]}", int(time.time())))

    # 4.2 Build edges (co-occurrence within same sentence)
    for pair in itertools.combinations(nouns, 2):
        # Ensure the order for consistency, though not strictly necessary for 'related'
        sorted_pair = tuple(sorted(pair))
        cur = con.execute("""
            SELECT c1.id, c2.id FROM concept c1, concept c2
            WHERE c1.name=? AND c2.name=?
        """, sorted_pair)
        ids = cur.fetchone()
        if ids:
            src_id, dst_id = ids
            con.execute("""
                INSERT INTO concept_link(src_id,dst_id,rel)
                VALUES (?,?,?)
                ON CONFLICT DO NOTHING""", (src_id, dst_id, 'related'))

    # 4.3 Summarise conversation every N turns
    # This part requires an LLM call, which is outside the current scope of this file
    # and will be handled by the main application logic or a separate module.
    # For now, we'll just track the turn count.
    # count = con.execute("SELECT COUNT(*) FROM conv_turn WHERE role=\'user\'").fetchone()[0]
    # if count % 10 == 0:
    #     summary = "# TODO: Summarize last 10 turns using LLM"
    #     con.execute("INSERT INTO concept(name,summary,meta,ts)
    #     VALUES (?,?,?,?)",
    #     (f"session-{count//10}", summary, json.dumps({"type": "session"}), int(time.time())))

    con.commit()
    con.close()



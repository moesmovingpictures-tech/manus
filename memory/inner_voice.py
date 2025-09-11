import os, json, random, difflib, sqlite3
from memory import db

def text_to_vector(text): # Placeholder for actual implementation
    # This should be a deterministic 192-dim hash based on the blueprint
    # For now, a simple placeholder
    return [float(ord(c)) / 128.0 for c in text[:24]] + [0.0] * (192 - len(text[:24]))

def extract_nouns(text):
    # Placeholder for actual implementation (e.g., using spaCy or regex)
    # For now, a simple split
    return [word for word in text.split() if len(word) > 3 and word[0].isupper()]

def reflect(last_turn: dict):
    con = sqlite3.connect("memory/db.sqlite")
    thoughts = []

    # 2.1 Do I understand the user’s real goal?
    goal_vector = text_to_vector(last_turn["text"])
    cur = con.execute("""
    SELECT text FROM conv_turn
    WHERE role=\'user\'
    ORDER BY embedding <-> ? LIMIT 3""", (goal_vector,))
    similar = [r[0] for r in cur.fetchall()]
    if similar and difflib.SequenceMatcher(None, last_turn["text"], similar[0]).ratio() > .9:
        thoughts.append("- User repeats themselves → I may be stuck in a loop.")

    # 2.2 Did I just invent a new concept?
    nouns = extract_nouns(last_turn["text"])
    for noun in nouns:
        cur.execute("SELECT 1 FROM concept WHERE name=?", (noun,))
        if not cur.fetchone():
            thoughts.append(f"- New concept detected: {noun} → will ask to confirm.")

    # 2.3 Credit check
    # bal = db.token_balance() # Assuming db.token_balance() exists or will be implemented
    # if bal < 50000:
    #     thoughts.append(f"- ⚠️  Only {bal/1000:.0f} kT left today → switch to thrift mode.")

    monologue = "\n".join(thoughts) or "- All quiet."
    con.execute("INSERT INTO conv_turn(role,text,meta) VALUES (
        \"self\",
        ?,
        ?)",
        (monologue, json.dumps({"type": "monologue"})))
    con.commit()
    con.close()
    print("🧠  " + monologue)



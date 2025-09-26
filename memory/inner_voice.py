import os, json, random, difflib
import asyncio
from memory import db
from memory.deepseek_utils import deepseek_chat_completion

def text_to_vector(text): # Placeholder for actual implementation
    # This should be a deterministic 192-dim hash based on the blueprint
    # For now, a simple placeholder
    return [float(ord(c)) / 128.0 for c in text[:24]] + [0.0] * (192 - len(text[:24]))

def extract_nouns(text):
    # Placeholder for actual implementation (e.g., using spaCy or regex)
    # For now, a simple split
    return [word for word in text.split() if len(word) > 3 and word[0].isupper()]

async def reflect(last_turn: dict):
    pool = await db.get_db_pool()
    thoughts = []

    # 2.1 Do I understand the user’s real goal?
    goal_vector = text_to_vector(last_turn["text"])
    cursor = await pool.execute("""
    SELECT text FROM conv_turn
    WHERE role=\'user\'
    ORDER BY embedding <-> ? LIMIT 3""", (json.dumps(goal_vector),))
    similar = [r[0] for r in await cursor.fetchall()]
    if similar and difflib.SequenceMatcher(None, last_turn["text"], similar[0]).ratio() > .9:
        thoughts.append("- User repeats themselves → I may be stuck in a loop.")

    # 2.2 Did I just invent a new concept?
    nouns = extract_nouns(last_turn["text"])
    for noun in nouns:
        cursor = await pool.execute("SELECT 1 FROM concept WHERE name=?", (noun,))
        if not await cursor.fetchone():
            thoughts.append(f"- New concept detected: {noun} → will ask to confirm.")

    # 2.3 Credit check
    bal = await db.token_balance() # Assuming db.token_balance() exists or will be implemented
    if bal < 50000:
        thoughts.append(f"- ⚠️  Only {bal/1000:.0f} kT left today → switch to thrift mode.")

    monologue = "\n".join(thoughts)

    # Use DeepSeek for more complex reflection if needed and budget allows
    if not monologue and bal > 10000: # Example condition: if no simple thoughts, and enough budget
        messages = [
            {"role": "system", "content": "You are an AI reflecting on its recent interaction. Provide concise, markdown-formatted thoughts on potential improvements, new concepts, or issues."},
            {"role": "user", "content": f"Reflect on the last assistant turn: {last_turn['text']}"}
        ]
        deepseek_response = await deepseek_chat_completion(messages, model="deepseek-reasoner")
        if deepseek_response and deepseek_response["choices"][0]["message"]["content"]:
            monologue = deepseek_response["choices"][0]["message"]["content"]
            # Deduct tokens for DeepSeek call (placeholder for actual token counting)
            await db.spend(500) # Example cost

    monologue = monologue or "- All quiet."

    await pool.execute("""INSERT INTO conv_turn(role,text,meta) VALUES (
        "self",
        ?,
        ?)""",
        (monologue, json.dumps({"type": "monologue"})))
    await pool.commit()
    print("🧠  " + monologue)



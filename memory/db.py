import sqlite3,json,os

def add(txt):
    con=sqlite3.connect("memory/db.sqlite")
    con.execute("INSERT INTO lessons(txt,ts) VALUES(?,?)",(txt,int(os.time())))
    con.commit();con.close()

def fetch(n=5):
    con=sqlite3.connect("memory/db.sqlite")
    rows=con.execute("SELECT txt FROM lessons ORDER BY ts DESC LIMIT ?", (n,)).fetchall()
    con.close();return [r[0] for r in rows]

def token_balance():
    balance_file = "token_balance.txt"
    if os.path.exists(balance_file):
        with open(balance_file, 'r') as f:
            return int(f.read().strip())
    return 300000 # Default daily limit if file not found

def add_turn(role, text, meta=None):
    con = sqlite3.connect("memory/db.sqlite")
    con.execute("INSERT INTO conv_turn(role,text,meta,ts) VALUES (?,?,?,?)",
                (role, text, json.dumps(meta) if meta else None, int(os.time())))
    con.commit()
    con.close()



def spend(tokens: int):
    balance_file = "token_balance.txt"
    current_balance = 300000 # Default if file not found
    if os.path.exists(balance_file):
        with open(balance_file, 'r') as f:
            current_balance = int(f.read().strip())
    new_balance = current_balance - tokens
    with open(balance_file, 'w') as f:
        f.write(str(new_balance))
    print(f"Spent {tokens} tokens. New balance: {new_balance}")



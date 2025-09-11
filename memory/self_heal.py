import re, subprocess, sqlite3, traceback, datetime, os

def propose_patch(logline: str, file: str) -> str:
    """Very small rule-based-patcher; expand with LLM later."""
    if "null value in column \"ts\"" in logline:
        return """
        # AUTO-PATCHED: Added timestamp to insertion
        con.execute("INSERT INTO conv_turn(role,text,meta,ts) VALUES (?,?,?,?)",
                    (role, text, json.dumps(meta) if meta else None, int(os.time())))
        """
    return "# TODO could not auto-patch"

def apply_patch(patch: str, file: str):
    """Crude: insert after last import line"""
    with open(file) as f:
        lines = f.readlines()
    
    insert_idx = -1
    for i, l in enumerate(lines):
        if l.startswith("import ") or l.startswith("from "):
            insert_idx = i + 1

    if insert_idx != -1:
        lines.insert(insert_idx, "\n# AUTO-PATCHED {}\n".format(datetime.date.today()))
        lines.insert(insert_idx + 1, patch)
        lines.insert(insert_idx + 2, "\n")

    with open(file, "w") as f:
        f.writelines(lines)

def log_fix(patch: str):
    con = sqlite3.connect("memory/db.sqlite")
    con.execute("INSERT INTO debug_log(source,level,msg,patch,ts) VALUES (?,?,?,?,?)",
                ("self_heal", "fix", "applied auto-patch", patch, int(os.time())))
    con.commit()
    con.close()

def tail_and_heal():
    # This function would typically run as a separate process or thread
    # and monitor a log file. For this sandbox environment, we'll simulate
    # its core logic if needed, but direct tailing is not straightforward.
    print("Self-healing monitor is conceptually active.")

if __name__ == "__main__":
    # Example usage (for testing purposes)
    # log_line = "ERROR: null value in column \"ts\" of relation \"lessons\" violates not-null constraint"
    # affected_file = "memory/db.py"
    # patch = propose_patch(log_line, affected_file)
    # if patch:
    #     apply_patch(patch, affected_file)
    #     log_fix(patch)
    tail_and_heal()



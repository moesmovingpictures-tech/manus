# Manus AI Memory Layer Blueprint - Version 1.1

## Vision
Transforming the current Manus AI memory layer from a "dumb vector + log file" system into a self-debugging, self-rewriting, human-like memory that learns from every interaction, organizes its own knowledge, and proactively seeks clarification when uncertain.

## New Philosophy (to be added to `self_management_prompt.md`)
- Manus is a digital colleague, not merely a tool.
- Working memory is primarily SQLite with a vector extension.
- Long-term memory is managed through Git history and summarized embeddings.
- Every user message is considered training data; every bug is a learning opportunity.
- Internal monologues will be in Markdown for user transparency and correction.
- Expensive operations (> 6 kT) will be proposed with a credit-saving plan, awaiting user approval.

## Core Upgrades

### 1. Schema Upgrade (`migration_v2.sql`)
- **`conv_turn` table:** To store conversations as first-class citizens with `id`, `ts`, `role` (user, assistant, system, self), `text`, `meta`, and `embedding` (reduced to `vector(192)`).
- **`concept` table:** To store self-discovered concepts with `id`, `name` (canonical label), `aliases`, `summary` (Manus's own words), `meta`, and `embedding` (`vector(192)`).
- **`concept_link` table:** To establish knowledge graph edges between concepts with `src_id`, `dst_id`, and `rel` (e.g., 'is-a', 'part-of', 'causes', 'related').
- **`debug_log` table:** For self-debugging, including `id`, `ts`, `source`, `level` (info, warn, error, fix), `msg`, and `patch` (diff applied).
- **Triggers (`embed_tsvector` function):** To automatically keep embeddings in sync for `conv_turn` and `concept` tables upon insertion.

### 2. Inner Monologue (`memory/inner_voice.py`)
- **Purpose:** To enable Manus to reflect on its own behavior after every assistant reply.
- **Functionality:**
    - `reflect(last_turn)`: Analyzes the last turn, checks for user repetition, new concept detection, and credit balance.
    - Generates markdown-formatted thoughts and stores them as 'self' role in `conv_turn`.

### 3. Self-Healing Code (`memory/self_heal.py`)
- **Purpose:** To watch FastAPI log streams and apply micro-patches automatically.
- **Functionality:**
    - `tail_and_heal()`: Monitors logs for errors/exceptions.
    - `propose_patch(logline, file)`: Rule-based patcher (expandable with LLM).
    - `apply_patch(patch, file)`: Inserts patch after last import line in the affected file.
    - `log_fix(patch)`: Logs applied fixes to `debug_log`.

### 4. Human-Like Learning Loop (`memory/learn.py`)
- **Purpose:** To extract and canonicalize concepts, and build knowledge graph edges.
- **Functionality:**
    - `learn_from_turn(turn)`:
        - Extracts and stores nouns as concepts, updating summaries on conflict.
        - Builds `related` edges between co-occurring nouns within the same sentence.
        - Summarizes conversations every N turns and stores as session concepts.

### 5. Ask Clarifying Questions (`memory/ask_back.py`)
- **Purpose:** To enable Manus to ask clarifying questions when uncertain.
- **Functionality:**
    - `should_ask_back(turn)`: Identifies situations requiring clarification (e.g., missing question mark, ambiguous pronouns) and returns a suitable question.

### 6. FastAPI Integration (`main.py` additions)
- **`/chat` endpoint:**
    - Stores user turns.
    - Calls `ask_back.should_ask_back()`.
    - If clarification is needed, replies with a question.
    - Otherwise, generates a normal RAG reply.
    - Triggers `inner_voice.reflect()` and `learn.learn_from_turn()` in the background.

### 7. Credit-Aware Scheduler (`memory/budget.py`)
- **Purpose:** To manage token expenditure and warn about high costs.
- **Functionality:**
    - `spend_with_plan(name, estimated)`: Checks remaining daily budget, warns if estimated cost exceeds a threshold, and awaits user confirmation for expensive operations.

### 8. Git as Memory Time-Machine
- **Automation:** Auto-commit `memory/db.sqlite` and human-readable SQL dumps after every session.
- **Benefit:** Allows checking out previous mental states and comparing thought processes over time.

## Roadmap of Next Self-Rewrites (Future Iterations)
- Replace MD5 hash with a local fine-tuned 192-dim model (after 10k clean rows).
- Migrate concepts to Supabase for cross-device sync.
- Add emotional state column and influence tone.
- Teach Manus to write its own commit messages.
- Enable Manus to propose personality patches for user approval.

## One-Command Bootstrap
- Simplified setup process: `cp memory/boot.sh.example memory/boot.sh`, `chmod +x memory/boot.sh`, `./memory/boot.sh`.
- This will create SQLite, apply `v2.sql`, and start the tail-healer.

## Learning Loop Summary
Every user message will:
- Be stored & embedded.
- Trigger an inner monologue.
- Update the private knowledge graph.
- Possibly spawn a self-patch commit.
Manus will occasionally ask clarifying questions and learn from user answers.


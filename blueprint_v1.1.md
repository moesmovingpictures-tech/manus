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



### New Schema Add-Ons (from `migration_v2.1.sql`)
- **`event` table:** To store typed event streams (`id`, `ts`, `who`, `what`, `meta`, `embedding vector(192)`), mirroring official Manus design for chain-of-thought and clean truncation.
- **`raci` table:** For RACI alignment guard (`agent`, `task`, `role`, `approver`), preventing value-drift as agents multiply.
- **`knowledge_api` table:** For domain knowledge APIs (`name`, `url`, `headers`, `cache_ttl`, `last_call`, `last_body`), enabling auto-calling for specialized tasks.




### Credit-Gated Self-Reflection (`memory/reflection.py`)
- **Purpose:** To enable Manus to reflect on its own behavior after every assistant reply, with a focus on credit conservation.
- **Functionality:**
    - `reflect(turn)`: Analyzes the last turn, potentially using a cheap local LLM or 3.5-turbo, and generates concise markdown bullets reflecting on understanding, new concepts, and risks/bugs. This reflection is credit-gated using `budget.spend_with_plan()`.

### RACI Gatekeeper (`memory/guard.py`)
- **Purpose:** To implement an alignment guard based on the RACI model, ensuring that actions are approved and aligned with user intent.
- **Functionality:**
    - `gate(agent, task)`: Queries the `raci` table to check for approval requirements. If an 'A' (Accountable) role is defined, it will ask for user approval before proceeding with the tool call. This check is designed to be low-cost (~40 tokens).




### Knowledge-API Auto-Injector (`memory/know.py`)
- **Purpose:** To automatically inject domain-specific knowledge by calling external APIs based on query relevance.
- **Functionality:**
    - `maybe_call_api(query_vec, top_k=1)`: Searches the `knowledge_api` table for relevant APIs based on embedding similarity. If a cached response is available and fresh, it returns it. Otherwise, it makes an HTTP request to the API, caches the response, and returns the body.

### Confidence Footer (`src/format.py`)
- **Purpose:** To provide the user with a visual indicator of Manus's confidence in its replies.
- **Functionality:**
    - `footer(last_turn_vec, history_vecs)`: Calculates a confidence score (1-5 scale) based on the cosine similarity between the last turn's vector and historical conversation vectors. This score is then represented visually with '◕' and '◔' characters and appended to every assistant reply, without incurring extra LLM tokens.




### Implementation Checklist (Credit-Safe)
- **Purpose:** Provides a step-by-step guide for implementing the new features with estimated token costs.
- **Cards:**
    - Add `v2.1.sql` tables (200 tokens)
    - Insert RACI csv (120 tokens)
    - Wire `guard.py` into router (180 tokens)
    - Add `know.py` caller (220 tokens)
    - Add `reflection.py` (190 tokens)
    - Append confidence footer (90 tokens)
- **Total Estimated Cost:** ≤ 1,000 tokens, leaving ample headroom for the next patch.

### One-Command Delta
- **Purpose:** Simplifies the application of the new features after the initial `boot.sh` setup.
- **Steps:**
    - `sqlite3 memory/db.sqlite < migration_v2.1.sql`
    - Populate `raci` table from `memory/raci.csv`.
    - Auto-commit all changes to Git with a descriptive message.

## Enhanced Learning Loop Summary
With these upgrades, every user message will now:
- Be stored & embedded.
- Trigger an inner monologue.
- Update the private knowledge graph.
- Possibly spawn a self-patch commit.
- Manus will occasionally ask clarifying questions and learn from user answers.

Additionally, Manus will now:
- Keep an event-stream identical to the official implementation.
- Ask permission before risky or expensive acts (HADA alignment).
- Pull domain APIs automatically instead of generic web-scrape.
- Show a live confidence score so you know when to doubt it.
- Still respect 300 kT/day and 4 kT/patch without exception.



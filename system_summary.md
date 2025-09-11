# Manus AI Memory Layer System Summary

## Overview
This document summarizes the architecture and functionality of the self-improving memory layer for Manus AI. The goal is to create a robust, self-hosted, and continuously evolving system that learns from user interactions and recursively refines its own prompts, roles, and chunking strategies.

## Components

### 1. Local Database (SQLite)
- **Purpose:** Primary storage for lessons learned from user interactions.
- **Implementation:** `memory/db.sqlite` managed by `sqlite3`.
- **Schema:** `CREATE TABLE lessons(id INTEGER PRIMARY KEY, txt TEXT, ts INTEGER);`

### 2. Local Connector (`memory/db.py`)
- **Purpose:** Provides an interface for adding and fetching data from the local SQLite database.
- **Functions:**
    - `add(txt)`: Persists text to SQLite.
    - `fetch(n=5)`: Retrieves the last `n` lessons.

### 3. Supabase Cloud Synchronization (Optional)
- **Purpose:** Provides an optional cloud backup and synchronization mechanism for the memory layer.
- **Implementation:** Uses Supabase REST API for data insertion and retrieval.
- **Credentials:** `SUPABASE_URL` and `SUPABASE_KEY` (anon key) are used from environment variables.
- **Note:** Requires `lessons` table to be created in Supabase with `id`, `txt`, and `ts` columns.

### 4. Self-Patch Loop (`memory/self_loop.py`)
- **Purpose:** Integrates the local database into the self-improvement process.
- **Function:** `self_patch(txt)`: Persists new information to SQLite and reloads the last 5 lessons.

### 5. Boot Script (`memory/boot.sh`)
- **Purpose:** Auto-injects the self-patch function into the system.

## Version Control
- **Tool:** Git
- **Purpose:** To track changes to system configuration, code, and documentation, enabling rollbacks and iterative improvements.
- **Managed Files:** `system_summary.md`, `memory/db.py`, `memory/self_loop.py`, `memory/boot.sh`, `logs/cost.csv`, `.env.example`, `main.py`, `requirements.txt`, `schema.sql`, `seed.sql`.

## Credit Management
- **Mechanism:** `logs/cost.csv` tracks token usage for various operations.
- **Goal:** Stay within defined token budgets (e.g., ≤ 6 kT per prompt, ≤ 300 kT/day total).

## Future Improvements (Self-Rewriting)
- The system aims to recursively rewrite its own prompts, roles, and chunking strategies to optimize performance and relevance.
- This will involve continuous evaluation and automated patching based on learned lessons and user feedback.



## Current Version: 1
This version establishes the foundational memory layer with local SQLite storage, optional Supabase cloud synchronization via REST API, and a basic self-patching mechanism. It also includes initial version control and credit management features.


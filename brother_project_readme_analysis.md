# Manus AI Smart Layer - README Analysis for Synchronization

## Project Overview

- **Goal**: Self-improving, credit-efficient personal management system using Manus AI.
- **Core Philosophy**: Persistence, recursive learning, phone-first accessibility (though user requested to de-emphasize this).
- **Credit Management**: Strict daily limit (≤300 kT/day).
- **Persistence**: Git for code, Supabase for dynamic data.

## Goals (Relevant for Synchronization)

- **Self-Improvement**: Continuous learning and adaptation.
- **Credit Efficiency**: Meticulous credit management.
- **Persistence**: All critical data, configurations, and learning trajectories persistently stored.
- **Recursive Learning**: AI reflects on performance, identifies improvements.

## Current Progress (Relevant for Synchronization)

### 1. Credit Survival Components Implemented
- **`memory/router.py`**: `call_r1()` for LLM calls, caching, `spend()` for credit management.
- **`logs/cost.csv`**: Ledger for token usage and credit history.

### 2. Git Repository Setup and Persistence
- **GitHub Integration**: `github.com/starsh00ter/manus_ai_smart_layer` for version control.
- **Auto-Push Functionality**: Automated processes to push changes.

### 3. Core Documentation Initiated
- **`README.md`**: Central point for project overview.

## Technical Context (Relevant for Synchronization)

- **LLM Provider**: DeepSeek API (`sk-54d1a6b52db44d5dab38fd5725773825`).
- **Version Control**: GitHub.
- **Database**: Supabase (URL and key configured, dedicated bucket for file storage).
- **Credit Management**: Strict daily credit limit of ≤300 kT.

## Key Files (Relevant for Synchronization)

- `/home/ubuntu/my_manus_knowledge/memory/router.py`: Manages API calls, caching, and credit expenditure.
- `/home/ubuntu/my_manus_knowledge/logs/cost.csv`: Records token usage and credit balance.
- `/home/ubuntu/my_manus_knowledge/memory/supabase_client.py`: Handles all interactions with the Supabase database.

## Next Steps (Relevant for Synchronization)

1.  **Complete and Commit `README.md`**.
2.  **Implement Supabase Integration**: Set up `pgvector` extension, create tables, implement embedding storage.
3.  **Develop Recursive Learning Layer**: Create `logs/trajectory.csv`, implement task scoring.

## Potential Synchronization Points

Based on this analysis, here are potential synchronization points between our Manus instance and your brother's:

1.  **GitHub Repository**: Both projects use GitHub for version control. We can potentially share code, blueprints, or documentation through pull requests or by monitoring each other's repositories.
2.  **Supabase Database**: Both projects leverage Supabase for persistent data storage. This is a strong candidate for sharing structured data, such as:
    -   **Learning Trajectories/Concepts**: If both systems learn similar concepts or patterns, they could share these to accelerate learning.
    -   **Cost/Budget Data**: Sharing cost data could help in collective budget management or understanding optimal spending strategies.
    -   **System Metrics/Logs**: Exchanging performance metrics or operational logs could help both systems self-diagnose and optimize.
3.  **DeepSeek API Usage**: Both rely on DeepSeek. While not a direct synchronization point, understanding each other's usage patterns or optimal prompt engineering strategies could be beneficial.
4.  **`logs/cost.csv`**: This file is explicitly mentioned in both projects as a ledger for token usage. A mechanism to share or aggregate this data could be valuable.
5.  **`memory/router.py`**: The brother's project has a `router.py` for LLM calls, caching, and credit management. Our orchestrator serves a similar purpose. Sharing insights or even components from these could lead to mutual improvements.

## Initial Thoughts on Inter-Manus Communication Feature

I propose focusing on Supabase as the primary channel for inter-Manus communication, given its explicit mention in both projects for dynamic data storage. We could define a shared schema within Supabase for exchanging specific types of information, such as:

-   **Shared Concepts/Knowledge Graph**: A table to store learned concepts and their relationships, allowing both systems to benefit from each other's knowledge acquisition.
-   **Performance/Cost Benchmarks**: A table to log and compare performance metrics and credit usage for different tasks or LLM calls.
-   **Blueprint/Idea Exchange**: A mechanism to share ideas for future improvements or blueprint updates.

For GitHub, we can continue to use it for code and documentation sharing, with a focus on clear commit messages for RAG system information. We can also explore automated ways to generate pull requests or notifications for relevant updates in each other's repositories.


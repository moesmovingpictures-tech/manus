# Git Commit Message Guidelines for Manus-Origin RAG System

To maintain a clean, tidy, and easy-to-understand Git history, especially for a self-improving RAG system like Manus-Origin, it is crucial to follow consistent and informative commit message practices. These guidelines aim to ensure that every commit provides useful context and facilitates future understanding and debugging.

## General Principles

1.  **Clarity and Conciseness**: Commit messages should be clear, concise, and to the point. They should quickly convey the purpose and scope of the changes.
2.  **Focus on RAG System**: Emphasize how the changes relate to the RAG system's functionality, performance, memory, or self-improvement capabilities.
3.  **Action-Oriented**: Start the subject line with an imperative verb (e.g., 


Add, Fix, Update, Refactor, Implement, Remove, Docs, Chore).
4.  **Separate Subject from Body**: Use a blank line to separate the subject from the body. The subject line should be 50-72 characters long.
5.  **Detailed Body**: The body should explain *what* changed and *why*. How it changed is less important unless it clarifies the *why*.
6.  **Reference Issues/Blueprints**: If a commit relates to a specific issue, blueprint item, or future idea, reference it in the body.

## Commit Message Structure

Each commit message should consist of a subject line and an optional body, separated by a blank line.

```
<type>: <subject>

<body>
```

### Subject Line (`<type>: <subject>`)

-   **`<type>`**: This is an imperative verb indicating the type of change. Use one of the following:
    -   **feat**: A new feature or capability (e.g., `feat: Implement orchestrator for request routing`)
    -   **fix**: A bug fix (e.g., `fix: Correct 'await' outside async function in budget.py`)
    -   **docs**: Documentation only changes (e.g., `docs: Update README with deployment instructions`)
    -   **style**: Changes that do not affect the meaning of the code (white-space, formatting, missing semi-colons, etc.)
    -   **refactor**: A code change that neither fixes a bug nor adds a feature (e.g., `refactor: Improve DeepSeek API call handling`)
    -   **perf**: A code change that improves performance (e.g., `perf: Optimize vector similarity calculation`)
    -   **test**: Adding missing tests or correcting existing tests (e.g., `test: Add unit tests for orchestrator routing`)
    -   **chore**: Maintenance tasks, build process changes, auxiliary tools, libraries, etc. (e.g., `chore: Update requirements.txt with aiohttp`)
    -   **ci**: Changes to our CI configuration files and scripts (e.g., `ci: Configure GitHub Actions for auto-deployment`)
    -   **build**: Changes that affect the build system or external dependencies (e.g., `build: Upgrade FastAPI version`)
    -   **revert**: Reverts a previous commit.
-   **`<subject>`**: A concise, imperative description of the change. Capitalize the first letter and do not end with a period.

### Body

-   Explain the motivation for the change, the problem it solves, and the approach taken.
-   Focus on the *why* and *what*, not necessarily the *how* (unless it clarifies the *why*).
-   Break paragraphs at around 72 characters.
-   For RAG-specific changes, explain the impact on:
    -   **Memory Management**: How does this change affect concept storage, retrieval, or learning?
    -   **Performance**: What are the expected performance implications (latency, throughput, resource usage)?
    -   **DeepSeek/LLM Usage**: How does it optimize or change the interaction with DeepSeek or other LLMs?
    -   **Self-Improvement**: How does this contribute to the system's ability to learn, reflect, or adapt?
    -   **Credit Efficiency**: What is the impact on token usage and cost?

## Examples

### Good Example

```
feat: Implement orchestrator for request routing

Introduces a new orchestrator module to manage all incoming requests.
This centralizes the decision-making process for LLM calls, ensuring
requests are routed through cache, local models, DeepSeek, or Manus
internal LLM based on predefined policies and budget constraints.

This improves credit efficiency by prioritizing cheaper options and
provides a single point for logging backend, cost, latency, and quality
for every request, which is crucial for self-improvement and monitoring.

References #BP-1.2.1
```

### Bad Example

```
Fixed bug

Changed some files to fix a bug.
```

## Adherence

All commits should strive to follow these guidelines. While minor formatting issues can be overlooked, significant deviations that hinder understanding will be addressed during code reviews or by the system's self-correction mechanisms.

This document will be regularly updated to reflect best practices and evolving project needs.


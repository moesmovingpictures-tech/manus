#!/bin/bash

# Auto-commit memory/db.sqlite and a human-readable dump after every session

# Create snapshots directory if it doesn't exist
mkdir -p memory/snapshots

# Dump SQLite database to a human-readable SQL file
sqlite3 memory/db.sqlite .dump > memory/snapshots/$(date +%F-%H-%M).sql

# Add all changes to Git
git add -A

# Commit changes with a descriptive message
git commit -m "session $(date): $(git diff --name-only | wc -l) files changed"

echo "Git memory time-machine automation complete."



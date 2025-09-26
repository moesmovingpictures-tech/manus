import asyncio
import json
import time
from datetime import datetime
import os
import subprocess
from typing import Dict, Any, Optional

from memory import db, budget

MANIFEST_FILE = "/home/ubuntu/manifest.json"

async def update_manifest():
    """Updates the manifest file with current system status."""
    manifest_data = {
        "timestamp": int(time.time()),
        "date": datetime.now().isoformat(),
        "current_credits": await db.token_balance(),
        "daily_credit_limit": budget.DAILY_CAP,
        "cache_hit_rate": await get_cache_hit_rate(), # Placeholder
        "backend_health": await get_backend_health(), # Placeholder
        "commit_hash": get_current_commit_hash(),
        "last_orchestrator_log": await get_last_orchestrator_log_summary()
    }

    with open(MANIFEST_FILE, "w") as f:
        json.dump(manifest_data, f, indent=4)
    print(f"Manifest updated: {MANIFEST_FILE}")
    return manifest_data

async def get_cache_hit_rate() -> float:
    """Placeholder for calculating cache hit rate."""
    # In a real implementation, this would query cache statistics
    return 0.0 # Assuming 0% for now

async def get_backend_health() -> str:
    """Placeholder for checking backend health."""
    # In a real implementation, this would check various service statuses
    return "healthy" # Assuming healthy for now

def get_current_commit_hash() -> str:
    """Retrieves the current Git commit hash."""
    try:
        # Ensure we are in the correct directory
        original_dir = os.getcwd()
        os.chdir("/home/ubuntu")
        commit_hash = subprocess.check_output(["git", "rev-parse", "HEAD"]).strip().decode("utf-8")
        os.chdir(original_dir)
        return commit_hash
    except Exception as e:
        print(f"Error getting commit hash: {e}")
        return "unknown"

async def get_last_orchestrator_log_summary() -> Optional[Dict[str, Any]]:
    """Retrieves a summary of the last orchestrator log entry."""
    try:
        pool = await db.get_db_pool()
        cursor = await pool.execute("""
            SELECT timestamp, user_message, deepseek_used, cost, latency, response, error
            FROM orchestrator_logs
            ORDER BY timestamp DESC
            LIMIT 1
        """
        )
        last_log = await cursor.fetchone()
        if last_log:
            return dict(last_log)
        return None
    except Exception as e:
        print(f"Error getting last orchestrator log: {e}")
        return None



import json
import os
from datetime import datetime
from typing import List, Dict, Any

LOG_FILE = "task4/query_logs.jsonl"  # JSON Lines format for easy appending

def log_query(query: str, chunks: List[Dict], response: str, sources: List[str]):
    """
    Log a query with all required fields.
    """
    timestamp = datetime.now().isoformat()
    chunks_found = len(chunks) > 0
    response_length = len(response)
    successful_response = _determine_success(response, chunks_found, sources)

    log_entry = {
        "timestamp": timestamp,
        "query": query,
        "chunks_found": chunks_found,
        "response_length": response_length,
        "successful_response": successful_response,
        "sources": sources,
        "response": response  # Optional, but useful for analysis
    }

    # Ensure directory exists
    os.makedirs(os.path.dirname(LOG_FILE), exist_ok=True)

    # Append to JSON Lines file
    with open(LOG_FILE, "a", encoding="utf-8") as f:
        f.write(json.dumps(log_entry, ensure_ascii=False) + "\n")

def _determine_success(response: str, chunks_found: bool, sources: List[str]) -> bool:
    """
    Determine if the response is successful based on:
    - Length (>50 chars)
    - Not containing "Я не знаю"
    - Has sources if chunks found
    """
    if len(response) < 50:
        return False
    if "Я не знаю" in response:
        return False
    if chunks_found and not sources:
        return False
    return True

def get_logs():
    """
    Read all logs from the file.
    """
    if not os.path.exists(LOG_FILE):
        return []
    logs = []
    with open(LOG_FILE, "r", encoding="utf-8") as f:
        for line in f:
            logs.append(json.loads(line.strip()))
    return logs

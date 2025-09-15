import requests
import os

CLICKUP_API_KEY = os.getenv("CLICKUP_API_KEY")
CLICKUP_TASK_ID = os.getenv("CLICKUP_TASK_ID")

def update_clickup_task(status: str, comment: str = None):
    if not CLICKUP_API_KEY or not CLICKUP_TASK_ID:
        print("ClickUp API key or Task ID not set. Skipping update.")
        return

    headers = {
        "Authorization": CLICKUP_API_KEY,
        "Content-Type": "application/json"
    }
    
    data = {"status": status}
    if comment:
        data["comment_text"] = comment

    url = f"https://api.clickup.com/api/v2/tasks/{CLICKUP_TASK_ID}"
    
    try:
        response = requests.put(url, headers=headers, json=data)
        response.raise_for_status()
        print(f"ClickUp task {CLICKUP_TASK_ID} updated to status: {status}")
        if comment:
            print(f"Comment added: {comment}")
    except requests.exceptions.RequestException as e:
        print(f"Error updating ClickUp task: {e}")




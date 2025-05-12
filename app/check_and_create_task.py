import os
import json
import requests
from datetime import datetime, timedelta
import calendar

API_URL = os.environ.get("TASK_API_URL")
SCHEDULE_FILE = os.environ.get("TASK_SCHEDULE_FILE", "/app/schedule.json")

def should_create_today(day):
    today = datetime.today()
    if isinstance(day, int):
        if day > 0:
            return today.day == day
        else:
            last_day = calendar.monthrange(today.year, today.month)[1]
            return today.day == (last_day + day + 1)
    return False

def main():
    with open(SCHEDULE_FILE, 'r') as f:
        tasks = json.load(f)

    today = datetime.today()

    for task in tasks:
        if should_create_today(task["day"]):
            due_date = today + timedelta(days=task.get("due_days", 0))
            data = {
                "title": task["title"],
                "notes": task.get("notes", ""),
                "due_date": due_date.strftime("%Y-%m-%d")
            }
            print(f"Creating task: {data}")
            try:
                response = requests.post(f"{API_URL}/create-task", json=data)
                print(f"Response: {response.status_code} - {response.text}")
            except Exception as e:
                print(f"Failed to call API: {e}")

if __name__ == "__main__":
    main()


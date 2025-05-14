import os
import datetime
import requests
from pymongo import MongoClient

# Load MongoDB connection info from environment
MONGO_HOST = os.getenv("MONGO_HOST", "localhost")
MONGO_PORT = os.getenv("MONGO_PORT", "27017")
MONGO_USER = os.getenv("MONGO_USER", "mongoadmin")
MONGO_PASS = os.getenv("MONGO_PASS", "secret")
MONGO_DB   = os.getenv("MONGO_DB", "task_db")

# Build MongoDB URI with auth
MONGO_URI = f"mongodb://{MONGO_USER}:{MONGO_PASS}@{MONGO_HOST}:{MONGO_PORT}/{MONGO_DB}?authSource=admin"
client = MongoClient(MONGO_URI)
db = client[MONGO_DB]
collection = db["task"]

# Google Task API endpoint
TASK_API_URL = os.getenv("TASK_API_URL", "http://task-api:5000/create-task")

def should_create_today(schedule_day):
    today = datetime.date.today()
    if schedule_day.startswith("-"):
        # Handle negative day from end of month
        days_before_end = int(schedule_day)
        last_day = (today.replace(day=28) + datetime.timedelta(days=4)).replace(day=1) - datetime.timedelta(days=1)
        return today == (last_day + datetime.timedelta(days=days_before_end + 1))
    else:
        return today.day == int(schedule_day)

def main():
    today = datetime.date.today()
    for task in collection.find():
        schedule_day = str(task.get("schedule_day"))
        if should_create_today(schedule_day):
            task_name = task.get("task_name")
            notes = task.get("notes")
            due_in_days = int(task.get("due_days", 0))
            due_date = today + datetime.timedelta(days=due_in_days)

            payload = {
                "title": task_name,
                "notes": notes,
                "due_date": due_date.isoformat()
            }

            try:
                response = requests.post(TASK_API_URL, json=payload)
                print(f"Created task: {task_name} – Status: {response.status_code}")
            except Exception as e:
                print(f"Error creating task '{task_name}': {e}")

if __name__ == "__main__":
    main()

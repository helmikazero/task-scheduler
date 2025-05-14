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
tasks_collection = db["tasks"]  # Consistent collection name

# Use your backend API instead of Google Task API
TASK_API_URL = os.getenv("TASK_API_URL", "http://localhost:5001/api/tasks")

def should_create_today(create_day):
    today = datetime.date.today()
    if create_day == -1:  # Handle last day of month
        last_day = (today.replace(day=28) + datetime.timedelta(days=4)).replace(day=1) - datetime.timedelta(days=1)
        return today.day == last_day.day
    else:
        return today.day == create_day

def main():
    today = datetime.date.today()
    for task in tasks_collection.find():
        create_day = task.get("create_day")
        if should_create_today(create_day):
            title = task.get("title")
            notes = task.get("notes", "")
            due_days = int(task.get("due_days", 0))
            due_date = today + datetime.timedelta(days=due_days)

            payload = {
                "title": title,  # Add prefix to distinguish
                "notes": notes,
                "due_date": due_date.isoformat()
            }

            try:
                response = requests.post(TASK_API_URL, json=payload)
                print(f"Created task: {title} – Status: {response.status_code}")
            except Exception as e:
                print(f"Error creating task '{title}': {e}")

if __name__ == "__main__":
    main()

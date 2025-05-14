# task_scheduler.py
# ------------------
# This script is the daily cron job inside the task-scheduler container.
# It checks MongoDB to see if a task needs to be created today and sends a request to task-api if so.

import os
import requests
from datetime import datetime, timedelta
from pymongo import MongoClient

MONGO_URI = os.getenv("MONGO_URI", "mongodb://mongodb:27017/")
TASK_API_URL = os.getenv("TASK_API_URL", "http://task-api:5000/create-task")
DB_NAME = "taskdb"
COLLECTION_NAME = "schedules"

client = MongoClient(MONGO_URI)
db = client[DB_NAME]
collection = db[COLLECTION_NAME]

today = datetime.now()
today_day = today.day
end_of_month = (today.replace(day=28) + timedelta(days=4)).replace(day=1) - timedelta(days=1)
days_in_month = end_of_month.day

schedules = collection.find()

for task in schedules:
    create_day = task.get("create_day")

    if create_day < 0:
        # handle "-X" case: days from the end of month
        scheduled_day = days_in_month + create_day + 1
    else:
        scheduled_day = create_day

    if today_day == scheduled_day:
        due_date = today + timedelta(days=task.get("due_days", 0))

        payload = {
            "task_name": task["task_name"],
            "notes": task.get("notes", ""),
            "due_date": due_date.strftime("%Y-%m-%d")
        }

        try:
            res = requests.post(TASK_API_URL, json=payload)
            print(f"Task created: {payload['task_name']} - Status: {res.status_code}")
        except Exception as e:
            print(f"Failed to create task: {e}")

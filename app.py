import json
from datetime import date

# The Task Blueprint
class Task:
    def __init__(self, title, is_done=False, task_date=None, priority=2):
        self.title = title
        self.is_done = is_done
        self.task_date = task_date or str(date.today())
        self.priority = priority

    def to_dict(self):
        return {"title": self.title, "is_done": self.is_done, "date": self.task_date, "priority": self.priority}

# Initial storage setup
def save_tasks(tasks):
    with open('tasks.json', 'w') as f:
        json.dump([t.to_dict() if isinstance(t, Task) else t for t in tasks], f, indent=4)

print("FocusFlow Engine Initialized.")


def sync_and_rollover():
    try:
        with open('tasks.json', 'r') as f:
            tasks = json.load(f)
    except FileNotFoundError:
        tasks = []

    today = str(date.today())
    for t in tasks:
        if not t['is_done'] and t['date'] < today:
            t['date'] = today
            t['title'] += " (Rolled Over)"

    save_tasks(tasks)
    return tasks
import time
import sys

def start_timer(minutes=25):
    seconds = minutes * 60
    while seconds > 0:
        mins, secs = divmod(seconds, 60)
        sys.stdout.write(f"\rFocus Mode: {mins:02d}:{secs:02d} remaining...")
        sys.stdout.flush()
        time.sleep(1)
        seconds -= 1
    print("\n✅ Session complete!")
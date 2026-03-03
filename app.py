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
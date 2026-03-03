import json
import time
import sys
from datetime import date


# --- CORE LOGIC ---
class Task:
    def __init__(self, title, is_done=False, task_date=None, priority=2):
        self.title = title
        self.is_done = is_done
        self.task_date = task_date or str(date.today())
        self.priority = priority

    def to_dict(self):
        return {"title": self.title, "is_done": self.is_done, "date": self.task_date, "priority": self.priority}


def save_tasks(tasks):
    with open('tasks.json', 'w') as f:
        json.dump(tasks, f, indent=4)


def load_tasks():
    try:
        with open('tasks.json', 'r') as f:
            return json.load(f)
    except (FileNotFoundError, json.JSONDecodeError):
        return []


def sync_and_rollover():
    tasks = load_tasks()
    today = str(date.today())
    changed = False
    for t in tasks:
        if not t['is_done'] and t['date'] < today:
            t['date'] = today
            if "(Rolled Over)" not in t['title']:
                t['title'] += " (Rolled Over)"
            changed = True
    if changed:
        save_tasks(tasks)
    return tasks


# --- FEATURES ---
def start_pomodoro(minutes=25):
    seconds = minutes * 60
    print(f"\n🔥 Focus session started for {minutes} minutes!")
    try:
        while seconds > 0:
            mins, secs = divmod(seconds, 60)
            sys.stdout.write(f"\rTime Remaining: {mins:02d}:{secs:02d} | Stay Focused!")
            sys.stdout.flush()
            time.sleep(1)
            seconds -= 1
        print("\n✅ Session complete! Take a break.")
    except KeyboardInterrupt:
        print("\n⚠️ Timer stopped.")


# --- MAIN MENU ---
def main():
    print("--- FocusFlow: Offline Timetable ---")
    tasks = sync_and_rollover()

    while True:
        print(f"\n📅 Today: {date.today()}")
        # Sort by priority (3 High, 1 Low)
        current_tasks = sorted([t for t in tasks if t['date'] == str(date.today())],
                               key=lambda x: x['priority'], reverse=True)

        for i, t in enumerate(current_tasks, 1):
            status = "[X]" if t['is_done'] else "[ ]"
            p_label = "!!!" if t['priority'] == 3 else "!! " if t['priority'] == 2 else "!  "
            print(f"{i}. {p_label} {status} {t['title']}")

        cmd = input("\nCommands: [add 'task'] [done 'id'] [focus] [exit]: ").strip().lower()

        if cmd.startswith("add "):
            title = cmd[4:]
            new_task = Task(title=title)
            tasks.append(new_task.to_dict())
            save_tasks(tasks)
        elif cmd.startswith("done "):
            try:
                idx = int(cmd[5:]) - 1
                current_tasks[idx]['is_done'] = True
                save_tasks(tasks)
            except (IndexError, ValueError):
                print("Invalid ID.")
        elif cmd == "focus":
            start_pomodoro()
        elif cmd == "exit":
            break

def test_task_creation():
    """Test if a task is created with the correct default values."""
    title = "Test Study Session"
    task = Task(title=title)
    
    assert task.title == title
    assert task.is_done is False
    assert task.task_date == str(date.today())
    assert task.priority == 2

def test_task_to_dict():
    """Test if the to_dict method returns the correct dictionary format."""
    task = Task(title="Complete Assignment", priority=3)
    data = task.to_dict()
    
    assert data["title"] == "Complete Assignment"
    assert data["priority"] == 3
    assert "date" in data
if __name__ == "__main__":
    main()

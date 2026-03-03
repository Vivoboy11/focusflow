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
    """Moves unfinished tasks from yesterday to today automatically."""
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


# --- UPDATED FEATURES ---
def start_pomodoro(minutes=25):
    """Counts down for a focus session. Now accepts custom minutes."""
    try:
        seconds = int(minutes) * 60
        print(f"\n🔥 Focus session started for {minutes} minutes!")
        while seconds > 0:
            m, s = divmod(seconds, 60)
            sys.stdout.write(f"\rTime Remaining: {m:02d}:{s:02d} | Stay Focused!")
            sys.stdout.flush()
            time.sleep(1)
            seconds -= 1
        print("\n✅ Session complete! Take a break.")
    except (KeyboardInterrupt, ValueError):
        print("\n⚠️ Timer stopped or invalid duration.")


# --- MAIN MENU ---
def main():
    print("--- FocusFlow: Offline Timetable ---")
    tasks = sync_and_rollover()

    while True:
        print(f"\n📅 Today: {date.today()}")
        # Sorting: Priority 3 (High) comes first
        current_tasks = sorted([t for t in tasks if t['date'] == str(date.today())],
                               key=lambda x: x['priority'], reverse=True)

        for i, t in enumerate(current_tasks, 1):
            status = "[X]" if t['is_done'] else "[ ]"
            p_label = "!!!" if t['priority'] == 3 else "!! " if t['priority'] == 2 else "!  "
            print(f"{i}. {p_label} {status} {t['title']}")

        print("\nCommands: [add 'task' --p 3] [done 'id'] [del 'id'] [focus 'min'] [exit]")
        cmd = input("Choice: ").strip().lower()

        # Feature: Add with optional Priority Flag
        if cmd.startswith("add "):
            raw_input = cmd[4:]
            priority = 2
            if " --p " in raw_input:
                title, p_val = raw_input.split(" --p ")
                try:
                    priority = int(p_val)
                except ValueError:
                    print("Invalid priority. Using 2.")
            else:
                title = raw_input

            new_task = Task(title=title, priority=priority)
            tasks.append(new_task.to_dict())
            save_tasks(tasks)

        # Feature: Mark Done
        elif cmd.startswith("done "):
            try:
                idx = int(cmd[5:]) - 1
                target = current_tasks[idx]
                for t in tasks:
                    if t['title'] == target['title'] and t['date'] == target['date']:
                        t['is_done'] = True
                save_tasks(tasks)
            except (IndexError, ValueError):
                print("Invalid ID.")

        # Feature: Delete Task
        elif cmd.startswith("del "):
            try:
                idx = int(cmd[4:]) - 1
                target = current_tasks[idx]
                tasks = [t for t in tasks if not (t['title'] == target['title'] and t['date'] == target['date'])]
                save_tasks(tasks)
                print("🗑️ Task deleted.")
            except (IndexError, ValueError):
                print("Invalid ID.")

        # Feature: Custom Timer
        elif cmd.startswith("focus"):
            parts = cmd.split()
            mins = parts[1] if len(parts) > 1 else 25
            start_pomodoro(mins)

        elif cmd == "exit":
            break


if __name__ == "__main__":
    main()
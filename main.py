import flet as ft
import time
import threading
from app import load_tasks, save_tasks, Task


def main(page: ft.Page):
    page.title = "FocusFlow Mobile"
    page.theme_mode = ft.ThemeMode.DARK
    page.padding = 20

    # --- UI COMPONENTS ---
    tasks_view = ft.Column()
    timer_text = ft.Text("25:00", size=40, weight="bold")
    new_task_input = ft.TextField(hint_text="New task...", expand=True)

    def get_stats():
        tasks = load_tasks()
        completed = len([t for t in tasks if t.get('is_done')])
        total = len(tasks)
        return f"Completed: {completed} / Total: {total}"

    stats_text = ft.Text(get_stats(), size=20, italic=True)

    def delete_task(task_row, task_title):
        tasks_view.controls.remove(task_row)
        current_data = load_tasks()
        save_tasks([t for t in current_data if t['title'] != task_title])
        stats_text.value = get_stats()
        page.update()

    def add_task_ui(task_title, is_done=False):
        task_row = ft.Row(alignment=ft.MainAxisAlignment.SPACE_BETWEEN)
        cb = ft.Checkbox(label=task_title, value=is_done, expand=True)

        delete_button = ft.TextButton(
            "Delete",
            style=ft.ButtonStyle(color="red"),
            on_click=lambda _: delete_task(task_row, task_title)
        )

        task_row.controls = [cb, delete_button]
        tasks_view.controls.append(task_row)
        page.update()

    def handle_add(e):
        if new_task_input.value:
            add_task_ui(new_task_input.value)
            tasks = load_tasks()
            tasks.append(Task(new_task_input.value).to_dict())
            save_tasks(tasks)
            new_task_input.value = ""
            stats_text.value = get_stats()
            page.update()

    # --- THE MULTITHREADING FIX ---
    def start_timer(e):
        def run_countdown():
            seconds = 25 * 60
            while seconds > 0:
                mins, secs = divmod(seconds, 60)
                timer_text.value = f"{mins:02d}:{secs:02d}"
                timer_text.update()  # Update just the text
                time.sleep(1)
                seconds -= 1
            timer_text.value = "Done!"
            timer_text.update()

        # This launches the countdown in the background so the UI doesn't freeze
        threading.Thread(target=run_countdown, daemon=True).start()

    # --- INITIAL LOAD ---
    for t in load_tasks():
        add_task_ui(t['title'], t.get('is_done', False))

    # --- TAB CONTENT SCREENS ---
    tasks_content = ft.Column([
        ft.Row([new_task_input, ft.ElevatedButton("Add", on_click=handle_add)]),
        ft.Divider(),
        stats_text,
        tasks_view
    ])

    focus_content = ft.Column(
        controls=[
            ft.Container(height=50),
            timer_text,
            ft.ElevatedButton("Start Focus", on_click=start_timer)
        ],
        horizontal_alignment=ft.CrossAxisAlignment.CENTER
    )

    # --- TABS ARCHITECTURE ---
    tabs = ft.Tabs(
        selected_index=0,
        length=2,
        expand=True,
        content=ft.Column(
            expand=True,
            controls=[
                ft.TabBar(
                    tabs=[
                        ft.Tab(label="TASKS"),
                        ft.Tab(label="FOCUS")
                    ]
                ),
                ft.TabBarView(
                    expand=True,
                    controls=[
                        tasks_content,
                        focus_content
                    ]
                )
            ]
        )
    )

    page.add(
        ft.Text("FocusFlow", size=32, weight="bold", color="blue"),
        tabs
    )


if __name__ == "__main__":
    ft.run(main)


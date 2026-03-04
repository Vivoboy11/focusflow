import flet as ft
import time
import asyncio
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

    # ADDED BACK: The function that actually saves the checkbox state
    def toggle_task_status(e, task_title):
        current_data = load_tasks()
        for t in current_data:
            if t['title'] == task_title:
                t['is_done'] = e.control.value
        save_tasks(current_data)
        stats_text.value = get_stats()
        page.update()

    def add_task_ui(task_title, is_done=False):
        task_row = ft.Row(alignment=ft.MainAxisAlignment.SPACE_BETWEEN)

        # ADDED BACK: The on_change event linking the checkbox to the function above
        cb = ft.Checkbox(
            label=task_title,
            value=is_done,
            expand=True,
            on_change=lambda e: toggle_task_status(e, task_title)
        )

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

    # --- THE ADVANCED ANDROID TIMER LOGIC ---
    timer_state = {
        "is_running": False,
        "time_left": 25 * 60
    }

    def start_timer(e):
        if timer_state["is_running"] or timer_state["time_left"] <= 0:
            return

        timer_state["is_running"] = True

        async def run_countdown():
            end_time = time.time() + timer_state["time_left"]

            while timer_state["is_running"]:
                seconds_left = int(end_time - time.time())

                if seconds_left <= 0:
                    timer_state["time_left"] = 0
                    timer_state["is_running"] = False
                    timer_text.value = "Done!"
                    page.update()
                    break

                timer_state["time_left"] = seconds_left

                mins, secs = divmod(seconds_left, 60)
                timer_text.value = f"{mins:02d}:{secs:02d}"
                page.update()

                await asyncio.sleep(0.5)

        page.run_task(run_countdown)

    def pause_timer(e):
        timer_state["is_running"] = False
        page.update()

    def reset_timer(e):
        timer_state["is_running"] = False
        timer_state["time_left"] = 60 * 60
        timer_text.value = "60:00"
        page.update()

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

    timer_controls = ft.Row(
        controls=[
            ft.ElevatedButton("Start", on_click=start_timer, color="green"),
            ft.ElevatedButton("Pause", on_click=pause_timer, color="orange"),
            ft.ElevatedButton("Reset", on_click=reset_timer, color="red"),
        ],
        alignment=ft.MainAxisAlignment.CENTER
    )

    focus_content = ft.Column(
        controls=[
            ft.Container(height=50),
            timer_text,
            timer_controls
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
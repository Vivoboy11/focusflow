import flet as ft
import time
from app import load_tasks, save_tasks, Task


def main(page: ft.Page):
    page.title = "FocusFlow Mobile"
    page.theme_mode = ft.ThemeMode.DARK
    page.padding = 20
    page.scroll = ft.ScrollMode.ADAPTIVE

    # UI Components
    tasks_view = ft.Column()
    timer_text = ft.Text("25:00", size=40, weight="bold", color="blue")

    def delete_task(task_row, task_obj):
        tasks_view.controls.remove(task_row)
        # Remove from backend
        current_data = load_tasks()
        updated_data = [t for t in current_data if t['title'] != task_obj['title']]
        save_tasks(updated_data)
        page.update()

    def add_task_ui(task_title, is_done=False):
        task_obj = {"title": task_title, "is_done": is_done}

        task_row = ft.Row(alignment=ft.MainAxisAlignment.SPACE_BETWEEN)
        cb = ft.Checkbox(label=task_title, value=is_done, expand=True)
        btn = ft.IconButton(icon="delete_outline", icon_color="red",
                            on_click=lambda _: delete_task(task_row, task_obj))

        task_row.controls = [cb, btn]
        tasks_view.controls.append(task_row)
        page.update()

    def handle_add(e):
        if new_task_input.value:
            add_task_ui(new_task_input.value)
            # Save to backend
            all_tasks = load_tasks()
            all_tasks.append(Task(new_task_input.value).to_dict())
            save_tasks(all_tasks)
            new_task_input.value = ""
            page.update()

    def start_timer(e):
        seconds = 25 * 60
        while seconds > 0:
            mins, secs = divmod(seconds, 60)
            timer_text.value = f"{mins:02d}:{secs:02d}"
            page.update()
            time.sleep(1)
            seconds -= 1
        timer_text.value = "Done!"
        page.update()

    # Load Existing Data on Start
    for t in load_tasks():
        add_task_ui(t['title'], t['is_done'])

    new_task_input = ft.TextField(hint_text="New task...", expand=True)

    page.add(
        ft.Text("FocusFlow", size=32, weight="bold", color="blue"),
        ft.Divider(),
        ft.Row([timer_text, ft.ElevatedButton("Start Focus", on_click=start_timer)]),
        ft.Row([new_task_input, ft.ElevatedButton("Add", on_click=handle_add)]),
        ft.Divider(),
        tasks_view
    )


if __name__ == "__main__":
    ft.app(target=main)
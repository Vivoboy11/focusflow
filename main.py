import flet as ft

def main(page: ft.Page):
    page.title = "FocusFlow Mobile"
    page.theme_mode = ft.ThemeMode.DARK
    page.padding = 20

    def add_clicked(e):
        if not new_task.value:
            new_task.error_text = "Please enter a task"
            page.update()
        else:
            new_task.error_text = None
            tasks_view.controls.append(ft.Checkbox(label=new_task.value))
            new_task.value = ""
            page.update()

    new_task = ft.TextField(hint_text="What needs to be done?", expand=True)
    tasks_view = ft.Column()

    page.add(
        ft.Row(
            [ft.Text("FocusFlow", size=32, weight="bold", color=ft.Colors.BLUE_500)],
            alignment=ft.MainAxisAlignment.CENTER
        ),
        ft.Row(
            controls=[
                new_task,
                # Using the string name "add" is the safest way to avoid the "nothing to display" error
                ft.FloatingActionButton(icon="add", on_click=add_clicked),
            ],
        ),
        ft.Divider(),
        tasks_view,
    )

if __name__ == "__main__":
    ft.app(target=main)






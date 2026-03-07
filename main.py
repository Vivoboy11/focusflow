import flet as ft
import time
import asyncio
import json
from datetime import datetime
import google.generativeai as genai
from app import load_tasks, save_tasks, Task

# --- AI CONFIGURATION ---
# Replace with your actual Gemini API Key
API_KEY = "AIzaSyCu0S_xarP7-qe4JbMVxqWzrOd_BdEbDuU"
genai.configure(api_key=API_KEY)
model = genai.GenerativeModel('gemini-2.5-flash')

# --- MODERN COLOR PALETTE ---
BG_COLOR = "#09090b"
CARD_BG = "#18181b"
ACCENT_PURPLE = "#8b5cf6"
ACCENT_BLUE = "#3b82f6"
TEXT_MAIN = "#f4f4f5"
TEXT_MUTED = "#a1a1aa"


def main(page: ft.Page):
    # --- PAGE STYLING ---
    page.title = "FocusFlow AI"
    page.bgcolor = BG_COLOR
    page.padding = 0
    page.theme_mode = ft.ThemeMode.LIGHT

    # --- CUSTOM FLOATING APP BAR ---
    header = ft.Container(
        content=ft.Row([
            ft.Icon(ft.Icons.AUTO_AWESOME_MOSAIC_ROUNDED, color=ACCENT_BLUE, size=30),
            ft.Text("FocusFlow", weight="bold", size=28, color=TEXT_MAIN),
        ], alignment=ft.MainAxisAlignment.CENTER),
        padding=ft.padding.only(top=40, bottom=20),
        bgcolor="#CC09090b",
    )

    # --- UI COMPONENTS ---
    tasks_view = ft.Column(spacing=15)

    # ⚡ BULLETPROOF GLOWING TIMER ⚡
    timer_text = ft.Text("25:00", size=65, weight="bold", color=TEXT_MAIN)
    timer_display = ft.Container(
        content=ft.Stack([
            ft.Container(content=timer_text, alignment=ft.Alignment(0, 0))
        ]),
        width=280,
        height=280,
        shape=ft.BoxShape.CIRCLE,
        bgcolor="#0f172a",
        border=ft.border.all(2, ACCENT_BLUE),
        shadow=ft.BoxShadow(spread_radius=5, blur_radius=40, color="#663b82f6"),
        animate=500
    )

    # Timer Setting Input
    timer_input = ft.TextField(
        value="25",
        label="Mins",
        width=80,
        border_radius=15,
        border_color=ACCENT_BLUE,
        text_align=ft.TextAlign.CENTER,
        keyboard_type=ft.KeyboardType.NUMBER,
        text_style=ft.TextStyle(color=TEXT_MAIN),
    )

    new_task_input = ft.TextField(
        hint_text="Add a manual task...",
        expand=True,
        border_radius=30,
        border_color=TEXT_MUTED,
        content_padding=20,
        text_style=ft.TextStyle(color=TEXT_MAIN)
    )

    ai_input = ft.TextField(
        hint_text="Ask AI to plan your session...",
        expand=True,
        multiline=True,
        min_lines=1,
        max_lines=3,
        border_width=0,
        bgcolor="#00000000",
        text_style=ft.TextStyle(color=TEXT_MAIN)
    )
    ai_loading = ft.ProgressRing(visible=False, width=20, height=20, color=ACCENT_PURPLE)

    def get_stats():
        tasks = load_tasks()
        completed = len([t for t in tasks if t.get('is_done')])
        total = len(tasks)
        return f"{completed}/{total} Tasks Completed"

    stats_text = ft.Text(get_stats(), size=13, color=ACCENT_BLUE, weight="bold")

    def delete_task(task_container, task_title):
        tasks_view.controls.remove(task_container)
        current_data = load_tasks()
        save_tasks([t for t in current_data if t['title'] != task_title])
        stats_text.value = get_stats()
        page.update()

    def toggle_task_status(e, task_title, label_text):
        current_data = load_tasks()
        for t in current_data:
            if t['title'] == task_title:
                t['is_done'] = e.control.value
        save_tasks(current_data)

        label_text.style = ft.TextStyle(
            color=TEXT_MUTED if e.control.value else TEXT_MAIN,
            decoration=ft.TextDecoration.LINE_THROUGH if e.control.value else ft.TextDecoration.NONE
        )

        stats_text.value = get_stats()
        page.update()

    def clear_completed(e):
        current_data = load_tasks()
        incomplete_tasks = [t for t in current_data if not t.get('is_done')]
        save_tasks(incomplete_tasks)
        tasks_view.controls.clear()
        for t in incomplete_tasks:
            add_task_ui(t['title'], t.get('is_done', False), t.get('date', ''))
        stats_text.value = get_stats()
        page.update()

    def add_task_ui(task_title, is_done=False, task_date=""):
        label_text = ft.Text(
            task_title,
            expand=True,
            size=15,
            style=ft.TextStyle(
                color=TEXT_MUTED if is_done else TEXT_MAIN,
                decoration=ft.TextDecoration.LINE_THROUGH if is_done else ft.TextDecoration.NONE
            )
        )

        cb = ft.Checkbox(
            value=is_done,
            fill_color=ACCENT_BLUE,
            on_change=lambda e: toggle_task_status(e, task_title, label_text)
        )

        delete_button = ft.IconButton(
            icon=ft.Icons.CLOSE_ROUNDED,
            icon_color=TEXT_MUTED,
            on_click=lambda _: delete_task(task_container, task_title)
        )

        task_container = ft.Container(
            content=ft.Row([cb, label_text, delete_button]),
            bgcolor=CARD_BG,
            padding=10,
            border_radius=15,
            border=ft.border.all(1, "#19f4f4f5"),
            animate=300
        )

        tasks_view.controls.append(task_container)
        page.update()

    def handle_add_manual(e):
        if new_task_input.value:
            _save_and_display_task(new_task_input.value)
            new_task_input.value = ""
            stats_text.value = get_stats()
            page.update()

    def _save_and_display_task(title_string):
        current_date = datetime.now().strftime("%b %d")
        add_task_ui(title_string, False, current_date)
        tasks = load_tasks()
        new_task_dict = Task(title_string).to_dict()
        new_task_dict["date"] = current_date
        tasks.append(new_task_dict)
        save_tasks(tasks)

    def handle_ai_generation(e):
        if not ai_input.value: return
        ai_loading.visible = True
        page.update()
        prompt = f"Break this into a Pomodoro schedule JSON array: {ai_input.value}. Format: [{{'task': 'name', 'duration_minutes': 25}}]"
        try:
            response = model.generate_content(prompt)
            clean_text = response.text.strip()
            if "```json" in clean_text:
                clean_text = clean_text.split("```json")[1].split("```")[0]
            elif "```" in clean_text:
                clean_text = clean_text.split("```")[1].split("```")[0]

            schedule = json.loads(clean_text)
            for item in schedule:
                _save_and_display_task(f"{item['duration_minutes']}m • {item['task']}")
            ai_input.value = ""
        except:
            pass
        ai_loading.visible = False
        stats_text.value = get_stats()
        page.update()

    # Timer Logic State
    timer_state = {
        "is_running": False,
        "time_left": 25 * 60,
        "allocated_time": 25 * 60
    }

    def set_timer_duration(e):
        try:
            mins = int(timer_input.value)
            if mins <= 0: mins = 25
        except:
            mins = 25

        timer_state["is_running"] = False
        timer_state["allocated_time"] = mins * 60
        timer_state["time_left"] = mins * 60
        timer_text.value = f"{mins:02d}:00"
        timer_display.shadow.color = "#663b82f6"
        page.update()

    def start_timer(e):
        if timer_state["is_running"]: return
        timer_state["is_running"] = True
        timer_display.shadow.color = "#ef4444"
        page.update()

        async def run():
            while timer_state["is_running"] and timer_state["time_left"] > 0:
                timer_state["time_left"] -= 1
                mins, secs = divmod(timer_state["time_left"], 60)
                timer_text.value = f"{mins:02d}:{secs:02d}"
                page.update()
                await asyncio.sleep(1)
            if timer_state["time_left"] <= 0:
                timer_text.value = "DONE"
            timer_state["is_running"] = False

        page.run_task(run)

    def pause_timer(e):
        timer_state["is_running"] = False
        timer_display.shadow.color = "#663b82f6"
        page.update()

    def reset_timer(e):
        timer_state["is_running"] = False
        timer_state["time_left"] = timer_state["allocated_time"]
        mins, secs = divmod(timer_state["time_left"], 60)
        timer_text.value = f"{mins:02d}:{secs:02d}"
        timer_display.shadow.color = "#663b82f6"
        page.update()

    # Initial Load
    for t in load_tasks(): add_task_ui(t['title'], t.get('is_done', False), t.get('date', ''))

    ai_container = ft.Container(
        content=ft.Row([
            ft.Icon(ft.Icons.AUTO_AWESOME, color=ACCENT_PURPLE),
            ai_input, ai_loading,
            ft.IconButton(icon=ft.Icons.SEND_ROUNDED, icon_color=ACCENT_PURPLE, on_click=handle_ai_generation)
        ]),
        padding=10, bgcolor=CARD_BG, border_radius=30, border=ft.border.all(1, "#4C8b5cf6")
    )

    tasks_content = ft.Container(
        content=ft.Column([
            ai_container, ft.Container(height=10),
            ft.Row([new_task_input,
                    ft.FloatingActionButton(icon=ft.Icons.ADD, on_click=handle_add_manual, bgcolor=ACCENT_BLUE,
                                            mini=True, foreground_color=TEXT_MAIN)]),
            ft.Row(
                [stats_text, ft.TextButton("Clean", on_click=clear_completed, style=ft.ButtonStyle(color=TEXT_MUTED))],
                alignment=ft.MainAxisAlignment.SPACE_BETWEEN),
            tasks_view
        ], scroll=ft.ScrollMode.AUTO),
        padding=20, expand=True
    )

    focus_content = ft.Container(
        content=ft.Column([
            ft.Container(height=40),
            timer_display,
            ft.Container(height=40),
            ft.Row([
                ft.IconButton(icon=ft.Icons.REPLAY_ROUNDED, on_click=reset_timer, icon_size=30),
                ft.FloatingActionButton(icon=ft.Icons.PLAY_ARROW_ROUNDED, on_click=start_timer, bgcolor=TEXT_MAIN,
                                        foreground_color=BG_COLOR, width=65, height=65),
                ft.IconButton(icon=ft.Icons.PAUSE_ROUNDED, on_click=pause_timer, icon_size=30),
            ], alignment=ft.MainAxisAlignment.CENTER),
            ft.Container(height=40),
            ft.Container(
                content=ft.Row([
                    timer_input,
                    ft.ElevatedButton("Set Timer", on_click=set_timer_duration, bgcolor=ACCENT_BLUE, color=TEXT_MAIN)
                ], alignment=ft.MainAxisAlignment.CENTER),
                padding=20,
                bgcolor=CARD_BG,
                border_radius=20,
                border=ft.border.all(1, "#19f4f4f5")
            )
        ], horizontal_alignment=ft.CrossAxisAlignment.CENTER),
        expand=True
    )

    content_area = ft.Container(content=tasks_content, expand=True)

    def nav_change(e):
        content_area.content = tasks_content if e.control.selected_index == 0 else focus_content
        page.update()

    page.add(header, content_area, ft.NavigationBar(
        selected_index=0, bgcolor=CARD_BG, on_change=nav_change,
        destinations=[
            ft.NavigationBarDestination(icon=ft.Icons.LIST, label="Tasks"),
            ft.NavigationBarDestination(icon=ft.Icons.TIMER, label="Focus")
        ]
    ))


if __name__ == "__main__":
    ft.run(main)
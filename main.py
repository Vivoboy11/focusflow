import flet as ft
import asyncio
import requests

API_URL = "http://127.0.0.1:8000"

BG_COLOR      = "#09090b"
CARD_BG       = "#18181b"
ACCENT_PURPLE = "#8b5cf6"
ACCENT_BLUE   = "#3b82f6"
TEXT_MAIN     = "#f4f4f5"
TEXT_MUTED    = "#a1a1aa"


def main(page: ft.Page):
    page.title        = "FocusFlow AI"
    page.bgcolor      = BG_COLOR
    page.padding      = 0
    page.theme_mode   = ft.ThemeMode.DARK
    page.window.width  = 420
    page.window.height = 800

    # --- HEADER ---
    header = ft.Container(
        content=ft.Row([
            ft.Icon(ft.Icons.AUTO_AWESOME, color=ACCENT_BLUE, size=30),
            ft.Text("FocusFlow", weight=ft.FontWeight.BOLD, size=28, color=TEXT_MAIN),
        ], alignment=ft.MainAxisAlignment.CENTER),
        padding=ft.Padding(0, 40, 0, 20),   # ✅ Padding.only replacement
    )

    # --- TASK LIST ---
    tasks_view = ft.Column(spacing=15, scroll=ft.ScrollMode.AUTO)

    # --- TIMER DISPLAY ---
    timer_text = ft.Text("25:00", size=65, weight=ft.FontWeight.BOLD, color=TEXT_MAIN)
    timer_display = ft.Container(
        content=ft.Stack([
            ft.Container(content=timer_text, alignment=ft.Alignment(0, 0))
        ]),
        width=280, height=280,
        shape=ft.BoxShape.CIRCLE,
        bgcolor="#0f172a",
        border=ft.Border(                   # ✅ Border.all replacement
            top=ft.BorderSide(2, ACCENT_BLUE),
            bottom=ft.BorderSide(2, ACCENT_BLUE),
            left=ft.BorderSide(2, ACCENT_BLUE),
            right=ft.BorderSide(2, ACCENT_BLUE),
        ),
        shadow=ft.BoxShadow(
            spread_radius=5, blur_radius=40,
            color="#663b82f6",
            offset=ft.Offset(0, 0),
        ),
    )

    # --- API HELPERS ---
    def refresh_tasks():
        tasks_view.controls.clear()
        try:
            response = requests.get(f"{API_URL}/tasks", timeout=4)
            if response.status_code == 200:
                for t in response.json():
                    add_task_to_ui(t["title"], t.get("is_done", False), t.get("date", ""))
        except Exception as e:
            print(f"Server not reachable: {e}")
        page.update()

    def add_task_to_ui(title, is_done, date_str=""):
        # ✅ FIX: decoration moved into ft.TextStyle
        label = ft.Text(
            title, expand=True, size=15,
            color=TEXT_MUTED if is_done else TEXT_MAIN,
            style=ft.TextStyle(
                decoration=ft.TextDecoration.LINE_THROUGH if is_done else ft.TextDecoration.NONE
            ),
        )

        def on_check_change(e):
            label.color = TEXT_MUTED if e.control.value else TEXT_MAIN
            label.style = ft.TextStyle(
                decoration=ft.TextDecoration.LINE_THROUGH if e.control.value
                           else ft.TextDecoration.NONE
            )
            page.update()

        cb = ft.Checkbox(value=is_done, fill_color=ACCENT_BLUE, on_change=on_check_change)
        container = ft.Container(
            content=ft.Row([cb, label]),
            bgcolor=CARD_BG, padding=12, border_radius=15,
            border=ft.Border(
                top=ft.BorderSide(1, "#19f4f4f5"),
                bottom=ft.BorderSide(1, "#19f4f4f5"),
                left=ft.BorderSide(1, "#19f4f4f5"),
                right=ft.BorderSide(1, "#19f4f4f5"),
            ),
            animate=ft.Animation(300, ft.AnimationCurve.EASE_IN_OUT),
        )
        tasks_view.controls.append(container)
        page.update()

    # --- INPUTS ---
    ai_input = ft.TextField(
        hint_text="Ask AI to plan your session...",
        expand=True, border_width=0, bgcolor="#00000000",
        text_style=ft.TextStyle(color=TEXT_MAIN),
        cursor_color=TEXT_MAIN,
    )
    ai_loading = ft.ProgressRing(visible=False, width=20, height=20, color=ACCENT_PURPLE)

    new_task_input = ft.TextField(
        hint_text="Manual task...", expand=True, border_radius=30,
        border_color=TEXT_MUTED,
        content_padding=ft.Padding(20, 12, 20, 12),   # ✅ Padding.symmetric replacement
        text_style=ft.TextStyle(color=TEXT_MAIN),
        cursor_color=TEXT_MAIN,
    )

    # --- ACTION HANDLERS ---
    def handle_ai_gen(e):
        if not ai_input.value: return
        ai_loading.visible = True
        page.update()
        try:
            requests.post(f"{API_URL}/generate-schedule",
                          json={"prompt": ai_input.value}, timeout=30)
            refresh_tasks()
            ai_input.value = ""
        except Exception as ex:
            print(f"AI generate error: {ex}")
        ai_loading.visible = False
        page.update()

    def handle_add_manual(e):
        if not new_task_input.value: return
        try:
            requests.post(f"{API_URL}/tasks",
                          json={"title": new_task_input.value, "is_done": False}, timeout=5)
            refresh_tasks()
            new_task_input.value = ""
        except Exception as ex:
            print(f"Add task error: {ex}")
        page.update()

    def clear_completed(e):
        try:
            requests.delete(f"{API_URL}/tasks/clear-completed", timeout=5)
            refresh_tasks()
        except Exception as ex:
            print(f"Clear error: {ex}")

    # ─── TIMER STATE ──────────────────────────────────────────
    timer_state = {"is_running": False, "time_left": 25 * 60, "total": 25 * 60}

    def apply_minutes(minutes):
        timer_state["is_running"] = False
        timer_state["time_left"]  = minutes * 60
        timer_state["total"]      = minutes * 60
        mins, secs = divmod(minutes * 60, 60)
        timer_text.value = f"{mins:02d}:{secs:02d}"
        try:
            timer_display.shadow.color = "#663b82f6"
        except Exception:
            pass
        page.update()

    def start_timer(e):
        if timer_state["is_running"]: return
        timer_state["is_running"] = True
        try:
            timer_display.shadow.color = "#ef4444"
        except Exception:
            pass
        page.update()

        async def countdown():
            while timer_state["is_running"] and timer_state["time_left"] > 0:
                await asyncio.sleep(1)
                timer_state["time_left"] -= 1
                mins, secs = divmod(timer_state["time_left"], 60)
                timer_text.value = f"{mins:02d}:{secs:02d}"
                page.update()
            if timer_state["time_left"] <= 0:
                timer_text.value = "DONE! 🎉"
            timer_state["is_running"] = False
            try:
                timer_display.shadow.color = "#663b82f6"
            except Exception:
                pass
            page.update()

        page.run_task(countdown)

    def pause_timer(e):
        timer_state["is_running"] = False
        try:
            timer_display.shadow.color = "#663b82f6"
        except Exception:
            pass
        page.update()

    def reset_timer(e):
        timer_state["is_running"] = False
        timer_state["time_left"]  = timer_state["total"]
        mins, secs = divmod(timer_state["total"], 60)
        timer_text.value = f"{mins:02d}:{secs:02d}"
        try:
            timer_display.shadow.color = "#663b82f6"
        except Exception:
            pass
        page.update()

    # ─── TIMER SETTINGS DIALOG ────────────────────────────────
    custom_input = ft.TextField(
        label="Custom minutes",
        keyboard_type=ft.KeyboardType.NUMBER,
        border_color=ACCENT_PURPLE,
        focused_border_color=ACCENT_PURPLE,
        label_style=ft.TextStyle(color=TEXT_MUTED),
        text_style=ft.TextStyle(color=TEXT_MAIN),
        cursor_color=ACCENT_PURPLE,
        bgcolor=BG_COLOR,
        border_radius=10,
        width=180,
    )

    timer_dialog = ft.AlertDialog(modal=True)

    def make_preset(label, mins, color):
        def on_click(e):
            apply_minutes(mins)
            timer_dialog.open = False
            page.update()
        return ft.Container(
            content=ft.Column([
                ft.Text(f"{mins}m", size=20, weight=ft.FontWeight.BOLD,
                        color=BG_COLOR, text_align=ft.TextAlign.CENTER),
                ft.Text(label, size=11, color=BG_COLOR,
                        text_align=ft.TextAlign.CENTER),
            ], horizontal_alignment=ft.CrossAxisAlignment.CENTER,
               alignment=ft.MainAxisAlignment.CENTER, spacing=2),
            width=70, height=65,
            bgcolor=color,
            border_radius=14,
            alignment=ft.Alignment(0, 0),
            on_click=on_click,
            ink=True,
        )

    def apply_custom(e):
        val = custom_input.value.strip()
        if val.isdigit() and int(val) > 0:
            apply_minutes(int(val))
            timer_dialog.open = False
            page.update()
        else:
            custom_input.error_text = "Enter a valid number"
            page.update()

    def open_settings(e):
        custom_input.value      = ""
        custom_input.error_text = ""
        timer_dialog.open = True
        page.update()

    timer_dialog.title   = ft.Text("⏱  Timer Settings",
                                    color=TEXT_MAIN, weight=ft.FontWeight.BOLD, size=18)
    timer_dialog.bgcolor = CARD_BG
    timer_dialog.shape   = ft.RoundedRectangleBorder(radius=20)
    timer_dialog.content = ft.Column([
        ft.Text("Quick Presets", color=TEXT_MUTED, size=12,
                style=ft.TextStyle(letter_spacing=1)),
        ft.Row([
            make_preset("Short\nBreak",  5,  "#22c55e"),
            make_preset("Long\nBreak",  15,  "#3b82f6"),
            make_preset("Pomodoro",     25,  "#8b5cf6"),
            make_preset("Deep\nWork",   50,  "#f59e0b"),
        ], spacing=10, alignment=ft.MainAxisAlignment.CENTER),
        ft.Divider(color="#2a2a3a", height=28),
        ft.Text("Custom Duration", color=TEXT_MUTED, size=12,
                style=ft.TextStyle(letter_spacing=1)),
        ft.Row([
            custom_input,
            ft.IconButton(
                icon=ft.Icons.CHECK_CIRCLE,
                icon_color=ACCENT_PURPLE,
                icon_size=32,
                tooltip="Apply",
                on_click=apply_custom,
            ),
        ], alignment=ft.MainAxisAlignment.CENTER, spacing=8),
    ], tight=True, spacing=12, width=310)
    timer_dialog.actions = [
        ft.TextButton("Cancel",
                      on_click=lambda e: (setattr(timer_dialog, "open", False),
                                          page.update()),
                      style=ft.ButtonStyle(color=TEXT_MUTED)),
    ]
    timer_dialog.actions_alignment = ft.MainAxisAlignment.END
    page.overlay.append(timer_dialog)

    # ─── LAYOUT ───────────────────────────────────────────────
    ai_bar = ft.Container(
        content=ft.Row([
            ft.Icon(ft.Icons.AUTO_AWESOME, color=ACCENT_PURPLE),
            ai_input, ai_loading,
            ft.IconButton(icon=ft.Icons.SEND, icon_color=ACCENT_PURPLE,
                          on_click=handle_ai_gen),
        ]),
        padding=10, bgcolor=CARD_BG, border_radius=30,
        border=ft.Border(
            top=ft.BorderSide(1, "#4C8b5cf6"),
            bottom=ft.BorderSide(1, "#4C8b5cf6"),
            left=ft.BorderSide(1, "#4C8b5cf6"),
            right=ft.BorderSide(1, "#4C8b5cf6"),
        ),
    )

    tasks_content = ft.Container(
        content=ft.Column([
            ai_bar,
            ft.Container(height=10),
            ft.Row([
                new_task_input,
                ft.FloatingActionButton(icon=ft.Icons.ADD, on_click=handle_add_manual,
                                        bgcolor=ACCENT_BLUE, mini=True),
            ]),
            ft.Row([
                ft.Text("Task List", color=ACCENT_BLUE, weight=ft.FontWeight.BOLD),
                ft.TextButton("Clear Done", on_click=clear_completed),
            ], alignment=ft.MainAxisAlignment.SPACE_BETWEEN),
            tasks_view,
        ]),
        padding=20, expand=True,
    )

    focus_content = ft.Container(
        content=ft.Column([
            ft.Container(height=20),
            ft.Row([
                ft.Container(expand=True),
                ft.IconButton(
                    icon=ft.Icons.SETTINGS,
                    icon_color=TEXT_MUTED,
                    icon_size=26,
                    tooltip="Timer Settings",
                    on_click=open_settings,
                ),
            ]),
            ft.Container(height=10),
            timer_display,
            ft.Container(height=20),
            ft.Row([
                ft.Container(
                    content=ft.Text(f"{m}m", size=12, color=TEXT_MAIN),
                    bgcolor="#1e1e2e",
                    border=ft.Border(
                        top=ft.BorderSide(1, "#3a3a5a"),
                        bottom=ft.BorderSide(1, "#3a3a5a"),
                        left=ft.BorderSide(1, "#3a3a5a"),
                        right=ft.BorderSide(1, "#3a3a5a"),
                    ),
                    border_radius=20,
                    padding=ft.Padding(14, 7, 14, 7),  # ✅ Padding.symmetric replacement
                    on_click=(lambda e, mins=m: apply_minutes(mins)),
                    ink=True,
                ) for m in [5, 15, 25, 50]
            ], alignment=ft.MainAxisAlignment.CENTER, spacing=8),
            ft.Container(height=30),
            ft.Row([
                ft.IconButton(icon=ft.Icons.REPLAY, on_click=reset_timer,
                              icon_size=30, icon_color=TEXT_MUTED),
                ft.FloatingActionButton(
                    icon=ft.Icons.PLAY_ARROW, on_click=start_timer,
                    bgcolor=TEXT_MAIN, foreground_color=BG_COLOR,
                    width=65, height=65,
                ),
                ft.IconButton(icon=ft.Icons.PAUSE, on_click=pause_timer,
                              icon_size=30, icon_color=TEXT_MUTED),
            ], alignment=ft.MainAxisAlignment.CENTER),
        ], horizontal_alignment=ft.CrossAxisAlignment.CENTER),
        expand=True, visible=False,
    )

    def nav_change(e):
        tasks_content.visible = (e.control.selected_index == 0)
        focus_content.visible = (e.control.selected_index == 1)
        page.update()

    page.add(
        header,
        ft.Column([tasks_content, focus_content], expand=True),
        ft.NavigationBar(
            selected_index=0, bgcolor=CARD_BG, on_change=nav_change,
            destinations=[
                ft.NavigationBarDestination(icon=ft.Icons.LIST_ALT,  label="Tasks"),
                ft.NavigationBarDestination(icon=ft.Icons.TIMER,     label="Focus"),
            ],
        ),
    )

    refresh_tasks()


if __name__ == "__main__":
    ft.run(main)   # ✅ ft.app → ft.run (0.80+)
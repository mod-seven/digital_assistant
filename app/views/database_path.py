import tkinter as tk
from pathlib import Path
from tkinter import filedialog

import flet as ft

from app.database.connection import (
    configure_database,
    init_database,
    test_database_connection,
)
from app.settings import get_signatures_db_path, save_signatures_db_path


class DatabasePathView:
    """Екран вибору/відновлення підключення до SQLite-бази."""

    def __init__(self, page, on_connected, current_path=None, startup_error=None):
        self.page = page
        self.on_connected = on_connected
        self.path_field = ft.TextField(
            label="Шлях до файлу бази даних (.db)",
            value=str(current_path or get_signatures_db_path()),
            width=620,
            hint_text=r"Наприклад: \\server\shared\signatures.db",
        )
        self.message = ft.Text(
            value=(
                f"Не вдалося підключитися до бази даних. {startup_error}"
                if startup_error
                else ""
            ),
            color=ft.Colors.RED,
        )

    def browse(self, e=None):
        root = tk.Tk()
        root.withdraw()
        try:
            path = filedialog.askopenfilename(
                title="Виберіть файл бази даних підписів",
                filetypes=[
                    ("SQLite database", "*.db *.sqlite *.sqlite3"),
                    ("Усі файли", "*.*"),
                ],
            )
        finally:
            root.destroy()
        if path:
            self.path_field.value = path
            self.page.update()

    def connect(self, e=None):
        raw_path = (self.path_field.value or "").strip().strip('"')
        if not raw_path:
            self.message.value = "Вкажіть шлях до файлу бази даних."
            self.message.color = ft.Colors.RED
            self.page.update()
            return
        path = Path(raw_path).expanduser()
        try:
            # Зберігаємо вибір навіть при тимчасовій недоступності мережевого диска.
            save_signatures_db_path(path)
            if not path.is_file():
                raise FileNotFoundError(
                    "Файл не знайдено. Якщо потрібно створити нову базу, скористайтеся окремою кнопкою нижче."
                )
            configure_database(path)
            test_database_connection()
            init_database()
            self.message.value = "Підключення успішне."
            self.message.color = ft.Colors.GREEN
            self.page.update()
            self.on_connected()
        except Exception as ex:
            self.message.value = f"Не вдалося підключитися: {ex}"
            self.message.color = ft.Colors.RED
            self.page.update()

    def create_database(self, e=None):
        raw_path = (self.path_field.value or "").strip().strip('"')
        if not raw_path:
            self.message.value = "Вкажіть шлях до нового файлу бази даних."
            self.message.color = ft.Colors.RED
            self.page.update()
            return
        path = Path(raw_path).expanduser()
        try:
            if path.exists():
                raise FileExistsError(
                    "Файл уже існує. Щоб використати його, натисніть «Підключитися»."
                )
            if not path.parent.is_dir():
                raise FileNotFoundError(
                    "Каталог, у якому має бути база даних, не існує або недоступний."
                )
            save_signatures_db_path(path)
            configure_database(path)
            init_database()
            test_database_connection()
            self.message.value = "Нову базу даних створено."
            self.message.color = ft.Colors.GREEN
            self.page.update()
            self.on_connected()
        except Exception as ex:
            self.message.value = f"Не вдалося створити базу даних: {ex}"
            self.message.color = ft.Colors.RED
            self.page.update()

    def build(self):
        return ft.Container(
            expand=True,
            alignment=ft.Alignment.CENTER,
            padding=24,
            content=ft.Column(
                tight=True,
                spacing=14,
                horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                controls=[
                    ft.Icon(ft.Icons.STORAGE_OUTLINED, size=48),
                    ft.Text(
                        "Підключення до бази даних", size=25, weight=ft.FontWeight.BOLD
                    ),
                    ft.Text(
                        "Перевірте шлях до спільного файлу бази даних або виберіть його заново.",
                        text_align=ft.TextAlign.CENTER,
                    ),
                    ft.Row(
                        controls=[
                            self.path_field,
                            ft.Button(
                                "Огляд…",
                                icon=ft.Icons.FOLDER_OPEN,
                                on_click=self.browse,
                            ),
                        ],
                        wrap=True,
                        alignment=ft.MainAxisAlignment.CENTER,
                    ),
                    self.message,
                    ft.Row(
                        controls=[
                            ft.Button(
                                "Підключитися",
                                icon=ft.Icons.LINK,
                                on_click=self.connect,
                            ),
                            ft.Button(
                                "Створити нову базу",
                                icon=ft.Icons.ADD,
                                on_click=self.create_database,
                            ),
                        ],
                        wrap=True,
                        alignment=ft.MainAxisAlignment.CENTER,
                    ),
                    ft.Text(
                        "Важливо: створюйте нову базу лише якщо вам справді потрібна порожня база. Для доступу до наявних підписів виберіть існуючий файл .db.",
                        size=12,
                        color=ft.Colors.GREY_700,
                        text_align=ft.TextAlign.CENTER,
                    ),
                ],
            ),
        )

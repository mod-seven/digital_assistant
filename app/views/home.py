# app/views/home.py

import tkinter as tk
from pathlib import Path
from tkinter import filedialog

import flet as ft

from app.components.sidebar import Sidebar
from app.services.import_excel import import_excel
from app.state import AppState
from app.styles import (
    BG_COLOR,
    BORDER,
    CARD_RADIUS,
    CONTENT_PADDING,
    PRIMARY,
    SUCCESS,
    TEXT,
    TEXT_SECONDARY,
    WHITE,
)


class HomeView:

    def __init__(
        self,
        page: ft.Page,
        state: AppState,
    ):
        self.page = page
        self.state = state

    # ---------------------------------------------------------
    # Вибір Excel
    # ---------------------------------------------------------

    def select_excel(self, e):

        root = tk.Tk()
        root.withdraw()

        root.attributes("-topmost", True)

        file_path = filedialog.askopenfilename(
            title="Виберіть Excel файл",
            filetypes=[
                ("Excel files", "*.xlsx"),
                ("Excel files", "*.xls"),
                ("All files", "*.*"),
            ],
        )

        root.destroy()

        if not file_path:
            return

        print("Вибраний файл:", file_path)

        import_excel(
            file_path,
            self.state,
        )

        self.page.controls.clear()
        self.page.add(self.build())
        self.page.update()

    def update_statistics(self):
        self.staff_value.value = self.state.number_of_staff_positions
        self.list_value.value = self.state.number_on_the_list
        self.rows_value.value = self.state.number_row

        self.page.update()

    # ---------------------------------------------------------
    # Картка статистики
    # ---------------------------------------------------------

    def statistic_card(
        self,
        icon,
        title,
        value,
    ):

        return ft.Container(
            expand=True,
            bgcolor=WHITE,
            border_radius=CARD_RADIUS,
            border=ft.Border.all(
                1,
                BORDER,
            ),
            padding=20,
            content=ft.Row(
                controls=[
                    ft.Container(
                        width=42,
                        height=42,
                        bgcolor="#EAF3FF",
                        border_radius=10,
                        alignment=ft.Alignment(
                            x=0,
                            y=0,
                        ),
                        content=ft.Icon(
                            icon,
                            color=PRIMARY,
                            size=21,
                        ),
                    ),
                    ft.Column(
                        spacing=2,
                        controls=[
                            ft.Text(
                                title,
                                size=13,
                                color=TEXT_SECONDARY,
                            ),
                            ft.Text(
                                value,
                                size=22,
                                weight=ft.FontWeight.BOLD,
                                color=TEXT,
                            ),
                        ],
                    ),
                ],
                spacing=14,
            ),
        )

    # ---------------------------------------------------------
    # Головна картка імпорту
    # ---------------------------------------------------------

    def import_card(self):

        imported = self.state.imported

        self.file_name_text = ft.Text(
            self.state.file_name if imported else "Файл ще не вибрано",
            size=15,
            weight=ft.FontWeight.BOLD if imported else None,
            color=TEXT if imported else TEXT_SECONDARY,
        )

        self.file_status = ft.Text(
            (
                "Excel успішно імпортовано"
                if imported
                else "Оберіть Excel файл для початку роботи"
            ),
            size=13,
            color=SUCCESS if imported else TEXT_SECONDARY,
        )

        self.import_button = ft.Button(
            content=ft.Row(
                controls=[
                    ft.Icon(
                        ft.Icons.CHECK if imported else ft.Icons.UPLOAD_FILE,
                        color=WHITE,
                    ),
                    ft.Text(
                        "Excel імпортовано" if imported else "Вибрати Excel",
                        color=WHITE,
                        weight=ft.FontWeight.BOLD,
                    ),
                ],
                alignment=ft.MainAxisAlignment.CENTER,
            ),
            bgcolor=SUCCESS if imported else PRIMARY,
            color=WHITE,
            on_click=self.select_excel,
        )

        return ft.Container(
            content=ft.Column(
                controls=[
                    ft.Text(
                        "Імпорт Excel",
                        size=20,
                        weight=ft.FontWeight.BOLD,
                        color=TEXT,
                    ),
                    ft.Text(
                        "Завантажте файл зі штатною структурою",
                        size=14,
                        color=TEXT_SECONDARY,
                    ),
                    self.file_name_text,
                    self.file_status,
                    self.import_button,
                ],
                spacing=10,
            ),
            padding=20,
            bgcolor=WHITE,
            border_radius=CARD_RADIUS,
        )

    # ---------------------------------------------------------
    # BUILD
    # ---------------------------------------------------------

    def build(self):

        return ft.Row(
            expand=True,
            spacing=0,
            controls=[
                # ---------------------------------------------
                # Ліва панель
                # ---------------------------------------------
                Sidebar(self.page, self.state).build(),
                ft.VerticalDivider(
                    width=1,
                    color=BORDER,
                ),
                # ---------------------------------------------
                # Основна частина
                # ---------------------------------------------
                ft.Container(
                    expand=True,
                    bgcolor=BG_COLOR,
                    padding=CONTENT_PADDING,
                    content=ft.Column(
                        expand=True,
                        spacing=25,
                        controls=[
                            # Заголовок
                            ft.Column(
                                spacing=5,
                                controls=[
                                    ft.Text(
                                        "Вітаємо!",
                                        size=30,
                                        weight=ft.FontWeight.BOLD,
                                        color=TEXT,
                                    ),
                                    ft.Text(
                                        "Робочий простір для роботи " "з даними Excel",
                                        size=15,
                                        color=TEXT_SECONDARY,
                                    ),
                                ],
                            ),
                            # Імпорт
                            self.import_card(),
                            # Статистика
                            ft.Row(
                                spacing=15,
                                controls=[
                                    self.statistic_card(
                                        ft.Icons.ACCOUNT_TREE_OUTLINED,
                                        "Штат",
                                        str(self.state.number_of_staff_positions),
                                    ),
                                    self.statistic_card(
                                        ft.Icons.PEOPLE_OUTLINE,
                                        "Список",
                                        str(self.state.number_on_the_list),
                                    ),
                                    self.statistic_card(
                                        ft.Icons.TABLE_ROWS_OUTLINED,
                                        "Рядки Excel",
                                        str(self.state.number_row),
                                    ),
                                ],
                            ),
                            # Підказка
                            ft.Container(
                                bgcolor=WHITE,
                                border_radius=CARD_RADIUS,
                                border=ft.Border.all(
                                    1,
                                    BORDER,
                                ),
                                padding=20,
                                content=ft.Row(
                                    controls=[
                                        ft.Icon(
                                            ft.Icons.INFO_OUTLINE,
                                            color=PRIMARY,
                                        ),
                                        ft.Column(
                                            spacing=3,
                                            controls=[
                                                ft.Text(
                                                    "Як почати роботу?",
                                                    size=14,
                                                    weight=ft.FontWeight.BOLD,
                                                    color=TEXT,
                                                ),
                                                ft.Text(
                                                    "Виберіть Excel-файл. "
                                                    "Після імпорту його дані "
                                                    "будуть доступні в усіх "
                                                    "розділах програми.",
                                                    size=13,
                                                    color=TEXT_SECONDARY,
                                                ),
                                            ],
                                        ),
                                    ],
                                    spacing=14,
                                ),
                            ),
                        ],
                    ),
                ),
            ],
        )

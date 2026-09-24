# app/components/sidebar.py

import flet as ft

from app.styles import PRIMARY, SIDEBAR_WIDTH, TEXT, TEXT_SECONDARY, WHITE


class Sidebar:

    def __init__(self, page: ft.Page):
        self.page = page

    def navigate(self, route: str):
        self.page.navigate(route)

    def menu_button(
        self,
        text: str,
        route: str,
        icon=None,
    ):
        return ft.Button(
            content=ft.Row(
                controls=[
                    (
                        ft.Icon(
                            icon,
                            size=19,
                            color=TEXT_SECONDARY,
                        )
                        if icon
                        else ft.Container()
                    ),
                    ft.Text(
                        text,
                        size=14,
                        color=TEXT,
                    ),
                ],
                spacing=12,
            ),
            width=SIDEBAR_WIDTH - 30,
            height=42,
            on_click=lambda e: self.navigate(route),
        )

    def build(self):

        return ft.Container(
            width=SIDEBAR_WIDTH,
            bgcolor=WHITE,
            padding=15,
            content=ft.Column(
                spacing=6,
                controls=[
                    # Логотип
                    ft.Container(
                        padding=10,
                        content=ft.Row(
                            controls=[
                                ft.Container(
                                    width=36,
                                    height=36,
                                    bgcolor=PRIMARY,
                                    border_radius=8,
                                    alignment=ft.Alignment(
                                        x=0,
                                        y=0,
                                    ),
                                    content=ft.Icon(
                                        ft.Icons.GRID_VIEW,
                                        color=WHITE,
                                        size=21,
                                    ),
                                ),
                                ft.Text(
                                    "Digital Assistant",
                                    size=16,
                                    weight=ft.FontWeight.BOLD,
                                    color=TEXT,
                                ),
                            ],
                            spacing=10,
                        ),
                    ),
                    ft.Container(height=10),
                    ft.Divider(
                        height=1,
                        color="#EEEEEE",
                    ),
                    ft.Container(height=8),
                    # Меню
                    self.menu_button(
                        "Головна",
                        "/",
                        ft.Icons.HOME_OUTLINED,
                    ),
                    self.menu_button(
                        "Працівники",
                        "/employees",
                        ft.Icons.PEOPLE_OUTLINE,
                    ),
                    self.menu_button(
                        "Посади",
                        "/positions",
                        ft.Icons.WORK_OUTLINE,
                    ),
                    self.menu_button(
                        "Підрозділи",
                        "/departments",
                        ft.Icons.ACCOUNT_TREE_OUTLINED,
                    ),
                    self.menu_button(
                        "Дані",
                        "/data",
                        ft.Icons.TABLE_VIEW,
                    ),
                    self.menu_button(
                        "Звіти",
                        "/reports",
                        ft.Icons.DESCRIPTION_OUTLINED,
                    ),
                    self.menu_button(
                        "Експорт",
                        "/export",
                        ft.Icons.UPLOAD_OUTLINED,
                    ),
                    # Заповнюємо простір
                    ft.Container(
                        expand=True,
                    ),
                    ft.Divider(
                        height=1,
                        color="#EEEEEE",
                    ),
                    ft.Button(
                        content=ft.Row(
                            controls=[
                                ft.Icon(
                                    ft.Icons.INFO_OUTLINE,
                                    size=18,
                                    color=TEXT_SECONDARY,
                                ),
                                ft.Text(
                                    "Про програму",
                                    size=13,
                                    color=TEXT_SECONDARY,
                                ),
                            ],
                            spacing=10,
                        ),
                        width=SIDEBAR_WIDTH - 30,
                        height=40,
                    ),
                    ft.Text(
                        "Digital Assistant v1.0",
                        size=11,
                        color="#9CA3AF",
                    ),
                ],
            ),
        )

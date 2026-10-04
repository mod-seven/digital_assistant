import flet as ft

from app.components.sidebar import Sidebar
from app.state import AppState
from app.styles import BG_COLOR, BORDER, CONTENT_PADDING
from app.views.home import HomeView
from app.views.reports import ReportsView
from app.views.signatures import SignaturesView


class AppRouter:

    def __init__(
        self,
        page: ft.Page,
        state: AppState,
    ):
        self.page = page
        self.state = state

    # =========================================================
    # START
    # =========================================================

    def start(self):
        # Реєструємо обробник маршруту
        self.page.on_route_change = self.route_change

        # Відразу будуємо поточний маршрут
        self.route_change()

    # =========================================================
    # ROUTE CHANGE
    # =========================================================

    def route_change(self, e=None):

        print("ROUTE:", self.page.route)

        route = self.page.route

        # -----------------------------------------------------
        # Очищаємо поточний екран
        # -----------------------------------------------------

        self.page.controls.clear()

        # -----------------------------------------------------
        # Вибір View
        # -----------------------------------------------------

        if route == "/":
            view = HomeView(
                self.page,
                self.state,
                self,
            )

        elif route == "/reports":

            view = ReportsView(
                self.page,
                self.state,
            )

        elif route == "/signatures":

            view = SignaturesView(
                page=self.page,
                state=self.state,
            )

        else:

            view = HomeView(
                self.page,
                self.state,
                self,
            )

        # -----------------------------------------------------
        # Створюємо основний layout
        # -----------------------------------------------------

        layout = self.build_layout(view.build())

        # -----------------------------------------------------
        # Додаємо layout на page
        # -----------------------------------------------------

        self.page.add(layout)

        # -----------------------------------------------------
        # Оновлюємо UI
        # -----------------------------------------------------

        self.page.update()

    # =========================================================
    # MAIN LAYOUT
    # =========================================================

    def build_layout(self, content):

        return ft.Row(
            expand=True,
            spacing=0,
            controls=[
                # ---------------------------------------------
                # Ліва панель
                # ---------------------------------------------
                Sidebar(
                    self.page,
                    self.state,
                ).build(),
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
                    content=content,
                ),
            ],
        )

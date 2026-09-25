import flet as ft

from app.state import AppState
from app.views.home import HomeView
from app.views.reports import ReportsView


class AppRouter:

    def __init__(
        self,
        page: ft.Page,
        state: AppState,
    ):
        self.page = page
        self.state = state

    def start(self):
        # Реєструємо обробник маршруту
        self.page.on_route_change = self.route_change

        # ВАЖЛИВО:
        # не navigate("/"), а відразу будуємо поточний маршрут
        self.route_change()

    def route_change(self, e=None):

        print("ROUTE:", self.page.route)

        route = self.page.route

        # Очистити поточний екран
        self.page.controls.clear()

        # Вибір сторінки
        if route == "/":
            view = HomeView(
                self.page,
                self.state,
            )

        elif route == "/reports":
            view = ReportsView(
                self.page,
                self.state,
            )

        else:
            view = HomeView(
                self.page,
                self.state,
            )

        # Додаємо сторінку
        self.page.add(view.build())

        # Оновлюємо UI
        self.page.update()

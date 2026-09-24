import flet as ft

from app.state import AppState
from app.views.home import HomeView

# from app.views.employees import EmployeesView
# from app.views.positions import PositionsView
# from app.views.departments import DepartmentsView
# from app.views.data import DataView
# from app.views.reports import ReportsView
# from app.views.export import ExportView


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

        # elif route == "/employees":
        #     view = EmployeesView(self.page)

        # elif route == "/positions":
        #     view = PositionsView(self.page)

        # elif route == "/departments":
        #     view = DepartmentsView(self.page)

        # elif route == "/data":
        #     view = DataView(self.page)

        # elif route == "/reports":
        #     view = ReportsView(self.page)

        # elif route == "/export":
        #     view = ExportView(self.page)

        else:
            view = HomeView(
                self.page,
                self.state,
            )

        # Додаємо сторінку
        self.page.add(view.build())

        # Оновлюємо UI
        self.page.update()

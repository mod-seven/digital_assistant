import flet as ft

from app.components.sidebar import Sidebar
from app.database.connection import (
    configure_database,
    init_database,
    test_database_connection,
)
from app.repositories.user import UserRepository
from app.settings import get_signatures_db_path
from app.state import AppState
from app.styles import BG_COLOR, BORDER, CONTENT_PADDING
from app.views.account import FirstAdminView, LoginView, SettingsView
from app.views.database_path import DatabasePathView
from app.views.home import HomeView
from app.views.reports import ReportsView
from app.views.signatures import SignaturesView


class AppRouter:
    def __init__(self, page: ft.Page, state: AppState):
        self.page = page
        self.state = state
        self.auth_ready = False
        self.auth_error = ""
        self.user_repository = UserRepository()

    def start(self):
        self.page.on_route_change = self.route_change
        try:
            path = get_signatures_db_path()
            if not path.is_file():
                raise FileNotFoundError(f"Файл бази даних не знайдено: {path}")
            configure_database(path)
            test_database_connection()
            init_database()
            self.auth_ready = True
            self.auth_error = ""
        except Exception as ex:
            self.auth_ready = False
            self.auth_error = str(ex)
        self.page.go("/database")

    def database_connected(self):
        self.auth_ready = True
        self.auth_error = ""
        # Після перемикання БД потрібно виконати вхід саме в обрану базу.
        self.state.current_user = None
        self.page.go("/login")

    def route_change(self, e=None):
        route = self.page.route or "/login"
        self.page.controls.clear()

        # Екран відновлення доступний незалежно від стану авторизації.
        if route == "/database" or not self.auth_ready:
            view = DatabasePathView(
                self.page,
                self.database_connected,
                current_path=get_signatures_db_path(),
                startup_error=self.auth_error,
            )
            self.page.add(view.build())
            self.page.update()
            return

        if route not in ("/login", "/setup-admin") and not self.state.current_user:
            self.page.go("/login")
            return
        if route == "/login" and self.state.current_user:
            self.page.go("/")
            return
        try:
            if route == "/login" and self.user_repository.user_count() == 0:
                self.page.go("/setup-admin")
                return
        except Exception as ex:
            self.auth_ready = False
            self.auth_error = str(ex)
            self.page.go("/database")
            return

        if route == "/login":
            view = LoginView(self.page, self.state, lambda: self.page.go("/"))
        elif route == "/setup-admin":
            view = FirstAdminView(self.page, self.state, lambda: self.page.go("/"))
        elif route == "/settings":
            view = SettingsView(
                self.page, self.state, on_database_changed=self.database_connected
            )
        elif route == "/":
            view = HomeView(self.page, self.state, self)
        elif route == "/reports":
            view = ReportsView(self.page, self.state)
        elif route == "/signatures":
            view = SignaturesView(page=self.page, state=self.state)
        else:
            view = HomeView(self.page, self.state, self)

        if route in ("/login", "/setup-admin"):
            self.page.add(view.build())
            self.page.update()
            return

        self.page.add(self.build_layout(view.build()))
        self.page.update()

    def build_layout(self, content):
        return ft.Row(
            expand=True,
            spacing=0,
            controls=[
                Sidebar(self.page, self.state).build(),
                ft.VerticalDivider(width=1, color=BORDER),
                ft.Container(
                    expand=True,
                    bgcolor=BG_COLOR,
                    padding=CONTENT_PADDING,
                    content=content,
                ),
            ],
        )

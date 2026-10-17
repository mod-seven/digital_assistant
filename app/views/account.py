import tkinter as tk
from pathlib import Path
from tkinter import filedialog

import flet as ft

from app.constants import ROLE_ADMIN, ROLES
from app.database.connection import (
    configure_database,
    init_database,
    test_database_connection,
)
from app.repositories.user import UserRepository
from app.services.auth import AuthService
from app.settings import get_signatures_db_path, save_signatures_db_path


class UserManagementMixin:
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.user_repository = UserRepository()
        self.auth_service = AuthService(user_repository=self.user_repository)


class LoginView(UserManagementMixin):
    def __init__(self, page, state, on_success):
        super().__init__()
        self.page, self.state, self.on_success = page, state, on_success
        self.username = ft.TextField(label="Логін", autofocus=True, width=320)
        self.password = ft.TextField(
            label="Пароль", password=True, can_reveal_password=True, width=320
        )
        self.message = ft.Text(color=ft.Colors.RED)

    def submit(self, e=None):
        user = self.auth_service.authenticate(
            self.username.value or "", self.password.value or ""
        )
        if not user:
            self.message.value = "Неправильний логін або пароль, або акаунт вимкнено."
            self.page.update()
            return
        self.state.current_user = user
        self.on_success()

    def build(self):
        return ft.Container(
            expand=True,
            alignment=ft.Alignment.CENTER,
            content=ft.Column(
                tight=True,
                horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                spacing=14,
                controls=[
                    ft.Text("Digital Assistant", size=28, weight=ft.FontWeight.BOLD),
                    ft.Text("Вхід до облікового запису", size=16),
                    self.username,
                    self.password,
                    self.message,
                    ft.Button("Увійти", width=320, on_click=self.submit),
                ],
            ),
        )


class FirstAdminView(UserManagementMixin):
    def __init__(self, page, state, on_success):
        super().__init__()
        self.page, self.state, self.on_success = page, state, on_success
        self.username = ft.TextField(label="Логін адміністратора", width=340)
        self.password = ft.TextField(
            label="Пароль (від 8 символів)",
            password=True,
            can_reveal_password=True,
            width=340,
        )
        self.confirm = ft.TextField(
            label="Повторіть пароль", password=True, can_reveal_password=True, width=340
        )
        self.message = ft.Text(color=ft.Colors.RED)

    def submit(self, e=None):
        if self.password.value != self.confirm.value:
            self.message.value = "Паролі не збігаються."
        else:
            try:
                self.auth_service.create_user(
                    self.username.value or "", self.password.value or "", ROLE_ADMIN
                )
                self.state.current_user = self.auth_service.authenticate(
                    self.username.value or "", self.password.value or ""
                )
                self.on_success()
                return
            except Exception as ex:
                self.message.value = str(ex)
        self.page.update()

    def build(self):
        return ft.Container(
            expand=True,
            alignment=ft.Alignment.CENTER,
            content=ft.Column(
                tight=True,
                horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                spacing=12,
                controls=[
                    ft.Text(
                        "Початкове налаштування", size=26, weight=ft.FontWeight.BOLD
                    ),
                    ft.Text("Створіть перший акаунт адміністратора."),
                    self.username,
                    self.password,
                    self.confirm,
                    self.message,
                    ft.Button(
                        "Створити адміністратора", width=340, on_click=self.submit
                    ),
                ],
            ),
        )


class SettingsView(UserManagementMixin):
    def __init__(self, page, state, on_database_changed=None):
        super().__init__()
        self.page, self.state = page, state
        self.on_database_changed = on_database_changed
        self.section = "Основні налаштування"
        self.content = ft.Column(expand=True, scroll=ft.ScrollMode.AUTO, spacing=12)

    def build(self):
        self.populate_section(self.section)
        return ft.Column(
            expand=True,
            spacing=16,
            controls=[
                ft.Text("Налаштування", size=26, weight=ft.FontWeight.BOLD),
                ft.Row(
                    controls=[
                        ft.Button(
                            "Основні налаштування",
                            on_click=lambda e: self.show_section(
                                "Основні налаштування"
                            ),
                        ),
                        ft.Button(
                            "Акаунт", on_click=lambda e: self.show_section("Акаунт")
                        ),
                    ]
                ),
                self.content,
            ],
        )

    def show_section(self, section):
        self.section = section
        self.populate_section(section)
        self.page.update()

    def populate_section(self, section):
        self.content.controls.clear()
        user = self.state.current_user or {}
        if section == "Основні налаштування":
            self.content.controls.extend(
                [
                    ft.Text("Основні налаштування", size=20, weight=ft.FontWeight.BOLD),
                    ft.Text("База даних підписів", size=18, weight=ft.FontWeight.BOLD),
                ]
            )
            self.content.controls.extend(self.database_path_controls())
            if user.get("role") == ROLE_ADMIN:
                self.content.controls.append(
                    ft.Text("Керування акаунтами", size=20, weight=ft.FontWeight.BOLD)
                )
                self.content.controls.extend(self.account_management_controls())
        else:
            self.content.controls.extend(
                [
                    ft.Text("Акаунт", size=20, weight=ft.FontWeight.BOLD),
                    ft.Text(f"Логін: {user.get('username', '')}"),
                    ft.Text(f"Роль: {ROLES.get(user.get('role'), 'Невідома роль')}"),
                ]
            )
            new_password = ft.TextField(
                label="Новий пароль", password=True, can_reveal_password=True, width=320
            )
            msg = ft.Text()

            def change(e):
                try:
                    self.auth_service.change_password(
                        user["id"], new_password.value or ""
                    )
                    msg.value = "Пароль змінено."
                    msg.color = ft.Colors.GREEN
                except Exception as ex:
                    msg.value = str(ex)
                    msg.color = ft.Colors.RED
                self.page.update()

            self.content.controls.extend(
                [
                    new_password,
                    ft.Button("Змінити пароль", on_click=change),
                    msg,
                    ft.Button("Вийти з акаунта", on_click=self.logout),
                ]
            )

    def database_path_controls(self):
        path_field = ft.TextField(
            label="Шлях до файлу бази даних (.db)",
            value=str(get_signatures_db_path()),
            width=620,
        )
        message = ft.Text()

        def browse(e=None):
            root = tk.Tk()
            root.withdraw()
            try:
                selected = filedialog.askopenfilename(
                    title="Виберіть файл бази даних",
                    filetypes=[
                        ("SQLite database", "*.db *.sqlite *.sqlite3"),
                        ("Усі файли", "*.*"),
                    ],
                )
            finally:
                root.destroy()
            if selected:
                path_field.value = selected
                self.page.update()

        def save_and_connect(e=None):
            raw = (path_field.value or "").strip().strip('"')
            if not raw:
                message.value = "Вкажіть шлях до файлу бази даних."
                message.color = ft.Colors.RED
                self.page.update()
                return
            path = Path(raw).expanduser()
            try:
                save_signatures_db_path(path)
                if not path.is_file():
                    raise FileNotFoundError(
                        "Файл не знайдено. Якщо це нова база, спочатку створіть її на екрані підключення."
                    )
                configure_database(path)
                test_database_connection()
                init_database()
                message.value = "Шлях збережено, підключення успішне. Потрібно повторно увійти в акаунт цієї бази."
                message.color = ft.Colors.GREEN
                self.page.update()
                if self.on_database_changed:
                    self.on_database_changed()
            except Exception as ex:
                message.value = f"Шлях збережено, але підключитися не вдалося: {ex}"
                message.color = ft.Colors.RED
                self.page.update()
                # Щоб користувач міг виправити шлях, відкриваємо екран відновлення.
                self.page.go("/database")

        return [
            ft.Text(
                "Файл БД та каталог images мають бути доступні користувачу програми."
            ),
            ft.Row(
                controls=[
                    path_field,
                    ft.Button("Огляд…", icon=ft.Icons.FOLDER_OPEN, on_click=browse),
                ],
                wrap=True,
            ),
            ft.Row(
                controls=[
                    ft.Button(
                        "Зберегти та підключитися",
                        icon=ft.Icons.LINK,
                        on_click=save_and_connect,
                    )
                ]
            ),
            message,
        ]

    def account_management_controls(self):
        username = ft.TextField(label="Новий логін", width=260)
        password = ft.TextField(
            label="Пароль (від 8 символів)",
            password=True,
            can_reveal_password=True,
            width=260,
        )
        role = ft.Dropdown(
            label="Роль",
            width=260,
            options=[ft.dropdown.Option(key=k, text=v) for k, v in ROLES.items()],
        )
        message = ft.Text()
        users_column = ft.Column(spacing=6)

        def refresh_users():
            users_column.controls.clear()
            for u in self.user_repository.list_users():
                users_column.controls.append(
                    ft.Row(
                        controls=[
                            ft.Text(
                                f"{u['username']} — {ROLES.get(u['role'], u['role'])}",
                                expand=True,
                            ),
                            ft.Text("Активний" if u["is_active"] else "Вимкнений"),
                            ft.Button(
                                "Вимкнути" if u["is_active"] else "Увімкнути",
                                on_click=lambda e, x=u: toggle(x),
                            ),
                        ]
                    )
                )

        def toggle(u):
            if u["id"] == self.state.current_user.get("id") and u["is_active"]:
                message.value = (
                    "Не можна вимкнути власний акаунт під час поточного сеансу."
                )
            else:
                self.user_repository.set_user_active(u["id"], not u["is_active"])
                refresh_users()
            self.page.update()

        def add(e):
            try:
                self.auth_service.create_user(
                    username.value or "", password.value or "", role.value or "viewer"
                )
                message.value = "Акаунт створено."
                message.color = ft.Colors.GREEN
                username.value = password.value = ""
                refresh_users()
            except Exception as ex:
                message.value = str(ex)
                message.color = ft.Colors.RED
            self.page.update()

        refresh_users()
        return [
            ft.Row(controls=[username, password, role], wrap=True),
            ft.Button("Створити акаунт", on_click=add),
            message,
            users_column,
        ]

    def logout(self, e=None):
        self.state.current_user = None
        self.page.go("/login")

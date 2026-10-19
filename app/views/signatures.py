import tkinter as tk
from tkinter import filedialog

import flet as ft

from app.constants import ROLE_ADMIN, ROLE_SIGNATURES
from app.repositories.signatures import SignaturesRepository


class SignaturesView:
    def __init__(self, page: ft.Page, state):
        self.page = page
        self.state = state

        self.repository: SignaturesRepository = state.signatures_repository
        current_role = (state.current_user or {}).get("role")
        self.is_admin = current_role == ROLE_ADMIN
        self.can_manage = current_role in {ROLE_ADMIN, ROLE_SIGNATURES}
        # Усі авторизовані користувачі можуть приховати підпис;
        # лише адміністратор може відновлювати приховані підписи.
        self.can_toggle = bool(state.current_user)

        # =====================================================
        # СТАН БАЗИ ДАНИХ
        # =====================================================

        self.database_available = True

        # =====================================================
        # SEARCH
        # =====================================================

        self.search_field = ft.TextField(
            label="Пошук за ПІБ",
            hint_text="Введіть прізвище, ім'я або по батькові",
            prefix_icon=ft.Icons.SEARCH,
            on_change=self.search_changed,
            expand=True,
        )

        # =====================================================
        # ADD BUTTON
        # =====================================================

        self.add_button = ft.Button(
            "Додати підпис",
            icon=ft.Icons.ADD,
            on_click=self.add_signature,
            visible=self.can_manage,
        )

        # =====================================================
        # LIST
        # =====================================================

        self.list_view = ft.Column(
            spacing=10,
            scroll=ft.ScrollMode.AUTO,
            expand=True,
        )

    # =========================================================
    # BUILD
    # =========================================================

    def build(self):
        self.load_signatures()

        return ft.Column(
            controls=[
                ft.Row(
                    controls=[
                        ft.Text(
                            "Підписи",
                            size=26,
                            weight=ft.FontWeight.BOLD,
                        ),
                        ft.Container(
                            expand=True,
                        ),
                        self.add_button,
                    ],
                ),
                ft.Container(
                    content=self.search_field,
                    margin=10,
                ),
                ft.Container(
                    content=self.list_view,
                    expand=True,
                ),
            ],
            expand=True,
        )

    # =========================================================
    # DATABASE UNAVAILABLE
    # =========================================================

    def set_database_unavailable(self):
        self.database_available = False

        self.search_field.disabled = True
        self.add_button.disabled = True

        self.list_view.controls.clear()

        self.list_view.controls.append(
            ft.Container(
                expand=True,
                alignment=ft.Alignment.CENTER,
                content=ft.Column(
                    horizontal_alignment=(ft.CrossAxisAlignment.CENTER),
                    spacing=10,
                    controls=[
                        ft.Icon(
                            ft.Icons.ERROR_OUTLINE,
                            size=48,
                        ),
                        ft.Text(
                            "Немає доступу до бази даних підписів",
                            size=18,
                            weight=ft.FontWeight.BOLD,
                            text_align=ft.TextAlign.CENTER,
                        ),
                        ft.Text(
                            "Перевірте підключення до мережевого диска.",
                            size=14,
                            text_align=ft.TextAlign.CENTER,
                        ),
                    ],
                ),
            )
        )

    # =========================================================
    # DATABASE AVAILABLE
    # =========================================================

    def set_database_available(self):
        self.database_available = True

        self.search_field.disabled = False
        self.add_button.disabled = False

    # =========================================================
    # LOAD
    # =========================================================

    def load_signatures(self, search: str = ""):
        try:
            # Адміністратор бачить також приховані підписи та може відновити їх.
            signatures = self.repository.search(search, include_inactive=self.is_admin)

        except Exception as ex:
            print(f"База підписів недоступна: {ex}")

            self.set_database_unavailable()
            return

        self.set_database_available()

        self.list_view.controls.clear()

        if not signatures:
            self.list_view.controls.append(
                ft.Container(
                    content=ft.Text(
                        "Підписи не знайдено.",
                        size=16,
                    ),
                    padding=20,
                    alignment=ft.Alignment.CENTER,
                )
            )
            return

        for signature in signatures:
            self.list_view.controls.append(self.create_signature_card(signature))

    # =========================================================
    # SEARCH
    # =========================================================

    def search_changed(self, e):
        if not self.database_available:
            return

        search = e.control.value or ""

        self.load_signatures(search)

        self.list_view.update()

    # =========================================================
    # CARD
    # =========================================================

    def create_signature_card(self, signature):
        image_path = self.repository.get_image_path(signature)

        image = ft.Image(
            src=str(image_path),
            width=180,
            height=100,
            fit=ft.BoxFit.CONTAIN,
        )

        # -----------------------------------------------------
        # NAME
        # -----------------------------------------------------

        name_text = ft.Text(
            signature.name,
            size=17,
            weight=ft.FontWeight.BOLD,
        )

        # -----------------------------------------------------
        # TAX ID
        # -----------------------------------------------------

        tax_id_text = ft.Text(
            f"ІПН: {signature.tax_id}",
            size=12,
            color=ft.Colors.GREY_600,
        )

        # -----------------------------------------------------
        # FILE
        # -----------------------------------------------------

        file_text = ft.Text(
            signature.file_name,
            size=12,
            color=ft.Colors.GREY_600,
        )

        created_by_text = ft.Text(
            f"Додав: {signature.created_by or 'Невідомо'}",
            size=12,
            color=ft.Colors.GREY_600,
        )

        # -----------------------------------------------------
        # EDIT
        # -----------------------------------------------------

        edit_button = ft.IconButton(
            icon=ft.Icons.EDIT,
            tooltip="Редагувати",
            on_click=lambda e, s=signature: (self.edit_signature(s)),
            visible=self.can_manage,
        )

        # -----------------------------------------------------
        # ПЕРЕМИКАЧ АКТИВНОСТІ (м'яке видалення / відновлення)
        # -----------------------------------------------------

        toggle_button = ft.IconButton(
            icon=(
                ft.Icons.VISIBILITY_OFF if signature.is_active else ft.Icons.VISIBILITY
            ),
            tooltip="Приховати підпис" if signature.is_active else "Відновити підпис",
            icon_color=ft.Colors.ORANGE if signature.is_active else ft.Colors.GREEN,
            on_click=lambda e, s=signature: self.toggle_signature(s),
            visible=self.can_toggle and (signature.is_active or self.is_admin),
        )

        permanent_delete_button = ft.IconButton(
            icon=ft.Icons.DELETE_FOREVER,
            tooltip="Видалити файл і запис назавжди",
            icon_color=ft.Colors.RED,
            on_click=lambda e, s=signature: self.confirm_permanent_delete(s),
            visible=self.is_admin,
        )

        status_text = ft.Text(
            "Статус: активний" if signature.is_active else "Статус: прихований",
            size=12,
            color=ft.Colors.GREY_600 if signature.is_active else ft.Colors.ORANGE,
        )

        # -----------------------------------------------------
        # CARD
        # -----------------------------------------------------

        return ft.Card(
            content=ft.Container(
                content=ft.Row(
                    controls=[
                        ft.Container(
                            content=image,
                            width=200,
                            alignment=ft.Alignment.CENTER,
                        ),
                        ft.Column(
                            controls=[
                                name_text,
                                tax_id_text,
                                created_by_text,
                                status_text,
                                file_text,
                            ],
                            expand=True,
                            spacing=5,
                        ),
                        edit_button,
                        toggle_button,
                        permanent_delete_button,
                    ],
                    vertical_alignment=(ft.CrossAxisAlignment.CENTER),
                ),
                padding=10,
            )
        )

    # =========================================================
    # ADD
    # =========================================================

    def add_signature(self, e):
        if not self.can_manage:
            return
        if not self.database_available:
            return

        root = tk.Tk()
        root.withdraw()

        try:
            root.attributes("-topmost", True)
        except Exception:
            pass

        file_path = filedialog.askopenfilename(
            title="Виберіть файл підпису",
            filetypes=[
                (
                    "Зображення",
                    "*.png *.jpg *.jpeg *.bmp",
                ),
                (
                    "PNG",
                    "*.png",
                ),
                (
                    "JPEG",
                    "*.jpg *.jpeg",
                ),
                (
                    "BMP",
                    "*.bmp",
                ),
                (
                    "Усі файли",
                    "*.*",
                ),
            ],
        )

        root.destroy()

        if not file_path:
            return

        self.show_signature_dialog(
            title="Додати підпис",
            initial_name="",
            initial_tax_id="",
            callback=lambda name, tax_id: (
                self.save_new_signature(
                    name=name,
                    tax_id=tax_id,
                    file_path=file_path,
                )
            ),
        )

    # =========================================================
    # SAVE NEW
    # =========================================================

    def save_new_signature(
        self,
        name: str,
        tax_id: str,
        file_path: str,
    ):
        if not self.database_available:
            return

        try:
            self.repository.add(
                name=name,
                tax_id=tax_id,
                source_image=file_path,
                created_by=(self.state.current_user or {}).get("username"),
            )

            self.close_dialog()

            self.load_signatures(self.search_field.value or "")

            if not self.database_available:
                return

            self.list_view.update()

            self.show_message("Підпис успішно додано.")

        except Exception as ex:
            print(f"Помилка додавання підпису: {ex}")

            self.set_database_unavailable()

            try:
                self.list_view.update()
            except Exception:
                pass

    # =========================================================
    # EDIT
    # =========================================================

    def edit_signature(self, signature):
        if not self.can_manage:
            return
        if not self.database_available:
            return

        self.show_signature_dialog(
            title="Редагувати підпис",
            initial_name=signature.name,
            initial_tax_id=signature.tax_id,
            callback=lambda name, tax_id: (
                self.save_edited_signature(
                    signature_id=signature.id,
                    name=name,
                    tax_id=tax_id,
                )
            ),
        )

    # =========================================================
    # SAVE EDIT
    # =========================================================

    def save_edited_signature(
        self,
        signature_id: int,
        name: str,
        tax_id: str,
    ):
        if not self.database_available:
            return

        try:
            result = self.repository.update(
                signature_id=signature_id,
                name=name,
                tax_id=tax_id,
            )

            if result is None:
                raise ValueError("Підпис не знайдено.")

            self.close_dialog()

            self.load_signatures(self.search_field.value or "")

            if not self.database_available:
                return

            self.list_view.update()

            self.show_message("Підпис успішно змінено.")

        except ValueError as ex:
            self.show_error(str(ex))

        except Exception as ex:
            print(f"Помилка редагування підпису: {ex}")

            self.set_database_unavailable()

            try:
                self.list_view.update()
            except Exception:
                pass

    # =========================================================
    # SOFT DELETE / RESTORE
    # =========================================================

    def toggle_signature(self, signature):
        if not self.can_toggle or not self.database_available:
            return

        # Неадміністратор може тільки приховувати активні підписи.
        if not self.is_admin and not signature.is_active:
            return

        new_active = not signature.is_active
        action = "відновити" if new_active else "приховати"
        dialog = ft.AlertDialog(
            modal=True,
            title=ft.Text("Зміна доступності підпису"),
            content=ft.Text(
                f"Ви дійсно хочете {action} підпис «{signature.name}»?\n\n"
                + (
                    "Файл залишиться в базі, підпис можна буде відновити."
                    if not new_active
                    else "Підпис знову з'явиться у загальному списку."
                )
            ),
            actions=[
                ft.TextButton("Скасувати", on_click=lambda e: self.close_dialog()),
                ft.Button(
                    "Підтвердити",
                    on_click=lambda e, sid=signature.id, active=new_active: self.set_signature_active(
                        sid, active
                    ),
                ),
            ],
            actions_alignment=ft.MainAxisAlignment.END,
        )
        self.page.show_dialog(dialog)

    def set_signature_active(self, signature_id: int, active: bool):
        if not self.can_toggle or not self.database_available:
            return
        if active and not self.is_admin:
            return

        try:
            if not self.repository.set_active(signature_id, active):
                raise ValueError("Підпис не знайдено.")
            self.close_dialog()
            self.load_signatures(self.search_field.value or "")
            if self.database_available:
                self.list_view.update()
                self.show_message(
                    "Підпис відновлено."
                    if active
                    else "Підпис приховано. Файл збережено."
                )
        except ValueError as ex:
            self.show_error(str(ex))
        except Exception as ex:
            print(f"Помилка зміни статусу підпису: {ex}")
            self.set_database_unavailable()
            try:
                self.list_view.update()
            except Exception:
                pass

    # =========================================================
    # PERMANENT DELETE (ADMIN ONLY)
    # =========================================================

    def confirm_permanent_delete(self, signature):
        if not self.is_admin or not self.database_available:
            return

        dialog = ft.AlertDialog(
            modal=True,
            title=ft.Text("Остаточне видалення"),
            content=ft.Text(
                f"Видалити підпис «{signature.name}» назавжди?\n\n"
                "Буде видалено запис із бази та файл зображення. Відновити його буде неможливо."
            ),
            actions=[
                ft.TextButton("Скасувати", on_click=lambda e: self.close_dialog()),
                ft.Button(
                    "Видалити назавжди",
                    icon=ft.Icons.DELETE_FOREVER,
                    on_click=lambda e, sid=signature.id: self.delete_signature_permanently(
                        sid
                    ),
                ),
            ],
            actions_alignment=ft.MainAxisAlignment.END,
        )
        self.page.show_dialog(dialog)

    def delete_signature_permanently(self, signature_id: int):
        if not self.is_admin or not self.database_available:
            return
        try:
            result = self.repository.delete_permanently(signature_id)
            if not result:
                raise ValueError("Підпис не знайдено.")
            self.close_dialog()
            self.load_signatures(self.search_field.value or "")
            if self.database_available:
                self.list_view.update()
                self.show_message("Підпис і файл остаточно видалено.")
        except ValueError as ex:
            self.show_error(str(ex))
        except Exception as ex:
            print(f"Помилка остаточного видалення підпису: {ex}")
            self.set_database_unavailable()
            try:
                self.list_view.update()
            except Exception:
                pass

    # Залишено для сумісності зі старими викликами: звичайне видалення лише приховує.
    def delete_signature(self, signature_id: int):
        if not self.can_manage or not self.database_available:
            return
        try:
            if not self.repository.set_active(signature_id, False):
                raise ValueError("Підпис не знайдено.")
            self.close_dialog()
            self.load_signatures(self.search_field.value or "")
            if self.database_available:
                self.list_view.update()
                self.show_message("Підпис приховано. Файл збережено.")
        except ValueError as ex:
            self.show_error(str(ex))
        except Exception as ex:
            print(f"Помилка приховування підпису: {ex}")
            self.set_database_unavailable()
            try:
                self.list_view.update()
            except Exception:
                pass

    # =========================================================
    # SIGNATURE DIALOG
    # =========================================================

    def show_signature_dialog(
        self,
        title: str,
        initial_name: str,
        initial_tax_id: str,
        callback,
    ):
        """
        Загальне вікно створення/редагування підпису.

        Обов'язкові поля:
        - ПІБ
        - ІПН
        """

        if not self.database_available:
            return

        # -----------------------------------------------------
        # NAME
        # -----------------------------------------------------

        name_field = ft.TextField(
            label="ПІБ",
            value=initial_name,
            autofocus=True,
            expand=True,
        )

        # -----------------------------------------------------
        # TAX ID
        # -----------------------------------------------------

        tax_id_field = ft.TextField(
            label="ІПН",
            value=initial_tax_id,
            hint_text="Введіть ІПН",
            max_length=20,
            keyboard_type=ft.KeyboardType.NUMBER,
            expand=True,
        )

        # -----------------------------------------------------
        # SAVE
        # -----------------------------------------------------

        def save(e):
            if not self.database_available:
                self.close_dialog()
                return

            # ---------------------------------------------
            # ПІБ
            # ---------------------------------------------

            name = (name_field.value or "").strip()

            if not name:
                name_field.error_text = "Введіть ПІБ."

                name_field.update()

                return

            # ---------------------------------------------
            # ІПН
            # ---------------------------------------------

            tax_id = (tax_id_field.value or "").strip()

            if not tax_id:
                tax_id_field.error_text = "Введіть ІПН."

                tax_id_field.update()

                return

            # ---------------------------------------------
            # Перевірка ІПН
            # ---------------------------------------------

            if not tax_id.isdigit():
                tax_id_field.error_text = "ІПН повинен містити тільки цифри."

                tax_id_field.update()

                return

            # ---------------------------------------------
            # Передаємо дані далі
            # ---------------------------------------------

            callback(
                name,
                tax_id,
            )

        # -----------------------------------------------------
        # DIALOG
        # -----------------------------------------------------

        dialog = ft.AlertDialog(
            modal=True,
            title=ft.Text(title),
            content=ft.Container(
                content=ft.Column(
                    controls=[
                        name_field,
                        tax_id_field,
                    ],
                    spacing=15,
                    tight=True,
                ),
                width=450,
            ),
            actions=[
                ft.TextButton(
                    "Скасувати",
                    on_click=lambda e: (self.close_dialog()),
                ),
                ft.Button(
                    "Зберегти",
                    icon=ft.Icons.SAVE,
                    on_click=save,
                ),
            ],
            actions_alignment=(ft.MainAxisAlignment.END),
        )

        self.page.show_dialog(dialog)

    # =========================================================
    # ERROR
    # =========================================================

    def show_error(self, message: str):
        dialog = ft.AlertDialog(
            modal=True,
            title=ft.Text("Помилка"),
            content=ft.Text(message),
            actions=[
                ft.TextButton(
                    "Закрити",
                    on_click=lambda e: (self.close_dialog()),
                ),
            ],
        )

        self.page.show_dialog(dialog)

    # =========================================================
    # MESSAGE
    # =========================================================

    def show_message(self, message: str):
        self.page.show_dialog(ft.SnackBar(content=ft.Text(message)))

    # =========================================================
    # CLOSE DIALOG
    # =========================================================

    def close_dialog(self):
        try:
            self.page.pop_dialog()
        except Exception:
            pass

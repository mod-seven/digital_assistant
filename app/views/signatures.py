import tkinter as tk
from tkinter import filedialog

import flet as ft

from app.repositories.signatures import SignaturesRepository


class SignaturesView:
    def __init__(self, page: ft.Page, state):
        self.page = page
        self.state = state

        self.repository: SignaturesRepository = state.signatures_repository

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
            signatures = self.repository.search(search)

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

        # -----------------------------------------------------
        # EDIT
        # -----------------------------------------------------

        edit_button = ft.IconButton(
            icon=ft.Icons.EDIT,
            tooltip="Редагувати",
            on_click=lambda e, s=signature: (self.edit_signature(s)),
        )

        # -----------------------------------------------------
        # DELETE
        # -----------------------------------------------------

        delete_button = ft.IconButton(
            icon=ft.Icons.DELETE,
            tooltip="Видалити",
            icon_color=ft.Colors.RED,
            on_click=lambda e, s=signature: (self.confirm_delete(s)),
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
                                file_text,
                            ],
                            expand=True,
                            spacing=5,
                        ),
                        edit_button,
                        delete_button,
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
    # DELETE CONFIRMATION
    # =========================================================

    def confirm_delete(self, signature):
        if not self.database_available:
            return

        dialog = ft.AlertDialog(
            modal=True,
            title=ft.Text("Видалення підпису"),
            content=ft.Text(
                f"Ви дійсно хочете видалити підпис\n" f"«{signature.name}»?"
            ),
            actions=[
                ft.TextButton(
                    "Скасувати",
                    on_click=lambda e: (self.close_dialog()),
                ),
                ft.Button(
                    "Видалити",
                    icon=ft.Icons.DELETE,
                    on_click=lambda e: (self.delete_signature(signature.id)),
                ),
            ],
            actions_alignment=(ft.MainAxisAlignment.END),
        )

        self.page.show_dialog(dialog)

    # =========================================================
    # DELETE
    # =========================================================

    def delete_signature(
        self,
        signature_id: int,
    ):
        if not self.database_available:
            return

        try:
            result = self.repository.delete(signature_id)

            if not result:
                raise ValueError("Підпис не знайдено.")

            self.close_dialog()

            self.load_signatures(self.search_field.value or "")

            if not self.database_available:
                return

            self.list_view.update()

            self.show_message("Підпис видалено.")

        except ValueError as ex:
            self.show_error(str(ex))

        except Exception as ex:
            print(f"Помилка видалення підпису: {ex}")

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

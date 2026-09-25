from datetime import datetime

import flet as ft

from app.components.sidebar import Sidebar
from app.constants import TableHeader
from app.services.report_generation import ReportGeneration
from app.state import AppState
from app.styles import (
    BG_COLOR,
    BORDER,
    CARD_RADIUS,
    CONTENT_PADDING,
    PRIMARY,
    TEXT,
    TEXT_SECONDARY,
    WHITE,
)


class ReportsView:

    def __init__(self, page: ft.Page, state: AppState):
        self.page = page
        self.state = state

        self.report_type = None

        self.report_type_dropdown = None
        self.form_container = None

    def build(self):

        self.report_type_dropdown = ft.Dropdown(
            label="Тип рапорту",
            hint_text="Оберіть тип рапорту",
            options=[
                ft.DropdownOption(
                    key="report_over_position",
                    text="Рапорт посаду здав",
                ),
                ft.DropdownOption(
                    key="report_accepted_position",
                    text="Рапорт посаду прийняв",
                ),
            ],
            on_select=self.report_type_changed,
        )

        self.form_container = ft.Container(
            content=self.empty_form(),
            expand=True,
        )

        content = ft.Column(
            controls=[
                ft.Text(
                    "Рапорти",
                    size=28,
                    weight=ft.FontWeight.BOLD,
                    color=TEXT,
                ),
                ft.Text(
                    "Створення та генерація службових документів",
                    size=14,
                    color=TEXT_SECONDARY,
                ),
                ft.Container(
                    content=self.report_type_dropdown,
                    padding=20,
                    bgcolor=WHITE,
                    border_radius=CARD_RADIUS,
                ),
                self.form_container,
            ],
            spacing=20,
            expand=True,
        )

        return ft.Row(
            controls=[
                Sidebar(self.page).build(),
                ft.Container(
                    content=content,
                    expand=True,
                    padding=CONTENT_PADDING,
                    bgcolor=BG_COLOR,
                ),
            ],
            expand=True,
        )

    # ---------------------------------------------------------
    # ЗМІНА ТИПУ РАПОРТУ
    # ---------------------------------------------------------

    def report_type_changed(self, e):

        self.report_type = e.control.value

        if self.report_type == "report_over_position":
            self.form_container.content = self.report_over_position_form()

        elif self.report_type == "report_accepted_position":
            self.form_container.content = self.report_accepted_position_form()

        self.page.update()

    # ---------------------------------------------------------
    # ПУСТА ФОРМА
    # ---------------------------------------------------------

    def empty_form(self):

        return ft.Container(
            content=ft.Column(
                controls=[
                    ft.Icon(
                        ft.Icons.DESCRIPTION_OUTLINED,
                        size=50,
                        color=TEXT_SECONDARY,
                    ),
                    ft.Text(
                        "Оберіть тип рапорту",
                        size=18,
                        weight=ft.FontWeight.BOLD,
                        color=TEXT,
                    ),
                    ft.Text(
                        "Після вибору типу тут з'являться " "необхідні параметри.",
                        color=TEXT_SECONDARY,
                    ),
                ],
                horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                alignment=ft.MainAxisAlignment.CENTER,
            ),
            expand=True,
        )

    # ---------------------------------------------------------
    # ЗАГАЛЬНІ ПОЛЯ
    # ---------------------------------------------------------

    def tax_id_changed(self, e):
        search = e.control.value.strip().lower()

        self.person_suggestions.controls.clear()

        if not search:
            self.person_suggestions.visible = False
            self.person_suggestions.update()
            return

        df = self.state.df

        if df is None or df.empty:
            self.person_suggestions.visible = False
            self.person_suggestions.update()
            return

        full_name = df[TableHeader.FULL_NAME].fillna("").astype(str)

        tax_id = df[TableHeader.TAX_ID].fillna("").astype(str)

        rows = (
            df[
                full_name.str.lower().str.contains(search, na=False)
                | tax_id.str.lower().str.contains(search, na=False)
            ]
            .drop_duplicates(subset=[TableHeader.TAX_ID])
            .head(20)
        )

        for _, row in rows.iterrows():

            name = str(row[TableHeader.FULL_NAME])
            person_tax_id = str(row[TableHeader.TAX_ID])

            self.person_suggestions.controls.append(
                ft.ListTile(
                    title=ft.Text(name),
                    subtitle=ft.Text(f"РНОКПП: {person_tax_id}"),
                    on_click=lambda e, tax_id=person_tax_id, name=name: self.person_selected(
                        tax_id, name
                    ),
                )
            )

        self.person_suggestions.visible = len(rows) > 0
        self.person_suggestions.update()

    def person_selected(self, tax_id, name):

        self.selected_tax_id = tax_id
        self.tax_id.value = name

        self.person_suggestions.controls.clear()
        self.person_suggestions.visible = False
        self.person_suggestions.update()

        self.page.update()

    def person_fields(self):

        self.selected_tax_id = None

        self.tax_id = ft.AutoComplete(
            value="",
            suggestions=[],
            suggestions_max_height=300,
            on_change=self.tax_id_changed,
            expand=True,
        )

        self.person_suggestions = ft.ListView(
            spacing=0,
            height=200,
            visible=False,
        )

        return [
            ft.Column(
                controls=[
                    ft.Row(
                        controls=[
                            ft.Text("Військовослужбовець"),
                            self.tax_id,
                        ],
                        spacing=10,
                    ),
                    self.person_suggestions,
                ],
                spacing=0,
                expand=True,
            ),
        ]

    def report_over_position_form(self):

        self.date_report = ft.TextField(
            label="Дата рапорту",
            hint_text="ДД.ММ.РРРР",
            value=datetime.now().strftime("%d.%m.%Y"),
            expand=True,
        )

        return self.form_card(
            title="Рапорт посаду здав",
            controls=[
                *self.person_fields(),
                ft.Divider(
                    color=BORDER,
                ),
                ft.Row(
                    controls=[
                        self.date_report,
                    ],
                ),
                self.action_buttons(),
            ],
        )

    def report_accepted_position_form(self):
        self.position_code = ft.TextField(
            label="Код посади (Імпульс)",
            hint_text="00000000",
            expand=True,
        )

        self.order_name = ft.TextField(
            label="Наказ по особовому складу",
            hint_text="Командира військової частини А7379",
            expand=True,
        )

        self.oder_number = ft.TextField(
            label="Номер наказу по особовому складу",
            hint_text="№",
            expand=True,
        )

        self.oder_date = ft.TextField(
            label="Дата наказу по особовому складу",
            hint_text="ДД.ММ.РРРР",
            value=datetime.now().strftime("%d.%m.%Y"),
            expand=True,
        )

        self.date_report = ft.TextField(
            label="Дата рапорту",
            hint_text="ДД.ММ.РРРР",
            value=datetime.now().strftime("%d.%m.%Y"),
            expand=True,
        )

        return self.form_card(
            title="Рапорт посаду прийняв",
            controls=[
                *self.person_fields(),
                ft.Row(
                    controls=[
                        self.position_code,
                    ],
                ),
                ft.Divider(
                    color=BORDER,
                ),
                ft.Row(
                    controls=[
                        self.order_name,
                        self.oder_number,
                        self.oder_date,
                    ],
                ),
                ft.Row(
                    controls=[
                        self.date_report,
                    ],
                ),
                self.action_buttons(),
            ],
        )

    # ---------------------------------------------------------
    # КАРТКА ФОРМИ
    # ---------------------------------------------------------

    def form_card(self, title, controls):

        return ft.Container(
            content=ft.Column(
                controls=[
                    ft.Text(
                        title,
                        size=20,
                        weight=ft.FontWeight.BOLD,
                        color=TEXT,
                    ),
                    ft.Divider(
                        color=BORDER,
                    ),
                    *controls,
                ],
                spacing=15,
            ),
            padding=25,
            bgcolor=WHITE,
            border_radius=CARD_RADIUS,
            expand=True,
        )

    # ---------------------------------------------------------
    # КНОПКИ
    # ---------------------------------------------------------

    def action_buttons(self):

        return ft.Row(
            controls=[
                ft.Button(
                    "Очистити",
                    icon=ft.Icons.CLEAR,
                    on_click=self.clear_form,
                ),
                ft.Button(
                    "Згенерувати рапорт",
                    icon=ft.Icons.DESCRIPTION,
                    on_click=self.generate_report,
                ),
            ],
            alignment=ft.MainAxisAlignment.END,
        )

    # ---------------------------------------------------------
    # ОЧИСТИТИ
    # ---------------------------------------------------------

    def clear_form(self, e):

        self.page.controls.clear()

        from app.router import AppRouter

        AppRouter(
            self.page,
            self.state,
        ).route_change()

    # ---------------------------------------------------------
    # ГЕНЕРАЦІЯ
    # ---------------------------------------------------------

    async def generate_report(self, e):
        file_picker = ft.FilePicker()

        file_path = await file_picker.save_file(
            dialog_title="Зберегти рапорт",
            file_name=f"{self.report_type_dropdown.text}_{self.tax_id.value}.docx",
            file_type=ft.FilePickerFileType.CUSTOM,
            allowed_extensions=["docx"],
        )

        if not file_path:
            return

        try:
            report_generation = ReportGeneration(
                repository=self.state.personnel_repository,
                path_save_report=file_path,
            )

            if self.report_type == "report_over_position":
                context = report_generation.get_context_report_over_position(
                    tax_id=self.selected_tax_id,
                    date_raport=self.date_report.value,
                )

            elif self.report_type == "report_accepted_position":
                context = report_generation.get_context_report_accepted_position(
                    position_code=self.position_code.value,
                    order_name=self.order_name.value,
                    oder_number=self.oder_number.value,
                    oder_date=datetime.strptime(
                        self.oder_date.value.strip(), "%d.%m.%Y"
                    ),
                    tax_id=self.selected_tax_id,
                    date_raport=self.date_report.value,
                )

            report_generation.generate_reports(contexts=[context])

            self.show_message(f"Рапорт збережено:\n{file_path}")

        except Exception as ex:
            self.show_message(f"Помилка генерації рапорту: {ex}")

    # ---------------------------------------------------------
    # ПОВІДОМЛЕННЯ
    # ---------------------------------------------------------

    def show_message(self, message):

        dialog = ft.AlertDialog(
            title=ft.Text("Рапорт"),
            content=ft.Text(message),
        )

        self.page.show_dialog(dialog)

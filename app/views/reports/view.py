import flet as ft

from app.constants import ReportType
from app.services.report_generation import ReportGeneration
from app.state import AppState
from app.styles import BG_COLOR, CONTENT_PADDING, TEXT, TEXT_SECONDARY, WHITE
from app.views.reports import (
    accepted_position,
    free_theme,
    from_file,
    over_position,
    ozdorovlennya,
    shhorichnu_vidpustku,
)
from app.views.reports.common import empty_form, person_selected, tax_id_changed


class ReportsView:

    def __init__(self, page: ft.Page, state: AppState):
        self.page = page
        self.state = state

        self.report_type = None
        self.tax_id = None
        self.person = {}

        self.report_type_dropdown = None
        self.form_container = None
        self.report_file_data = None

    def build(self):
        self.report_type_dropdown = ft.Dropdown(
            label="Тип рапорту",
            hint_text="Оберіть тип рапорту",
            options=[
                ft.DropdownOption(
                    key=ReportType.REPORT_OVER_POSITION.name,
                    text=ReportType.REPORT_OVER_POSITION.value,
                ),
                ft.DropdownOption(
                    key=ReportType.REPORT_ACCEPTED_POSITION.name,
                    text=ReportType.REPORT_ACCEPTED_POSITION.value,
                ),
                ft.DropdownOption(
                    key=ReportType.REPOST_SHHORICHNU_VIDPUSTKU.name,
                    text=ReportType.REPOST_SHHORICHNU_VIDPUSTKU.value,
                ),
                ft.DropdownOption(
                    key=ReportType.REPOST_OZDOROVLENNYA.name,
                    text=ReportType.REPOST_OZDOROVLENNYA.value,
                ),
                ft.DropdownOption(
                    key=ReportType.REPOST_FREE_THEME.name,
                    text=ReportType.REPOST_FREE_THEME.value,
                ),
                ft.DropdownOption(
                    key=ReportType.REPOSTS_FFROM_FILE.name,
                    text=ReportType.REPOSTS_FFROM_FILE.value,
                ),
            ],
            on_select=self.report_type_changed,
        )

        self.form_container = ft.Container(
            content=empty_form(),
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
                ),
                self.form_container,
            ],
            spacing=20,
            expand=True,
        )

        return ft.Row(
            controls=[
                ft.Container(
                    content=content,
                    expand=True,
                    padding=CONTENT_PADDING,
                    bgcolor=BG_COLOR,
                ),
            ],
            expand=True,
        )

    def report_type_changed(self, e):
        self.report_type = e.control.value

        forms = {
            ReportType.REPORT_OVER_POSITION.name: over_position.build,
            ReportType.REPORT_ACCEPTED_POSITION.name: accepted_position.build,
            ReportType.REPOSTS_FFROM_FILE.name: from_file.build,
            ReportType.REPOST_OZDOROVLENNYA.name: ozdorovlennya.build,
            ReportType.REPOST_SHHORICHNU_VIDPUSTKU.name: shhorichnu_vidpustku.build,
            ReportType.REPOST_FREE_THEME.name: free_theme.build,
        }

        form_builder = forms.get(self.report_type)

        if form_builder:
            self.form_container.content = form_builder(self)
        else:
            self.form_container.content = empty_form()

        self.page.update()

    def tax_id_changed(self, e):
        tax_id_changed(self, e)

    def person_selected(self, tax_id, name):
        person_selected(self, tax_id, name)

    def clear_form(self, e):
        self.page.controls.clear()

        from app.router import AppRouter

        AppRouter(
            self.page,
            self.state,
        ).route_change()

    async def generate_report(self, e):
        file_picker = ft.FilePicker()

        file_path = await file_picker.save_file(
            dialog_title="Зберегти рапорт",
            file_name=(
                f"{self.report_type_dropdown.text}_"
                f"{self.tax_id.value if self.tax_id else ''}.docx"
            ),
            file_type=ft.FilePickerFileType.CUSTOM,
            allowed_extensions=["docx"],
        )

        if not file_path:
            return

        try:
            contexts = []

            report_generation = ReportGeneration(
                repository=self.state.personnel_repository,
                path_save_report=file_path,
            )

            if self.report_type == ReportType.REPORT_OVER_POSITION.name:
                context = report_generation.get_context_report_over_position(
                    tax_id=self.selected_tax_id,
                    date_raport=self.date_report.value,
                )
                contexts.append(context)

            elif self.report_type == ReportType.REPORT_ACCEPTED_POSITION.name:
                context = report_generation.get_context_report_accepted_position(
                    position_code=self.position_code.value,
                    order_name=self.order_name.value,
                    oder_number=self.oder_number.value,
                    oder_date=self.oder_date.value.strip(),
                    tax_id=self.selected_tax_id,
                    date_raport=self.date_report.value,
                )
                contexts.append(context)

            elif self.report_type == ReportType.REPOSTS_FFROM_FILE.name:
                contexts = report_generation.get_contexts(
                    file_data=self.report_file_data
                )

            elif self.report_type == ReportType.REPOST_OZDOROVLENNYA.name:
                context = report_generation.get_context_ozdorovlennya(
                    tax_id=self.selected_tax_id,
                    year=self.year.value,
                )
                contexts.append(context)

            elif self.report_type == ReportType.REPOST_SHHORICHNU_VIDPUSTKU.name:
                context = report_generation.get_shhorichnu_vidpustku(
                    tax_id=self.selected_tax_id,
                    tvo_tax_id=self.tvo_tax_id.value,
                    star_data=self.star_data.value,
                    year=self.year.value,
                    days=int(self.days.value),
                    roud_days=self.roud_days.value,
                    adress=self.adress.value,
                    phone=self.phone.value,
                    date_raport=self.date_report.value,
                )
                contexts.append(context)

            elif self.report_type == ReportType.REPOST_FREE_THEME.name:
                context = report_generation.get_context_free_theme(
                    tax_id=self.selected_tax_id,
                    date_raport=self.date_report.value,
                )
                contexts.append(context)

            report_generation.generate_reports(contexts=contexts)

            self.show_message(f"Рапорт збережено:{file_path}")

        except Exception as ex:
            self.show_message(f"Помилка генерації рапорту: {ex}")

    def show_message(self, message):
        dialog = ft.AlertDialog(
            title=ft.Text("Рапорт"),
            content=ft.Text(message),
        )

        self.page.show_dialog(dialog)

    def select_report_excel(self, e):
        from_file.select_report_excel(self, e)

    async def select_report_download_excel(self, e):
        await from_file.select_report_download_excel(self, e)

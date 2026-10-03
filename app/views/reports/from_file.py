from pathlib import Path

import flet as ft

from app.services.report_file import ReportFile
from app.styles import (
    BORDER,
    CARD_RADIUS,
    PRIMARY,
    SUCCESS,
    TEXT,
    TEXT_SECONDARY,
    WHITE,
)
from app.views.reports.common import action_buttons


def build(view):
    view.report_excel_file = None

    view.report_excel_name = ft.Text(
        "Файл з даними для рапртів не вибраний",
        color=TEXT_SECONDARY,
    )

    view.report_excel_status = ft.Text(
        "Завантажте Excel з параметрами для рапортів",
        color=TEXT_SECONDARY,
    )

    view.report_excel_button = ft.Button(
        "Завантажити Excel",
        icon=ft.Icons.UPLOAD_FILE,
        on_click=view.select_report_excel,
    )

    view.report_download_excel_button = ft.Button(
        "Імпорт шаблон Excel",
        icon=ft.Icons.FILE_DOWNLOAD_OUTLINED,
        on_click=view.select_report_download_excel,
    )

    return ft.Container(
        content=ft.Column(
            controls=[
                ft.Text(
                    "Рапорти",
                    size=22,
                    weight=ft.FontWeight.BOLD,
                    color=TEXT,
                ),
                ft.Divider(color=BORDER),
                ft.Text(
                    "Параметри рапортів",
                    size=18,
                    weight=ft.FontWeight.BOLD,
                    color=TEXT,
                ),
                ft.Container(
                    content=ft.Column(
                        controls=[
                            ft.Icon(
                                ft.Icons.TABLE_VIEW_OUTLINED,
                                size=45,
                                color=PRIMARY,
                            ),
                            ft.Text(
                                "Excel-файл з даними для рапортів",
                                size=16,
                                weight=ft.FontWeight.BOLD,
                            ),
                            view.report_excel_name,
                            view.report_excel_status,
                            view.report_excel_button,
                            view.report_download_excel_button,
                        ],
                        horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                        spacing=10,
                    ),
                    padding=30,
                    bgcolor=WHITE,
                    border_radius=CARD_RADIUS,
                    border=ft.Border.all(1, BORDER),
                ),
                action_buttons(view),
            ],
            spacing=20,
        ),
        padding=25,
        bgcolor=WHITE,
        border_radius=CARD_RADIUS,
        expand=True,
    )


def select_report_excel(view, e):
    import tkinter as tk
    from tkinter import filedialog

    root = tk.Tk()
    root.withdraw()

    file_path = filedialog.askopenfilename(
        title="Виберіть Excel з параметрами рапортів",
        filetypes=[
            ("Excel files", "*.xlsx"),
        ],
    )

    root.destroy()

    if not file_path:
        return

    view.report_excel_file = file_path
    view.report_excel_name.value = Path(file_path).name
    view.report_excel_status.value = "Excel успішно завантажено"
    view.report_excel_status.color = SUCCESS

    report_file = ReportFile()
    view.report_file_data = report_file.load_excel(filename=file_path)

    view.page.update()


async def select_report_download_excel(view, e):
    file_picker = ft.FilePicker()

    file_path = await file_picker.save_file(
        dialog_title="Зберегти шаблон",
        file_name="Шаблон_генерації_рапортів.xlsx",
        file_type=ft.FilePickerFileType.CUSTOM,
        allowed_extensions=["xlsx"],
    )

    if not file_path:
        return

    report_file = ReportFile()
    report_file.create_excel_template(filename=file_path)

    view.show_message(f"Рапорт збережено:{file_path}")

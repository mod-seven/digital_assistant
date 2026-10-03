from datetime import datetime

import flet as ft

from app.styles import BORDER
from app.views.reports.common import action_buttons, form_card, person_fields


def build(view):
    view.position_code = ft.TextField(
        label="Код посади (Імпульс)",
        hint_text="00000000",
        expand=True,
    )

    view.order_name = ft.TextField(
        label="Наказ по особовому складу",
        hint_text="Командира військової частини А7379",
        expand=True,
    )

    view.oder_number = ft.TextField(
        label="Номер наказу по особовому складу",
        hint_text="№",
        expand=True,
    )

    view.oder_date = ft.TextField(
        label="Дата наказу по особовому складу",
        hint_text="ДД.ММ.РРРР",
        expand=True,
    )

    view.date_report = ft.TextField(
        label="Дата рапорту",
        hint_text="ДД.ММ.РРРР",
        value=datetime.now().strftime("%d.%m.%Y"),
        expand=True,
    )

    return form_card(
        title="Рапорт посаду прийняв",
        controls=[
            *person_fields(view),
            ft.Row(
                controls=[
                    view.position_code,
                ],
            ),
            ft.Divider(color=BORDER),
            ft.Row(
                controls=[
                    view.order_name,
                    view.oder_number,
                    view.oder_date,
                ],
            ),
            ft.Row(
                controls=[
                    view.date_report,
                ],
            ),
            action_buttons(view),
        ],
    )

from datetime import datetime

import flet as ft

from app.views.reports.common import action_buttons, form_card, person_fields


def build(view):
    view.year = ft.TextField(
        label="Рік",
        hint_text="2026",
        value=datetime.now().strftime("%Y"),
        expand=True,
    )

    view.date_report = ft.TextField(
        label="Дата рапорту",
        hint_text="ДД.ММ.РРРР",
        value=datetime.now().strftime("%d.%m.%Y"),
        expand=True,
    )

    return form_card(
        title="Рапорт на оздоровчі",
        controls=[
            *person_fields(view),
            ft.Row(
                controls=[
                    view.year,
                    view.date_report,
                ],
            ),
            action_buttons(view),
        ],
    )

from datetime import datetime

import flet as ft

from app.styles import BORDER
from app.views.reports.common import action_buttons, form_card, person_fields


def build(view):
    view.date_report = ft.TextField(
        label="Дата рапорту",
        hint_text="ДД.ММ.РРРР",
        value=datetime.now().strftime("%d.%m.%Y"),
        expand=True,
    )

    return form_card(
        title="Рапорт на вільну тему",
        controls=[
            *person_fields(view),
            ft.Divider(color=BORDER),
            ft.Row(
                controls=[
                    view.date_report,
                ],
            ),
            action_buttons(view),
        ],
    )

from datetime import datetime

import flet as ft

from app.styles import BORDER
from app.views.reports.common import action_buttons, form_card, person_fields


def build(view):
    view.year = ft.TextField(
        label="Рік",
        hint_text="2026",
        value=datetime.now().strftime("%Y"),
        expand=True,
    )

    view.days = ft.TextField(
        label="Кількість днів відпустки",
        expand=True,
    )

    view.roud_days = ft.TextField(
        label="Кількість днів на дорогу",
        expand=True,
    )

    view.adress = ft.TextField(
        label="Адреса",
        expand=True,
    )

    view.phone = ft.TextField(
        label="Телефон",
        hint_text="+380000000000",
        expand=True,
    )

    view.tvo_tax_id = ft.TextField(
        label="ТВО (ІПН)",
        expand=True,
    )

    view.star_data = ft.TextField(
        label="Дата початку відпустки",
        hint_text="ДД.ММ.РРРР",
        value=datetime.now().strftime("%d.%m.%Y"),
        expand=True,
    )

    view.date_report = ft.TextField(
        label="Дата рапорту",
        hint_text="ДД.ММ.РРРР",
        value=datetime.now().strftime("%d.%m.%Y"),
        expand=True,
    )

    return form_card(
        title="Рапорт на щорічну основну відпустку",
        controls=[
            *person_fields(view),
            ft.Row(
                controls=[
                    view.star_data,
                    view.days,
                    view.roud_days,
                    view.year,
                ],
            ),
            ft.Divider(color=BORDER),
            ft.Row(
                controls=[
                    view.adress,
                    view.phone,
                    view.tvo_tax_id,
                    view.date_report,
                ],
            ),
            action_buttons(view),
        ],
    )

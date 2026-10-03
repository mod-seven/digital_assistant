import flet as ft

from app.constants import TableHeader
from app.styles import BORDER, CARD_RADIUS, TEXT, TEXT_SECONDARY, WHITE


def empty_form():
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
                    "Після вибору типу тут з'являться необхідні параметри.",
                    color=TEXT_SECONDARY,
                ),
            ],
            horizontal_alignment=ft.CrossAxisAlignment.CENTER,
            alignment=ft.MainAxisAlignment.CENTER,
        ),
        expand=True,
    )


def form_card(title, controls):
    return ft.Container(
        content=ft.Column(
            controls=[
                ft.Text(
                    title,
                    size=20,
                    weight=ft.FontWeight.BOLD,
                    color=TEXT,
                ),
                ft.Divider(color=BORDER),
                *controls,
            ],
            spacing=15,
        ),
        padding=25,
        bgcolor=WHITE,
        border_radius=CARD_RADIUS,
        expand=True,
    )


def action_buttons(view):
    return ft.Row(
        controls=[
            ft.Button(
                "Очистити",
                icon=ft.Icons.CLEAR,
                on_click=view.clear_form,
            ),
            ft.Button(
                "Згенерувати рапорт",
                icon=ft.Icons.DESCRIPTION,
                on_click=view.generate_report,
            ),
        ],
        alignment=ft.MainAxisAlignment.END,
    )


def person_fields(view):
    view.selected_tax_id = None

    view.tax_id = ft.AutoComplete(
        value="",
        suggestions=[],
        suggestions_max_height=300,
        on_change=view.tax_id_changed,
        expand=True,
    )

    view.person_suggestions = ft.ListView(
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
                        view.tax_id,
                    ],
                    spacing=10,
                ),
                view.person_suggestions,
            ],
            spacing=0,
            expand=True,
        ),
    ]


def tax_id_changed(view, e):
    search = e.control.value.strip().lower()

    view.person_suggestions.controls.clear()

    if not search:
        view.person_suggestions.visible = False
        view.person_suggestions.update()
        return

    df = view.state.df

    if df is None or df.empty:
        view.person_suggestions.visible = False
        view.person_suggestions.update()
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

        view.person_suggestions.controls.append(
            ft.ListTile(
                title=ft.Text(name),
                subtitle=ft.Text(f"РНОКПП: {person_tax_id}"),
                on_click=lambda e, tax_id=person_tax_id, name=name: view.person_selected(
                    tax_id, name
                ),
            )
        )

    view.person_suggestions.visible = len(rows) > 0
    view.person_suggestions.update()


def person_selected(view, tax_id, name):
    view.selected_tax_id = tax_id
    view.tax_id.value = name

    view.person_suggestions.controls.clear()
    view.person_suggestions.visible = False
    view.person_suggestions.update()

    view.page.update()

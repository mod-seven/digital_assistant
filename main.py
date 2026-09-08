from pathlib import Path

import flet as ft
import pandas as pd

# ============================================================
# STATE
# ============================================================


class AppState:
    def __init__(self):
        self.file_path = None
        self.file_name = None

        # Всі Excel-аркуші
        # {
        #     "Штат": DataFrame,
        #     "Посади": DataFrame,
        # }
        self.sheets = {}

        # Основний DataFrame
        self.df = None

        self.imported = False


state = AppState()


# ============================================================
# MAIN
# ============================================================


def main(page: ft.Page):

    # --------------------------------------------------------
    # WINDOW
    # --------------------------------------------------------

    page.title = "Мій додаток"

    page.window.width = 1400
    page.window.height = 850

    page.bgcolor = "#F5F7FA"

    page.padding = 0

    # --------------------------------------------------------
    # FILE PICKER
    # --------------------------------------------------------

    file_picker = ft.FilePicker()

    page.overlay.append(file_picker)

    # --------------------------------------------------------
    # MAIN CONTENT
    # --------------------------------------------------------

    content = ft.Container(
        expand=True,
        padding=30,
    )

    # ========================================================
    # MESSAGE
    # ========================================================

    def show_message(text):

        page.snack_bar = ft.SnackBar(content=ft.Text(text))

        page.snack_bar.open = True

        page.update()

    # ========================================================
    # FORMAT VALUE
    # ========================================================

    def format_value(value):

        if pd.isna(value):
            return ""

        if isinstance(value, pd.Timestamp):
            return value.strftime("%d.%m.%Y")

        return str(value)

    # ========================================================
    # NORMALIZE DATES
    # ========================================================

    def normalize_dates(df):

        df = df.copy()

        for column in df.columns:

            name = str(column).lower()

            if "дата" in name:

                try:

                    df[column] = pd.to_datetime(
                        df[column],
                        errors="coerce",
                        dayfirst=True,
                    )

                except Exception:
                    pass

        return df

    # ========================================================
    # IMPORT EXCEL
    # ========================================================

    def import_excel(file_path):

        try:

            path = Path(file_path)

            # Читаємо всі аркуші Excel
            sheets = pd.read_excel(
                path,
                sheet_name=None,
                engine="openpyxl",
            )

            state.file_path = path
            state.file_name = path.name

            state.sheets = {}

            # Обробляємо кожен аркуш
            for sheet_name, df in sheets.items():

                df = normalize_dates(df)

                state.sheets[sheet_name] = df

            # Перший аркуш робимо основним
            if state.sheets:

                first_sheet = list(state.sheets.keys())[0]

                state.df = state.sheets[first_sheet]

            else:

                state.df = None

            state.imported = True

            show_message(f"Файл успішно імпортовано: {path.name}")

            show_home()

        except Exception as error:

            show_message(f"Помилка імпорту: {error}")

    # ========================================================
    # SELECT EXCEL FILE
    # ========================================================

    async def select_file(e=None):

        files = await file_picker.pick_files(
            allow_multiple=False,
            allowed_extensions=["xlsx"],
        )

        if not files:
            return

        selected_file = files[0]

        if not selected_file.path:

            show_message("Не вдалося отримати шлях до файлу.")

            return

        import_excel(selected_file.path)

    # ========================================================
    # COUNT DATES
    # ========================================================

    def count_dates():

        if state.df is None:
            return 0

        total = 0

        for column in state.df.columns:

            if "дата" in str(column).lower():

                total += state.df[column].notna().sum()

        return total

    # ========================================================
    # STATISTIC CARD
    # ========================================================

    def statistic_card(
        title,
        value,
        icon,
    ):

        return ft.Container(
            expand=True,
            bgcolor="#FFFFFF",
            padding=20,
            border_radius=10,
            content=ft.Row(
                [
                    ft.Container(
                        width=50,
                        height=50,
                        bgcolor="#EAF2FF",
                        border_radius=10,
                        alignment=ft.Alignment(
                            0,
                            0,
                        ),
                        content=ft.Icon(
                            icon,
                            color="#1677FF",
                            size=26,
                        ),
                    ),
                    ft.Column(
                        [
                            ft.Text(
                                title,
                                size=13,
                                color="#667085",
                            ),
                            ft.Text(
                                str(value),
                                size=25,
                                weight=ft.FontWeight.BOLD,
                                color="#101828",
                            ),
                        ],
                        spacing=3,
                    ),
                ],
                spacing=15,
            ),
        )

    # ========================================================
    # MENU BUTTON
    # ========================================================

    def menu_button(
        title,
        icon,
        callback,
    ):

        return ft.Container(
            padding=12,
            border_radius=8,
            ink=True,
            on_click=callback,
            content=ft.Row(
                [
                    ft.Icon(
                        icon,
                        size=21,
                        color="#475467",
                    ),
                    ft.Text(
                        title,
                        size=15,
                        color="#344054",
                    ),
                ],
                spacing=12,
            ),
        )

    # ========================================================
    # SIDEBAR
    # ========================================================

    sidebar = ft.Container(
        width=240,
        bgcolor="#FFFFFF",
        padding=15,
        content=ft.Column(
            [
                # ------------------------------------------------
                # LOGO
                # ------------------------------------------------
                ft.Container(
                    padding=15,
                    content=ft.Row(
                        [
                            ft.Container(
                                width=42,
                                height=42,
                                bgcolor="#1677FF",
                                border_radius=10,
                                alignment=ft.Alignment(
                                    0,
                                    0,
                                ),
                                content=ft.Icon(
                                    ft.Icons.GRID_VIEW,
                                    color="#FFFFFF",
                                ),
                            ),
                            ft.Text(
                                "Мій додаток",
                                size=18,
                                weight=ft.FontWeight.BOLD,
                                color="#101828",
                            ),
                        ],
                        spacing=10,
                    ),
                ),
                ft.Container(height=15),
                # ------------------------------------------------
                # MENU
                # ------------------------------------------------
                menu_button(
                    "Головна",
                    ft.Icons.HOME_OUTLINED,
                    lambda e: show_home(),
                ),
                menu_button(
                    "Працівники",
                    ft.Icons.PEOPLE_OUTLINE,
                    lambda e: show_placeholder("Працівники"),
                ),
                menu_button(
                    "Посади",
                    ft.Icons.WORK_OUTLINE,
                    lambda e: show_placeholder("Посади"),
                ),
                menu_button(
                    "Підрозділи",
                    ft.Icons.ACCOUNT_TREE_OUTLINED,
                    lambda e: show_placeholder("Підрозділи"),
                ),
                menu_button(
                    "Дані",
                    ft.Icons.TABLE_CHART_OUTLINED,
                    lambda e: show_data(),
                ),
                menu_button(
                    "Звіти",
                    ft.Icons.BAR_CHART_OUTLINED,
                    lambda e: show_placeholder("Звіти"),
                ),
                menu_button(
                    "Експорт",
                    ft.Icons.UPLOAD_OUTLINED,
                    lambda e: show_placeholder("Експорт"),
                ),
                ft.Divider(),
                ft.Container(expand=True),
                menu_button(
                    "Про програму",
                    ft.Icons.INFO_OUTLINE,
                    lambda e: show_placeholder("Про програму"),
                ),
            ],
            expand=True,
        ),
    )

    # ========================================================
    # HOME
    # ========================================================

    def show_home():

        # ----------------------------------------------------
        # NO DATA
        # ----------------------------------------------------

        if not state.imported:

            content.content = ft.Column(
                [
                    ft.Text(
                        "Вітаю!",
                        size=32,
                        weight=ft.FontWeight.BOLD,
                        color="#101828",
                    ),
                    ft.Text(
                        "Для початку роботи імпортуйте Excel-файл.",
                        size=16,
                        color="#667085",
                    ),
                    ft.Container(height=25),
                    ft.Container(
                        bgcolor="#FFFFFF",
                        padding=40,
                        border_radius=12,
                        content=ft.Column(
                            [
                                ft.Icon(
                                    ft.Icons.TABLE_CHART,
                                    size=65,
                                    color="#1677FF",
                                ),
                                ft.Text(
                                    "Імпортувати Excel",
                                    size=24,
                                    weight=ft.FontWeight.BOLD,
                                    color="#101828",
                                ),
                                ft.Text(
                                    "Виберіть файл Excel для початку роботи.",
                                    size=15,
                                    color="#667085",
                                ),
                                ft.Container(height=10),
                                ft.ElevatedButton(
                                    "Вибрати файл",
                                    icon=ft.Icons.FOLDER_OPEN,
                                    on_click=select_file,
                                ),
                                ft.Text(
                                    "Підтримується формат .xlsx",
                                    size=12,
                                    color="#98A2B3",
                                ),
                            ],
                            horizontal_alignment=(ft.CrossAxisAlignment.CENTER),
                            spacing=12,
                        ),
                    ),
                ],
                scroll=ft.ScrollMode.AUTO,
            )

            page.update()

            return

        # ----------------------------------------------------
        # DATA IMPORTED
        # ----------------------------------------------------

        content.content = ft.Column(
            [
                # HEADER
                ft.Row(
                    [
                        ft.Column(
                            [
                                ft.Text(
                                    "Головна",
                                    size=30,
                                    weight=ft.FontWeight.BOLD,
                                    color="#101828",
                                ),
                                ft.Text(
                                    "Робота з даними Excel",
                                    size=15,
                                    color="#667085",
                                ),
                            ],
                            expand=True,
                        ),
                        ft.ElevatedButton(
                            "Оновити Excel",
                            icon=ft.Icons.REFRESH,
                            on_click=select_file,
                        ),
                    ]
                ),
                ft.Container(height=20),
                # ------------------------------------------------
                # FILE CARD
                # ------------------------------------------------
                ft.Container(
                    bgcolor="#FFFFFF",
                    padding=25,
                    border_radius=12,
                    content=ft.Row(
                        [
                            ft.Container(
                                width=60,
                                height=60,
                                bgcolor="#EAF2FF",
                                border_radius=10,
                                alignment=ft.Alignment(
                                    0,
                                    0,
                                ),
                                content=ft.Icon(
                                    ft.Icons.TABLE_CHART,
                                    size=32,
                                    color="#1677FF",
                                ),
                            ),
                            ft.Column(
                                [
                                    ft.Text(
                                        "Джерело даних",
                                        size=13,
                                        color="#667085",
                                    ),
                                    ft.Text(
                                        state.file_name,
                                        size=19,
                                        weight=ft.FontWeight.BOLD,
                                    ),
                                    ft.Text(
                                        str(state.file_path),
                                        size=12,
                                        color="#98A2B3",
                                    ),
                                ],
                                expand=True,
                                spacing=4,
                            ),
                            ft.Column(
                                [
                                    ft.Text(
                                        "Рядків",
                                        color="#667085",
                                    ),
                                    ft.Text(
                                        f"{state.total_rows:,}",
                                        size=22,
                                        weight=ft.FontWeight.BOLD,
                                    ),
                                ],
                            ),
                            ft.Column(
                                [
                                    ft.Text(
                                        "Аркушів",
                                        color="#667085",
                                    ),
                                    ft.Text(
                                        str(state.total_sheets),
                                        size=22,
                                        weight=ft.FontWeight.BOLD,
                                    ),
                                ],
                            ),
                            ft.Column(
                                [
                                    ft.Text(
                                        "Колонок",
                                        color="#667085",
                                    ),
                                    ft.Text(
                                        str(state.total_columns),
                                        size=22,
                                        weight=ft.FontWeight.BOLD,
                                    ),
                                ],
                            ),
                        ],
                        spacing=25,
                    ),
                ),
                ft.Container(height=20),
                # ------------------------------------------------
                # STATISTICS
                # ------------------------------------------------
                ft.Row(
                    [
                        statistic_card(
                            "Записи",
                            state.total_rows,
                            ft.Icons.PEOPLE_OUTLINE,
                        ),
                        statistic_card(
                            "Аркуші",
                            state.total_sheets,
                            ft.Icons.DESCRIPTION_OUTLINED,
                        ),
                        statistic_card(
                            "Колонки",
                            state.total_columns,
                            ft.Icons.TABLE_CHART_OUTLINED,
                        ),
                        statistic_card(
                            "Дати",
                            count_dates(),
                            ft.Icons.CALENDAR_TODAY_OUTLINED,
                        ),
                    ],
                    spacing=15,
                ),
                ft.Container(height=20),
                # ------------------------------------------------
                # EXCEL SHEETS
                # ------------------------------------------------
                ft.Container(
                    bgcolor="#FFFFFF",
                    padding=25,
                    border_radius=12,
                    content=ft.Column(
                        [
                            ft.Text(
                                "Аркуші Excel",
                                size=20,
                                weight=ft.FontWeight.BOLD,
                            ),
                            ft.Divider(),
                            *[
                                ft.ListTile(
                                    leading=ft.Icon(
                                        ft.Icons.TABLE_CHART_OUTLINED,
                                        color="#1677FF",
                                    ),
                                    title=ft.Text(sheet_name),
                                    subtitle=ft.Text(
                                        f"{len(df)} рядків × "
                                        f"{len(df.columns)} колонок"
                                    ),
                                )
                                for sheet_name, df in state.sheets.items()
                            ],
                        ]
                    ),
                ),
            ],
            scroll=ft.ScrollMode.AUTO,
        )

        page.update()

    # ========================================================
    # DATA PAGE
    # ========================================================

    def show_data():

        if not state.imported:

            show_home()

            return

        if state.df is None:

            show_message("Дані відсутні.")

            return

        df = state.df

        # Максимум 12 колонок для відображення
        columns = list(df.columns)[:12]

        rows = []

        for _, row in df.head(50).iterrows():

            cells = []

            for column in columns:

                cells.append(
                    ft.DataCell(
                        ft.Text(
                            format_value(row[column]),
                            size=13,
                        )
                    )
                )

            rows.append(ft.DataRow(cells=cells))

        table = ft.DataTable(
            columns=[
                ft.DataColumn(
                    ft.Text(
                        str(column),
                        weight=ft.FontWeight.BOLD,
                    )
                )
                for column in columns
            ],
            rows=rows,
            column_spacing=25,
        )

        content.content = ft.Column(
            [
                ft.Row(
                    [
                        ft.Column(
                            [
                                ft.Text(
                                    "Дані",
                                    size=30,
                                    weight=ft.FontWeight.BOLD,
                                ),
                                ft.Text(
                                    f"Файл: {state.file_name}",
                                    color="#667085",
                                ),
                            ],
                            expand=True,
                        ),
                        ft.Text(
                            f"Всього записів: {len(df)}",
                            color="#667085",
                        ),
                    ]
                ),
                ft.Container(height=20),
                ft.Container(
                    bgcolor="#FFFFFF",
                    padding=20,
                    border_radius=12,
                    content=ft.Column(
                        [
                            ft.Text(
                                "Перегляд даних",
                                size=20,
                                weight=ft.FontWeight.BOLD,
                            ),
                            ft.Divider(),
                            ft.Row(
                                [table],
                                scroll=ft.ScrollMode.AUTO,
                            ),
                        ]
                    ),
                ),
            ],
            scroll=ft.ScrollMode.AUTO,
        )

        page.update()

    # ========================================================
    # PLACEHOLDER PAGE
    # ========================================================

    def show_placeholder(title):

        content.content = ft.Column(
            [
                ft.Text(
                    title,
                    size=30,
                    weight=ft.FontWeight.BOLD,
                ),
                ft.Container(height=10),
                ft.Text(
                    "Цей розділ буде реалізований пізніше.",
                    size=16,
                    color="#667085",
                ),
            ]
        )

        page.update()

    # ========================================================
    # LAYOUT
    # ========================================================

    page.add(
        ft.Row(
            [
                sidebar,
                ft.Container(
                    content=content,
                    expand=True,
                ),
            ],
            expand=True,
            spacing=0,
        )
    )

    # ========================================================
    # START
    # ========================================================

    show_home()


# ============================================================
# RUN
# ============================================================

if __name__ == "__main__":
    ft.run(main)

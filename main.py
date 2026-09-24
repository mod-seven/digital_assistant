import flet as ft

from app.router import AppRouter
from app.state import AppState


def main(page: ft.Page):

    page.title = "Digital Assistant"

    page.window.width = 1400
    page.window.height = 850

    page.window.min_width = 1100
    page.window.min_height = 700

    page.bgcolor = "#F5F7FA"

    state = AppState()
    router = AppRouter(page, state)

    router.start()


if __name__ == "__main__":
    ft.run(main)

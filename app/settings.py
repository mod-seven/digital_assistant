import sys
from pathlib import Path

if getattr(sys, "frozen", False):
    BASE_DIR = Path(sys._MEIPASS)
else:
    BASE_DIR = Path(__file__).resolve().parent.parent


TEMPLATE_REPORT_PATH = BASE_DIR / "assets" / "templates" / "template_report.docx"

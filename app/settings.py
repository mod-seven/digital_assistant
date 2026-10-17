import json
import os
import sys
from pathlib import Path

if getattr(sys, "frozen", False):
    BASE_DIR = Path(sys._MEIPASS)
else:
    BASE_DIR = Path(__file__).resolve().parent.parent

TEMPLATE_REPORT_PATH = BASE_DIR / "assets" / "templates" / "template_report.docx"

# Налаштування зберігаються окремо від каталогу програми, щоб не втрачатися
# після перезапуску та працювати в зібраному застосунку.
if os.name == "nt":
    _config_root = Path(
        os.environ.get("LOCALAPPDATA", Path.home() / "AppData" / "Local")
    )
else:
    _config_root = Path(os.environ.get("XDG_CONFIG_HOME", Path.home() / ".config"))
APP_CONFIG_DIR = _config_root / "DigitalAssistant"
APP_CONFIG_FILE = APP_CONFIG_DIR / "config.json"
APP_VERSION = "1.0.3"
DEFAULT_SIGNATURES_DB = Path(r"C:\Users\chewbaka\Desktop\Signatures\signatures.db")


def get_signatures_db_path() -> Path:
    try:
        config = json.loads(APP_CONFIG_FILE.read_text(encoding="utf-8"))
        value = config.get("signatures_db_path")
        if value:
            return Path(value).expanduser()
    except (OSError, ValueError, TypeError):
        pass
    return DEFAULT_SIGNATURES_DB


def save_signatures_db_path(path: str | Path) -> Path:
    resolved = Path(path).expanduser()
    APP_CONFIG_DIR.mkdir(parents=True, exist_ok=True)
    APP_CONFIG_FILE.write_text(
        json.dumps({"signatures_db_path": str(resolved)}, ensure_ascii=False, indent=2),
        encoding="utf-8",
    )
    return resolved


def get_signatures_images_dir() -> Path:
    # Файли підписів зберігаються поруч із БД у підкаталозі images.
    return get_signatures_db_path().parent / "images"


# Сумісність з кодом, який міг використовувати ці константи.
SIGNATURES_DB = get_signatures_db_path()
SIGNATURES_ROOT = SIGNATURES_DB.parent
SIGNATURES_IMAGES = get_signatures_images_dir()

from enum import Enum


class TableSheet(str, Enum):
    PERSONNEL = "ОСОБОВИЙ СКЛАД"


class TableHeader(str, Enum):
    ROW_NUMBER = "№ З/П"
    POSITION_CODE = "Індекс посади"
    UNIT = "Підрозділ"
    POSITION = "Посада"
    RANK = "Військове звання фактичне"
    RELEVANCE_TO_THE_POSITION = "Зв'язок з посадою"
    FULL_NAME = "ПІБ"
    STATUS = "Статус"
    TAX_ID = "РНОКПП (ІПН)"
    FULL_JOB_TITLE = "Повна назва посади"
    FULL_JOB_TITLE_ACCUSATIVE = "Повна назва посади (знахідний)"
    FULL_JOB_TITLE_DATIVE = "Повна назва посади (давальний)"
    GENDER = "Стать"


class StatusPersonal(str, Enum):
    IN_STOCK = "В наявності"


class RelevanceToThePosition(str, Enum):
    STATE = "Штат"
    TVO = "ТВО"


TVO_TEXT = "ТВО"
MILITARY_UNIT_NUMBER = "А7379"
MILITARY_UNIT = f"військова частина {MILITARY_UNIT_NUMBER}"

WORD_FONT = "Times New Roman"
WORD_SIZE = 24


class ReportType(str, Enum):
    REPORT_OVER_POSITION = "Рапорт посаду здав"
    REPORT_ACCEPTED_POSITION = "Рапорт посаду прийняв"
    REPOSTS_FFROM_FILE = "Генерація рапортів з файлу"

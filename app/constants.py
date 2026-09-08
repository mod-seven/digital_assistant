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

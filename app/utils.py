from datetime import date


def format_date_ukrainian(value: date) -> str:
    months = {
        1: "січня",
        2: "лютого",
        3: "березня",
        4: "квітня",
        5: "травня",
        6: "червня",
        7: "липня",
        8: "серпня",
        9: "вересня",
        10: "жовтня",
        11: "листопада",
        12: "грудня",
    }

    return f"“{value.day:02d}” {months[value.month]} {value.year} року"


def number_to_words_ua(number: int) -> str:
    units = [
        "",
        "один",
        "два",
        "три",
        "чотири",
        "п’ять",
        "шість",
        "сім",
        "вісім",
        "дев’ять",
    ]
    teens = [
        "десять",
        "одинадцять",
        "дванадцять",
        "тринадцять",
        "чотирнадцять",
        "п’ятнадцять",
        "шістнадцять",
        "сімнадцять",
        "вісімнадцять",
        "дев’ятнадцять",
    ]
    tens = [
        "",
        "",
        "двадцять",
        "тридцять",
        "сорок",
        "п’ятдесят",
        "шістдесят",
        "сімдесят",
        "вісімдесят",
        "дев’яносто",
    ]
    hundreds = [
        "",
        "сто",
        "двісті",
        "триста",
        "чотириста",
        "п’ятсот",
        "шістсот",
        "сімсот",
        "вісімсот",
        "дев’ятсот",
    ]
    thousands = [
        "",
        "тисяча",
        "дві тисячі",
        "три тисячі",
        "чотири тисячі",
        "п’ять тисяч",
        "шість тисяч",
        "сім тисяч",
        "вісім тисяч",
        "дев’ять тисяч",
    ]

    if number == 0:
        return "нуль"

    parts = []

    if number >= 1000:
        t = number // 1000
        parts.append(thousands[t])
        number %= 1000

    if number >= 100:
        h = number // 100
        parts.append(hundreds[h])
        number %= 100

    if 10 <= number <= 19:
        parts.append(teens[number - 10])
    else:
        if number >= 20:
            t = number // 10
            parts.append(tens[t])
            number %= 10
        if number > 0:
            parts.append(units[number])

    return " ".join([p for p in parts if p])


def format_day_text(n: int) -> str:
    if n % 10 == 1 and n % 100 != 11:
        word = "добу"
    elif n % 10 in [2, 3, 4] and not (12 <= n % 100 <= 14):
        word = "доби"
    else:
        word = "діб"
    return word

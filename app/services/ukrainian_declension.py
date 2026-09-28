from shevchenko import GrammaticalCase, GrammaticalGender, inflect
from shevchenko.extension import register_extension
from shevchenko_ext_military import military_extension

from app.exclusion import ShevchenkoExclusion

register_extension(military_extension)


def get_shevchenko_result(
    grammatacal_case: GrammaticalCase,
    gender: str,
    given_name: str = "",
    patronymic_name: str = "",
    family_name: str = "",
    military_rank: str = "",
    military_appointment: str = "",
):
    gender_result = (
        GrammaticalGender.MASCULINE if gender == "Ч" else GrammaticalGender.FEMININE
    )

    input_data = {
        "gender": gender_result,
        "givenName": given_name,
        "familyName": family_name,
        "patronymicName": patronymic_name,
        "militaryRank": military_rank,
        "militaryAppointment": military_appointment,
    }

    try:
        result = inflect(input_data, grammatacal_case)
    except Exception as error:
        raise ShevchenkoExclusion(f"Помилка відмінювання: {error}") from error

    return result

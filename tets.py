from app.constants import TableSheet
from app.repositories.personnel import PandasExcelPersonnelRepository
from app.services.import_excel import import_excel
from app.state import AppState

state = AppState()
import_excel(
    "C:/Users/chewbaka/Desktop/21.08.2026/04.09.2026_11.23-Експорт ШПС.xlsx", state
)

# print(state.sheets[TableSheet.PERSONNEL].columns)
repository = PandasExcelPersonnelRepository(state.sheets[TableSheet.PERSONNEL])

# print(repository.get_number_of_staff_positions())
# print(repository.get_number_on_the_list())

subordination = repository.get_subordination_by_full_name(
    "ХОМА Володимир Володимирович"
)
print(subordination)

class BaseExclusion(Exception):
    def __init__(self, msg: str, **kwargs):
        self.msg = msg


class ImportExcelExclusion(BaseExclusion):
    pass


class ExcelPersonalRepositoryExclusion(BaseExclusion):
    pass

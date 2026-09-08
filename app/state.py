class AppState:
    def __init__(self):
        self.file_path = None
        self.file_name = None

        self.sheets = {}
        self.df = None

        self.imported = False

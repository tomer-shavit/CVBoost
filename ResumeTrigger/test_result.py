class TestResult:
    def __init__(self, status: bool, error_type: int, error_message: str):
        self.status = status
        self.error_type = error_type
        self.error_message = error_message

    def is_passed(self) -> bool:
        return self.status


class FileTestResult(TestResult):
    DEFAULT = 0
    TYPE = 1
    LANG = 2
    LENGTH = 3

    def __init__(self, status: bool, error_type: int, error_message: str):
        super().__init__(status, error_type, error_message)

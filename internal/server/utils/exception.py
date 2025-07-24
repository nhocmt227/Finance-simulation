class ApiLimitError(Exception):
    def __init__(self, message="This is a custom exception"):
        self.message = message
        super().__init__(self.message)

class ApiLimitError(Exception):
    def __init__(self, message="This is a custome exception"):
        self.message = message
        super().__init__(self.message)
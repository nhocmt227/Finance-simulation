class ApiLimitError(Exception):
    def __init__(self, message="API limit reached, please wait for a while"):
        self.message = message
        super().__init__(self.message)

class Status:

    def __init__(self, message: str=None, code: int=None, is_successful: bool=None):
        self.message = message
        self.is_successful = is_successful
        self.code = code

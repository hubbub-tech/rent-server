class Status:

    def __init__(self, messages: list=[], code: int=None, is_successful: bool=None):
        self.messages = messages
        self.is_successful = is_successful

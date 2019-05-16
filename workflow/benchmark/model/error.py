class WorkflowError(Exception):

    def __init__(self, message, error_code=9999):
        self.message = message
        self.error_code = error_code

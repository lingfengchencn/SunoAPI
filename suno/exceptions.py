
# Service Unavailable Exception
class ServiceUnavailableException(Exception):
    def __init__(self, message):
        self.message = message
        super().__init__(message)
# '{"detail": "Unauthorized"}'

class UnauthorizedException(Exception):
    def __init__(self, message):
        self.message = message
        super().__init__(message)

class TooManyRequestsException(Exception):
    def __init__(self, message):
        self.message = message
        super().__init__(message)
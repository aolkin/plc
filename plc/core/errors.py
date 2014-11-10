
class PLCException(Exception): pass

class IntegrationException(PLCException): pass

class DisallowedOperation(PLCException): pass

class InvalidLevelError(PLCException):
    def __init__(self):
        super().__init__("Levels should be represented as fractions of 1")

class MissingDefaultError(PLCException):
    def __init__(self, group, key):
        super().__init__("Missing default value for {} {}".format(group, key))

class SecurityError(PLCException): pass

class NetworkError(PLCException): pass

class ScreenException(PLCException): pass

class PadSizeError(ScreenException): pass

class HuumError(Exception):
    pass


class SafetyException(HuumError):
    pass


class BadRequest(HuumError):
    pass


class NotAuthenticated(HuumError):
    pass


class Forbidden(HuumError):
    pass


class RequestError(HuumError):
    pass

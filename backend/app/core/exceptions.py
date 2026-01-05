"""Custom Exceptions"""


class AppException(Exception):
    """Base application exception"""
    def __init__(self, detail: str, status_code: int = 500):
        self.detail = detail
        self.status_code = status_code
        super().__init__(detail)


class AuthenticationException(AppException):
    """Authentication failed"""
    def __init__(self, detail: str = "Authentication failed"):
        super().__init__(detail, status_code=401)


class AuthorizationException(AppException):
    """Authorization/permission denied"""
    def __init__(self, detail: str = "Permission denied"):
        super().__init__(detail, status_code=403)


class NotFoundException(AppException):
    """Resource not found"""
    def __init__(self, detail: str = "Resource not found"):
        super().__init__(detail, status_code=404)


class ValidationException(AppException):
    """Validation error"""
    def __init__(self, detail: str = "Validation error"):
        super().__init__(detail, status_code=422)


class ConflictException(AppException):
    """Resource conflict"""
    def __init__(self, detail: str = "Resource conflict"):
        super().__init__(detail, status_code=409)


class RateLimitException(AppException):
    """Rate limit exceeded"""
    def __init__(self, detail: str = "Rate limit exceeded"):
        super().__init__(detail, status_code=429)


class ServiceUnavailableException(AppException):
    """External service unavailable"""
    def __init__(self, detail: str = "Service temporarily unavailable"):
        super().__init__(detail, status_code=503)


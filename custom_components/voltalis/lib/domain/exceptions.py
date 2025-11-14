class VoltalisException(Exception):
    """Base Exception for the integration exception"""


class VoltalisAuthenticationException(VoltalisException):
    """Exception that will be thrown when there's some error during the authentification process"""

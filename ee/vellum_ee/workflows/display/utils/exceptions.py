class UserFacingException(Exception):
    def to_message(self) -> str:
        return str(self)


class UnsupportedSerializationException(UserFacingException):
    pass

class PasswordPolicyError(ValueError):
    pass


COMMON_PASSWORDS = frozenset(
    {
        "password1234567",
        "123456789123456",
        "qwertyuiopasdfg",
        "letmeinletmein",
        "adminadminadmin",
        "welcome12345678",
    }
)


def validate_password_policy(password: str) -> None:
    if password.casefold() in COMMON_PASSWORDS:
        raise PasswordPolicyError("Password is too common")

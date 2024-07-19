from enum import Enum


class UserFlag(Enum):
    HELLO_I_AM_A_FLAG = 0


class UserBitflag:
    def __init__(self, default: int | None) -> None:
        if default is not None:
            self.current_permissions: int = default
        else:
            self.current_permissions: int = 0

    def add(self, flag: UserFlag) -> None:
        self.current_permissions |= 1 << flag.value

    def remove(self, flag: UserFlag) -> None:
        self.current_permissions &= ~(1 << flag.value)

    def zip(self):
        return self.current_permissions

    @staticmethod
    def unzip(permissions: int) -> "UserBitflag":
        bitflag = UserBitflag()
        bitflag.current_permissions = permissions
        return bitflag

    def has(self, flag) -> bool:
        return (self.current_permissions & (1 << flag.value)) != 0

    def to_list(self) -> list[UserFlag]:
        flags: list[UserFlag] = []
        for flag in UserFlag:
            if self.has(flag):
                flags.append(flag)
        return flags

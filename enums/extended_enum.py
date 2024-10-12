from enum import Enum


class ExtendedEnum(Enum):
    @classmethod
    def values(cls) -> list[str]:
        return [member.value for member in cls]

    @classmethod
    def dict(cls) -> dict[str, str]:
        return {member.name: member.value for member in cls}

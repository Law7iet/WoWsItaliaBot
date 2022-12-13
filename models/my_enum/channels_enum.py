from enum import Enum


class ChannelsEnum(Enum):
    TXT_LOG_EVENT = 681962602657873990
    TXT_TESTING = 953598226160836618
    TXT_ADMIN = 696853218642231346

    TXT_PODIO_CUP = 818856265237266473
    TXT_PODIO_LEAGUE = 779449057600602123
    TXT_CLASSIFICA_CB = 847179325349429258
    TXT_DEV_BLOG = 696853825247772733

    def __str__(self) -> str:
        return str(self.value)

    def __int__(self) -> int:
        return self.value

from enum import Enum


class RolesEnum(Enum):
    ADMIN = 379688107433525271
    CC = 408628827737161728
    CM = 430713251085418517
    MOD = 539071779247751181
    ORG_CUP = 828669190398935100
    ORG_LEAGUE = 828669615289663499
    REF = 914534808221274182
    STREAMER = 539755783488012289
    REP = 408630527583846413
    SAILOR = 383279930886062082
    AUTH = 1024602087377600582
    EVERYONE = 0

    WOWS_ITALIA = 780427147658919946
    BOT = 439020331039064064

    def __str__(self) -> str:
        return str(self.value)

    def __int__(self) -> int:
        return self.value

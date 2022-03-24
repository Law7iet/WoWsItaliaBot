from enum import Enum

from utils.constants import *


class RolesEnum(Enum):
    ADMIN = 0
    MODERATOR = 1
    ORG_CUP = 2
    ORG_LEAGUE = 3
    REPRESENTATIVE = 4
    SAILOR = 5
    NOT_AUTH = 6

    def __str__(self):
        match self.value:
            case 0:
                return str(ROLE_ADMIN)
            case 1:
                return str(ROLE_MODERATORE)
            case 2:
                return str(ROLE_ORG_CUP)
            case 3:
                return str(ROLE_ORG_LEAGUE)
            case 4:
                return str(ROLE_RAPPRESENTANTE_CLAN)
            case 5:
                return str(ROLE_MARINAIO)
            case 6:
                return str(ROLE_NON_AUTENTICATO)
            case _:
                return ''

    def __int__(self):
        return self.value

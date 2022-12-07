from enum import Enum

from utils.constants import *


class RolesEnum(Enum):
    ADMIN = 0
    MODERATOR = 1
    ORG_CUP = 2
    ORG_LEAGUE = 3
    REFEREE = 4
    REPRESENTATIVE = 5
    SAILOR = 6
    AUTH = 7
    EVERYONE = 8

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
                return str(ROLE_ARBITRO)
            case 5:
                return str(ROLE_RAPPRESENTANTE_CLAN)
            case 6:
                return str(ROLE_MARINAIO)
            case 7:
                return str(ROLE_NON_AUTENTICATO)
            case _:
                return 'No role'

    def id(self) -> int:
        match self.value:
            case 0:
                return ROLE_ADMIN
            case 1:
                return ROLE_MODERATORE
            case 2:
                return ROLE_ORG_CUP
            case 3:
                return ROLE_ORG_LEAGUE
            case 4:
                return ROLE_ARBITRO
            case 5:
                return ROLE_RAPPRESENTANTE_CLAN
            case 6:
                return ROLE_MARINAIO
            case 7:
                return ROLE_NON_AUTENTICATO
            case _:
                return -1

    def __int__(self):
        return self.value

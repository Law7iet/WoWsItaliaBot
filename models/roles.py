from utils.constants import *
from enum import Enum


class RolesEnum(Enum):
    ADMIN = 0, str(ROLE_ADMIN)
    MODERATOR = 1, str(ROLE_MODERATORE)
    ORG_CUP = 2, str(ROLE_ORG_CUP)
    ORG_LEGUE = 3, str(ROLE_ORG_LEAGUE)
    REPRESENTATIVE = 4, str(ROLE_RAPPRESENTANTE_CLAN)
    SAILOR = 5, str(ROLE_MARINAIO)
    NOT_AUTH = 6, str(ROLE_NON_AUTENTICATO)

    def __index__(self):
        return self.value

    # def __str__(self):
    #     match self.value:
    #         case 0:
    #             return self.value
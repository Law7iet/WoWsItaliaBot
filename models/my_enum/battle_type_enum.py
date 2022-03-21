from enum import Enum


class BattleTypeEnum(Enum):
    BO1 = "BO1"
    BO3 = "BO3"
    BO5 = "BO5"

    def __index__(self):
        return self.value

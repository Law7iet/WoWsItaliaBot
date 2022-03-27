from enum import Enum


class PlayoffFormatEnum(Enum):
    BO1 = 'Bo1'
    BO3 = 'Bo3'
    BO5 = 'Bo5'

    def __index__(self):
        return self.value

    def __str__(self):
        return self.value

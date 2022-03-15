# Objects used for the ranking of the tournament ranking.
from enum import Enum


class TournamentEnum(Enum):
    _init_ = -1, ''
    LEAGUE = 0, "League"
    CUP = 1, "Cup"

    def __index__(self):
        return self.value[0]

    def __str__(self):
        return self.value[1]


class PodiumEnum(Enum):
    _init_ = -1, 0x000000, ''
    OTHER = 0, 0xFFFFFF, ''
    FIRST = 1, 0xFFD700, 'Primo'
    SECOND = 2, 0xC0C0C0, 'Secondo'
    THIRD = 3, 0xCD7F32, 'Terzo'

    def __index__(self):
        return self.value[0]

    def __hex__(self):
        return self.value[1]

    def __str__(self):
        return self.value[2]
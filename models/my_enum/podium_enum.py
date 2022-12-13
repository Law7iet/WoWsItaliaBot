# Objects used for the ranking of the tournament ranking.
from enum import Enum


class TournamentEnum(Enum):
    LEAGUE = 0
    CUP = 1

    def __str__(self):
        match self.value:
            case 0: return "League"
            case 1: return "Cup"
            case _: return ""


class PodiumEnum(Enum):
    OTHER = 0
    FIRST = 1
    SECOND = 2
    THIRD = 3

    def __int__(self):
        match self.value:
            case 0: return 0xFFFFFF
            case 1: return 0xFFD700
            case 2: return 0xC0C0C0
            case 3: return 0xCD7F32
            case _: return 0xFFFFFF

    def __str__(self):
        match self.value:
            case 0: return ""
            case 1: return "Primo"
            case 2: return "Secondo"
            case 3: return "Terzo"
            case _: return ""

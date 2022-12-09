from enum import Enum


class LeagueType(Enum):
    HURRICANE = 0
    TYPHOON = 1
    STORM = 2
    GALE = 3
    SQUALL = 4

    def __int__(self):
        return self.value

    def __str__(self):
        match self.value:
            case 0: return "Uragano"
            case 1: return "Tifone"
            case 2: return "Tempesta"
            case 3: return "Burrasca"
            case 4: return "Temporale"
            case _: return ""

    def color(self):
        match self.value:
            case 0: return ":purple_square:"
            case 1: return ":green_square:"
            case 2: return ":yellow_square:"
            case 3: return ":white_large_square:"
            case 4: return ":brown_square:"
            case _: return ""

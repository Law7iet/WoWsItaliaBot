from enum import IntEnum


class SquadType(IntEnum):
    ALPHA = 0
    BRAVO = 1

    def __str__(self):
        match self.value:
            case 0: return "alpha"
            case 1: return "bravo"

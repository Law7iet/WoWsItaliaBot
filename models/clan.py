# Objects used for the ranking of the clan battle.
from enum import Enum


class LeagueTypeEnum(Enum):
    HURRICANE = 0
    TYPHOON = 1
    STORM = 2
    GALE = 3
    SQUALL = 4

    def __index__(self):
        return self.value

    def __str__(self):
        match self.value:
            case 0:
                return 'Uragano'
            case 1:
                return 'Tifone'
            case 2:
                return 'Tempesta'
            case 3:
                return 'Burrasca'
            case 4:
                return 'Temporale'
            case _:
                return ''


class LeagueColorEnum(Enum):
    HURRICANE = 0
    TYPHOON = 1
    STORM = 2
    GALE = 3
    SQUALL = 4

    def __index__(self):
        return self.value

    def __str__(self):
        match self.value:
            case 0:
                return ':purple_square:'
            case 1:
                return ':green_square:'
            case 2:
                return ':yellow_square:'
            case 3:
                return ':white_large_square:'
            case 4:
                return ':brown_square:'
            case _:
                return ''


class Clan:
    def __init__(self, tag: str, squad: str, win_rate: str, battles: int, league: LeagueTypeEnum, division: int,
                 score: int, promotion: list):
        self.tag = tag
        self.squad = squad
        self.win_rate = win_rate
        self.battles = battles
        self.league = league
        self.division = division
        self.score = score
        self.promotion = promotion

    def convert_promo_to_string(self) -> str:
        """
        Convert the promo message to a string.

        Returns:
            `str`: the promo message.
        """
        promotion = ''
        for battle in self.promotion:
            promotion = promotion + battle + ', '
        if promotion == '':
            return promotion
        else:
            return '[' + promotion[:-2] + ']'

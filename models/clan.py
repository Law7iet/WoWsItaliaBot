# Objects used for the ranking of the clan battle.
from enum import Enum


class LeagueTypeEnum(Enum):
    HURRICANE = 0, 'Uragano'
    TYPHOON = 1, 'Tifone'
    STORM = 2, 'Tempesta'
    GALE = 3, 'Burrasca'
    SQUALL = 4, 'Temporale'

    def __index__(self):
        return self.value[0]

    def __str__(self):
        return self.value[1]


class LeagueColorEnum(Enum):
    HURRICANE = 0, ':purple_square:'
    TYPHOON = 1, ':green_square:'
    STORM = 2, ':yellow_square:'
    GALE = 3, ':white_large_square:'
    SQUALL = 4, ':brown_square:'

    def __index__(self):
        return self.value[0]

    def __str__(self):
        return self.value[1]


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

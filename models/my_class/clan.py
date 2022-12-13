# Objects used for the ranking of the clan battle.
from models.my_enum.league_type_enum import LeagueType


class Clan:
    def __init__(self, tag: str, squad: str, win_rate: str, battles: int, league: LeagueType, division: int,
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

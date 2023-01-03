# Objects used for the ranking of the clan battle.
from models.enum.league_type import LeagueType
from models.enum.squad_type import SquadType


class Clan:
    def __init__(
            self,
            tag: str,
            squad: SquadType,
            win_rate: float,
            battles: int,
            league: LeagueType,
            division: int,
            score: int,
            promotion: list
    ):
        self.tag = tag
        self.squad = squad
        self.win_rate = win_rate
        self.battles = battles
        self.league = league
        self.division = division
        self.score = score
        self.promotion = promotion

        score = self.score
        division = (3 - self.division) * 100
        league = (4 - int(self.league)) * 500
        self.raw = score + division + league

    def convert_promo_to_string(self) -> str:
        """
        Convert the promo message to a string.

        Returns:
            The promo message.
        """
        promotion = ''
        for battle in self.promotion:
            promotion = promotion + battle + ', '
        if promotion == '':
            return promotion
        else:
            return '[' + promotion[:-2] + ']'

    def convert_to_dict(self, clan_tag: str, season: int, day: int, date: str) -> dict:
        """
        Convert the class to a dict, according to the rank collection of the WoWsItalia database.
        Returns:
            The dictionary.
        """
        return {
            "clan": clan_tag,
            "season": season,
            "day": day,
            "date": date,
            "squad": str(self.squad),
            "battles": self.battles,
            "win-rate": self.win_rate,
            "league": int(self.league),
            "division": self.division,
            "score": self.score,
            "raw": self.raw
        }

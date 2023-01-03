from enum import Enum


class DBCollections(str, Enum):
    CONFIG = "config"
    CLANS = "clans"
    PLAYERS = "players"
    RANK = "rank"

    def __str__(self) -> str:
        return self.value


class ConfigKeys(str, Enum):
    CB_CURRENT_SEASON = "season"
    CB_STARTING_DAY = "start_date"
    CB_ENDING_DAY = "end_date"

    def __str__(self) -> str:
        return self.value

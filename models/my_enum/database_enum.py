# Object used for the database collection.
from enum import Enum


class DBCollections(str, Enum):
    CONFIG = "Config"
    CLANS = "Clans"


class ConfigKeys(str, Enum):
    CB_CURRENT_SEASON = "clan_battle_current_season"
    CB_STARTING_DAY = "start_date"
    CB_ENDING_DAY = "end_date"

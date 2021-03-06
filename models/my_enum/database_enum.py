# Object used for the database collection.
from enum import Enum


class DatabaseCollection(Enum):
    CONFIG = 'Config'
    CLANS = 'Clans'
    PICKANDBANMAP = 'PickAndBanMap'

    def __str__(self):
        return self.value


class ConfigFileKeys(Enum):
    BANNED_SHIPS = 'banned_ships'
    CLAN_BATTLE_CURRENT_SEASON = 'clan_battle_current_season'
    MAPS = 'maps'
    PLAYOFF_FORMAT = 'playoff_format'

    def __str__(self):
        return self.value

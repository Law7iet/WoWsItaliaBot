# Object used for the database collection.
from enum import Enum


class DatabaseCollection(Enum):
    CONFIG = 0
    CLANS = 1

    def __index__(self):
        return self.value

    def __str__(self):
        match self.value:
            case 0:
                return 'Config'
            case 1:
                return 'Clans'
            case _:
                return ''

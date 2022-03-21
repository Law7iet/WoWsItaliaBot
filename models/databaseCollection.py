# Object used for the database collection.
from enum import Enum


class DatabaseCollection(Enum):
    CONFIG = 1
    CLANS = 2

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

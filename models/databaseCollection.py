# Object used for the database collection.
from enum import Enum


class DatabaseCollection(Enum):
    CONFIG = 1, 'Config'
    CLANS = 2, 'Clans'

    def __index__(self):
        return self.value[0]

    def __str__(self):
        return self.value[1]
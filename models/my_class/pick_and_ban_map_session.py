from bson import ObjectId
from discord import Embed, Colour

from models.my_enum.playoff_format_enum import PlayoffFormatEnum
from utils.functions import get_maps_reactions


class PickAndBanMapSession:
    def __init__(self, representant_a: str, representant_b: str, maps: list[str], playoff_format: PlayoffFormatEnum):
        self.__id = ObjectId()
        self.turn = 0
        self.representant_a = representant_a
        self.representant_b = representant_b
        self.banned = []
        self.picked = []
        self.maps = maps
        self.playoff_format = playoff_format

    # È utilizzato?
    def get_id(self) -> str:
        return self.__id.__str__()

    def get_dict(self, with_id: bool) -> dict:
        data = {
            'turn': self.turn,
            'representant_a': self.representant_a,
            'representant_b': self.representant_b,
            'banned': self.banned,
            'picked': self.picked,
            'available': self.maps,
            'playoff_format': str(self.playoff_format)
        }
        if with_id:
            data['_id'] = self.__id
        return data

    def get_embed(self) -> Embed:
        # Legend
        message = []
        emojis = get_maps_reactions(len(self.maps))
        for index in range(0, len(self.maps)):
            message.append(emojis[index] + ' ' + self.maps[index] + '\n')
        # Header
        match self.playoff_format:
            case PlayoffFormatEnum.BO1:
                return
            case _:
                pass
        message.insert(0, str(self.playoff_format) + ": <@" + self.representant_a + "> vs <@" +
                       self.representant_b + ">\n\n")
        # Footer
        message.append("\nTurno di <@" + self.representant_a + "> - Fase di ban")
        # Create the embed
        descrizione = "".join(message)
        embed = Embed(title="WoWs Italia - Map Vote", description=descrizione, color=0xff0000)
        embed.colour = Colour.from_rgb(255, 255, 255)
        return embed

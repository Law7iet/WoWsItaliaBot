from disnake import ApplicationCommandInteraction, Attachment
from disnake.ext import commands

from models.my_enum.roles_enum import RolesEnum
from utils.constants import *
from utils.functions import check_role
from utils.functions import send_response_and_clear
from utils.modal import ModalPodium

PodiumOptions = commands.option_enum({
    "Primo": "Primo",
    "Secondo": "Secondo",
    "Terzo": "Terzo",
    "Partecipante": "Partecipante"
})

TournamentOptions = commands.option_enum({
    "Italian League": "Italian League",
    "Italian Cup": "Italian Cup",
})


class TournamentRanking(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot

    @commands.slash_command()
    async def podium(
            self,
            inter: ApplicationCommandInteraction,
            torneo: TournamentOptions,
            edizione: int,
            posizione: PodiumOptions,
            immagine: Attachment
    ) -> None:
        if not await check_role(inter, inter.guild.get_role(RolesEnum.ADMIN.id())):
            await send_response_and_clear(inter, False, "Non hai i permessi.")
            return
        if not immagine.content_type:
            await send_response_and_clear(inter, False, "Formato immagine vuoto.")
            return
        if not immagine.content_type == "image/jpeg" and not immagine.content_type == "image/png":
            await send_response_and_clear(inter, False,
                                          "Formato immagine (`" + immagine.content_type + "`) non corretto. Formati ammessi: `jpg` e `png`")
            return
        if edizione <= 0:
            await send_response_and_clear(inter, False, "Il numero dell'edizione dev'essere maggiore di 0.")
            return
        if DEBUG:
            channel = inter.guild.get_channel(CH_TXT_TESTING)
        else:
            match torneo:
                case "Italian League":
                    channel = inter.guild.get_channel(CH_TXT_PODIO_LEAGUE)
                case "Italian Cup":
                    channel = inter.guild.get_channel(CH_TXT_PODIO_LEAGUE)
                case _:
                    channel = inter.guild.get_channel(CH_TXT_TESTING)
        try:
            await inter.response.send_modal(modal=ModalPodium(channel, torneo, edizione, posizione, immagine))
        except Exception as error:
            await self.bot.get_channel(CH_TXT_TESTING).send('**/podium command exception: ModalPodium error**')
            await self.bot.get_channel(CH_TXT_TESTING).send('```' + str(error) + '```')


def setup(bot):
    bot.add_cog(TournamentRanking(bot))

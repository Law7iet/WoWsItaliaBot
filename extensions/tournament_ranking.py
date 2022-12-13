from disnake import ApplicationCommandInteraction, Attachment
from disnake.ext import commands

from models.my_enum.roles_enum import RolesEnum
from models.my_enum.channels_enum import ChannelsEnum
from utils.functions import check_role, is_debugging
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
        self.debugging = is_debugging()

    @commands.slash_command()
    async def podium(
        self,
        inter: ApplicationCommandInteraction,
        torneo: TournamentOptions,
        edizione: int,
        posizione: PodiumOptions,
        immagine: Attachment
    ) -> None:
        if not await check_role(inter, RolesEnum.ADMIN):
            await inter.send("Non hai i permessi.")
            return
        if not immagine.content_type:
            await inter.send("Formato immagine vuoto.")
            return
        if not immagine.content_type == "image/jpeg" and not immagine.content_type == "image/png":
            msg = "Formato immagine (`" + immagine.content_type + "`) non corretto. Formati ammessi: `jpg` e `png`"
            await inter.send(msg)
            return
        if edizione <= 0:
            await inter.send("Il numero dell'edizione dev'essere maggiore di 0.")
            return
        if self.debugging:
            channel = inter.guild.get_channel(int(ChannelsEnum.TXT_TESTING))
        else:
            match torneo:
                case "Italian League":
                    channel = inter.guild.get_channel(int(ChannelsEnum.TXT_PODIO_LEAGUE))
                case "Italian Cup":
                    channel = inter.guild.get_channel(int(ChannelsEnum.TXT_PODIO_CUP))
                case _:
                    channel = inter.guild.get_channel(int(ChannelsEnum.TXT_TESTING))
        try:
            await inter.response.send_modal(modal=ModalPodium(channel, torneo, edizione, posizione, immagine))
        except Exception as error:
            msg = '**>podium command exception: ModalPodium error**'
            await self.bot.get_channel(int(ChannelsEnum.TXT_TESTING)).send(msg)
            await self.bot.get_channel(int(ChannelsEnum.TXT_TESTING)).send('```' + str(error) + '```')


def setup(bot):
    bot.add_cog(TournamentRanking(bot))

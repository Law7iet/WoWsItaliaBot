from disnake import ApplicationCommandInteraction, Attachment
from disnake.ext import commands

from models.enum.discord_id import MyChannels, MyRoles
from models.modal_podium import ModalPodium
from utils.functions import check_role, is_debugging


class TournamentRanking(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot
        self.debugging = is_debugging()

    @commands.slash_command(name="podio")
    async def podium(
        self,
        inter: ApplicationCommandInteraction,
        tournament: str = commands.Param(name="torneo", choices=["Italian League", "Italian Cup"]),
        edition: int = commands.Param(name="edizione"),
        pos: str = commands.Param(name="posizione", choices=["Primo", "Secondo", "Terzo", "Partecipante"]),
        image: Attachment = commands.Param(name="immagine")
    ) -> None:
        if not await check_role(inter, MyRoles.ADMIN):
            await inter.send("Non hai i permessi.")
            return
        if not image.content_type:
            await inter.send("Formato immagine vuoto.")
            return
        if not image.content_type == "image/jpeg" and not image.content_type == "image/png":
            msg = "Formato immagine (`" + image.content_type + "`) non corretto. Formati ammessi: `jpg` e `png`"
            await inter.send(msg)
            return
        if edition <= 0:
            await inter.send("Il numero dell'edizione dev'essere maggiore di 0.")
            return
        if self.debugging:
            channel = inter.guild.get_channel(int(MyChannels.TXT_TESTING))
        else:
            match tournament:
                case "Italian League":
                    channel = inter.guild.get_channel(int(MyChannels.TXT_PODIO_LEAGUE))
                case "Italian Cup":
                    channel = inter.guild.get_channel(int(MyChannels.TXT_PODIO_CUP))
                case _:
                    channel = inter.guild.get_channel(int(MyChannels.TXT_TESTING))
        try:
            await inter.response.send_modal(modal=ModalPodium(channel, tournament, edition, pos, image))
        except Exception as error:
            print(error)
            msg = f"**Errore** `podium(inter, {tournament}, {edition}, {pos}, {image})`"
            await inter.response.send_message(f"{msg} Controllare il terminale e/o log.")


def setup(bot):
    bot.add_cog(TournamentRanking(bot))

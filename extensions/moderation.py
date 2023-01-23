from disnake import ApplicationCommandInteraction, Role, TextChannel, Member
from disnake.ext import commands

from api.mongo.api import ApiMongoDB
from api.wows.api import WoWsSession
from models.enum.discord_id import MyRoles
from models.modal import Modal
from settings import config
from utils.functions import check_role, is_debugging


class Moderation(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot
        self.debugging = is_debugging()
        self.api_wows = WoWsSession(config.data["APPLICATION_ID"], is_debugging())
        self.api_mongo = ApiMongoDB()

    @commands.slash_command(name="messaggio", description="Scrive un messaggio embed e menziona un ruolo.")
    async def write_message(
            self,
            inter: ApplicationCommandInteraction,
            channel: TextChannel = commands.Param(name="canale"),
            role: Role | None = commands.Param(name="ruolo", default=None)
    ) -> None:
        if not await check_role(inter, MyRoles.ADMIN):
            await inter.send("Non hai i permessi.")
            return
        try:
            await inter.response.send_modal(modal=Modal(role, channel))
        except Exception as error:
            print(error)
            await inter.send(f"**Errore** `write_message(inter, <#{channel.id}>)")


def setup(bot):
    bot.add_cog(Moderation(bot))

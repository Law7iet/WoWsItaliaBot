from disnake import ApplicationCommandInteraction, Role, TextChannel
from disnake.ext import commands

from api.wows.api import WoWsSession
from models.my_enum.roles_enum import RolesEnum
from models.my_enum.channels_enum import ChannelsEnum
from settings import config
from utils.functions import check_role, is_debugging
from utils.modal import Modal


class Moderation(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot
        self.debugging = is_debugging()
        self.wargaming_api = WoWsSession(config.data["APPLICATION_ID"], is_debugging())

    @commands.slash_command(name="write", description="Write a embed message and ping a role to notify them.")
    async def write(self, inter: ApplicationCommandInteraction, canale: TextChannel, ruolo: Role) -> None:
        if not await check_role(inter, RolesEnum.ADMIN):
            await inter.send("Non hai i permessi.")
            return
        try:
            await inter.response.send_modal(modal=Modal(ruolo, canale))
        except Exception as error:
            await self.bot.get_channel(int(ChannelsEnum.TXT_TESTING)).send("**>write command exception**")
            await self.bot.get_channel(int(ChannelsEnum.TXT_TESTING)).send("```" + str(error) + "```")


def setup(bot):
    bot.add_cog(Moderation(bot))

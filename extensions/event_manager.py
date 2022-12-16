from disnake import Message, MessageInteraction
from disnake.ext import commands

from api.mongo.api import ApiMongoDB
from models.my_enum.channels_enum import ChannelsEnum
from models.my_enum.roles_enum import RolesEnum


class EventManager(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot
        self.api_mongo_db = ApiMongoDB()

    @commands.Cog.listener()
    async def on_message(self, message: Message):
        if message.author.bot and message.channel.id == int(ChannelsEnum.TXT_DEV_BLOG):
            await message.publish()

    @commands.Cog.listener("on_button_click")
    async def help_listener(self, inter: MessageInteraction):
        if inter.component.custom_id not in ["logout"]:
            # We filter out any other button presses except the components we wish to process.
            return

        elif inter.component.custom_id == "logout":
            data = self.api_mongo_db.delete_player(str(inter.author.id))
            try:
                if data.deleted_count == 1:
                    await inter.author.remove_roles(inter.guild.get_role(int(RolesEnum.AUTH)))
                    await inter.author.edit(nick=None)
                    await inter.response.send_message("Hai effettuato correttamente il logout.", ephemeral=True)
            except AttributeError:
                await inter.response.send_message("Non hai effettuato il login.", ephemeral=True)


def setup(bot):
    bot.add_cog(EventManager(bot))

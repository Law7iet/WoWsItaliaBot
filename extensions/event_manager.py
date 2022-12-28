from disnake import Message, MessageInteraction
from disnake.ext import commands

from api.mongo.api import ApiMongoDB
from models.my_enum.channels_enum import ChannelsEnum

from utils.functions import logout


class EventManager(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot
        self.api_mongo = ApiMongoDB()

    @commands.Cog.listener()
    async def on_message(self, message: Message) -> None:
        if message.author.bot and message.channel.id == int(ChannelsEnum.TXT_DEV_BLOG):
            await message.publish()

    @commands.Cog.listener("on_button_click")
    async def help_listener(self, inter: MessageInteraction) -> None:
        if inter.component.custom_id not in ["logout"]:
            return
        elif inter.component.custom_id == "logout":
            await logout(inter, self.api_mongo)


def setup(bot):
    bot.add_cog(EventManager(bot))

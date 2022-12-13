from disnake import Message
from disnake.ext import commands

from models.my_enum.channels_enum import ChannelsEnum


class EventManager(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot

    @commands.Cog.listener()
    async def on_message(self, message: Message):
        if message.author.bot and message.channel.id == int(ChannelsEnum.TXT_DEV_BLOG):
            await message.publish()


def setup(bot):
    bot.add_cog(EventManager(bot))

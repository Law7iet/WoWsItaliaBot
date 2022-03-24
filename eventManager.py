from discord.ext import commands
from utils import *

class EventManager(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.Cog.listener()
    async def on_message(self, message):
        if message.author.bot and message.channel.id == CH_TXT_DEV_BLOG:
            await message.publish()

def setup(bot):
    bot.add_cog(EventManager(bot))
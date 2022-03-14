from discord.ext import commands
from utils.constants import CH_TXT_DEV_BLOG

class EventManager(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.Cog.listener()
    async def on_message(message):
        if message.author.bot and message.channel.id == CH_TXT_DEV_BLOG:
            message.publish()

def setup(bot):
    bot.add_cog(EventManager(bot))
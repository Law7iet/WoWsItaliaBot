from discord.ext import commands
from discord import Message
from utils.constants import CH_TXT_DEV_BLOG, CH_TXT_CLASSIFICA_CB


class EventManager(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot

    @commands.Cog.listener()
    async def on_message(self, message: Message):
        if message.author.bot and message.channel.id == CH_TXT_DEV_BLOG:
            await message.publish()
        # if message.author.bot and message.channel.id == CH_TXT_CLASSIFICA_CB:
        #     await message.publish()
        match message.content.split(' ')[0]:
            case '>pick_map':
                await message.channel.send("Pong")


def setup(bot):
    bot.add_cog(EventManager(bot))

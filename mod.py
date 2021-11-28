from discord.ext import commands
from utils import *

class Mod(commands.Cog):

    def __init__(self, bot):
        self.bot = bot

    @commands.command()
    async def write(self, ctx, channel_id, *message):
        admin_role = ctx.guild.get_role(ADMIN)
        if admin_role in ctx.author.roles:
            guild = ctx.guild
            channel = guild.get_channel(int(channel_id))
            text = ""
            for word in message:
                text = text + " " + word
            await channel.send(text)
        else:
            await ctx.send("Permesso negato")

    @commands.command()
    async def edit(self, ctx, channel_id, message_id, *new_message):
        admin_role = ctx.guild.get_role(ADMIN)
        if admin_role in ctx.author.roles:
            guild = ctx.guild
            channel = guild.get_channel(int(channel_id))
            message = await channel.fetch_message(int(message_id))
            text = ""
            for word in new_message:
                text = text + " " + word
            await message.edit(content = text)
        else:
            await ctx.send("Permesso negato")


def setup(bot):
    bot.add_cog(Mod(bot))
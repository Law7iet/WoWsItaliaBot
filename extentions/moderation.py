import re

from discord.ext import commands

from api.wargaming import ApiWargaming
from utils.constants import *
from utils.functions import my_align


class Moderation(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot

    @commands.command()
    async def write(self, ctx: commands.context.Context, channel_id: str, *, message: str):
        try:
            admin_role = ctx.guild.get_role(ROLE_ADMIN)
            if admin_role in ctx.author.roles:
                guild = ctx.guild
                # Discord 1.7.3
                # channel = guild.get_channel(int(channel_id)) if not DEBUG else self.bot.get_channel(CH_TXT_ADMIN)
                channel = guild.get_channel_or_thread(int(channel_id)) if not DEBUG else self.bot.get_channel(
                    CH_TXT_ADMIN)
                await channel.send(message)
            else:
                await ctx.send("Permesso negato")
        except Exception as error:
            print(error)
            return

    @commands.command()
    async def edit(self, ctx: commands.context.Context, channel_id: str, message_id: str, *, new_message: str):
        try:
            admin_role = ctx.guild.get_role(ROLE_ADMIN)
            if admin_role in ctx.author.roles:
                guild = ctx.guild
                # Discord 1.7.3
                # channel = guild.get_channel(int(channel_id))
                channel = guild.get_channel_or_thread(int(channel_id))
                message = await channel.fetch_message(int(message_id))
                await message.edit(content=new_message)
            else:
                await ctx.send("Permesso negato")
        except Exception as error:
            print(error)
            return

    @commands.command()
    async def nickname(self, ctx: commands.context.Context):
        try:
            admin_role = ctx.guild.get_role(ROLE_ADMIN)
            if admin_role in ctx.author.roles:
                # Get all the server's members
                guild = ctx.guild
                members = guild.members
                for member in members:
                    # Print check
                    # print(fun.my_align(member.display_name, 35, "left"))
                    # Skip if member has admin, mod, cc, cm, org tag
                    if guild.get_role(ROLE_ADMIN) in member.roles:
                        continue
                    if guild.get_role(ROLE_MODERATORE) in member.roles:
                        continue
                    if guild.get_role(ROLE_CM) in member.roles:
                        continue
                    if guild.get_role(ROLE_CC) in member.roles:
                        continue
                    if guild.get_role(ROLE_ORG_CUP) in member.roles:
                        continue
                    if guild.get_role(ROLE_ORG_LEAGUE) in member.roles:
                        continue
                    # Select who has "marinario" role
                    if guild.get_role(ROLE_MARINAIO) in member.roles:
                        api = ApiWargaming()
                        # select their nickname or their name if they don't have a nickname
                        user = member.display_name
                        # delete clan tag and their real name
                        user = re.sub(r'[.+]', '', user)
                        user = user.lstrip()
                        name = re.search(r'\(([A-Za-z0-9_]+)\)', user)
                        if name is not None:
                            user = re.sub(r'\(.+\)', '', user)
                            name = name.group(1)
                        # get user's nickname and his clan tag using WoWs API
                        player_info = api.get_player_by_nick(user)
                        if not player_info:
                            print(my_align(member.display_name, 35, "left") + "non è stato trovato")
                            continue
                        try:
                            player_id = player_info[0]
                            game_nick = player_info[1]
                            clan_id = api.get_clan_by_player_id(player_id)
                            # select user's nickname
                            new_nick = game_nick
                            if clan_id:
                                # add his clan's tag
                                clanInfo = api.get_clan_name_by_id(clan_id[0])
                                new_nick = '[' + clanInfo[1] + '] ' + game_nick

                            if name is not None and len(new_nick + ' (' + name + ')') <= 32:
                                # add his name
                                new_nick = new_nick + ' (' + name + ')'
                            # change nickname
                            if new_nick is not member.display_name:
                                await member.edit(nick=new_nick)
                                print(my_align(member.display_name, 35, "left") + "-> " + new_nick)
                        except Exception as error:
                            print("api.get_player_by_nick(user)")
                            pass
                            # await ctx.send('Il membro `' + user + '` non è stato trovato.')

                await ctx.send("Aggiornamento finito")
            else:
                await ctx.send("Permesso negato")
        except Exception as error:
            # print(error)
            return


def setup(bot):
    bot.add_cog(Moderation(bot))

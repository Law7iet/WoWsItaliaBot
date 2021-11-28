import fun
import re
from discord.ext import commands
from utils import *

class Nickname(commands.Cog):

    def __init__(self, bot):
        self.bot = bot

    @commands.command()
    async def nickname(self, ctx):
        # Get all the server's members
        guild = ctx.guild
        members = guild.members
        for member in members:
            # Print check
            #print(fun.my_align(member.display_name, 35, "left"))
            # Skip if member has admin, mod, cc, cm, org tag
            if guild.get_role(ADMIN) in member.roles:
                continue
            if guild.get_role(MOD) in member.roles:
                continue
            if guild.get_role(CM) in member.roles:
                continue
            if guild.get_role(CC) in member.roles:
                continue
            if guild.get_role(ORG) in member.roles:
                continue
            # Select who has marinario
            if guild.get_role(MARINAIO) in member.roles:
                # select their nickname or their name if they don't have a nickname
                user = member.display_name
                # delete clan tag and their real name
                user = re.sub(r'\[.+\]', '', user)
                user = user.lstrip()
                name = re.search(r'\(([A-Za-z0-9_]+)\)', user)
                if name != None:
                    user = re.sub(r'\(.+\)', '', user)
                    name = name.group(1)
                # get user's nickname and his's clan tag using WoWs API
                player_info = fun.get_player_ID(user)
                try:
                    game_nick = player_info[0]
                    player_id = player_info[1]
                    clan_id = fun.get_clan_ID(player_id)
                    # select user's nickname
                    new_nick = game_nick
                    if clan_id != -1:
                        # add his clan's tag
                        clan_tag = fun.get_clan_name(clan_id)
                        new_nick = '[' + clan_tag + '] ' + game_nick
                    if name != None and len(new_nick + ' (' + name + ')') <= 32:
                        # add his name
                        new_nick = new_nick + ' (' + name + ')'
                    # change nickname
                    await member.edit(nick=new_nick)
                    print(fun.my_align(member.display_name, 35, "left") + "-> " + new_nick)
                except:
                    #pass
                    print(fun.my_align(member.display_name, 35, "left") + "non è stato trovato")
                    # await ctx.send('Il membro `' + user + '` non è stato trovato.')
        await ctx.send("Aggiornamento finito")

def setup(bot):
    bot.add_cog(Nickname(bot))
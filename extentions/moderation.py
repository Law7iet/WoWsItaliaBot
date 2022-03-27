import re

from discord.ext import commands

from api.wargaming import ApiWargaming
from models.my_enum.roles_enum import RolesEnum
from utils.constants import *
from utils.functions import my_align, check_role


class Moderation(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot
        self.wargamingApi = ApiWargaming()

    @commands.command()
    async def write(self, ctx: commands.context.Context, channel_id: str, *, message: str):
        if not await check_role(ctx, RolesEnum.ADMIN):
            return
        try:
            guild = ctx.guild
            # Discord 1.7.3
            # channel = guild.get_channel(int(channel_id)) if not DEBUG else self.bot.get_channel(CH_TXT_ADMIN)
            channel = guild.get_channel_or_thread(int(channel_id)) if not DEBUG else self.bot.get_channel(
                CH_TXT_TESTING)
            await channel.send(message)
        except Exception as error:
            await self.bot.get_channel(CH_TXT_TESTING).send('**>write command exception**')
            await self.bot.get_channel(CH_TXT_TESTING).send('```' + str(error) + '```')

    @commands.command()
    async def edit(self, ctx: commands.context.Context, channel_id: str, message_id: str, *, new_message: str):
        if not await check_role(ctx, RolesEnum.ADMIN):
            return
        try:
            guild = ctx.guild
            # Discord 1.7.3
            # channel = guild.get_channel(int(channel_id))
            channel = guild.get_channel_or_thread(int(channel_id))
            message = await channel.fetch_message(int(message_id))
            await message.edit(content=new_message)
        except Exception as error:
            await self.bot.get_channel(CH_TXT_TESTING).send('**>edit command exception**')
            await self.bot.get_channel(CH_TXT_TESTING).send('```' + str(error) + '```')

    @commands.command()
    async def nickname(self, ctx: commands.context.Context):
        if not await check_role(ctx, RolesEnum.ADMIN):
            return
        try:
            # Get all the server's members
            guild = ctx.guild
            members = guild.members
            for member in members:
                try:
                    # Print check
                    # if DEBUG:
                    #     print(my_align(member.display_name, 35, 'left'))

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
                    if not(guild.get_role(ROLE_MARINAIO) in member.roles):
                        continue

                    # Select their nickname or their name if they don't have a nickname
                    user = member.display_name
                    # Delete clan tag and their real name
                    user = re.sub(r'\[.+\]', '', user)
                    user = user.lstrip()
                    name = re.search(r'\(([A-Za-z0-9_]+)\)', user)
                    if name is not None:
                        user = re.sub(r'\(.+\)', '', user)
                        name = name.group(1)
                    # Get user's nickname and his clan tag using WoWs API
                    player_info = self.wargamingApi.get_player_by_nick(user)
                    if not player_info:
                        # The string "user" isn't an in-game nickname
                        if DEBUG:
                            print(my_align(member.display_name, 35, 'left') + 'non è stato trovato')
                        continue
                    player_id = player_info[0]
                    game_nick = player_info[1]
                    # Select user's nickname
                    new_nick = game_nick
                    # Check if user is in a clan
                    clan_id = self.wargamingApi.get_clan_by_player_id(player_id)
                    if clan_id:
                        # The user has a clan. Add his clan's tag
                        clanInfo = self.wargamingApi.get_clan_name_by_id(clan_id[0])
                        new_nick = '[' + clanInfo[1] + '] ' + game_nick
                    # Check if the user has a name. If it's true restore the name if is shorter than 32
                    if name is not None and len(new_nick + ' (' + name + ')') <= 32:
                        # Add his name
                        new_nick = new_nick + ' (' + name + ')'
                    # Change nickname if the original nickname was changed
                    if new_nick is not member.display_name:
                        await member.edit(nick=new_nick)
                        if DEBUG:
                            print(my_align(member.display_name, 35, 'left') + '-> ' + new_nick)
                except Exception as error:
                    # Unexpected error during the member iteration
                    await self.bot.get_channel(CH_TXT_TESTING).send('**>nickname command exception in the iteration**')
                    await self.bot.get_channel(CH_TXT_TESTING).send('```' + str(error) + '```')
                    # Continue the iteration
                    pass
            await ctx.send('Aggiornamento finito')
        except Exception as error:
            await self.bot.get_channel(CH_TXT_TESTING).send('**>nickname command exception**')
            await self.bot.get_channel(CH_TXT_TESTING).send('```' + str(error) + '```')


def setup(bot):
    bot.add_cog(Moderation(bot))

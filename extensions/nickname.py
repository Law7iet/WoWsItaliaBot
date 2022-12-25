import re

from disnake import ApplicationCommandInteraction
from disnake.ext import commands

from api.wows.api import WoWsSession
from models.my_enum.roles_enum import RolesEnum
from settings import config
from utils.functions import my_align, send_response_and_clear, check_role, is_debugging


class Nickname(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot
        self.debugging = is_debugging()
        self.api_wows = WoWsSession(config.data["APPLICATION_ID"], is_debugging())

    async def check_own_nickname(self, inter: ApplicationCommandInteraction):
        return

    @commands.slash_command(name="controlla-nickname", description="Controlla che il nickname sia corretto.")
    async def nickname(self, inter: ApplicationCommandInteraction):
        # Get user has AUTH
        # Check if is admin
        await inter.response.defer()
        if not await check_role(inter, RolesEnum.ADMIN):
            await inter.send("Non hai i permessi.")
            return
        # Get all the server's members
        guild = inter.guild
        members = guild.members
        for member in members:
            # Print check
            if self.debugging:
                print("USER: " + my_align(member.display_name, 35, "left"))

            # Skip if member has admin, mod, cc, cm, org tag
            if guild.get_role(int(RolesEnum.ADMIN)) in member.roles:
                continue
            if guild.get_role(int(RolesEnum.MOD)) in member.roles:
                continue
            if guild.get_role(int(RolesEnum.CM)) in member.roles:
                continue
            if guild.get_role(int(RolesEnum.CC)) in member.roles:
                continue
            if guild.get_role(int(RolesEnum.ORG_CUP)) in member.roles:
                continue
            if guild.get_role(int(RolesEnum.ORG_LEAGUE)) in member.roles:
                continue
            if guild.get_role(int(RolesEnum.REF)) in member.roles:
                continue
            # Select who has "marinario" role
            if not (guild.get_role(int(RolesEnum.SAILOR)) in member.roles):
                continue
            # Select nickname
            tmp = re.sub(r"\[.+]", "", member.display_name)
            tmp = re.sub(r"\(.+\)", "", tmp)
            old_nick = tmp.lstrip().rstrip()
            # Select clan tag
            try:
                old_tag = re.search(r"\[.+]", member.display_name).group(0)[1:-1]
            except AttributeError:
                old_tag = ''
            # Select name
            try:
                name = re.search(r"\(.+\)", member.display_name).group(0)
            except AttributeError:
                name = ''
            # Get user's current nickname and his clan tag using WoWs API
            try:
                player_info = self.api_wows.players(old_nick)[0]
            except IndexError:
                print(my_align(member.display_name, 35, 'left') + 'non è stato trovato')
                continue
            player_id = player_info["account_id"]
            game_nick = player_info["nickname"]
            # Select user's nickname
            new_nick = game_nick
            # Check if user is in a clan
            try:
                # The player has a clan
                clan_id = self.api_wows.player_clan_data([player_id])[0]["clan_id"]
                if clan_id:
                    clan_tag = self.api_wows.clan_detail([clan_id])[0]["tag"]
                    new_tag = "[" + clan_tag + "] "
                else:
                    raise IndexError
            except IndexError:
                # The players don't have a clan
                new_tag = ""

            # Check if the user changed clan
            if old_tag != new_tag[1:-2]:
                representation = guild.get_role(int(RolesEnum.REP))
                if representation in member.roles:
                    await member.remove_roles(representation)
            # Check if the user has a name. If it's true restore the name if is shorter than 32
            final_nick = new_tag + new_nick
            if name != "":
                if len(final_nick + " " + name) <= 32:
                    final_nick = final_nick + " " + name
            # Change nickname if the original nickname was changed
            if final_nick != member.display_name:
                await member.edit(nick=final_nick)
                if self.debugging:
                    print(my_align(member.display_name, 35, 'left') + '-> ' + final_nick)

        await send_response_and_clear(inter, True, "Fatto!")


def setup(bot):
    bot.add_cog(Nickname(bot))

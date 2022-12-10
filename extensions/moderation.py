import re

from disnake import ApplicationCommandInteraction, Role, TextChannel
from disnake.ext import commands

from api.wows.api import WoWsSession
from models.my_enum.roles_enum import RolesEnum
from settings import config
from utils.constants import CH_TXT_TESTING
from utils.functions import my_align, send_response_and_clear, check_role, is_debugging
from utils.modal import Modal


class Moderation(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot
        self.debugging = is_debugging()
        self.wargaming_api = WoWsSession(config.data["APPLICATION_ID"], is_debugging())

    @commands.slash_command(name="write", description="Write a embed message and ping a role to notify them.")
    async def write(self, inter: ApplicationCommandInteraction, canale: TextChannel, ruolo: Role) -> None:
        if not await check_role(inter, RolesEnum.ADMIN):
            await inter.send("Non hai i permessi.")
            return
        try:
            await inter.response.send_modal(modal=Modal(ruolo, canale))
        except Exception as error:
            await self.bot.get_channel(CH_TXT_TESTING).send("**>write command exception**")
            await self.bot.get_channel(CH_TXT_TESTING).send("```" + str(error) + "```")

    @commands.slash_command(name="nickname", description="Change the members' nickname with the in-game nickname")
    async def nickname(self, inter: ApplicationCommandInteraction):
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
                player_info = self.wargaming_api.players(old_nick)[0]
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
                clan_id = self.wargaming_api.player_clan_data([player_id])[0]["clan_id"]
                if clan_id:
                    clan_tag = self.wargaming_api.clan_detail([clan_id])[0]["tag"]
                    new_tag = clan_tag
                else:
                    raise IndexError
            except IndexError:
                # The players don't have a clan
                new_tag = ""

            # Check if the user changed clan
            if old_tag != new_tag:
                representation = guild.get_role(int(RolesEnum.REP))
                if representation in member.roles:
                    await member.remove_roles(representation)
            # Check if the user has a name. If it's true restore the name if is shorter than 32
            final_nick = "[" + new_tag + "] " + new_nick
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
    bot.add_cog(Moderation(bot))

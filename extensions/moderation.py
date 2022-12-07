import re

from disnake import ApplicationCommandInteraction, Role, TextChannel
from disnake.ext import commands

from api.wargaming import ApiWargaming
from utils.constants import *
from utils.functions import my_align, send_response_and_clear, check_role
from utils.modal import Modal


class Moderation(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot
        self.wargamingApi = ApiWargaming()

    @commands.slash_command(name="write", description="Write a embed message and ping a role to notify them.")
    async def write(
            self,
            inter: ApplicationCommandInteraction,
            canale: TextChannel,
            ruolo: Role
    ) -> None:
        if not await check_role(inter, inter.guild.get_role(ROLE_ADMIN)):
            await send_response_and_clear(inter, False, "Non hai i permessi.")
            return
        try:
            await inter.response.send_modal(modal=Modal(ruolo, canale))
        except Exception as error:
            await self.bot.get_channel(CH_TXT_TESTING).send('**>write command exception**')
            await self.bot.get_channel(CH_TXT_TESTING).send('```' + str(error) + '```')

    @commands.slash_command(name="nickname", description="Change the members' nickname with the in-game nickname")
    async def nickname(self, inter: ApplicationCommandInteraction):
        await inter.response.defer()
        if not await check_role(inter, inter.guild.get_role(ROLE_ADMIN)):
            await send_response_and_clear(inter, False, "Non hai i permessi.")
            return
        try:
            # Get all the server's members
            guild = inter.guild
            members = guild.members
            for member in members:
                try:
                    # Print check
                    if DEBUG:
                        print("USER: " + my_align(member.display_name, 35, 'left'))

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
                    if guild.get_role(ROLE_ARBITRO) in member.roles:
                        continue
                    # Select who has "marinario" role
                    if not (guild.get_role(ROLE_MARINAIO) in member.roles):
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
                    player_info = self.wargamingApi.get_player_by_nick(old_nick)
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
                    clan_id = self.wargamingApi.get_clan_by_player_id(str(player_id))
                    new_tag = ""
                    if clan_id is not None:
                        if clan_id[0] is not None:
                            # The user has a clan. Find the clan tag
                            clanInfo = self.wargamingApi.get_clan_name_by_id(str(clan_id[0]))
                            new_tag = "[" + clanInfo[1] + "]"

                    # Check if the user changed clan
                    if old_tag != new_tag:
                        representation = guild.get_role(ROLE_RAPPRESENTANTE_CLAN)
                        if representation in member.roles:
                            await member.remove_roles(representation)

                    # Check if the user has a name. If it's true restore the name if is shorter than 32
                    final_nick = new_tag + ' ' + new_nick
                    if name != "":
                        if len(final_nick + ' (' + name + ')') <= 32:
                            final_nick = final_nick + " " + name

                    # Change nickname if the original nickname was changed
                    if final_nick != member.display_name:
                        await member.edit(nick=final_nick)
                        if DEBUG:
                            print(my_align(member.display_name, 35, 'left') + '-> ' + final_nick)

                except Exception as error:
                    # Unexpected error during the member iteration
                    await self.bot.get_channel(CH_TXT_TESTING).send('**>nickname command exception in the iteration**')
                    await self.bot.get_channel(CH_TXT_TESTING).send('```' + str(error) + '```')
                    # Continue the iteration
                    pass
            await send_response_and_clear(inter, True, "Fatto!")
        except Exception as error:
            await self.bot.get_channel(CH_TXT_TESTING).send('**>nickname command exception**')
            await self.bot.get_channel(CH_TXT_TESTING).send('```' + str(error) + '```')


def setup(bot):
    bot.add_cog(Moderation(bot))

import re

from disnake import ApplicationCommandInteraction, errors
from disnake.ext import commands

from api.mongo.api import ApiMongoDB
from api.wows.api import WoWsSession
from models.enum.discord_id import MyRoles
from settings import config
from utils.functions import align, check_role, is_debugging, remove_representation


class Nickname(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot
        self.debugging = is_debugging()
        self.api_wows = WoWsSession(config.data["APPLICATION_ID"], is_debugging())
        self.api_mongo = ApiMongoDB()

    @commands.slash_command(name="nickname", description="Controlla il nome in gioco e imposta il nickname.")
    async def check_own_nickname(
            self,
            inter: ApplicationCommandInteraction,
            nickname: str | None = commands.Param(min_length=1, max_length=28, default=None)
    ) -> None:
        await inter.response.defer()
        if not await check_role(inter, MyRoles.AUTH):
            await inter.send("Non sei autenticato. Digita `/login`")
            return
        try:
            player_id = self.api_mongo.get_player_by_discord(str(inter.author.id))["wows_id"]
            player = self.api_wows.player_personal_data([player_id])[0]
        except (KeyError, IndexError):
            await inter.send(f"Errore utente <@{inter.author.id}> non trovato.")
            return
        try:
            old_tag = re.search(r"\[.+]", inter.author.display_name).group(0)[1:-1]
        except AttributeError:
            old_tag = ""
        new_nickname = player["nickname"]
        try:
            clan_id = self.api_wows.player_clan_data([player_id])[0]["clan_id"]
            clan_tag = "[" + self.api_wows.clan_detail([clan_id])[0]["tag"] + "] "
        except (KeyError, IndexError):
            clan_tag = ""
        new_nickname = clan_tag + new_nickname
        if len(new_nickname + nickname) + 3 <= 32:
            new_nickname = f"{new_nickname} ({nickname})"
            if clan_tag != old_tag:
                representation = inter.guild.get_role(int(MyRoles.REP))
                if representation in inter.author.roles:
                    if not await remove_representation(inter.author, representation, self.api_mongo, old_tag):
                        await inter.send(f"Rappresentante non rimosso nel clan {old_tag} nel database.")
                        return
            msg = "Fatto!"
            try:
                await inter.author.edit(nick=new_nickname)
            except errors.Forbidden:
                msg = f"{msg}\nPermessi negati durante la modifica dell'utente <@{inter.author.id}>."
            await inter.send(msg)
        else:
            max_length = 32 - len(new_nickname) - 3
            await inter.send(f"Il nickname è troppo lungo. Utilizza un nickname di {max_length} caratteri.")

    @commands.slash_command(name="mod-nickname", description="Controlla che i nickname sia corretto.")
    async def check_nickname(self, inter: ApplicationCommandInteraction):
        # Get user has AUTH
        # Check if the user has the admin role.
        await inter.response.defer()
        if not await check_role(inter, MyRoles.ADMIN):
            await inter.send("Non hai i permessi.")
            return
        # Get all the server's members
        guild = inter.guild
        members = guild.members
        for member in members:
            # Print check
            if self.debugging:
                print("USER: " + align(member.display_name, 35, "left"))
            # Skip if member has admin, mod, cc, cm, org tag
            if guild.get_role(int(MyRoles.ADMIN)) in member.roles:
                continue
            if guild.get_role(int(MyRoles.MOD)) in member.roles:
                continue
            if guild.get_role(int(MyRoles.CM)) in member.roles:
                continue
            if guild.get_role(int(MyRoles.CC)) in member.roles:
                continue
            if guild.get_role(int(MyRoles.ORG_CUP)) in member.roles:
                continue
            if guild.get_role(int(MyRoles.ORG_LEAGUE)) in member.roles:
                continue
            if guild.get_role(int(MyRoles.REF)) in member.roles:
                continue
            # Select who has 'marinario' role
            if not (guild.get_role(int(MyRoles.SAILOR)) in member.roles):
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
            # Get the nickname, and the clan tag of the current user using the WoWs' API.
            try:
                player_info = self.api_wows.players(old_nick)[0]
            except IndexError:
                print(align(member.display_name, 35, 'left') + 'non è stato trovato')
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
                representation = guild.get_role(int(MyRoles.REP))
                if representation in member.roles:
                    if not await remove_representation(member, representation, self.api_mongo, old_tag):
                        await inter.send("Non è stato possibile modificare il database.")
            # Check if the user has a name. If it is true restore the name if is shorter than 32.
            final_nick = new_tag + new_nick
            if name != "":
                if len(final_nick + " " + name) <= 32:
                    final_nick = final_nick + " " + name
            # Change nickname if the original nickname was changed
            if final_nick != member.display_name:
                await member.edit(nick=final_nick)
                if self.debugging:
                    print(align(member.display_name, 35, 'left') + '-> ' + final_nick)

        await inter.send("Fatto!")


def setup(bot):
    bot.add_cog(Nickname(bot))

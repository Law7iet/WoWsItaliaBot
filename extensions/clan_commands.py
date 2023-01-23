import re

from disnake import ApplicationCommandInteraction, Embed, Member
from disnake.ext import commands

from api.mongo.api import ApiMongoDB
from api.wows.api import WoWsSession
from models.enum.discord_id import MyRoles
from settings import config
from utils.functions import check_role, is_debugging


class ClanCommands(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot
        self.api_mongo = ApiMongoDB()
        self.api_wows = WoWsSession(config.data["APPLICATION_ID"], is_debugging())
        self.debugging = is_debugging()

    async def check_player(self, inter: ApplicationCommandInteraction, member: Member, clan_id: str) -> bool:
        """
        Check if the player is authenticated, and he is in the clan.

        Args:
            inter: the context.
            member: the clan member.
            clan_id: the clan identifier.

        Returns:
            A boolean value that states if the player is authenticated, and if hs is in the clan.

        """
        msg = f"**Errore** `check_player(inter, <@{member.id}>, {clan_id})`"
        if inter.guild.get_role(int(MyRoles.AUTH)) in member.roles:
            player = self.api_mongo.get_player_by_discord(str(member.id))
            if not player:
                # This should never happen: an authenticated player is not found in the database.
                await inter.send(f"{msg}\n<@{member.id}> non è nel database.")
                return False
            try:
                clan = self.api_wows.player_clan_data([player["wows"]])[0]
                if str(clan["clan_id"]) == clan_id:
                    return True
                else:
                    raise TypeError
            except (TypeError, IndexError):
                await inter.send(f"{msg}\n<@{member.id}> non è nel clan.")
                return False
        else:
            await inter.send(f"{msg}\n<@{member.id}> non è autenticato. Digita `/login`.")
            return False

    @commands.slash_command(name="clan-dettagli", description="Visualizza le statistiche di un clan nel dabatase.")
    async def details(
            self,
            inter: ApplicationCommandInteraction,
            clan_id: int = commands.Param(name="clan-id"),
    ) -> None:
        await inter.response.defer()
        details = self.api_mongo.get_clan_by_id(str(clan_id))
        if details:
            embed = Embed(title=details["name"], description=details["tag"], color=0xffffff)
            representations = ""
            for representant in details["representations"]:
                representations = representations + f"\n<@{representant}>"
            if representations:
                embed.add_field(name="Representants", value=representations, inline=False)
            await inter.send(embed=embed)
        else:
            await inter.send(f"Clan con ID {clan_id} non presente nel DB")

    @commands.slash_command(name="clan-aggiungi", description="Aggiunge un clan nel database.")
    async def insert(
            self,
            inter: ApplicationCommandInteraction,
            clan_id: int = commands.Param(name="clan-id"),
            rep_1: Member | None = commands.Param(name="rappresentante-1", default=None),
            rep_2: Member | None = commands.Param(name="rappresentante-2", default=None)
    ):
        if not await check_role(inter, MyRoles.MOD):
            await inter.response.send_message("Non hai i permessi.")
            return
        await inter.response.defer()
        # Check clan's identifier
        try:
            clan_detail = self.api_wows.clan_detail([clan_id])[0]
            if not clan_detail:
                raise IndexError
        except IndexError:
            await inter.send(f"Clan ID {clan_id} errato.")
            return
        # Check representations
        representation = []
        for rep in [rep_1, rep_2]:
            if rep:
                if await self.check_player(inter, rep, str(clan_detail["clan_id"])):
                    representation.append(str(rep.id))
                else:
                    return
        # Update data
        result = self.api_mongo.insert_clan({
            "id": clan_detail["clan_id"],
            "tag": clan_detail["tag"],
            "name": clan_detail["name"],
            "representations": representation
        })
        # Send output
        role = inter.guild.get_role(int(MyRoles.REP))
        if result:
            msg = "Clan " + clan_detail["tag"] + " inserito.\n"
            if rep_1 and rep_2:
                await rep_1.add_roles(role)
                await rep_2.add_roles(role)
                msg = msg + "Rappresentanti: <@" + str(rep_1.id) + "> e <@" + str(rep_2.id) + ">"
            elif rep_1:
                await rep_1.add_roles(role)
                msg = msg + "Rappresentante: <@" + str(rep_1.id) + ">"
            elif rep_2:
                await rep_2.add_roles(role)
                msg = msg + "Rappresentante: <@" + str(rep_2.id) + ">"
            await inter.send(msg)
        else:
            msg = f"**Errore.**\nDatabase non aggiornato."
            await inter.send(f"{msg} Controllare che il clan non sia già inserito e il terminale e/o log.")

    @commands.slash_command(name="clan-aggiorna", description="Aggiorna il nome e/o il tag del clan.")
    async def update(
            self,
            inter: ApplicationCommandInteraction,
            clan_id: int = commands.Param(name="clan-id")
    ) -> None:
        # Check clan's identifier
        clan = self.api_mongo.get_clan_by_id(str(clan_id))
        if not clan:
            await inter.send(f"Clan `{clan_id}` non trovato nel database.")
            return
        permission = False
        # Check permissions
        if await check_role(inter, MyRoles.MOD):
            permission = True
        elif await check_role(inter, MyRoles.REP):
            # Catturare il tag
            user_tag = re.search(r"\[.+]", inter.author.display_name)
            # He must have a user tag
            user_tag = user_tag.group(0)
            # Confrontare il tag col tag del clan id
            if clan["tag"] == user_tag[1:-1]:
                permission = True
        if permission:
            try:
                clan_detail = self.api_wows.clan_detail([clan_id])[0]
                if not clan_detail:
                    raise IndexError
            except IndexError:
                await inter.send(f"Clan ID {clan_id} errato.")
                return
            result = self.api_mongo.update_clan_by_id(
                clan_detail["clan_id"],
                {
                    "tag": clan_detail["tag"],
                    "name": clan_detail["name"]
                }
            )
            if result:
                await inter.send(f"Dati del clan {clan_id} aggiornati.")
            else:
                msg = f"**Errore.**\nDatabase non aggiornato."
                await inter.send(f"{msg} Controllare il terminale e/o log.")

    @commands.slash_command(name="clan-rimuovi", description="Rimuove un clan nel dabatase.")
    async def remove(
        self,
        inter: ApplicationCommandInteraction,
        clan_id: int = commands.Param(name="clan-id"),
    ) -> None:
        if not await check_role(inter, MyRoles.MOD):
            await inter.send("Non hai i permessi.")
            return
        await inter.response.defer()
        # Check clan's identifier
        clan = self.api_mongo.get_clan_by_id(str(clan_id))
        if not clan:
            await inter.send(f"Clan `{clan_id}` non trovato nel database.")
            return
        # Remove clan
        if self.api_mongo.delete_clan_by_id(str(clan_id)):
            # Clan removed
            # Remove representations role
            representations = clan["representations"]
            for rep_id in representations:
                rep = await inter.guild.get_member(int(rep_id))
                await rep.remove_roles(inter.guild.get_role(int(MyRoles.REP)))
            msg = "Clan rimosso."
        else:
            # Mongo error
            msg = "Clan non rimosso. Controllare che il clan non sia già inserito e il terminale e/o log."
        await inter.send(msg)


def setup(bot):
    bot.add_cog(ClanCommands(bot))

from disnake import ApplicationCommandInteraction, Role, TextChannel, Member
from disnake.ext import commands

from api.mongo.api import ApiMongoDB
from api.wows.api import WoWsSession
from models.enum.discord_id import MyRoles
from models.modal import Modal
from settings import config
from utils.functions import check_role, is_debugging


class Moderation(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot
        self.debugging = is_debugging()
        self.api_wows = WoWsSession(config.data["APPLICATION_ID"], is_debugging())
        self.api_mongo = ApiMongoDB()

    async def check_player(self, inter: ApplicationCommandInteraction, member: Member, clan_id: str) -> bool:
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

    @commands.slash_command(name="messaggio", description="Scrive un messaggio embed e menziona un ruolo.")
    async def write_message(
            self,
            inter: ApplicationCommandInteraction,
            channel: TextChannel = commands.Param(name="canale"),
            role: Role | None = commands.Param(name="ruolo", default=None)
    ) -> None:
        if not await check_role(inter, MyRoles.ADMIN):
            await inter.send("Non hai i permessi.")
            return
        try:
            await inter.response.send_modal(modal=Modal(role, channel))
        except Exception as error:
            print(error)
            await inter.send(f"**Errore** `write_message(inter, <#{channel.id}>)")

    @commands.slash_command(name="clan", description="Aggiunge o rimuove un clan nel dabatase.")
    async def clan(
        self,
        inter: ApplicationCommandInteraction,
        action: str = commands.Param(name="azione", choices=["Aggiungi", "Rimuovi"]),
        clan_id: int = commands.Param(name="clan-id"),
        rep_1: Member | None = commands.Param(name="rappresentante-1", default=None),
        rep_2: Member | None = commands.Param(name="rappresentante-2", default=None)
    ) -> None:
        if not await check_role(inter, MyRoles.MOD):
            await inter.send("Non hai i permessi.")
            return
        await inter.response.defer()
        role = inter.guild.get_role(int(MyRoles.REP))
        if action == "Aggiungi":
            # Check clan's identifier
            try:
                clan_detail = self.api_wows.clan_detail([clan_id])[0]
            except IndexError:
                await inter.send("Clan ID errato.")
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
                msg = f"**Error** `add_clan(inter, {clan_id}, <@{rep_1.id}>, <@{rep_2}>)`\nDatabase non aggiornato."
                await inter.send(f"{msg} Controllare che il clan non sia già inserito e il terminale e/o log.")
        else:
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
                    await rep.remove_roles(role)
                msg = "Clan rimosso."
            else:
                # Mongo error
                msg = "Clan non rimosso. Controllare che il clan non sia già inserito e il terminale e/o log."
            await inter.send(msg)


def setup(bot):
    bot.add_cog(Moderation(bot))

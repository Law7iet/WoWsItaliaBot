from disnake import ApplicationCommandInteraction, Member
from disnake.ext import commands

from api.mongo.api import ApiMongoDB
from api.wows.api import WoWsSession
from models.enum.discord_id import MyRoles
from settings import config
from utils.functions import check_role, is_debugging, sync_clan


class Representant(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot
        self.api_wows = WoWsSession(config.data["APPLICATION_ID"], is_debugging())
        self.api_mongo = ApiMongoDB()

    async def add(self, inter: ApplicationCommandInteraction, member: Member, clan: dict) -> None:
        if await check_role(inter, MyRoles.REP, member):
            await inter.send("Hai già i ruoli da rappresentante di clan.")
            return
        representations = clan["representations"]
        if len(representations) == 2:
            await inter.send("Il tuo clan ha già 2 rappresentanti di clan.")
        else:
            representations.append(str(member.id))
            updated_clan = self.api_mongo.update_clan_by_id(clan["id"], {"representations": representations})
            if updated_clan:
                await member.add_roles(inter.guild.get_role(int(MyRoles.REP)))
                await inter.send("Fatto!")
            else:
                await inter.send("Errore durante l'aggiornamento del clan. Controllare il terminale e/o log.")

    async def remove(self, inter: ApplicationCommandInteraction, member: Member, clan: dict) -> None:
        if not await check_role(inter, MyRoles.REP, member):
            await inter.send("Non sei un rappresentante di clan.")
            return
        representations = clan["representations"]
        representations.remove(str(member.id))
        updated_clan = self.api_mongo.update_clan_by_id(clan["id"], {"representations": representations})
        if updated_clan:
            await member.remove_roles(inter.guild.get_role(int(MyRoles.REP)))
            await inter.send("Fatto!")
        else:
            await inter.send("Errore durante l'aggiornamento del clan. Controllare il terminale e/o log.")

    async def representant(self, inter: ApplicationCommandInteraction, is_adding: bool, member: Member) -> None:
        # Get raw data
        player = self.api_mongo.get_player_by_discord(str(member.id))
        clan_id = self.api_wows.player_clan_data([player["wows"]])[0]["clan_id"]
        if not clan_id:
            await inter.send("Non fai parte di un clan.")
        else:
            # Sync mongo
            clan_mongo = await sync_clan(inter, self.api_mongo, self.api_wows, str(clan_id))
            # Add or remove
            if is_adding:
                await self.add(inter, member, clan_mongo)
            else:
                await self.remove(inter, member, clan_mongo)

    @commands.slash_command(name="rappresentante", description="Aggiunge o rimuove un rappresentante di un clan")
    async def representation(
            self,
            inter: ApplicationCommandInteraction,
            action: str = commands.Param(name="azione", choices=["Aggiungi", "Rimuovi"])
    ) -> None:
        await inter.response.defer()
        if not await check_role(inter, MyRoles.AUTH):
            await inter.send("Non hai i permessi: utente non autenticato. Effettua prima il login (`/login`)")
        else:
            await self.representant(inter, action == "Aggiungi", inter.author)

    @commands.slash_command(name="mod-rappresentante", description="Aggiunge o rimuove un rappresentante di un clan")
    async def mod_representation(
            self,
            inter: ApplicationCommandInteraction,
            action: str = commands.Param(name="azione", choices=["Aggiungi", "Rimuovi"]),
            user: Member = commands.Param(name="utente")
    ) -> None:
        await inter.response.defer()
        if not await check_role(inter, MyRoles.MOD):
            await inter.send("Non hai i permessi: utente non autenticato. Effettua prima il login (`/login`)")
        else:
            await self.representant(inter, action == "Aggiungi", user)


def setup(bot):
    bot.add_cog(Representant(bot))

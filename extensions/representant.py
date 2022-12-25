from disnake import ApplicationCommandInteraction
from disnake.ext import commands

from api.mongo.api import ApiMongoDB
from api.wows.api import WoWsSession
from models.my_enum.roles_enum import RolesEnum
from settings import config
from utils.functions import send_response_and_clear, check_role, is_debugging, check_clan

ActionOptions = commands.option_enum({
    "Aggiungi": "Aggiungi",
    "Rimuovi": "Rimuovi"
})


class Representant(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot
        self.api_wows = WoWsSession(config.data["APPLICATION_ID"], is_debugging())
        self.api_mongo = ApiMongoDB()

    @commands.slash_command(name="rappresentante", description="Aggiunge o rimuove un rappresentante di un clan")
    async def representant(self, inter: ApplicationCommandInteraction, azione: ActionOptions):
        await inter.response.defer()
        if not await check_role(inter, RolesEnum.AUTH):
            await inter.send("Non hai i permessi: utente non autenticato. Effettua prima il login (`/login`)")
            return
        player = self.api_mongo.get_player_by_discord(str(inter.author.id))
        clan_id = self.api_wows.player_clan_data([player["wows"]])[0]["clan_id"]
        if not clan_id:
            await inter.send("Non fai parte di un clan.")
            return
        # Sync mongo
        clan_mongo = await check_clan(inter, self.api_mongo, self.api_wows, str(clan_id))

        if azione == "Aggiungi":
            if await check_role(inter, RolesEnum.REP):
                await inter.send("Hai già i ruoli da rappresentante di clan.")
                return
            representations = clan_mongo["representations"]
            if len(representations) == 2:
                await inter.send("Il tuo clan ha già 2 rappresentanti di clan.")
                return
            representations.append(str(inter.author.id))
            x = self.api_mongo.update_clan_by_id(str(clan_id), {"representations": representations})
            await inter.author.add_roles(inter.guild.get_role(int(RolesEnum.REP)))
            await send_response_and_clear(inter, True, "Fatto!")
            print(x)
        else:
            if not await check_role(inter, RolesEnum.REP):
                await inter.send("Non sei un rappresentante di clan.")
                return
            representations = clan_mongo["representations"]
            representations.remove(str(inter.author.id))
            self.api_mongo.update_clan_by_id(str(clan_id), {"representations": representations})
            await inter.author.remove_roles(inter.guild.get_role(int(RolesEnum.REP)))
            await send_response_and_clear(inter, True, "Fatto!")


def setup(bot):
    bot.add_cog(Representant(bot))

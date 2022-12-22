import datetime

from disnake import ApplicationCommandInteraction
from disnake.ext import commands

from api.mongo.api import ApiMongoDB
from models.my_enum.database_enum import ConfigKeys
from models.my_enum.roles_enum import RolesEnum
from models.my_enum.channels_enum import ChannelsEnum
from utils.functions import check_role, send_response_and_clear

EventOptions = commands.option_enum({
    "Data di inizio": "Data di inizio",
    "Data di fine": "Data di fine"
})


class ClanBattleSettings(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot
        self.api_mongo_db = ApiMongoDB()

    async def getter(self, config_key: ConfigKeys) -> dict:
        config_file = self.api_mongo_db.get_config()
        return config_file["clan_battle_info"][str(config_key)]

    @commands.slash_command(name="clan-battle")
    async def clan_battle(self, inter: ApplicationCommandInteraction) -> None:
        pass

    @clan_battle.sub_command(name="get-season", description="Ritorna il numero della stagione delle clan battle.")
    async def get_season(self, inter: ApplicationCommandInteraction) -> None:
        value = await self.getter(ConfigKeys.CB_CURRENT_SEASON)
        if value:
            await inter.send('La stagione delle clan battle è: `' + str(value) + '`.')
        else:
            await inter.send('Valore incorretto: `' + str(value) + '`.')

    @clan_battle.sub_command(name="get-days", description="Ritorna le date delle clan battle")
    async def get_days(self, inter: ApplicationCommandInteraction) -> None:
        start = await self.getter(ConfigKeys.CB_STARTING_DAY)
        end = await self.getter(ConfigKeys.CB_ENDING_DAY)
        if start and end:
            await inter.send('Le date delle clan battle sono: `' + str(start) + '` e `' + str(end) + '`.')
        elif not start:
            await inter.send('Data d\'inizio vuota: : `' + str(start) + '`.')
        elif not end:
            await inter.send('Data di fine vuota: : `' + str(end) + '`.')

    @clan_battle.sub_command(name="set-season", description="Imposta il numero della stagione delle clan battle")
    async def set_season(self, inter: ApplicationCommandInteraction, season: str):
        if not await check_role(inter, RolesEnum.ADMIN):
            await inter.send("Non hai i permessi")
            return
        try:
            msg = "Errore durante l'impostazione della stagione. Controllare il terminale e/o log."
            value = int(season)
            if value <= 0:
                return
            data = {"clan_battle_info": {str(ConfigKeys.CB_CURRENT_SEASON): value}}
            if self.api_mongo_db.update_config(data):
                await inter.send('Impostato la stagione: `' + str(value) + '`.')
            else:
                await inter.send(msg)
        except Exception as error:
            print(f"set-season exception says: {error}")
            await inter.send(msg)

    @clan_battle.sub_command(name="set-days", description="Imposta i giorni delle clan battle: AAAA-MM-GG")
    async def set_days(self, inter: ApplicationCommandInteraction, start_date: str, end_date: str):
        if not await check_role(inter, RolesEnum.ADMIN):
            await inter.send("Non hai i permessi")
            return
        start = start_date.split('-')
        end = end_date.split('-')
        try:
            # Check integrity
            start = datetime.datetime(int(start[0]), int(start[1]), int(start[2]))
            end = datetime.datetime(int(end[0]), int(end[1]), int(end[2]))
        except Exception as error:
            print(error)
            await inter.send("Errore. Sintassi: AAAA-MM-GG AAAA-MM-GG")
            return
        else:
            data1 = {"clan_battle_info": {str(ConfigKeys.CB_STARTING_DAY): start.strftime('%Y-%m-%d')}}
            data2 = {"clan_battle_info": {str(ConfigKeys.CB_ENDING_DAY): end.strftime('%Y-%m-%d')}}
            res1 = self.api_mongo_db.update_config(data1)
            res2 = self.api_mongo_db.update_config(data2)
            msg = "Controllare il terminale e/o log."
            if res1 and res2:
                await inter.send("Impostato le date `" + start_date + "` e `" + end_date + "`.")
            elif res1:
                await inter.send("Impostato la data di inizio clan battle `" + start_date + "`.")
                await inter.channel.send("Errore durante l'impostazione della data di fine clan battle. " + msg)
            elif res2:
                await inter.send("Impostato la data di fine clan battle `" + end_date + "`.")
                await inter.channel.send("Errore durante l'impostazione della data di inizio clan battle. " + msg)
            else:
                await inter.send("Errore durante l'impostazione delle date delle clan battle." + msg)


def setup(bot):
    bot.add_cog(ClanBattleSettings(bot))

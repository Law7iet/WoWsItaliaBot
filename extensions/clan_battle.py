import datetime
import time

from disnake import ApplicationCommandInteraction
from disnake.ext import commands

from api.mongo.api import ApiMongoDB
from api.wows.api import cb_ranking
from models.my_class.clan import Clan
from models.my_enum.database_enum import ConfigKeys
from models.my_enum.league_type_enum import LeagueType
from models.my_enum.roles_enum import RolesEnum
from models.my_enum.channels_enum import ChannelsEnum
from utils.functions import align, convert_string_to_datetime, check_role

EventOptions = commands.option_enum({
    "Data di inizio": "Data di inizio",
    "Data di fine": "Data di fine"
})


class ClanBattle(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot
        self.api_mongo = ApiMongoDB()

    async def getter(self, config_key: ConfigKeys) -> dict:
        config_file = self.api_mongo.get_config()
        return config_file["clan_battle_info"][str(config_key)]

    def make_ranking(self, config: dict) -> list[list[[]]]:
        # Each element represent a league.
        # The leagues are Hurricane, Typhoon, Storm, Gale and Squall
        # Each league has 3 divisions
        # TODO: Hurricane has only one division.
        clan_battle_ranking = [[[], [], []], [[], [], []], [[], [], []], [[], [], []], [[], [], []]]
        for italian_clan in self.api_mongo.get_clans_by_name(''):
            data = cb_ranking(int(italian_clan['id']), self.debugging)
            for element in data:
                if str(element['season_number']) == str(config[str(ConfigKeys.CB_CURRENT_SEASON)]):
                    promotion = []
                    # Compute squad (str)
                    match element['team_number']:
                        case 1: squad = 'A'
                        case 2: squad = 'B'
                        case _: continue
                    # Compute tag (str)
                    tag = italian_clan['tag']
                    # Check if a clan is inactive in the clan battles
                    if element['battles_count'] == 0:
                        continue
                    # Compute win_rate (str)
                    win_rate = '%.2f' % (element['wins_count'] / element['battles_count'] * 100) + '%'
                    # Compute battles (int)
                    battles = element['battles_count']
                    # Compute league (LeagueType)
                    match element['league']:
                        case 0: league = LeagueType.HURRICANE
                        case 1: league = LeagueType.TYPHOON
                        case 2: league = LeagueType.STORM
                        case 3: league = LeagueType.GALE
                        case 4: league = LeagueType.SQUALL
                        case _: continue
                    # Compute division (int)
                    division = element['division']
                    # Compute division (int)
                    score = element['division_rating']
                    # Compute promotion (list(str))
                    if element['stage']:
                        progress = element['stage']['progress']
                        for promoBattle in progress:
                            match promoBattle:
                                case 'victory': promotion.append('+')
                                case 'defeat': promotion.append('-')
                                case _: continue
                    # Create a Clan instance
                    clan = Clan(tag, squad, win_rate, battles, league, division, score, promotion)
                    # Insert the clan to the correct league and division
                    clan_battle_ranking[int(clan.league)][clan.division - 1].append(clan)
        # Sorting
        for league in clan_battle_ranking:
            i = 0
            for division in league:
                league[i] = sorted(division, key=lambda x: x.score, reverse=True)
                i = i + 1
        return clan_battle_ranking

    @commands.slash_command(
        name="clan-battle-get-season",
        description="Ritorna il numero della stagione delle clan battle."
    )
    async def get_season(self, inter: ApplicationCommandInteraction) -> None:
        value = await self.getter(ConfigKeys.CB_CURRENT_SEASON)
        if value:
            await inter.send('La stagione delle clan battle è: `' + str(value) + '`.')
        else:
            await inter.send('Valore incorretto: `' + str(value) + '`.')

    @commands.slash_command(name="clan-battle-get-days", description="Ritorna le date delle clan battle")
    async def get_days(self, inter: ApplicationCommandInteraction) -> None:
        start = await self.getter(ConfigKeys.CB_STARTING_DAY)
        end = await self.getter(ConfigKeys.CB_ENDING_DAY)
        if start and end:
            await inter.send('Le date delle clan battle sono: `' + str(start) + '` e `' + str(end) + '`.')
        elif not start:
            await inter.send('Data d\'inizio vuota: : `' + str(start) + '`.')
        elif not end:
            await inter.send('Data di fine vuota: : `' + str(end) + '`.')

    @commands.slash_command(
        name="clan-battle-set-season",
        description="Imposta il numero della stagione delle clan battle"
    )
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
            if self.api_mongo.update_config(data):
                await inter.send('Impostato la stagione: `' + str(value) + '`.')
            else:
                await inter.send(msg)
        except Exception as error:
            print(f"set-season exception says: {error}")
            await inter.send(msg)

    @commands.slash_command(name="set-days", description="Imposta i giorni delle clan battle: AAAA-MM-GG")
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
            res1 = self.api_mongo.update_config(data1)
            res2 = self.api_mongo.update_config(data2)
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

    @commands.slash_command(name="get-ranking", description="Genera la classifica delle Clan Battle.")
    async def get_ranking(self, inter: ApplicationCommandInteraction) -> None:
        if not await check_role(inter, RolesEnum.ADMIN):
            await inter.send("Non hai i permessi.")
            return
        try:
            await inter.response.defer()
            mongo_config = self.api_mongo.get_config()["clan_battle_info"]
            x = self.make_ranking(mongo_config)
            pos = 1
            league_index = 0
            if self.debugging:
                channel = self.bot.get_channel(int(ChannelsEnum.TXT_TESTING))
            else:
                channel = self.bot.get_channel(int(ChannelsEnum.TXT_CLASSIFICA_CB))
            message_list = []
            # Compute the progressive day of CB
            start = convert_string_to_datetime(mongo_config[str(ConfigKeys.CB_STARTING_DAY)])
            end = convert_string_to_datetime(mongo_config[str(ConfigKeys.CB_ENDING_DAY)])
            today = (datetime.datetime.now() + datetime.timedelta(days=1)).date()
            totalCount = 0
            index = 0
            for d_ord in range(start.toordinal(), end.toordinal()):
                d = datetime.date.fromordinal(d_ord)
                if d.weekday() == 2 or d.weekday() == 3 or d.weekday() == 5 or d.weekday() == 6:
                    totalCount += 1
                    if d < today:
                        index += 1
            day_message = '**\nGiornata ' + str(index) + ' di ' + str(totalCount) + '**\n'
            if today < start.date():
                msg = "La data odierna (" + today.strftime("%d/%m/%Y") + ") è minore della data di inizio ("
                msg = msg + start.strftime("%d/%m/%Y") + ")"
                await channel.send(msg)
                day_message = '\n'
            if today > end.date():
                msg = "La data odierna (" + today.strftime("%d/%m/%Y") + ") è maggiore della data di fine ("
                msg = msg + end.strftime("%d/%m/%Y") + ")"
                await channel.send(msg)
                day_message = '\n'
            # Compute the content
            title = '**Risultati Clan Battle Season ' + str(mongo_config[str(ConfigKeys.CB_CURRENT_SEASON)])
            title = title + day_message + '**'
            message_list.append(title)
            # Add clans in the message
            for league in x:
                division_index = 1
                for division in league:
                    message = LeagueType(league_index).color() + ' **Lega ' + str(LeagueType(league_index))
                    message = message + ' - Divisione ' + str(division_index) + '**\n'
                    message = message + '```\n### Clan    - WinRate - Btl - Score - Promo\n'
                    for clan in division:
                        body = align(str(pos), 3, 'right') + ' '
                        body = body + align(clan.tag, 5, 'left') + ' ' + clan.squad + ' - '
                        body = body + align(clan.win_rate, 7, 'right') + ' - '
                        body = body + align(str(clan.battles), 3, 'right') + ' -   '
                        body = body + align(str(clan.score), 2, 'right') + '  - '
                        body = body + clan.convert_promo_to_string()
                        message = message + body + '\n'
                        pos = pos + 1
                    message = message + '\n```'
                    if division:
                        message_list.append(message)
                    division_index = division_index + 1
                league_index = league_index + 1
            # Send and publish the message
            while len(message_list) != 0:
                flag = False
                if len(message_list) > 1:
                    if len(message_list[0] + message_list[1]) < 1999:
                        message_list[0] = message_list[0] + message_list.pop(1)
                    else:
                        flag = True
                else:
                    flag = True
                if flag:
                    print(message_list[0] + '\n')
                    msg = await channel.send(message_list.pop(0))
                    await msg.publish()
                    time.sleep(10)
            await inter.send("Fatto!")

        except Exception as error:
            print(f"classifica exception says: {error}")
            msg = "Errore durante la generazione della classifica. Controllare il terminale e/o log."
            await inter.send(msg)


def setup(bot):
    bot.add_cog(ClanBattle(bot))
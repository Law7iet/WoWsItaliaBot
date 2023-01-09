import datetime
import time

from disnake import ApplicationCommandInteraction
from disnake.ext import commands

from api.mongo.api import ApiMongoDB
from api.mongo.utils import ConfigKeys
from api.wows.api import cb_ranking
from models.clan import Clan
from models.enum.discord_id import MyChannels, MyRoles
from models.enum.league_type import LeagueType
from models.enum.squad_type import SquadType
from utils.functions import align, convert_string_to_datetime, check_role, is_debugging


class ClanBattle(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot
        self.api_mongo = ApiMongoDB()
        self.debugging = is_debugging()

    async def getter(self, config_key: ConfigKeys) -> dict:
        config_file = self.api_mongo.get_config()
        return config_file[str(config_key)]

    def make_ranking(self, season: int, day: int, date: str) -> list[list[[]]]:
        # Each element represent a league.
        clan_battle_ranking = [
            [[]],           # Hurricane (1 division)
            [[], [], []],   # Typhoon (3 divisions)
            [[], [], []],   # Storm (3 divisions)
            [[], [], []],   # Gale (3 divisions)
            [[], [], []]    # Squall (3 divisions)
        ]
        for italian_clan in self.api_mongo.get_clans_by_name(""):
            data = cb_ranking(int(italian_clan["id"]), self.debugging)
            for element in data:
                if str(element["season_number"]) == str(season):
                    promotion = []
                    # Compute squad (SquadType)
                    match element["team_number"]:
                        case 1: squad = SquadType.ALPHA
                        case 2: squad = SquadType.BRAVO
                        case _: continue
                    # Compute tag (str)
                    tag = italian_clan["tag"]
                    # Check if a clan is inactive in the clan battles
                    if element["battles_count"] == 0:
                        continue
                    # Compute win_rate (float)
                    win_rate = element['wins_count'] / element['battles_count'] * 100
                    # Compute battles (int)
                    battles = element["battles_count"]
                    # Compute league (LeagueType)
                    match element["league"]:
                        case 0: league = LeagueType.HURRICANE
                        case 1: league = LeagueType.TYPHOON
                        case 2: league = LeagueType.STORM
                        case 3: league = LeagueType.GALE
                        case 4: league = LeagueType.SQUALL
                        case _: continue
                    # Compute division (int)
                    division = element["division"]
                    # Compute score (int)
                    score = element["division_rating"]
                    # Compute promotion (list(str))
                    if element["stage"]:
                        progress = element["stage"]["progress"]
                        for promoBattle in progress:
                            match promoBattle:
                                case "victory": promotion.append("+")
                                case "defeat": promotion.append("-")
                                case _: continue
                    # Create a clan instance
                    clan = Clan(tag, squad, win_rate, battles, league, division, score, promotion)
                    # Add the clan data in the rank collection
                    inserted_rank = self.api_mongo.insert_rank(season, day, date, clan)
                    if not inserted_rank:
                        continue
                    # Insert the clan to the correct league and division
                    if clan.league == LeagueType.HURRICANE:
                        clan_battle_ranking[int(clan.league)][0].append(clan)
                    else:
                        clan_battle_ranking[int(clan.league)][clan.division - 1].append(clan)
        # Sorting
        for league in clan_battle_ranking:
            i = 0
            for division in league:
                league[i] = sorted(division, key=lambda x: x.score, reverse=True)
                i = i + 1
        return clan_battle_ranking

    @commands.slash_command(
        name="clan-battle-stagione",
        description="Vedi o imposta il numero della stagione delle clan battle salvato nel database."
    )
    async def season(
            self,
            inter: ApplicationCommandInteraction,
            action: str = commands.Param(name="azione", choices=["Vedi", "Imposta"]),
            season: int = commands.Param(name="stagione", default=0)
    ) -> None:
        if action == "Vedi":
            value = await self.getter(ConfigKeys.CB_CURRENT_SEASON)
            if value:
                await inter.response.send_message(f"La stagione delle clan battle è: `{value}`.")
            else:
                await inter.response.send_message(f"**Errore** `get_season(inter)`\nValore `{value}` incorretto.")
        else:
            if not await check_role(inter, MyRoles.ADMIN):
                await inter.response.send_message("Non hai i permessi.")
            else:
                msg = f"**Errore** `set_season(inter, {season})`\nControllare il terminale e/o log."
                try:
                    if season <= 0:
                        return
                    data = {str(ConfigKeys.CB_CURRENT_SEASON): season}
                    if self.api_mongo.update_config(data):
                        await inter.response.send_message(f"Impostato la stagione: `{season}`.")
                    else:
                        await inter.response.send_message(msg)
                except Exception as error:
                    print(f"set_season exception says: {error}")
                    await inter.response.send_message(msg)

    @commands.slash_command(
        name="clan-battle-date",
        description="Vedi o imposta le date delle clan battle salvato nel database."
    )
    async def get_days(
            self,
            inter: ApplicationCommandInteraction,
            action: str = commands.Param(name="azione", choices=["Vedi", "Imposta"]),
            s_date: str = commands.Param(name="data-inizio", description="Formato AAAA-MM-GG.", default=""),
            e_date: str = commands.Param(name="data-fine", description="Formato AAAA-MM-GG.", default="")
    ) -> None:
        if action == "Vedi":
            start = await self.getter(ConfigKeys.CB_STARTING_DAY)
            end = await self.getter(ConfigKeys.CB_ENDING_DAY)
            if start and end:
                await inter.response.send_message(f"Le date delle clan battle sono: `{start}` e `{end}`.")
            elif not start:
                await inter.response.send_message(f"**Errore** `get_days(inter)`\nData d\'inizio `{start}` non valida.")
            elif not end:
                await inter.response.send_message(f"**Errore** `get_days(inter)`\nData d\'inizio `{end}` non valida.")
        else:
            if not await check_role(inter, MyRoles.ADMIN):
                await inter.response.send_message("Non hai i permessi.")
            else:
                await inter.response.defer()
                # Check params' format
                try:
                    start = str(s_date).split("-")
                    end = str(e_date).split("-")
                    start = datetime.datetime(int(start[0]), int(start[1]), int(start[2]))
                    end = datetime.datetime(int(end[0]), int(end[1]), int(end[2]))
                except (IndexError, ValueError):
                    msg = f"**Errore** `set_dates(inter, {s_date}, {e_date})`\n"
                    msg = f"{msg}\nUtilizzare la sintassi `AAAA-MM-GG` per le date."
                    await inter.send(msg)
                else:
                    # Update date
                    data1 = {str(ConfigKeys.CB_STARTING_DAY): start.strftime("%Y-%m-%d")}
                    data2 = {str(ConfigKeys.CB_ENDING_DAY): end.strftime("%Y-%m-%d")}
                    res1 = self.api_mongo.update_config(data1)
                    res2 = self.api_mongo.update_config(data2)
                    # Output
                    error = f"\n**Errore** `set_dates(inter, {s_date}, {e_date})`\nControllare il terminale e/o log."
                    if res1 and res2:
                        await inter.send(f"Impostato le date `{s_date}` e `{e_date}`.")
                    elif res1:
                        await inter.send(f"Impostato la data di inizio clan battle `{s_date}`.{error}")
                    elif res2:
                        await inter.send(f"Impostato la data di fine clan battle `{e_date}`.{error}")
                    else:
                        await inter.send(error)

    @commands.slash_command(
        name="clan-battle-classifica",
        description="Genera la classifica delle Clan Battle."
    )
    async def get_ranking(
            self,
            inter: ApplicationCommandInteraction,
            number: int = commands.Param(default=0, ge=0)
    ) -> None:
        if not await check_role(inter, MyRoles.ADMIN):
            await inter.send("Non hai i permessi.")
            return
        try:
            await inter.response.defer()
            mongo_config = self.api_mongo.get_config()
            pos = 1
            league_index = 0
            if self.debugging:
                channel = self.bot.get_channel(int(MyChannels.TXT_TESTING))
            else:
                channel = self.bot.get_channel(int(MyChannels.TXT_CLASSIFICA_CB))
            message_list = []
            # Compute the progressive day of CB
            start = convert_string_to_datetime(mongo_config[str(ConfigKeys.CB_STARTING_DAY)])
            end = convert_string_to_datetime(mongo_config[str(ConfigKeys.CB_ENDING_DAY)])
            today = datetime.datetime.now()
            totalCount = 0
            index = 0
            for d_ord in range(start.toordinal(), end.toordinal()):
                d = datetime.datetime.fromordinal(d_ord)
                if d.weekday() == 2 or d.weekday() == 3 or d.weekday() == 5 or d.weekday() == 6:
                    totalCount += 1
                    d = d.replace(hour=23, minute=20)
                    if d < today:
                        index += 1
            if number > totalCount:
                await inter.send("Numero progressivo maggiore del numero delle giornate totali")
                return
            if number != 0:
                index = number
            day_message = f"\nGiornata {index} di {totalCount}\n"
            if today < start:
                msg = f"La data odierna è minore della data di inizio `{start.strftime('%d/%m/%Y')}`."
                await channel.send(msg)
                day_message = '\n'
            if today > end:
                msg = f"La data odierna è maggiore della data di fine `{end.strftime('%d/%m/%Y')}`."
                await channel.send(msg)
                day_message = '\n'
            # Compute the content
            season = mongo_config[str(ConfigKeys.CB_CURRENT_SEASON)]
            title = f"**Risultati Clan Battle Season {season}**{day_message}"
            # Add clans in the message
            x = self.make_ranking(season, index, today.strftime('%Y-%m-%d, %H:%M:%S'))
            for league in x:
                division_index = 1
                for division in league:
                    message = f"{LeagueType(league_index).color()} **Lega {LeagueType(league_index).nome()}**"
                    if league_index != 0:
                        message = message + f" - Divisione {division_index}"
                    message = message + "\n```\n### Clan    - WinRate - Btl - Score - Promo\n"
                    for clan in division:
                        body = align(str(pos), 3, "right") + " "
                        body = body + align(clan.tag, 5, "left") + f" {clan.squad.nome()} - "
                        body = body + align(f"{clan.win_rate:.2f}%", 7, "right") + " - "
                        body = body + align(str(clan.battles), 3, "right") + " -   "
                        body = body + align(str(clan.score), 2, "right") + "  - "
                        body = body + clan.convert_promo_to_string()
                        message = message + body + "\n"
                        pos = pos + 1
                    message = message + "```"
                    if division:
                        message_list.append(message)
                    division_index = division_index + 1
                league_index = league_index + 1
            # Send and publish the message
            msg = await channel.send(title)
            await msg.publish()
            time.sleep(10)
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
            print(f"get_ranking exception says: {error}")
            msg = "**Errore** `get-ranking(inter)`\nControllare il terminale e/o log."
            await inter.send(msg)


def setup(bot):
    bot.add_cog(ClanBattle(bot))

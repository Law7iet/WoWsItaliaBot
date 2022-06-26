import datetime
import time

import pandas
from discord.ext import commands

from api.mongo_db import ApiMongoDB
from api.wargaming import ApiWargaming
from models.my_class.clan import Clan
from models.my_enum.database_enum import ConfigFileKeys
from models.my_enum.league_type_enum import LeagueTypeEnum, LeagueColorEnum
from models.my_enum.roles_enum import RolesEnum
from utils.constants import *
from utils.functions import my_align, check_role, convert_string_to_date, nearest


class ClanBattleRanking(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot
        self.apiMongo = ApiMongoDB()
        self.apiWargaming = ApiWargaming()

    def my_rank(self) -> list[list[Clan]]:
        clan_battle_inactive = []
        clan_battle_ranking = [
            # DO-TO: Hurricane has only one division.
            # Hurricane - Division 1, 2, 3
            [[], [], []],
            # Typhoon - Division 1, 2, 3
            [[], [], []],
            # Storm - Division 1, 2, 3
            [[], [], []],
            # Gale - Division 1, 2, 3
            [[], [], []],
            # Squall - Division 1, 2, 3
            [[], [], []]
        ]

        for italian_clan in self.apiMongo.get_clans_by_name(''):
            data = self.apiWargaming.get_clan_ranking(italian_clan['id'])

            for element in data:
                if str(element['season_number']) == str(
                        self.apiMongo.get_config()[str(ConfigFileKeys.CLAN_BATTLE_CURRENT_SEASON)]):
                    promotion = []
                    # Compute squad (str)
                    if element['team_number'] == 1:
                        squad = 'A'
                    elif element['team_number'] == 2:
                        squad = 'B'
                    else:
                        print('Error - ratings has season_number 12 but team_number isn\'t equal to 1 or 2')
                        continue
                    # Compute tag (str)
                    tag = italian_clan['tag']
                    # Check if a clan is inactive in the clan battles
                    if element['battles_count'] == 0:
                        clan_battle_inactive.append(tag)
                        continue
                    # Compute win_rate (str)
                    win_rate = '%.2f' % (element['wins_count'] / element['battles_count'] * 100) + '%'
                    # Compute battles (int)
                    battles = element['battles_count']
                    # Compute league (LeagueType)
                    match element['league']:
                        case 0:
                            league = LeagueTypeEnum.HURRICANE
                        case 1:
                            league = LeagueTypeEnum.TYPHOON
                        case 2:
                            league = LeagueTypeEnum.STORM
                        case 3:
                            league = LeagueTypeEnum.GALE
                        case 4:
                            league = LeagueTypeEnum.SQUALL
                        case _:
                            continue
                    # Compute division (int)
                    division = element['division']
                    # Compute division (int)
                    score = element['division_rating']
                    # Compute promotion (list(str))
                    if element['stage']:
                        progress = element['stage']['progress']
                        for promoBattle in progress:
                            if promoBattle == 'victory':
                                promotion.append('+')
                            elif promoBattle == 'defeat':
                                promotion.append('-')
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

    @commands.command()
    async def cb(self, ctx: commands.context.Context):
        if not await check_role(ctx, RolesEnum.ADMIN):
            return
        try:
            x = self.my_rank()
            pos = 1
            league_index = 0
            channel = self.bot.get_channel(CH_TXT_CLASSIFICA_CB) if not DEBUG else self.bot.get_channel(
                CH_TXT_TESTING)
            message_list = []

            # Compute the progressive day of CB
            tmp_config = self.apiMongo.get_config()
            start = convert_string_to_date(tmp_config[str(ConfigFileKeys.CLAN_BATTLE_STARTING_DAY)])
            end = convert_string_to_date(tmp_config[str(ConfigFileKeys.CLAN_BATTLE_FINAL_DAY)])
            now = datetime.datetime.now()

            days_range = pandas.date_range(start, end, freq='W-WED')
            days_range = days_range.union(pandas.date_range(start, end, freq='W-THU'))
            days_range = days_range.union(pandas.date_range(start, end, freq='W-SAT'))
            days_range = days_range.union(pandas.date_range(start, end, freq='W-SUN'))

            day = nearest(days_range, now)
            index = days_range.get_loc(day) + 1

            title = '**Risultati Clan Battle Season ' \
                    + str(self.apiMongo.get_config()[str(ConfigFileKeys.CLAN_BATTLE_CURRENT_SEASON)]) \
                    + '**\n Giornata ' + str(index) + ' di ' + str(len(days_range) + '\n')

            message_list.append(title)

            # Add clans in the message
            for league in x:
                division_index = 1
                for division in league:
                    message = str(LeagueColorEnum(league_index)) + ' **Lega ' + str(LeagueTypeEnum(league_index)) \
                              + ' - Divisione ' + str(division_index) + '**\n'
                    message = message + '```\n### Clan    - WinRate - Btl - Score - Promo\n'
                    for clan in division:
                        body = my_align(str(pos), 3, 'right') + ' '
                        body = body + my_align(clan.tag, 5, 'left') + ' ' + clan.squad + ' - '
                        body = body + my_align(clan.win_rate, 7, 'right') + ' - '
                        body = body + my_align(str(clan.battles), 3, 'right') + ' -   '
                        body = body + my_align(str(clan.score), 2, 'right') + '  - '
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
        except Exception as error:
            await self.bot.get_channel(CH_TXT_TESTING).send('**>ranking command exception**')
            await self.bot.get_channel(CH_TXT_TESTING).send('```' + str(error) + '```')


def setup(bot):
    bot.add_cog(ClanBattleRanking(bot))

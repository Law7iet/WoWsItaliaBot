import json
import requests
from discord.ext import commands
from utils import *
from apiMongoDB import ApiMongoDB
from apiWarGaming import ApiWarGaming

class Clan:
    def __init__(self, tag, squadra, winrate, battles, lega, divisione, punteggio, promozione):
        self.tag = tag
        self.squadra = squadra
        self.winrate = winrate
        self.battles = battles
        self.lega = lega
        self.divisione = divisione
        self.punteggio = punteggio
        self.promozione = promozione

    def getPromoInString(self):
        promozione = ''
        for battaglia in self.promozione:
            promozione = promozione + battaglia + ', '
        if promozione == '':
            return promozione
        else:
            return '[' + promozione[:-2] + ']'

class Ranking(commands.Cog):

    leagueType = [
        'Uragano',
        'Tifone',
        'Tempesta',
        'Burrasca',
        'Temporale'
    ]

    leagueColor = [
        ':purple_square:',
        ':green_square:',
        ':yellow_square:',
        ':white_large_square:',
        ':brown_square:'
    ]

    def __init__(self, bot):
        self.bot = bot
        self.apiMongo = ApiMongoDB()

    def my_rank(self):
        clanBattleInactive = []
        clanBattleRanking = [
            # Hurricane - Division 1, 2, 3
            [ [], [], [] ],
            # Typhoon - Division 1, 2, 3
            [ [], [], [] ],
            # Storm - Division 1, 2, 3
            [ [], [], [] ],
            # Gale - Division 1, 2, 3
            [ [], [], [] ],
            # Squall - Division 1, 2, 3
            [ [], [], [] ]
        ]

        for italianClan in self.apiMongo.getClansByName(''):
            link = ApiWarGaming().getUrlClanRanking() + italianClan['id'] + '/claninfo/'
            data = json.loads((requests.get(url = link)).text)['clanview']['wows_ladder']['ratings']

            for element in data:
                if str(element['season_number']) == str(self.apiMongo.getConfig()['CBCurrentSeason']):
                    promozione = []
                    squadra = ''
                    # Calcolo Squadra (stringa)
                    if element['team_number'] == 1:
                        squadra = 'A'
                    elif element['team_number'] == 2:
                        squadra = 'B'
                    else:
                        print("Error - ratings has season_number 12 but team_number isn't equal to 1 or 2")
                        continue
                    # Calcolo Tag (stringa)
                    tag = italianClan['tag']
                    # Calcolo inattività del clan nelle CB
                    if element['battles_count'] == 0:
                        clanBattleInactive.append(tag)
                        continue
                    # Calcolo Winrate (stringa)
                    winrate = '%.2f' % (element['wins_count'] / element['battles_count'] * 100) + '%'
                    # Calcolo del numero di battaglie
                    battles = str(element['battles_count'])
                    # Calcolo Lega (intero)
                    lega = element['league']
                    # Calcolo Divisione (intero)
                    divisione = element['division']
                    # Calcolo Punteggio (intero)
                    punteggio = element['division_rating']
                    # Calcolo Promozione (array di stringhe)
                    if element['stage']:
                        progress = element['stage']['progress']
                        for promoBattle in progress:
                            if promoBattle == 'victory':
                                promozione.append('+')
                            elif promoBattle == 'defeat':
                                promozione.append('-')
                    # Creazione di un clan attivo
                    clan = Clan(tag, squadra, winrate, battles, lega, divisione, punteggio, promozione)
                    # Inserimento nella lega e divisione di riferimento
                    clanBattleRanking[clan.lega][clan.divisione - 1].append(clan)

        # Ordinamento della ranking
        for league in clanBattleRanking:
            i = 0
            for division in league:
                league[i] = sorted(division, key = lambda x: x.punteggio, reverse = True)
                i = i + 1

        return clanBattleRanking

    @commands.command()
    async def ranking(self, ctx):
        try:
            admin_role = ctx.guild.get_role(ROLE_ADMIN)
            if admin_role in ctx.author.roles:
                x = self.my_rank()
                pos = 1
                league_index = 0
                channel = self.bot.get_channel(CH_TXT_CLASSIFICA_CB)
                # channel = self.bot.get_channel(CH_TXT_ADMIN)
                messageList = ['**Risultati Clan Battle Season ' + str(self.apiMongo.getConfig()['CBCurrentSeason']) + '**\n']
                for league in x:
                    division_index = 1
                    for division in league:
                        message = self.leagueColor[league_index] + ' **Lega ' + self.leagueType[league_index] + ' - Divisione ' + str(division_index) + '**\n'
                        message = message + '```\n### Clan    - WinRate - Btl - Score - Promo\n'
                        for clan in division:
                            body = ''
                            body = my_align(str(pos), 3, 'right') + ' '
                            body = body + my_align(clan.tag, 5, 'left') + ' ' + clan.squadra + ' - '
                            body = body + my_align(clan.winrate, 7, 'right') + ' - '
                            body = body + my_align(clan.battles, 3, 'right') + ' -   '
                            body = body + my_align(str(clan.punteggio), 2, 'right') + '  - '
                            body = body + clan.getPromoInString()
                            message = message + body + '\n'
                            pos = pos + 1
                        message = message + '\n```'
                        if division:
                            messageList.append(message)
                        division_index = division_index + 1
                    league_index = league_index + 1
                # Send and publish message
                while len(messageList) != 0:
                    flag = False
                    if len(messageList) > 1:
                        if len(messageList[0] + messageList[1]) < 1900:
                                messageList[0] = messageList[0] + messageList.pop(1)
                        else:
                            flag = True
                    else:
                        flag = True
                    if flag:
                        print(messageList[0] + '\n')
                        sentMessage = await channel.send(messageList.pop(0))
                        # await sentMessage.publish()
            else:
                await ctx.send('Permesso negato')
        except Exception as error:
            print(error)
            return

def setup(bot):
    bot.add_cog(Ranking(bot))
import fun
import json
import requests
from discord.ext import commands
from utils import *

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

    def get_promozione_in_string(self):
        promozione = ""
        for battaglia in self.promozione:
            promozione = promozione + battaglia + ", "
        if promozione == "":
            return promozione
        else:
            return "[" + promozione[:-2] + "]"

class Ranking(commands.Cog):

    league_type = [
        "Uragano",
        "Tifone",
        "Tempesta",
        "Burrasca",
        "Temporale"
    ]

    league_color = [
        ":purple_square:",
        ":green_square:",
        ":yellow_square:",
        ":white_large_square:",
        ":brown_square:"
    ]

    def __init__(self, bot):
        self.bot = bot

    def my_rank(self):
        clan_battle_inactive = []
        clan_battle_ranking = [
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

        for CLAN_ID in CLANS_ID:
            link = WOWS_CLAN_BATTLE + CLAN_ID + "/claninfo/"
            data = json.loads((requests.get(url = link)).text)["clanview"]["wows_ladder"]["ratings"]

            for element in data:
                if element["season_number"] == CB_CURRENT_SEASON:
                    promozione = []
                    squadra = ""
                    # Calcolo Squadra (stringa)
                    if element["team_number"] == 1:
                        squadra = "A"
                    elif element["team_number"] == 2:
                        squadra = "B"
                    else:
                        print("Error - ratings has season_number 12 but team_number isn't equal to 1 or 2")
                        continue
                    # Calcolo Tag (stringa)
                    tag = fun.get_clan_name(CLAN_ID)
                    # Calcolo inattività del clan nelle CB
                    if element["battles_count"] == 0:
                        clan_battle_inactive.append(tag)
                        continue
                    # Calcolo Winrate (stringa)
                    winrate = "%.2f" % (element["wins_count"] / element["battles_count"] * 100) + "%"
                    # Calcolo del numero di battaglie
                    battles = str(element["battles_count"])
                    # Calcolo Lega (intero)
                    lega = element["league"]
                    # Calcolo Divisione (intero)
                    divisione = element["division"]
                    # Calcolo Punteggio (intero)
                    punteggio = element["division_rating"]
                    # Calcolo Promozione (array di stringhe)
                    if element["stage"]:
                        progress = element["stage"]["progress"]
                        for promo_battle in progress:
                            if promo_battle == "victory":
                                promozione.append("+")
                            elif promo_battle == "defeat":
                                promozione.append("-")
                    # Creazione di un clan attivo
                    clan = Clan(tag, squadra, winrate, battles, lega, divisione, punteggio, promozione)
                    # Inserimento nella lega e divisione di riferimento
                    clan_battle_ranking[clan.lega][clan.divisione - 1].append(clan)

        # Ordinamento della ranking
        for league in clan_battle_ranking:
            i = 0
            for division in league:
                league[i] = sorted(division, key = lambda x: x.punteggio, reverse = True)
                i = i + 1

        return clan_battle_ranking

    @commands.command()
    async def ranking(self, ctx):
        x = self.my_rank()
        pos = 1
        league_index = 0
        channel = self.bot.get_channel(CLASSIFICA_CLAN_BATTLE)
        # channel = self.bot.get_channel(ADMIN_BOT)
        await channel.send("**Risultati Clan Battle Season " + str(CB_CURRENT_SEASON) + "**")
        for league in x:
            division_index = 1
            for division in league:
                message = self.league_color[league_index] + " **Lega " + self.league_type[league_index] + " - Divisione " + str(division_index) + "**\n"
                message = message + "```\n### Clan    - WinRate - Btl - Score - Promo\n"
                for clan in division:
                    body = ""
                    body = fun.my_align(str(pos), 3, "right") + " "
                    body = body + fun.my_align(clan.tag, 5, "left") + " " + clan.squadra + " - "
                    body = body + fun.my_align(clan.winrate, 7, "right") + " - "
                    body = body + fun.my_align(clan.battles, 3, "right") + " -   "
                    body = body + fun.my_align(str(clan.punteggio), 2, "right") + "  - "
                    body = body + clan.get_promozione_in_string()
                    message = message + body + "\n"
                    pos = pos + 1
                message = message + "\n```"
                if division:
                    await channel.send(message)
                    print(message + "\n")
                division_index = division_index + 1
            league_index = league_index + 1

def setup(bot):
    bot.add_cog(Ranking(bot))
import discord
from discord.ext import commands
from utils.constants import *
from models.podium import *
import validators


def podio(torneo: TournamentEnum, edizione: int, posizione: int, team: str, immagine: str, partecipanti: tuple[str]):
    match torneo:
        case TournamentEnum.LEAGUE:
            evento = str(TournamentEnum.LEAGUE)
        case TournamentEnum.LEAGUE:
            evento = str(TournamentEnum.LEAGUE)
        case _:
            return None
    match posizione:
        case int(PodiumEnum.FIRST):
            classificato = PodiumEnum.FIRST
        case int(PodiumEnum.SECOND):
            classificato = PodiumEnum.SECOND
        case int(PodiumEnum.THIRD):
            classificato = PodiumEnum.THIRD
        case _:
            classificato = PodiumEnum.OTHER
    color = hex(classificato)
    if posizione is not PodiumEnum.OTHER:
        descrizione = str(classificato) + " classificato dell\'Italian " + str(evento) + str(edizione) + "."
    else:
        descrizione = "Partecipante dell\'Italian " + str(evento) + str(edizione) + "."
    embed = discord.Embed(title=team, description=descrizione, color=color)
    embed.set_thumbnail(url=immagine)
    embed.set_footer(text="Congratulazioni!")
    if partecipanti:
        giocatori = ""
        for partecipante in partecipanti:
            giocatori = giocatori + partecipante.replace(",", "") + ", "
        giocatori = giocatori[:-2]
        embed.add_field(name="Partecipanti:", value=giocatori, inline=True)
    return embed


class TournamentRanking(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot

    @commands.command()
    async def league(self, ctx: commands.context.Context, edizione: str, posizione: str, team: str, immagine: str,
                     *partecipanti: str):
        try:
            if not (edizione.isdigit()) or not (posizione.isdigit() or not (validators.url(immagine))):
                return
            embed = podio(TournamentEnum.LEAGUE, int(edizione), int(posizione), team, immagine, partecipanti)
            if not embed:
                return
            channel = self.bot.get_channel(CH_TXT_PODIO_LEAGUE) if not DEBUG else self.bot.get_channel(CH_TXT_ADMIN)
            await channel.send(embed=embed)
        except Exception as error:
            print(error)

    @commands.command()
    async def cup(self, ctx: commands.context.Context, edizione: str, posizione: str, team: str, immagine: str,
                  *partecipanti: str):
        try:
            if not (edizione.isdigit()) or not (posizione.isdigit()):
                return
            embed = podio(TournamentEnum.CUP, int(edizione), int(posizione), team, immagine, *partecipanti)
            if not embed:
                return
            channel = self.bot.get_channel(CH_TXT_PODIO_CUP) if not DEBUG else self.bot.get_channel(CH_TXT_ADMIN)
            await channel.send(embed=embed)
        except Exception as error:
            print(error)


def setup(bot):
    bot.add_cog(TournamentRanking(bot))

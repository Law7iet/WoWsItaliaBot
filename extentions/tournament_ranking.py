import discord
from discord.ext import commands
from utils.constants import *
from models.podium import *
from models.roles import RolesEnum
from utils.functions import check_role


def podio(torneo: TournamentEnum, edizione: int, posizione: int, team: str, immagine: str, partecipanti: tuple[str]):
    match torneo:
        case TournamentEnum.LEAGUE:
            evento = str(TournamentEnum.LEAGUE)
        case TournamentEnum.LEAGUE:
            evento = str(TournamentEnum.LEAGUE)
        case _:
            return None
    match posizione:
        case PodiumEnum.FIRST.value:
            classificato = PodiumEnum.FIRST
        case PodiumEnum.SECOND.value:
            classificato = PodiumEnum.SECOND
        case PodiumEnum.THIRD.value:
            classificato = PodiumEnum.THIRD
        case _:
            classificato = PodiumEnum.OTHER
    color = int(classificato)
    if posizione is not PodiumEnum.OTHER:
        descrizione = str(classificato) + " classificato dell\'Italian " + str(evento) + " " + str(edizione) + "."
    else:
        descrizione = "Partecipante dell\'Italian " + str(evento) + str(edizione) + "."
    embed = discord.Embed(title=team, description=descrizione, color=discord.Colour(int(color)))
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
        if not check_role(ctx, RolesEnum.ADMIN):
            return
        try:
            if not (edizione.isdigit()) or not (posizione.isdigit()):
                return
            embed = podio(TournamentEnum.LEAGUE, int(edizione), int(posizione), team, immagine, partecipanti)
            if not embed:
                return
            channel = self.bot.get_channel(CH_TXT_PODIO_LEAGUE) if not DEBUG else self.bot.get_channel(CH_TXT_TESTING)
            await channel.send(embed=embed)
        except Exception as error:
            await self.bot.get_channel(CH_TXT_TESTING).send("**>league command exception**")
            await self.bot.get_channel(CH_TXT_TESTING).send("```" + error + "```")

    @commands.command()
    async def cup(self, ctx: commands.context.Context, edizione: str, posizione: str, team: str, immagine: str,
                  *partecipanti: str):
        if not check_role(ctx, RolesEnum.ADMIN):
            return
        try:
            if not (edizione.isdigit()) or not (posizione.isdigit()):
                return
            embed = podio(TournamentEnum.CUP, int(edizione), int(posizione), team, immagine, *partecipanti)
            if not embed:
                return
            channel = self.bot.get_channel(CH_TXT_PODIO_CUP) if not DEBUG else self.bot.get_channel(CH_TXT_TESTING)
            await channel.send(embed=embed)
        except Exception as error:
            await self.bot.get_channel(CH_TXT_TESTING).send("**>cup command exception**")
            await self.bot.get_channel(CH_TXT_TESTING).send("```" + error + "```")


def setup(bot):
    bot.add_cog(TournamentRanking(bot))

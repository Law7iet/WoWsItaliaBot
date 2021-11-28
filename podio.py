import discord
from discord.ext import commands
from utils import *

class Podio(commands.Cog):

    torneo = {
        "1": ["Primo", 0xFFD700],
        "2": ["Secondo", 0xC0C0C0],
        "3": ["Terzo", 0xCD7F32]
    }

    def __init__(self, bot):
        self.bot = bot
    
    def podio(self, torneo, edizione, posizione, team, immagine, *partecipanti):
        classificato = self.torneo[posizione][0]
        colore = self.torneo[posizione][1]
        descrizione = classificato + " classificato della " + edizione + " edizione dell'Italian " + torneo + "."
        embed = discord.Embed(title = team, description = descrizione, color = colore)
        embed.set_thumbnail(url = immagine)
        embed.set_footer(text = "Congratulazioni!")
        if partecipanti:
            giocatori = ""
            for partecipante in partecipanti:
                giocatori = giocatori + partecipante + ", "
            giocatori = giocatori[:-2]
            embed.add_field(name = "Partecipanti:", value = giocatori, inline = True)
        return embed

    @commands.command()
    async def league(self, ctx, edizione, posizione, team, immagine, *partecipanti):
        embed = self.podio("League", edizione, posizione, team, immagine, *partecipanti)
        channel = self.bot.get_channel(PODIO_LEAGUE)
        await channel.send(embed = embed)

    @commands.command()
    async def cup(self, ctx, edizione, posizione, team, immagine, *partecipanti):
        embed = self.podio("Cup", edizione, posizione, team, immagine, *partecipanti)
        channel = self.bot.get_channel(PODIO_CUP)
        await channel.send(embed = embed)

def setup(bot):
    bot.add_cog(Podio(bot))

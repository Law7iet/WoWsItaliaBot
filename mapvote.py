import discord
import random
import re
from discord.ext import commands
from utils import *

class MapVote(commands.Cog):

    def __init__(self, bot):
        self.bot = bot
    
    def EMOJI_POOL(self):
        return [
            "1️⃣",
            "2️⃣",
            "3️⃣",
            "4️⃣",
            "5️⃣",
            "6️⃣",
            "7️⃣",
            "8️⃣",
            "9️⃣",
            "🅰️",
            "🅱️"
        ]

    def MAP_POOL(self):
        return [
            "Acque Settentrionali",
            "Catena Montuosa",
            "Gigante Dormiente",
            "Grecia",
            "Isole di Ghiaccio",
            "Lacrime del Deserto",
            "Mare della Fortuna",
            "Nord",
            "Zona Calda"
        ]

    def make_body(self):
        map_list = self.MAP_POOL()
        emoji_list = self.EMOJI_POOL()
        for i in range (0, 9):
            map_list[i] = emoji_list[i] + " " + map_list[i] + "\n"
        return map_list

    @commands.command()
    async def mapvote(self, ctx, input_A, input_B):
        # Controllo dei permessi
        org_role = ctx.guild.get_role(ADMIN)
        if org_role in ctx.author.roles:
            # Controllo degli argomenti
            rappr_A = ctx.guild.get_member(int(input_A[3:-1]))
            rappr_B = ctx.guild.get_member(int(input_B[3:-1]))
            if rappr_A and rappr_B:
                # Generazione del messaggio
                message = self.make_body()
                message.insert(0, "<@" + str(rappr_A.id) + "> vs <@" + str(rappr_B.id) + ">\n\n")
                message.append("\nTurno di <@" + str(rappr_A.id) + "> - Fase di ban")
                descrizione = "".join(message)
                # Generazione dell'embed
                embed = discord.Embed(title = "WoWs Italia - Map Vote", description = descrizione, color = 0xff0000)
                # Invio dell'embed
                msg = await ctx.send(embed = embed)
                # Aggiunta delle reazioni
                for i in self.EMOJI_POOL():
                    await msg.add_reaction(i)
            else:
                await ctx.send("Argomento errato (consiglio: tagga un utente)")
        else:
            await ctx.send("Permesso negato")

    @commands.Cog.listener()
    async def on_reaction_add(self, reaction, user):
        # Identificazione del turno (chi deve reagire)
        tmp = reaction.message.embeds[0].description.split("\n")[-1]
        turn = re.search(r'<@(.*?)>', tmp).group(1)
        # Controllo delle reazioni del bot stesso
        if user.id != WOWS_ITALIA_BOT:
            # Controllo del turno
            if int(user.id) != int(turn):
                # Non è il turno dell'utente che ha reagito
                await reaction.message.remove_reaction(reaction, user)
            else:
                # È il turno dell'utente che ha reagito
                # Controllo dell'emoji
                if reaction.emoji in self.EMOJI_POOL():
                    # L'emoji è corretto
                    i = self.EMOJI_POOL().index(reaction.emoji)
                    # Segmentazione dell'embed
                    message = (reaction.message.embeds)[0].description.split("\n\n")
                    # Intestazione
                    header = message[0]
                    # Lista delle mappe
                    body = message[1]
                    # Piè di pagina
                    footer = message[2].split("\n")
                    # Individualizzazione degli utenti taggati            
                    rappr_A = re.findall(r'<@(.*?)>', header)[0]
                    rappr_B = re.findall(r'<@(.*?)>', header)[1]  
                    edit = False
                    # Modifica del piè di pagina
                    if i < 9:
                        # La reazione indica una mappa
                        map = self.MAP_POOL()[i]
                        # Controllo del piè di pagina per identificare il turno
                        if len(footer) == 1:
                            # Modifica del piè di pagina
                            footer[0] = footer[0].replace("- Fase di ban", "ha bannato " + map)
                            footer[0] = footer[0][9:]
                            footer.append("Turno di <@" + str(rappr_B) + "> - Fase di ban")
                            edit = True
                            # Rimozione della reazione del bot
                            await reaction.message.remove_reaction(reaction, self.bot.get_user(WOWS_ITALIA_BOT))
                        elif len(footer) == 2:
                            # Modifica del piè di pagina
                            footer[1] = footer[1].replace("- Fase di ban", "ha bannato " + map)
                            footer[1] = footer[1][9:]
                            footer.append("Turno di <@" + str(rappr_A) + "> - Fase di pick")
                            edit = True
                            # Rimozione della reazione del bot
                            await reaction.message.remove_reaction(reaction, self.bot.get_user(WOWS_ITALIA_BOT))
                        elif len(footer) == 3:
                            # Modifica del piè di pagina
                            footer[2] = footer[2].replace("- Fase di pick", "ha scelto " + map)
                            footer[2] = footer[2][9:]
                            footer.append("Turno di <@" + str(rappr_A) + "> - Scelta dello spawn")
                            edit = True
                            # Rimozione della reazione del bot
                            await reaction.message.remove_reaction(reaction, self.bot.get_user(WOWS_ITALIA_BOT))
                        elif len(footer) == 4 and footer[3] != "Turno di <@" + str(rappr_A) + "> - Scelta dello spawn":
                            # Modifica del piè di pagina
                            footer[3] = footer[3].replace("- Fase di pick", "ha scelto " + map)
                            footer[3] = footer[3][9:]
                            footer.append("Turno di <@" + str(rappr_B) + "> - Scelta dello spawn")
                            edit = True
                            # Rimozione della reazione del bot
                            await reaction.message.remove_reaction(reaction, self.bot.get_user(WOWS_ITALIA_BOT))
                    else:
                        # La reazione indica uno spawn
                        # Controllo del piè di pagina per identificare il turno
                        if len(footer) == 4:
                            if footer[3] == "Turno di <@" + str(rappr_A) + "> - Scelta dello spawn":
                                # Modifica del piè di pagina
                                footer[2] = footer[2] + ", spawn " + ("alpha" if i == 9 else "bravo")
                                footer[3] = "Turno di <@" + str(rappr_B) + "> - Fase di pick"
                                edit = True
                        if len(footer) == 5:
                            if footer[4] == "Turno di <@" + str(rappr_B) + "> - Scelta dello spawn":
                                # Calcolo della mappa casuale
                                random_choice = random.choice(reaction.message.reactions[:-2])
                                map_index = self.EMOJI_POOL().index(str(random_choice))
                                map = self.MAP_POOL()[map_index]
                                spawn = random.choice(["alpha", "bravo"])
                                # Modifica del piè di pagina
                                footer[3] = footer[3] + ", spawn " + ("alpha" if i == 9 else "bravo")
                                footer[4] = "Scelta casuale: " + map + ", <@" + str(rappr_A) + ">, spawn " + spawn
                                edit = True
                    if edit == True:
                        # Generazione del nuovo messaggio
                        final_message = header + "\n\n" + body + "\n\n" + "\n".join(footer)
                        descrizione = "".join(final_message)
                        # Generazione del nuovo embed
                        embed = discord.Embed(title = "WoWs Italia - Map Vote", description = descrizione, color = 0xff0000)
                        # Modifica dell'embed
                        await reaction.message.edit(embed = embed)

                    # Rimozione della reazione dell'utente
                    await reaction.message.remove_reaction(reaction, user)

def setup(bot):
    bot.add_cog(MapVote(bot))
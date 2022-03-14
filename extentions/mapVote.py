import discord
import random
import re
from discord.ext import commands
from utils.constants import *

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
            "Acque Settentrionali", #
            "Catena Montuosa", #
            "Gigante Dormiente", #
            "Lacrime del Deserto", #
            "Mare della Fortuna", #
            "Nord", #
            "Terra del Fuoco", #
            "Via del Guerriero", #
            "Zona Calda" #
        ]

    def make_body(self):
        map_list = self.MAP_POOL()
        emoji_list = self.EMOJI_POOL()
        for i in range (0, 9):
            map_list[i] = emoji_list[i] + " " + map_list[i] + "\n"
        return map_list

    async def makeMapVote(self, ctx: commands.context.Context, input_A, input_B, matches):
        try:
            # Controllo dei permessi
            admin_role = ctx.guild.get_role(ROLE_ADMIN)
            org_league_role = ctx.guild.get_role(ROLE_ORG_LEAGUE)
            org_cup_role = ctx.guild.get_role(ROLE_ORG_CUP)
            rappr_role = ctx.guild.get_role(ROLE_RAPPRESENTANTE_CLAN)
            if  (admin_role in ctx.author.roles) or (org_league_role in ctx.author.roles) or (org_cup_role in ctx.author.roles) or (rappr_role in ctx.author.roles):
                # Controllo degli argomenti
                rappr_A = ctx.guild.get_member(int(input_A[3:-1]))
                rappr_B = ctx.guild.get_member(int(input_B[3:-1]))
                if rappr_A and rappr_B:
                    # Generazione del messaggio
                    message = self.make_body()
                    if matches == 3:
                        message.insert(0, "Bo3: <@" + str(rappr_A.id) + "> vs <@" + str(rappr_B.id) + ">\n\n")
                    elif matches == 5:
                        message.insert(0, "Bo5: <@" + str(rappr_A.id) + "> vs <@" + str(rappr_B.id) + ">\n\n")
                    message.append("\nTurno di <@" + str(rappr_A.id) + "> - Fase di ban")
                    descrizione = "".join(message)
                    # Generazione dell'embed
                    embed = discord.Embed(title = "WoWs Italia - Map Vote", description = descrizione, color = 0xff0000)
                    embed.colour = discord.Colour.from_rgb(255, 255, 255)
                    # Invio dell'embed
                    msg = await ctx.send(embed = embed)
                    # Aggiunta delle reazioni
                    for i in self.EMOJI_POOL():
                        await msg.add_reaction(i)
                else:
                    await ctx.send("Argomento errato (consiglio: tagga un utente)")
            else:
                await ctx.send("Permesso negato")
        except Exception as error:
            print(error)
            return

    @commands.command()
    async def mapvote3(self, ctx: commands.context.Context, input_A, input_B):
        await self.makeMapVote(ctx, input_A, input_B, 3)

    @commands.command()
    async def mapvote5(self, ctx: commands.context.Context, input_A, input_B):
        await self.makeMapVote(ctx, input_A, input_B, 5)

    @commands.Cog.listener()
    async def on_reaction_add(self, reaction, user):
        # Identificazione del turno (chi deve reagire)
        # try:
            tmp = reaction.message.embeds[0].description.split("\n")[-1]
            turn = re.search(r'<@(.*?)>', tmp).group(1)
            # Controllo delle reazioni del bot stesso
            if user.id != ROLE_WOWS_ITALIA:
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
                            print(len(footer))             
                            print(footer)
                            # Controllo del piè di pagina per identificare il turno
                            if len(footer) == 1:
                                # Modifica del piè di pagina
                                footer[0] = footer[0].replace("- Fase di ban", "ha bannato " + map)
                                footer[0] = footer[0][9:]
                                footer.append("Turno di <@" + str(rappr_B) + "> - Fase di ban")
                                edit = True
                                # Rimozione della reazione del bot
                                await reaction.message.remove_reaction(reaction, self.bot.get_user(ROLE_WOWS_ITALIA))
                            elif len(footer) == 2:
                                # Modifica del piè di pagina
                                footer[1] = footer[1].replace("- Fase di ban", "ha bannato " + map)
                                footer[1] = footer[1][9:]
                                footer.append("Turno di <@" + str(rappr_A) + "> - Fase di pick")
                                edit = True
                                # Rimozione della reazione del bot
                                await reaction.message.remove_reaction(reaction, self.bot.get_user(ROLE_WOWS_ITALIA))
                            elif len(footer) == 3:
                                # Modifica del piè di pagina
                                footer[2] = footer[2].replace("- Fase di pick", "ha scelto " + map)
                                footer[2] = footer[2][9:]
                                footer.append("Turno di <@" + str(rappr_A) + "> - Scelta dello spawn")
                                edit = True
                                # Rimozione della reazione del bot
                                await reaction.message.remove_reaction(reaction, self.bot.get_user(ROLE_WOWS_ITALIA))
                            elif len(footer) == 4 and footer[3] != "Turno di <@" + str(rappr_A) + "> - Scelta dello spawn":
                                # Modifica del piè di pagina
                                footer[3] = footer[3].replace("- Fase di pick", "ha scelto " + map)
                                footer[3] = footer[3][9:]
                                footer.append("Turno di <@" + str(rappr_B) + "> - Scelta dello spawn")
                                edit = True
                                # Rimozione della reazione del bot
                                await reaction.message.remove_reaction(reaction, self.bot.get_user(ROLE_WOWS_ITALIA))
                            # Bo5
                            elif len(footer) == 5 and header[2] == '5':
                                print('^ 2 round of pick')
                                print(footer)
                                print(len(footer))
                                if footer[4] == "Turno di <@" + str(rappr_A) + "> - Fase di pick":
                                    # Modifica del piè di pagina
                                    footer[4] = footer[4].replace("- Fase di pick", "ha scelto " + map)
                                    footer[4] = footer[4][9:]
                                    footer.append("Turno di <@" + str(rappr_A) + "> - Scelta dello spawn")
                                    edit = True
                                    # Rimozione della reazione del bot
                                    await reaction.message.remove_reaction(reaction, self.bot.get_user(ROLE_WOWS_ITALIA))
                            elif len(footer) == 6 and footer[5] == "Turno di <@" + str(rappr_B) + "> - Fase di pick" and header[2] == '5':
                                # Modifica del piè di pagina
                                footer[5] = footer[5].replace("- Fase di pick", "ha scelto " + map)
                                footer[5] = footer[5][9:]
                                footer.append("Turno di <@" + str(rappr_B) + "> - Scelta dello spawn")
                                edit = True
                                # Rimozione della reazione del bot
                                await reaction.message.remove_reaction(reaction, self.bot.get_user(ROLE_WOWS_ITALIA))
                        else:
                            # La reazione indica uno spawn
                            # Controllo del piè di pagina per identificare il turno
                            if len(footer) == 4:
                                if footer[3] == "Turno di <@" + str(rappr_A) + "> - Scelta dello spawn":
                                    # Modifica del piè di pagina
                                    footer[2] = footer[2] + ", spawn " + ("alpha" if i == 9 else "bravo")
                                    footer[3] = "Turno di <@" + str(rappr_B) + "> - Fase di pick"
                                    edit = True
                            elif len(footer) == 5 and header[2] == '3':
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
                            elif len(footer) == 5 and header[2] == '5':
                                if footer[4] == "Turno di <@" + str(rappr_B) + "> - Scelta dello spawn":
                                    # Modifica del piè di pagina
                                    footer[3] = footer[3] + ", spawn " + ("alpha" if i == 9 else "bravo")
                                    footer[4] = "Turno di <@" + str(rappr_A) + "> - Fase di pick"
                                    edit = True
                            elif len(footer) == 6:
                                if footer[5] == "Turno di <@" + str(rappr_A) + "> - Scelta dello spawn":
                                    # Modifica del piè di pagina
                                    footer[4] = footer[4] + ", spawn " + ("alpha" if i == 9 else "bravo")
                                    footer[5] = "Turno di <@" + str(rappr_B) + "> - Fase di pick"
                                    edit = True
                            elif len(footer) == 7:
                                if footer[6] == "Turno di <@" + str(rappr_B) + "> - Scelta dello spawn":
                                    footer[5] = footer[5] + ", spawn " + ("alpha" if i == 9 else "bravo")
                                    # Calcolo della mappa casuale
                                    random_choice = random.choice(reaction.message.reactions[:-2])
                                    map_index = self.EMOJI_POOL().index(str(random_choice))
                                    map = self.MAP_POOL()[map_index]
                                    spawn = random.choice(["alpha", "bravo"])
                                    # Modifica del piè di pagina
                                    footer[4] = footer[4] + ", spawn " + ("alpha" if i == 9 else "bravo")
                                    footer[6] = "Scelta casuale: " + map + ", <@" + str(rappr_A) + ">, spawn " + spawn
                                    edit = True
                        if edit == True:
                            # Generazione del nuovo messaggio
                            final_message = header + "\n\n" + body + "\n\n" + "\n".join(footer)
                            descrizione = "".join(final_message)
                            # Generazione del nuovo embed
                            embed = discord.Embed(title = "WoWs Italia - Map Vote", description = descrizione, color = 0xff0000)
                            embed.colour = discord.Colour.from_rgb(255, 255, 255)
                            # Modifica dell'embed
                            await reaction.message.edit(embed = embed)

                        # Rimozione della reazione dell'utente
                        await reaction.message.remove_reaction(reaction, user)
        # except Exception as error:
        #     print(error)
            return

def setup(bot):
    bot.add_cog(MapVote(bot))
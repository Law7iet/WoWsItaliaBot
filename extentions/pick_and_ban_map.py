# TODO: Refactor

import random
import re

import discord
from discord.ext import commands

from api.mongo_db import ApiMongoDB
from models.my_class.pick_and_ban_map_session import PickAndBanMapSession
from models.my_enum.database_enum import ConfigFileKeys
from models.my_enum.playoff_format_enum import PlayoffFormatEnum
from models.my_enum.roles_enum import RolesEnum
from utils.constants import *
from utils.functions import check_role, get_maps_reactions, get_spawn_reactions


class PickAndBanMap(commands.Cog):
    def __init__(self, bot: commands.bot):
        self.bot = bot
        self.api_mongo_db = ApiMongoDB()
        self.api_mongo_db = ApiMongoDB()

    def get_available_map(self) -> list[str]:
        config_file = self.api_mongo_db.get_config()
        return config_file[str(ConfigFileKeys.MAPS)]

    def get_playoff_format(self) -> PlayoffFormatEnum | None:
        config_file = self.api_mongo_db.get_config()
        match config_file[str(ConfigFileKeys.PLAYOFF_FORMAT)]:
            case 'Bo1':
                return PlayoffFormatEnum.BO1
            case 'Bo3':
                return PlayoffFormatEnum.BO3
            case 'Bo5':
                return PlayoffFormatEnum.BO5
            case _:
                return

    @commands.command()
    # async def map_pick_and_ban(self, ctx: commands.context.Context, input_a: str, input_b: str):
    async def test(self, ctx: commands.context.Context, input_a: str, input_b: str):
        # Role check
        if not await check_role(ctx, RolesEnum.ORG_LEAGUE):
            return
        # Representations check
        representant_a = ctx.guild.get_member(int(input_a[3:-1]))
        representant_b = ctx.guild.get_member(int(input_b[3:-1]))
        if (not representant_a) or (not representant_b):
            await ctx.send("Argomento errato (consiglio: tagga un utente)")
            return
        # Maps check
        maps = self.get_available_map()
        if not maps:
            await ctx.send("Non ci sono mappe disponibili (consiglio: chiedi agli organizzatori)")
            return
        # Playoff type check
        playoff_format = self.get_playoff_format()
        match playoff_format:
            case None:
                await self.bot.get_channel(CH_TXT_TESTING).send('Formato playoff invalido')
                return
            case PlayoffFormatEnum.BO1:
                await ctx.send('Nella modalità Bo1 non è possibile effettuare il Pick&Ban delle mappe.')
                return
            case _:
                pass
        # Make a session
        session = PickAndBanMapSession(str(representant_a.id), str(representant_b.id), maps, playoff_format)
        # Save session on DB
        self.api_mongo_db.insert_map_session(session.get_dict(True))
        # Display the session
        embed = session.get_embed()
        msg = await ctx.send(embed=embed)
        for emoji in get_maps_reactions(len(maps)):
            await msg.add_reaction(emoji)
        for emoji in get_spawn_reactions():
            await msg.add_reaction(emoji)
        return

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
                        elif len(footer) == 6 and footer[5] == "Turno di <@" + str(rappr_B) + "> - Fase di pick" and \
                                header[2] == '5':
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
                        embed = discord.Embed(title="WoWs Italia - Map Vote", description=descrizione, color=0xff0000)
                        embed.colour = discord.Colour.from_rgb(255, 255, 255)
                        # Modifica dell'embed
                        await reaction.message.edit(embed=embed)

                    # Rimozione della reazione dell'utente
                    await reaction.message.remove_reaction(reaction, user)
        # except Exception as error:
        #     print(error)
        return


def setup(bot):
    bot.add_cog(PickAndBanMap(bot))

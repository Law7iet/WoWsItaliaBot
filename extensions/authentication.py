import disnake
import requests
from disnake import ApplicationCommandInteraction, Embed, errors
from disnake.ext import commands
from disnake.ui import Button

from api.mongo.api import ApiMongoDB
from api.wows.api import WoWsSession
from models.my_enum.roles_enum import RolesEnum
from settings import config
from utils.functions import is_debugging, logout


class Authentication(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot
        self.api_mongo_db = ApiMongoDB()
        self.api_wows = WoWsSession(config.data["APPLICATION_ID"], is_debugging())

    @commands.slash_command(name="auth", description="Autentifica l'account di Discord con quello di WoWs")
    async def auth(self, inter: ApplicationCommandInteraction):
        # TODO: change che URL with the correct IP and port
        url = "http://127.0.0.1:5000/create"
        params = "?discord=" + str(inter.author.id)
        msg = """
Il servizio utilizzerà i seguenti dati personali:
:white_check_mark: il nome utente

Il servizio **non avrà accesso** a:
:x: l'email
:x: la password
:x: il numero di cellulare
Informazioni ulteriori **non verranno utilizzati**.
"""
        res = requests.get(url + params)
        if res.status_code == 200:
            embed = Embed(title="WoWsItaliaBot", description=msg)
            embed.set_footer(text="Eventuali nuovi permessi verranno notificati.")
            await inter.response.send_message(
                embed=embed,
                components=[
                    Button(label="Login", style=disnake.ButtonStyle.url, url=res.text),
                    Button(label="Logout", style=disnake.ButtonStyle.danger, custom_id="logout")
                ],
                ephemeral=True
            )
        else:
            await inter.response.send_message("Errore del server (" + str(res.status_code) + ").", ephemeral=True)

    @commands.slash_command(name="login", description="Controlla che l'autenticazione sia stata effettuata.")
    async def login(self, inter: ApplicationCommandInteraction):
        await inter.response.defer()
        # Get player info
        try:
            data = self.api_mongo_db.get_player_by_discord(str(inter.author.id))
            player_id = data["wows"]
        except (TypeError, KeyError):
            await inter.send("Non hai effettuato l'autenticazione. Digita `/auth`")
            return

        nickname = self.api_wows.player_personal_data([player_id])[0]["account_name"]
        try:
            clan_id = self.api_wows.player_clan_data([player_id])[0]["clan_id"]
            clan_tag = self.api_wows.clan_detail([clan_id])[0]["tag"]
            clan_tag = "[" + clan_tag + "] "
        except TypeError:
            clan_tag = ""

        # Add role and change nickname
        await inter.author.add_roles(inter.guild.get_role(int(RolesEnum.AUTH)))
        try:
            await inter.author.edit(nick=clan_tag + nickname)
        except errors.Forbidden:
            pass
        await inter.send("Login effettuato. Benvenut* " + nickname + "!")

    @commands.slash_command(name="logout", description="Effettua il logout.")
    async def logout(self, inter: ApplicationCommandInteraction):
        await logout(inter, self.api_mongo_db)


def setup(bot):
    bot.add_cog(Authentication(bot))

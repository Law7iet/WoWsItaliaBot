import disnake
import requests
from disnake import ApplicationCommandInteraction, Embed, errors
from disnake.ext import commands
from disnake.ui import Button

from api.mongo.api import ApiMongoDB
from api.wows.api import WoWsSession
from models.enum.discord_id import MyRoles
from settings import config
from utils.functions import is_debugging, logout


class Authentication(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot
        self.api_mongo = ApiMongoDB()
        self.api_wows = WoWsSession(config.data["APPLICATION_ID"], is_debugging())

    @commands.slash_command(name="login", description="Associa l'account di Discord con quello di WoWs.")
    async def login(self, inter: ApplicationCommandInteraction) -> None:
        msg = [
            "Il servizio utilizzerà i seguenti dati personali:",
            ":white_check_mark: il nome utente",
            "",
            "Il servizio **non avrà accesso** a:",
            ":x: l'email",
            ":x: la password",
            ":x: il numero di cellulare",
            "Informazioni ulteriori **non verranno utilizzati**."
        ]
        url = "https://server.law7iet.repl.co/create"
        res = requests.get(f"{url}?discord={inter.author.id}")
        if res.status_code == 200:
            embed = Embed(title="WoWsItaliaBot", description="\n".join(msg))
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
            await inter.response.send_message(f"Errore del server: status `{res.status_code}`.", ephemeral=True)

    @commands.slash_command(name="auth", description="Controlla e concede i permessi all'utente.")
    async def auth(self, inter: ApplicationCommandInteraction) -> None:
        await inter.response.defer()
        # Get the player from the database
        try:
            data = self.api_mongo.get_player_by_discord(str(inter.author.id))
            player_id = data["wows"]
        except (TypeError, KeyError):
            await inter.send("Non hai effettuato l'autenticazione. Digita `/login`.")
            return
        # Get the player's in-game name and his clan
        nickname = self.api_wows.player_personal_data([player_id])[0]["account_name"]
        try:
            clan_id = self.api_wows.player_clan_data([player_id])[0]["clan_id"]
            clan_tag = self.api_wows.clan_detail([clan_id])[0]["tag"]
            clan_tag = f"[{clan_tag}] "
        except (IndexError, TypeError):
            clan_tag = ""
        # Add the role and change the player's nickname
        msg = f"Autenticazione effettuata. Benvenut* <@{inter.author.id}>!"
        try:
            await inter.author.add_roles(inter.guild.get_role(int(MyRoles.AUTH)))
            await inter.author.edit(nick=clan_tag + nickname)
        except errors.Forbidden:
            msg = f"{msg}\n*Avviso* `auth(inter)`"
            msg = f"{msg}\nPermessi negati durante la modifica dell'utente <@{inter.author.id}>."
        await inter.send(msg)

    @commands.slash_command(name="logout", description="Scollega l'account di Discord con quello di WoWs.")
    async def logout(self, inter: ApplicationCommandInteraction) -> None:
        await logout(inter, self.api_mongo)


def setup(bot):
    bot.add_cog(Authentication(bot))

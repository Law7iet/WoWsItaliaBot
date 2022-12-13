from disnake import ApplicationCommandInteraction
from disnake.ext import commands


class Authentication(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot

    @commands.slash_command(name="auth", description="Authenticate your discord account and bind it with WoWs' account")
    async def authenticate(self, inter: ApplicationCommandInteraction):
        # TODO:
        #   Call the server, that returns a URL.
        #   Show the URL to the user, with a "OK" button.
        #   The user must click on the button after complete the Oauth
        #   - Server side:
        #     After the login the server inserts the user in the database
        #   - Client side:
        #     The "ok" button search the user in the db.
        #     If the user is in, add role, else no.
        pass


def setup(bot):
    bot.add_cog(Authentication(bot))

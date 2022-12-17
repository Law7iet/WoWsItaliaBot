from disnake import ApplicationCommandInteraction, Role, TextChannel, Member
from disnake.ext import commands

from api.mongo.api import ApiMongoDB
from api.wows.api import WoWsSession
from models.my_enum.roles_enum import RolesEnum
from models.my_enum.channels_enum import ChannelsEnum
from settings import config
from utils.functions import check_role, is_debugging, send_response_and_clear
from utils.modal import Modal


class Moderation(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot
        self.debugging = is_debugging()
        self.wargaming_api = WoWsSession(config.data["APPLICATION_ID"], is_debugging())
        self.mongo_api = ApiMongoDB()

    @commands.slash_command(name="write", description="Write a embed message and ping a role to notify them.")
    async def write(self, inter: ApplicationCommandInteraction, canale: TextChannel, ruolo: Role) -> None:
        if not await check_role(inter, RolesEnum.ADMIN):
            await inter.send("Non hai i permessi.")
            return
        try:
            await inter.response.send_modal(modal=Modal(ruolo, canale))
        except Exception as error:
            await self.bot.get_channel(int(ChannelsEnum.TXT_TESTING)).send("**>write command exception**")
            await self.bot.get_channel(int(ChannelsEnum.TXT_TESTING)).send("```" + str(error) + "```")

    @commands.slash_command(name="aggiungi")
    async def aggiungi(self, inter: ApplicationCommandInteraction) -> None:
        pass

    @aggiungi.sub_command(name="clan", description="Aggiunge un clan nel database.")
    async def clan(
        self,
        inter: ApplicationCommandInteraction,
        clan_id: int,
        rappresentante_1: Member = None,
        rappresentante_2: Member = None
    ) -> None:
        if not await check_role(inter, RolesEnum.ADMIN):
            await inter.send("Non hai i permessi.")
            return
        try:
            clan_detail = self.wargaming_api.clan_detail([clan_id])[0]
        except IndexError:
            await inter.send("Clan ID errato.")
            return

        await inter.response.defer()

        representation = []
        if rappresentante_1:
            representation.append(rappresentante_1.id)
        if rappresentante_2:
            representation.append(rappresentante_2.id)

        # TODO: Check representation TAG

        result = self.mongo_api.insert_clan({
            "id": clan_detail["clan_id"],
            "tag": clan_detail["tag"],
            "name": clan_detail["name"],
            "representation": representation
        })

        if result:
            msg = "Clan " + clan_detail["tag"] + " inserito."
            if rappresentante_1 and rappresentante_2:
                msg = msg + "Rappresentanti: <@" + str(rappresentante_1.id) + "> e <@" + str(rappresentante_2.id) + ">"
            elif rappresentante_1:
                msg = msg + "Rappresentante: <@" + str(rappresentante_1.id) + ">"
            elif rappresentante_2:
                msg = msg + "Rappresentante: <@" + str(rappresentante_2.id) + ">"
            await inter.send(msg)
        else:
            await inter.send("Clan non inserito.")


def setup(bot):
    bot.add_cog(Moderation(bot))

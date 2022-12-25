from disnake import ApplicationCommandInteraction, Role, TextChannel, Member
from disnake.ext import commands

from api.mongo.api import ApiMongoDB
from api.wows.api import WoWsSession
from models.my_enum.roles_enum import RolesEnum
from models.my_enum.channels_enum import ChannelsEnum
from settings import config
from utils.functions import check_role, is_debugging
from utils.modal import Modal


class Moderation(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot
        self.debugging = is_debugging()
        self.api_wows = WoWsSession(config.data["APPLICATION_ID"], is_debugging())
        self.api_mongo = ApiMongoDB()

    async def check_player(self, inter: ApplicationCommandInteraction, member: Member, clan_id: str) -> bool:
        if inter.guild.get_role(int(RolesEnum.AUTH)) in member.roles:
            player = self.api_mongo.get_player_by_discord(str(member.id))
            if not player:
                # This should never happen: an authenticated player is not found in the db
                await inter.send("<@" + str(member.id) + "> non è nel db.")
                return False
            try:
                clan = self.api_wows.player_clan_data([player["wows"]])[0]
                if str(clan["clan_id"]) == clan_id:
                    return True
                else:
                    raise TypeError
            except (TypeError, IndexError):
                await inter.send("<@" + str(member.id) + "> non è nel clan.")
                return False
        else:
            await inter.send("<@" + str(member.id) + "> non è autenticato.")
            return False

    @commands.slash_command(name="scrivi-messaggio", description="Scrive un messaggio embed e tagga un ruolo.")
    async def write_message(self, inter: ApplicationCommandInteraction, canale: TextChannel, ruolo: Role) -> None:
        if not await check_role(inter, RolesEnum.ADMIN):
            await inter.send("Non hai i permessi.")
            return
        try:
            await inter.response.send_modal(modal=Modal(ruolo, canale))
        except Exception as error:
            await self.bot.get_channel(int(ChannelsEnum.TXT_TESTING)).send("**>write command exception**")
            await self.bot.get_channel(int(ChannelsEnum.TXT_TESTING)).send("```" + str(error) + "```")

    @commands.slash_command(name="aggiungi-clan", description="Aggiunge un clan nel database.")
    async def add_clan(
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
            clan_detail = self.api_wows.clan_detail([clan_id])[0]
        except IndexError:
            await inter.send("Clan ID errato.")
            return

        await inter.response.defer()

        representation = []
        if rappresentante_1:
            if await self.check_player(inter, rappresentante_1, str(clan_detail["clan_id"])):
                representation.append(str(rappresentante_1.id))
            else:
                return
        if rappresentante_2:
            if await self.check_player(inter, rappresentante_2, str(clan_detail["clan_id"])):
                representation.append(str(rappresentante_2.id))
            else:
                return

        result = self.api_mongo.insert_clan({
            "id": clan_detail["clan_id"],
            "tag": clan_detail["tag"],
            "name": clan_detail["name"],
            "representations": representation
        })

        if result:
            role = inter.guild.get_role(int(RolesEnum.REP))
            msg = "Clan " + clan_detail["tag"] + " inserito.\n"
            if rappresentante_1 and rappresentante_2:
                await rappresentante_1.add_roles(role)
                await rappresentante_2.add_roles(role)
                msg = msg + "Rappresentanti: <@" + str(rappresentante_1.id) + "> e <@" + str(rappresentante_2.id) + ">"
            elif rappresentante_1:
                await rappresentante_1.add_roles(role)
                msg = msg + "Rappresentante: <@" + str(rappresentante_1.id) + ">"
            elif rappresentante_2:
                await rappresentante_2.add_roles(role)
                msg = msg + "Rappresentante: <@" + str(rappresentante_2.id) + ">"
            await inter.send(msg)
        else:
            await inter.send("Clan non inserito. Controllare che il clan non sia già inserito e il terminale e/o log.")


def setup(bot):
    bot.add_cog(Moderation(bot))

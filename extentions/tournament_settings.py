from discord.ext import commands
from models.my_enum.battle_type_enum import BattleTypeEnum
from api.mongo_db import ApiMongoDB

from models.my_enum.roles_enum import RolesEnum
from utils.functions import check_role


class TournamentSettings(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot
        self.apiMongoDB = ApiMongoDB()

    @commands.command()
    async def set_battle_type(self, ctx: commands.context.Context, battle_type: str):
        if not await check_role(ctx, RolesEnum.ADMIN):
            return
        battle_type = battle_type.upper()
        battle_type = BattleTypeEnum(battle_type)
        match battle_type:
            case BattleTypeEnum.BO1:
                value = "Bo1"
            case BattleTypeEnum.BO3:
                value = "Bo3"
            case BattleTypeEnum.BO5:
                value = "Bo5"
            case _:
                return
        data = {"battleMode": value}
        self.apiMongoDB.update_config(data)
        await ctx.send("Impostato la modalità " + value)

    @commands.command()
    async def set_maps(self, ctx: commands.context.Context, *, maps: str):
        if not await check_role(ctx, RolesEnum.ADMIN):
            return
        map_list = maps.split(',')
        value_list = []
        message = ""
        for element in map_list:
            x = element.lstrip(' ')
            y = x.rstrip(' ')
            if y:
                value_list.append(y)
                message = message + "- " + y + "\n"
        data = {"maps": value_list}
        self.apiMongoDB.update_config(data)
        await ctx.send("Impostato le mappe:\n" + message[:-2])


def setup(bot):
    bot.add_cog(TournamentSettings(bot))
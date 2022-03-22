from discord.ext import commands
from models.my_enum.battle_type_enum import BattleTypeEnum
from api.mongo_db import ApiMongoDB

from utils.constants import CH_TXT_TESTING
from models.my_enum.roles_enum import RolesEnum
from models.my_enum.database_enum import ConfigFileKeys
from utils.functions import check_role


class ConfigSettings(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot
        self.apiMongoDB = ApiMongoDB()

    async def getter(self, ctx: commands.context.Context, config_key: ConfigFileKeys):
        if not await check_role(ctx, RolesEnum.SAILOR):
            return
        try:
            config_file = self.apiMongoDB.get_config()
            return config_file[str(config_key)]
        except Exception as error:
            await self.bot.get_channel(CH_TXT_TESTING).send('**getter of ' + str(config_key)
                                                            + ' type command exception**')
            await self.bot.get_channel(CH_TXT_TESTING).send('```' + str(error) + '```')

    @commands.command()
    async def get_battle_type(self, ctx: commands.context.Context):
        value = await self.getter(ctx, ConfigFileKeys.PLAYOFF_FORMAT)
        if value:
            await ctx.send('La modalità di battaglia è: ' + value + '.')

    @commands.command()
    async def get_clan_battle_season(self, ctx: commands.context.Context):
        value = await self.getter(ctx, ConfigFileKeys.CLAN_BATTLE_CURRENT_SEASON)
        if value:
            await ctx.send('La stagione delle clan battle è: ' + str(value) + '.')

    @commands.command()
    async def get_maps(self, ctx: commands.context.Context):
        value = await self.getter(ctx, ConfigFileKeys.MAPS)
        if value:
            message = ''
            for element in value:
                message = message + '- ' + element + '\n'
            await ctx.send('Le mappe sono:\n' + message)
        else:
            await ctx.send('Non è stata impostata nessuna mappa.')

    @commands.command()
    async def set_battle_type(self, ctx: commands.context.Context, battle_type: str):
        if not await check_role(ctx, RolesEnum.ADMIN):
            return
        try:
            battle_type = battle_type.upper()
            battle_type = BattleTypeEnum(battle_type)
            match battle_type:
                case BattleTypeEnum.BO1:
                    value = 'Bo1'
                case BattleTypeEnum.BO3:
                    value = 'Bo3'
                case BattleTypeEnum.BO5:
                    value = 'Bo5'
                case _:
                    return
            data = {str(ConfigFileKeys.PLAYOFF_FORMAT): value}
            result = self.apiMongoDB.update_config(data)
            if result.matched_count == 1:
                await ctx.send('Impostato la modalità: ' + value + '.')
            else:
                raise Exception(result)
        except Exception as error:
            await self.bot.get_channel(CH_TXT_TESTING).send('**>set_battle_type command exception**')
            await self.bot.get_channel(CH_TXT_TESTING).send('```' + str(error) + '```')

    @commands.command()
    async def set_clan_battle_season(self, ctx: commands.context.Context, season: str):
        if not await check_role(ctx, RolesEnum.ADMIN):
            return
        try:
            value = int(season)
            if value <= 0:
                return
            data = {str(ConfigFileKeys.CLAN_BATTLE_CURRENT_SEASON): value}
            result = self.apiMongoDB.update_config(data)
            if result.matched_count == 1:
                await ctx.send('Impostato la stagione: ' + str(value) + '.')
            else:
                raise Exception(result)
        except Exception as error:
            await self.bot.get_channel(CH_TXT_TESTING).send('**>set_clan_battle_season command exception**')
            await self.bot.get_channel(CH_TXT_TESTING).send('```' + str(error) + '```')

    @commands.command()
    async def set_maps(self, ctx: commands.context.Context, *, maps: str):
        if not await check_role(ctx, RolesEnum.ADMIN):
            return
        try:
            map_list = maps.split(',')
            value_list = []
            message = ''
            for element in map_list:
                x = element.lstrip(' ')
                y = x.rstrip(' ')
                if y:
                    value_list.append(y)
                    message = message + '- ' + y + '\n'
            data = {str(ConfigFileKeys.MAPS): value_list}
            result = self.apiMongoDB.update_config(data)
            if result.matched_count == 1:
                await ctx.send('Impostato le mappe:\n' + message[:-2])
            else:
                raise Exception(result)
        except Exception as error:
            await self.bot.get_channel(CH_TXT_TESTING).send('**>set_maps command exception**')
            await self.bot.get_channel(CH_TXT_TESTING).send('```' + str(error) + '```')


def setup(bot):
    bot.add_cog(ConfigSettings(bot))

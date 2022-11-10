import datetime

from discord.ext import commands

from api.mongo_db import ApiMongoDB
from models.my_enum.database_enum import ConfigFileKeys
from models.my_enum.playoff_format_enum import PlayoffFormatEnum
from models.my_enum.roles_enum import RolesEnum
from utils.constants import CH_TXT_TESTING
from utils.functions import check_role


class ConfigSettings(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot
        self.api_mongo_db = ApiMongoDB()

    async def getter(self, ctx: commands.context.Context, config_key: ConfigFileKeys):
        if not await check_role(ctx, RolesEnum.SAILOR):
            return
        try:
            config_file = self.api_mongo_db.get_config()
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
            battle_type = PlayoffFormatEnum(battle_type)
            match battle_type:
                case PlayoffFormatEnum.BO1:
                    value = 'Bo1'
                case PlayoffFormatEnum.BO3:
                    value = 'Bo3'
                case PlayoffFormatEnum.BO5:
                    value = 'Bo5'
                case _:
                    return
            data = {str(ConfigFileKeys.PLAYOFF_FORMAT): value}
            result = self.api_mongo_db.update_config(data)
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
            result = self.api_mongo_db.update_config(data)
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
            result = self.api_mongo_db.update_config(data)
            if result.matched_count == 1:
                await ctx.send('Impostato le mappe:\n' + message[:-2])
            else:
                raise Exception(result)
        except Exception as error:
            await self.bot.get_channel(CH_TXT_TESTING).send('**>set_maps command exception**')
            await self.bot.get_channel(CH_TXT_TESTING).send('```' + str(error) + '```')

    @commands.command()
    async def set_cb_days(self, ctx: commands.context.Context, start: str, end: str):
        if not await check_role(ctx, RolesEnum.ADMIN):
            return
        start = start.split('-')
        end = end.split('-')
        try:
            # Check integrity
            start = datetime.datetime(int(start[0]), int(start[1]), int(start[2]))
            end = datetime.datetime(int(end[0]), int(end[1]), int(end[2]))
            data1 = {str(ConfigFileKeys.CLAN_BATTLE_STARTING_DAY): start.strftime('%Y-%m-%d')}
            data2 = {str(ConfigFileKeys.CLAN_BATTLE_FINAL_DAY): end.strftime('%Y-%m-%d')}
            result = self.api_mongo_db.update_config(data1)
            result = self.api_mongo_db.update_config(data2)
        except:
            await ctx.send("Errore. sintassi: AAAA-MM-GG AAAA-MM-GG")


def setup(bot):
    bot.add_cog(ConfigSettings(bot))

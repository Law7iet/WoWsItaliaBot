from disnake import Intents, VersionInfo
from disnake.ext import commands

import config
from utils.constants import CH_TXT_LOG_EVENT

if __name__ == "__main__":

    print("Disnake version: " + str(VersionInfo))

    # Bots setup
    intents = Intents.default()
    intents.members = True
    intents.message_content = True
    bot = commands.Bot(
            command_prefix=commands.when_mentioned_or(">"),
            intents=intents
    )
    # Extensions setup
    extensions = [
        "clan_battle_ranking",
        "event_manager",
        "pick_and_ban_map",
        "moderation",
        "tournament_ranking",
        "config_settings"
    ]
    for extension in extensions:
        try:
            bot.load_extension("extensions." + extension)
        except Exception as error:
            print("{} cannot be loaded. [{}]".format(extension, error))

    # Ack
    @bot.event
    async def on_ready():
        try:
            channel = bot.get_channel(CH_TXT_LOG_EVENT)
            await channel.send('WoWsItalia bot is up.')
        except Exception as error:
            print(error)
            return

    # Run bot
    bot.run(config.data["TOKEN"])
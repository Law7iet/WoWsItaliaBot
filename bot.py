import discord
from discord.ext import commands

import config
from utils.constants import CH_TXT_LOG_EVENT

if __name__ == "__main__":

    print(discord.version_info)
    # Bot's setup
    intents = discord.Intents.default()
    intents.members = True
    bot = commands.Bot(command_prefix = ">", intents = intents)
    bot.remove_command("help")

    extensions = ["clan_battle_ranking", "event_manager", "pick_and_ban_map", "moderation", "tournament_ranking",
                  "config_settings"]
    for extension in extensions:
        try:
            bot.load_extension("extensions." + extension)
        except Exception as error:
            print("{} cannot be loaded. [{}]".format(extension, error))

    @bot.event
    async def on_ready():
        try:
            channel = bot.get_channel(CH_TXT_LOG_EVENT)
            await channel.send('WoWsItalia bot is up.')
        except Exception as error:
            print(error)
            return

    @bot.command()
    async def ping(ctx):
        await ctx.send("Pong")

    @bot.command()
    async def help(ctx):
        try:
            embed = discord.Embed()
            embed.set_author(name = 'WoWsItaliaBot', icon_url = 'https://cdn.discordapp.com/attachments/696853218642231346/780440538604109844/wowsITA.png')
            embed.colour = discord.Colour.from_rgb(255, 255, 255)
            embed.description = 'Il prefisso da usare è: `>`\n `[]` indica un parametro opzionale. \n `{}` indica un parametro ripetibile.'
            embed.add_field(name = '`write channel_ID message`', value = 'Scrive *message* nel canale con ID *channel_ID*', inline = False)
            embed.add_field(name = '`edit channel_ID message_ID "messagge"`', value = 'Sostituisce il messaggio con ID *message_ID* col testo *messagge*.', inline = False)
            embed.add_field(name = '`league edizione posizione team url partecipanti`', value = 'Crea un embed per l\'Italian League. `edizione` è una stringa (prima, seconda,... ), `posizione` è un numero intero (deve essere 1, 2 o 3), `team` è il nome del team, `url` è il logo del team, `partecipanti` è una lista dei partecipanti divisi da uno spazio (un partecipante è una parola).', inline = False)
            embed.add_field(name = '`cup edizione posizione team url partecipanti`', value = 'Crea un embed per l\'Italian Cup. `edizione` è una stringa (prima, seconda,... ), `posizione` è un numero intero (deve essere 1, 2 o 3), `team` è il nome del team, `url` è il logo del team, `partecipanti` è una lista opzionale dei partecipanti divisi da uno spazio (un partecipante è una parola).', inline = False)
            embed.add_field(name = '`mapvote @user1 @user2`', value = 'Genera un embed per votare le mappe per i giocatori @user1 e @user2', inline = False)
            embed.set_footer(text = 'Per avere l\'ID di un messaggio o canale, bisogna attivare la modalità sviluppatore su Discord.' )
            await ctx.send(embed = embed)
        except Exception as error:
            print(error)
            return

    # Run bot
    bot.run(config.data["TOKEN"])

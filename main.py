from os import system

from disnake import Intents, HTTPException, ApplicationCommandInteraction
from disnake.ext import commands

from settings import config
from settings.keep_alive import keep_alive
from utils.functions import is_debugging

if __name__ == "__main__":

	if is_debugging():
		print("--------------------------------------------------------------------------------")
		print("                                   DEBUGGING                                    ")
		print("--------------------------------------------------------------------------------")
	
	# Bots setup
	intents = Intents.default()
	intents.members = True
	bot = commands.InteractionBot(intents=intents, test_guilds=[379679393989001221])
	extensions = [
		"authentication",
		"clan_battle",
		"event_manager",
		"moderation",
		"nickname",
		"representation",
		"tournament_ranking"
	]
	for extension in extensions:
		try:
			bot.load_extension("extensions." + extension)
		except Exception as error:
			print("{} cannot be loaded. [{}]".format(extension, error))
	
	# Bot test slash command
	@bot.slash_command(description="Pong!")
	async def ping(inter: ApplicationCommandInteraction):
		await inter.response.send_message(f"Pong! `{round(bot.latency * 1000)}`ms")

	# Bot ack
	@bot.event
	async def on_ready():
		print("WoWsItalia is up")
	
	# Run bot
	try:
		keep_alive()
		bot.run(config.data["DISCORD_TOKEN"])
	except HTTPException as e:
		if e.status == 429:
			print("\n\n\nDiscord servers denied the connection: too many requests")
			print("Stopping the process and restart it")
			system("python ./settings/restarter.py")
			system("kill 1")
		else:
			raise e
	
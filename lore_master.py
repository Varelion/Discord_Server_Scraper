import discord
from discord.ext import commands
import os
from dotenv import load_dotenv
from datetime import datetime
import string

load_dotenv()

# Load bot token from environment variable
TOKEN = os.getenv("LORE_MASTER_TOKEN")

#desired SERVER ID
SERVER_ID = os.getenv("SERVER_ID")

# Set up the bot with appropriate intents
intents = discord.Intents.default()
intents.messages = True
intents.guilds = True
intents.message_content = True  # Required for reading message content

bot = commands.Bot(command_prefix="!", intents=intents)

def num(x : str ) -> int:
	if isinstance(x, int):
		return x
	return int(x.strip())

def format_filename(s):
	"""Take a string and return a valid filename constructed from the string.
		Uses a whitelist approach: any characters not present in valid_chars are
		removed. Also spaces are replaced with underscores.

		Note: this method may produce invalid filenames such as ``, `.` or `..`
		When I use this method I prepend a date string like '2009_01_15_19_46_32_'
		and append a file extension like '.txt', so I avoid the potential of using
		an invalid filename.

	"""
	valid_chars = "-_.() %s%s" % (string.ascii_letters, string.digits)
	filename = ''.join(c for c in s if c in valid_chars)
	filename = filename.replace(' ','_') # I don't like spaces in filenames.
	return filename

async def scrape_all_channels(guild: discord.guild):
	# Create the directory for saving messages if it doesn't exist
	FOLDER_NAME = (f"./lore_master_output_{guild.name.replace(" ", "-")}_{datetime.now().strftime("%Y-%m-%d")}")
	if not os.path.exists(FOLDER_NAME):
		os.makedirs(FOLDER_NAME)

	# Loop through each channel in the guild
	for channel in guild.text_channels:
		CHANNEL_NAME = format_filename(channel.name)
		print(f"Scraping messages from #{CHANNEL_NAME}...")

		# Create a file name with channel name and the current timestamp
		timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
		filename = f"./{FOLDER_NAME}/{CHANNEL_NAME}_{timestamp}.txt"

		# Open the file to save messages
		with open(filename, "w", encoding="utf-8") as file:
			# Fetch and write messages from the channel
			async for message in channel.history(limit=None, oldest_first=True):
				timestamp = message.created_at.strftime("%Y-%m-%d %H:%M:%S")
				file.write(f"[{timestamp}] {message.author.name}: {message.content}\n")

		print(f"Messages from #{CHANNEL_NAME} saved to {filename}")

@bot.event
async def on_ready():
	print(f"Logged in as {bot.user}!")

	for guild in bot.guilds:
		if num(guild.id) == num(SERVER_ID):
			await scrape_all_channels(guild)
		else:
			print("BOT NOT IN SERVER_ID: ", SERVER_ID)
			await bot.close()




	print("Scraping completed. Closing bot...")
	await bot.close()

bot.run(TOKEN)

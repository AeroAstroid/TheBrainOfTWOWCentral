# TEMPORARY

MESSAGE_ID = 913191494159044609
SIGNUPS_CHANNEL = "twows-in-signups"

# Import discord
import discord

def HELP(PREFIX):
	return {
		"COOLDOWN": 1,
		"MAIN": "Testing command.",
		"FORMAT": "",
		"CHANNEL": 0,
		"USAGE": f"""idk lol
		""".replace("\n", "").replace("\t", ""),
		"CATEGORY" : "Fun"
	}

PERMS = 0 # Non-members
ALIASES = []
REQ = []

async def MAIN(message, args, level, perms, SERVER):

    # Get signups channel
    signups_channel = discord.utils.get(SERVER["MAIN"].channels, name=SIGNUPS_CHANNEL) # Post messages in here
    signups_msg = await signups_channel.fetch_message(MESSAGE_ID)

    await message.channel.send(signups_msg.content)

from Config._const import PREFIX
import time

HELP = {
	"MAIN": "Reimports the commands, updating command code without needing to restart",
	"FORMAT": "",
	"CHANNEL": 2,
	"USAGE": f"""Using `{PREFIX}reimport` will trigger a command reimport. 
	It'll report the time it took to import the commands.""".replace("\n", "").replace("\t", "")
}

PERMS = 2 # Staff
ALIASES = []
REQ = []

async def MAIN(message, args, level, perms):
	await message.channel.send("Reimporting commands...")
	print(f"Reimporting command files on command by {message.author.name} // {message.created_at} UTC.\n\n")
	return [3, time.time()] # Flag to reimport commands
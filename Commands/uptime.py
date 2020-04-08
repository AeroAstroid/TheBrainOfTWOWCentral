import time

def HELP(PREFIX):
	return {
		"COOLDOWN": 1,
		"MAIN": "Displays how long the bot has been up for",
		"FORMAT": "",
		"CHANNEL": 1,
		"USAGE": f"""Using `{PREFIX}uptime` simply returns the amount of time since 
		the bot last restarted.""".replace("\n", "").replace("\t", "")
	}

PERMS = 0 # Non-member
ALIASES = ["UP"]
REQ = ["LOGIN"]

async def MAIN(message, args, level, perms, SERVER, LOGIN):
	# 1000 * seconds = milliseconds
	delta = 1000 * (time.time() - LOGIN)

	abs_delta = [
		int(delta), # Milliseconds
		int(delta / 1000), # Seconds
		int(delta / (1000 * 60)), # Minutes
		int(delta / (1000 * 60 * 60)), # Hours
		int(delta / (1000 * 60 * 60 * 24))] # Days

	ml = abs_delta[0] % 1000
	sc = abs_delta[1] % 60
	mi = abs_delta[2] % 60
	hr = abs_delta[3] % 24
	dy = abs_delta[4]

	await message.channel.send(f"Bot has been up for {dy}d {hr}h {mi}m {sc}s {ml}ms.")
	return
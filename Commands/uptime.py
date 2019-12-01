import time
from Config._const import PREFIX

HELP = {
	"MAIN": "Displays how long the bot has been up for",
	"FORMAT": "",
	"CHANNEL": 1,
	"USAGE": f"""Using `{PREFIX}uptime` simply returns the amount of time since 
	the bot last restarted.""".replace("\n", "").replace("\t", "")
}

PERMS = 0
ALIASES = ["UP"]
REQ = ["LOGIN"]

async def MAIN(message, args, level, perms, LOGIN):
	delta = 1000 * (time.time() - LOGIN)
	abs_delta = [
		int(delta),
		int(delta / 1000),
		int(delta / (1000 * 60)),
		int(delta / (1000 * 60 * 60)),
		int(delta / (1000 * 60 * 60 * 24))]

	ml = abs_delta[0] % 1000
	sc = abs_delta[1] % 60
	mi = abs_delta[2] % 60
	hr = abs_delta[3] % 24
	dy = abs_delta[4]

	await message.channel.send(f"Bot has been up for {dy}d {hr}h {mi}m {sc}s {ml}ms.")
	return
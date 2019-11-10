import time

HELP = "Displays the amount of time since the bot was last booted up"
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
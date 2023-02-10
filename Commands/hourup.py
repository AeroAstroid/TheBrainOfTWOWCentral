def HELP(PREFIX):
	return {
		"COOLDOWN": 10,
		"MAIN": "",
		"FORMAT": "",
		"CHANNEL": 2,
		"USAGE": f"""Using `{PREFIX}hourup` will add 1 hour to `PARAMS["HOUR"]`.""".replace("\n", "").replace("\t", ""),
		"CATEGORY" : "Developer"
	}

PERMS = 3 # Developer
ALIASES = []
REQ = ["PARAMS"]

async def MAIN(message, args, level, perms, SERVER, PARAMS):
  PARAMS["HOUR"] += 1
	return

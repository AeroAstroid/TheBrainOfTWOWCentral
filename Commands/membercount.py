import discord, os

def HELP(PREFIX):
	return {
		"COOLDOWN": 1,
		"MAIN": "Displays the server's current member count",
		"FORMAT": "",
		"CHANNEL": 0,
		"USAGE": f"""Using `{PREFIX}membercount` will return the current member count of the server 
		it's used in.""".replace("\n", "").replace("\t", ""),
		"CATEGORY" : "Community"
	}

PERMS = 0 # Non-members
ALIASES = ["MEMBERS", "M"]
REQ = []

async def MAIN(message, args, level, perms, SERVER):
	if level == 1:
		member_count = len(SERVER["MAIN"].members)
		await message.channel.send(f"We have **{member_count}** members.")
	elif args[1].lower() == "list":
		member_list = sorted([f"{x.name}#{x.discriminator}" for x in SERVER["MAIN"].members])
		open("member_list.txt", "w", encoding="utf-8").write("\n".join(member_list))
		await message.channel.send(f"Here's a list of all **{len(member_list)}** server members:",
		file=discord.File("member_list.txt"))
		os.remove("member_list.txt")
	return
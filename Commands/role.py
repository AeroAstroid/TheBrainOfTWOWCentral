import discord
from Config._functions import is_whole

def HELP(PREFIX):
	return {
		"COOLDOWN": 5,
		"MAIN": "Role distribution command",
		"FORMAT": "",
		"CHANNEL": 0,
		"USAGE": f"""wip""".replace("\n", "").replace("\t", ""),
		"CATEGORY" : "Staff"
	}

PERMS = 2 # Staff
ALIASES = []
REQ = []

async def MAIN(message, args, level, perms, SERVER):
	if level == 1:
		await message.channel.send("Provide a role ID!")
		return
	
	if not is_whole(args[1]):
		await message.channel.send("Invalid role ID!")
		return

	role_id = int(args[1])
	role = discord.utils.get(SERVER["MAIN"].roles, id=role_id)

	if role is None:
		await message.channel.send("Invalid role ID!")
		return

	if level == 2:
		await message.channel.send("Specify whether you want to remove or add the roles to the users!")
		return
	
	if args[2] not in ["remove", "add"]:
		await message.channel.send("Specify whether you want to remove or add the roles to the users!")
		return
	
	if level == 3:
		await message.channel.send("Send a list of IDs that you want to do role manipulation with!")
		return
	
	for member_id in args[3:]:
		if member_id == "all" and args[2] == "remove":
			all_members = role.members
			for m in all_members:
				await m.remove_roles(role)
			
		else:
			member = SERVER["MAIN"].get_member(int(member_id))
			try:
				if args[2] == "remove":
					await member.remove_roles(role)
				else:
					await member.add_roles(role)
			except:
				await message.channel.send(member_id + " not found")
	
	await message.channel.send(f"Successfully updated {role.name} members")
	return

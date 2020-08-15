import discord
from Config._db import Database

def HELP(PREFIX):
	return {
		"COOLDOWN": 3,
		"MAIN": "Team flair distribution command",
		"FORMAT": "(subcommand) (team_name/contestant)",
		"CHANNEL": 0,
		"USAGE": f"""Using `{PREFIX}team` or `{PREFIX}team` followed by `teams`, `list` or `options` gives you a list 
		of the current team flairs. Using `{PREFIX}team count` gives you a list of all team flairs and how many people 
		have each one. To get a team flair, use `{PREFIX}team get` followed by either the name of the team or the name 
		of its contestant. To remove a team flair that you have, use `{PREFIX}team remove`, followed by either the 
		name of the team or the name of its contestant.""".replace("\n", "").replace("\t", "")
	}

PERMS = 1 # Member
ALIASES = []
REQ = []

async def MAIN(message, args, level, perms, SERVER):
	db = Database()

	id_search_key = str(SERVER["MAIN"].id)

	try:
		roles, contestants, contnames, emojis, limit = db.get_entries(
			"teamdata", columns=["roles", "contestants", "contname", "emojis", "teamlimit"],
			conditions={"server":id_search_key}
		)[0]
	except IndexError:
		await message.channel.send("There are no team flairs in this server!")
		return

	flair_list = False
	count = False
	if level == 1:
		flair_list = True
	elif args[1].lower() in ["teams", "list", "options"]:
		flair_list = True
	elif args[1].lower() == "count":
		flair_list = True
		count = True
	
	if flair_list:
		role_list = roles.split(" ")

		if contnames != "":
			cont_list = contnames.split(" / ")
		
		if emojis != "":
			emoji_list = emojis.split(" ")

		if count:
			output = [f"Here's the current team member standings.\n\n"]

			teams = []
			for t in range(len(role_list)):
				team_info = []
				
				try:
					team_info.append(emoji_list[t])
				except:
					pass

				try:
					team_info.append("**" + cont_list[t] + "** -")
				except:
					team_info.append("<@&" + role_list[t] + "> -")
				
				try:
					counter = len(discord.utils.get(SERVER["MAIN"].roles, id=int(role_list[t])).members)
				except:
					counter = 0
				
				team_info.append(counter)
				team_info.append("member" + ('' if counter == 1 else 's') + "\n")
			
				teams.append(team_info)
			
			teams = sorted(teams, reverse=True, key=lambda m: m[1])

			teams = [" ".join([str(a) for a in t]) for t in teams]

			for t in teams:
				if len(output[-1]) + len(t) > 1980:
					output.append("")
				
				output[-1] += t

		else:
			output = [f"Here's a list of available team flairs.\nYou can pick **{limit}** at most.\n\n"]

			for t in range(len(role_list)):
				line = ""

				try:
					line += emoji_list[t] + " - "
				except:
					pass

				try:
					line += "**" + cont_list[t] + "** - "
				except:
					pass

				line += "<@&" + role_list[t] + ">\n"

				if len(output[-1]) + len(line) > 1980:
					output.append("")
				
				output[-1] += line

		for m in output:
			await message.channel.send(m)
		return
	
	if args[1].lower() in ["get", "remove"]:
		if level == 2:
			await message.channel.send(f"Specify the team flair you want to {args[1].lower()}!")
			return
		
		cont_list = contnames.split(" / ")
		cont_id_list = contestants.split(" ")
		role_list = roles.split(" ")

		cont_list_l = [x.lower() for x in cont_list]

		key = " ".join(args[2:]).lower()

		found_first = False
		picked = []

		found_list = [x for x in cont_list_l if x.startswith(key)]

		if len(found_list) == 1:
			ind = cont_list_l.index(found_list[0])
			picked = [cont_list[ind], cont_id_list[ind], role_list[ind]]
		elif len(found_list) > 1:
			found_first = True
		
		if picked == []:
			role_name_list = [
				discord.utils.get(SERVER["MAIN"].roles, id=int(x)).name for x in role_list
				if discord.utils.get(SERVER["MAIN"].roles, id=int(x)) != None]

			found_list = [x for x in role_name_list if x.lower().startswith(key)]
			
			if len(found_list) == 1:
				ind = role_name_list.index(found_list[0])
				picked = [cont_list[ind], cont_id_list[ind], role_list[ind]]
			elif len(found_list) > 1:
				found_first = True
		
		if picked == []:
			if found_first:
				await message.channel.send(
					"There seem to be multiple flairs matching that search key. Please specify more!")
			else:
				await message.channel.send("I couldn't find a team flair matching that search key!")
			return

		author_member = SERVER["MAIN"].get_member(message.author.id)
		current_flair_list = [str(x.id) for x in author_member.roles if str(x.id) in role_list]

		if args[1].lower() == "get":
			if picked[1] == str(message.author.id):
				await message.channel.send("You can't pick your own team flair!")
				return
			
			if picked[2] in current_flair_list:
				await message.channel.send("You already have that team flair!")
				return
			
			if len(current_flair_list) >= limit:
				await message.channel.send(
					f"You already have {limit} flair{'' if limit==1 else 's'}. You can't get any more!")
				return
			
			team_role = discord.utils.get(SERVER["MAIN"].roles, id=int(picked[2]))
			await author_member.add_roles(team_role)
			await message.channel.send(f"You have been added to **{picked[0]}**'s team!")
			return
		
		if args[1].lower() == "remove":
			if picked[2] not in current_flair_list:
				await message.channel.send("You don't have that team flair!")
			
			team_role = discord.utils.get(SERVER["MAIN"].roles, id=int(picked[2]))
			await author_member.remove_roles(team_role)
			await message.channel.send(f"You are no longer on **{picked[0]}**'s team.")
			return

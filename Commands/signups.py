import discord, datetime
from Config._functions import is_whole
from Config._db import Database

def HELP(PREFIX):
	return {
		"COOLDOWN": 2,
		"MAIN": "Command to manage the #twows-in-signups channel",
		"FORMAT": "wip",
		"CHANNEL": 0,
		"USAGE": f"""wip""".replace("\n", "").replace("\t", ""),
		"CATEGORY" : "Staff"
	}

PERMS = 2 # Staff
ALIASES = []
REQ = []

async def MAIN(message, args, level, perms, SERVER):
	if level == 1:
		await message.channel.send("Include a subcommand!")
		return
	
	if args[1].lower() == "setup":
		if level == 2:
			n = 10
		elif is_whole(args[2]):
			n = int(args[2])
		else:
			n = 10
		
		msg_ids = [str(message.channel.id)]
		for _ in range(n):
			msg = await message.channel.send("\u200b")
			msg_ids.append(str(msg.id))
		
		await message.channel.send(" ".join(msg_ids))
		return
	
	if args[1].lower() == "update":
		await message.channel.send("Updating list...")
		await SERVER["EVENTS"]["SIGNUPS"].update_list(update_channel=True)
		await message.channel.send("Updated list!")
		return
	
	if args[1].lower() == "clearrecent":
		db = Database()
		id_list = db.get_entries("signupmessages")[0][0].split(" ")
		
		channel_id = int(id_list[0])
		recent_list_id = int(id_list[-1])
		
		ch = discord.utils.get(SERVER["MAIN"].channels, id=channel_id)
		r_list_msg = None
		
		async for msg in ch.history(limit=100):
			if msg.id == recent_list_id:
				r_list_msg = msg
		
		if r_list_msg is not None:
			await r_list_msg.edit(content="__**Recent list changes:**__")
			await message.channel.send("Updated list!")
		return
	
	if args[1].lower() == "edit":
		msg = message.content

		if "name:[" not in msg:
			await message.channel.send("Include the name of the TWOW you want to edit!")
			return

		db = Database()
		
		starting_bound = msg[msg.find("name:[") + 6:]
		twow_name = starting_bound[:starting_bound.find("]")]

		twow_list = db.get_entries("signuptwows", conditions={"name": twow_name})

		if len(twow_list) == 0:
			await message.channel.send(f"There's no TWOW named **{twow_name}** in the signup list!")
			return
		
		old_entry = twow_list[0]
		old_entry = dict(zip(["name", "hosts", "link", "description", "time", "verified"], old_entry))
		
		entry = {
			"name": None,
			"hosts": None,
			"link": None,
			"description": None,
			"time": None,
			"verified": None}
		
		cond = {"name": twow_name}

		if "newname:[" in msg:
			starting_bound = msg[msg.find("newname:[") + 9:]
			new_name = starting_bound[:starting_bound.find("]")]
			entry["name"] = new_name
		
		if "host:[" in msg:
			starting_bound = msg[msg.find("host:[") + 6:]
			hosts = starting_bound[:starting_bound.find("]")]
			entry["hosts"] = hosts
		
		if "link:[" in msg:
			starting_bound = msg[msg.find("link:[") + 6:]
			link = starting_bound[:starting_bound.find("]")].replace("<", "").replace(">", "")
			entry["link"] = link
		
		if "desc:[" in msg:
			starting_bound = msg[msg.find("desc:[") + 6:]
			desc = starting_bound[:starting_bound.find("]")]
			entry["description"] = desc
		
		if "deadline:[" in msg:
			starting_bound = msg[msg.find("deadline:[") + 10:]
			dl_string = starting_bound[:starting_bound.find("]")]
			deadline = datetime.datetime.strptime(dl_string, "%d/%m/%Y %H:%M")
			deadline = deadline.replace(tzinfo=datetime.timezone.utc).timestamp()
			entry["time"] = deadline
		
		if "verified:[" in msg:
			starting_bound = msg[msg.find("verified:[") + 10:]
			verified = starting_bound[:starting_bound.find("]")]
			if verified in ["0", ""]:
				vf = 0
			else:
				vf = 1
			entry["verified"] = vf
		
		entry = {k: d for k, d in entry.items() if d is not None}
		
		if len(entry.keys()) == 0:
			await message.channel.send("You've made no edits to this TWOW!")
			return
		
		db.edit_entry("signuptwows", entry=entry, conditions=cond)

		announce = "dont_announce" not in msg
		await SERVER["EVENTS"]["SIGNUPS"].update_list(announce=announce)

		old_info_string = ""
		for k, v in old_entry.items():
			if v != "":
				tag = k
				if k == "hosts":
					tag = "host"
				if k == "time":
					tag = "deadline"
				if k == "description":
					tag = "desc"
				
				old_info_string += f"{tag}:[{v}] "
		
		for k, v in entry.items():
			old_entry[k] = v
		
		new_info_string = ""
		for k, v in old_entry.items():
			if v != "":
				tag = k
				if k == "hosts":
					tag = "host"
				if k == "time":
					tag = "deadline"
				if k == "description":
					tag = "desc"
				
				if k == "link":
					v = f"<{v}>"
				new_info_string += f"{tag}:[{v}] "
		
		await message.channel.send(f"""**{cond['name']}** has been edited in the signup list.
		
		**Old TWOW Info**:
		{old_info_string}

		**New TWOW Info**:
		{new_info_string}""".replace("\t", ""))
	
	if args[1].lower() == "remove":
		msg = message.content

		if level == 2:
			await message.channel.send("Include the name of the TWOW you want to remove!")
			return
		
		db = Database()
		
		if "dont_announce" in msg:
			twow_name = " ".join(args[2:-1])
		else:
			twow_name = " ".join(args[2:])

		twow_list = db.get_entries("signuptwows", conditions={"name": twow_name})

		if len(twow_list) == 0:
			await message.channel.send(f"There's no TWOW named **{twow_name}** in the signup list!")
			return
		
		twow_info = twow_list[0]
		dl_format = datetime.datetime.utcfromtimestamp(twow_info[4]).strftime("%d/%m/%Y %H:%M")

		db.remove_entry("signuptwows", conditions={"name": twow_name})

		announce = "dont_announce" not in msg
		await SERVER["EVENTS"]["SIGNUPS"].update_list(announce=announce)

		await message.channel.send(f"""**{twow_info[0]}** has been removed from the signup list!
		
		**TWOW Info**:
		""".replace("\t", "") + f"""name:[{twow_info[0]}] 
		host:[{twow_info[1]}] 
		link:[{twow_info[2]}] 
		desc:[{twow_info[3]}] 
		deadline:[{dl_format}] 
		{'is_verified' if bool(twow_info[5]) else ''}""".replace("\n", "").replace("\t", ""))

		return
		
	if args[1].lower() == "add":
		msg = message.content

		if "name:[" not in msg:
			await message.channel.send("Include the name of the TWOW you want to add!")
			return
		
		db = Database()
		
		starting_bound = msg[msg.find("name:[") + 6:]
		twow_name = starting_bound[:starting_bound.find("]")]

		entry = [twow_name, "", "", "", 0, 0, ""]
		
		if "host:[" in msg:
			starting_bound = msg[msg.find("host:[") + 6:]
			hosts = starting_bound[:starting_bound.find("]")]
			entry[1] = hosts
		
		if "link:[" in msg:
			starting_bound = msg[msg.find("link:[") + 6:]
			link = starting_bound[:starting_bound.find("]")].replace("<", "").replace(">", "")
			entry[2] = link
		
		if "desc:[":
			starting_bound = msg[msg.find("desc:[") + 6:]
			desc = starting_bound[:starting_bound.find("]")]
			entry[3] = desc
		
		if "deadline:[" in msg:
			starting_bound = msg[msg.find("deadline:[") + 10:]
			deadline = starting_bound[:starting_bound.find("]")]
			entry[6] = deadline
			deadline = datetime.datetime.strptime(deadline, "%d/%m/%Y %H:%M")
			deadline = deadline.replace(tzinfo=datetime.timezone.utc).timestamp()
			entry[4] = deadline
		
		vf = 0
		if "verified:[" in msg:
			starting_bound = msg[msg.find("verified:[") + 10:]
			verified = starting_bound[:starting_bound.find("]")]
			if verified not in ["0", ""]:
				vf = 1
		entry[5] = vf

		db.add_entry("signuptwows", entry[:6])
		
		announce = "dont_announce" not in msg
		await SERVER["EVENTS"]["SIGNUPS"].update_list(announce=announce)

		await message.channel.send(f"""**{entry[0]}** has been added to the list of TWOWs in signups!
		**Host:** {entry[1]}
		**Description:** {entry[3]}
		**Deadline:** {entry[6]}
		**Deadline Timestamp:** {entry[4]}
		**Link:** <{entry[2]}>""".replace("\t", ""))

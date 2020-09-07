import discord, io, asyncio, aiohttp
from Config._functions import is_whole
from Config._db import Database

def HELP(PREFIX):
	return {
		"COOLDOWN": 2,
		"MAIN": "Command to manage the TWOW Central banner",
		"FORMAT": "wip",
		"CHANNEL": 0,
		"USAGE": f"""wip""".replace("\n", "").replace("\t", ""),
		"CATEGORY" : "Staff"
	}

PERMS = 1 # Member
ALIASES = []
REQ = []

async def MAIN(message, args, level, perms, SERVER):
	if "BANNER" not in SERVER["MAIN"].features:
		await message.channel.send("This server cannot have banners!")
		return
	
	if level == 1:
		await message.channel.send("Include a subcommand!")
		return
	
	db = Database()
	
	banner_ind, banner_list = db.get_entries("tcbanner")[0]
	banner_list = banner_list.split(" ")

	if args[1].lower() == "list":
		msg = [f"Here's a list of all the set banners.\nCurrent banner: **#{banner_ind}**\n"]

		for ind, url in enumerate(banner_list):
			to_add_line = f"**Banner #{ind}** : {url}\n"

			if len(msg[-1]) + len(to_add_line) > 1900:
				msg.append("")
			
			msg[-1] += to_add_line
		
		for z in msg:
			await message.channel.send(z)
		return

	if args[1].lower() == "cycle" and perms >= 2:
		await message.channel.send("Stepping through the banner list.")

		banner_ind += 1
		banner_ind %= len(banner_list)

		new_banner = banner_list[banner_ind]

		db.edit_entry("tcbanner", entry={"current": banner_ind, "url": " ".join(banner_list)})

		async with aiohttp.ClientSession() as session:
			try:
				async with session.get(new_banner) as resp:
					if resp.status != 200:
						await message.channel.send(f'<{new_banner}> is an invalid link!')
						return
					
					data = io.BytesIO(await resp.read())
					await SERVER["MAIN"].edit(banner=data.read())

					await message.channel.send(f"Successfully set to banner **#{banner_ind}**!")
				
			except aiohttp.client_exceptions.InvalidURL:
				await message.channel.send(f'<{new_banner}> is an invalid link!')
				return
		return
	
	if args[1].lower() == "add" and perms >= 2:
		if level == 2:
			await message.channel.send("Send an image link!")
			return
		
		banner_link = args[2]

		if banner_link in banner_list:
			await message.channel.send("This banner image is already in the list!")
			return
		
		async with aiohttp.ClientSession() as session:
			try:
				async with session.get(banner_link) as resp:
					if resp.status != 200:
						await message.channel.send(f'<{banner_link}> is an invalid link!')
						return
					
					banner_list.append(banner_link)
					db.edit_entry("tcbanner", entry={"current": banner_ind, "url": " ".join(banner_list)})
					await message.channel.send(f"Successfully added the image as banner **#{len(banner_list)-1}**!")
			except aiohttp.client_exceptions.InvalidURL:
				await message.channel.send(f'<{banner_link}> is an invalid link!')
				return
		return
	
	if args[1].lower() == "remove" and perms >= 2:
		if level == 2:
			await message.channel.send("Include either the number of the banner you want to remove or its image link!")
			return
		
		if is_whole(args[2]):
			ind = int(args[2])
			target = banner_list[ind]
		elif args[2] in banner_list:
			target = args[2]
			ind = banner_list.index(target)

		if not 0 <= ind < len(banner_list):
			await message.channel.send("There's no banner with that number!")
			return

		banner_list = [x for x in banner_list if x != target]

		await message.channel.send(f"Removed banner **#{ind}** from the list.")

		if banner_ind > ind:
			banner_ind -= 1
		
		elif banner_ind == ind:
			try:
				banner_ind %= len(banner_list)

				banner_link = banner_list[banner_ind]

				async with aiohttp.ClientSession() as session:
					try:
						async with session.get(banner_link) as resp:
							data = io.BytesIO(await resp.read())
							await SERVER["MAIN"].edit(banner=data.read())
							await message.channel.send("Moved on to the next banner, as the current one was deleted.")

					except aiohttp.client_exceptions.InvalidURL:
						pass
			
			except ZeroDivisionError:
				banner_ind = 0
		
		db.edit_entry("tcbanner", entry={"current": banner_ind, "url": " ".join(banner_list)})

		return
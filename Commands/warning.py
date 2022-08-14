import discord, requests, asyncio
from Config._functions import is_whole
from Config._const import WARNING_APP, BRAIN

def HELP(PREFIX):
	return {
		"COOLDOWN": 1,
		"MAIN": "Command to automatically manage the warning sheet",
		"FORMAT": "",
		"CHANNEL": 0,
		"USAGE": f"""W.I.P. help message!""".replace("\n", "").replace("\t", ""),
		"CATEGORY" : "Staff"
	}

PERMS = 2 # Staff
ALIASES = ["WARN", "WARNINGS", "W"]
REQ = []

async def MAIN(message, args, level, perms, SERVER):
	if level == 1:
		await message.channel.send("Include a subcommand!")
		return
	
	args = message.content.split("\n")[0].split(" ")
	level = len(args)

	if args[1].lower() == "add":
		if level == 2:
			await message.channel.send("Include a user to warn along with warning information!")
			return
		
		user = " ".join(args[2:]).strip()
		if user.startswith("<@") and user.endswith(">"): user = user[2:-1]

		memberbase = SERVER["MAIN"].members
		m_names = [m.name for m in memberbase]
		m_ids = [m.id for m in memberbase]

		matched = False

		if is_whole(user):
			if int(user) in m_ids:
				matched = memberbase[m_ids.index(int(user))]
		
		if not matched:
			m_l_names = [n.lower() for n in m_names]

			if user in m_names:
				matched = memberbase[m_names.index(user)]
			
			if not matched and user.lower() in m_l_names:
				matched = memberbase[m_l_names.index(user.lower())]

		if not matched:
			start_match = [n for n in m_names if n.startswith(user)]
			if len(start_match) == 1:
				matched = memberbase[m_names.index(start_match[0])]
			
			else:
				start_match_l = [n for n in m_l_names if n.startswith(user.lower())]
				if len(start_match_l) == 1:
					matched = memberbase[m_l_names.index(start_match_l[0])]
		
		if not matched:
			mid_match = [n for n in m_names if user in n]
			if len(mid_match) == 1:
				matched = memberbase[m_names.index(mid_match[0])]
			
			else:
				mid_match_l = [n for n in m_l_names if user.lower() in n]
				if len(mid_match_l) == 1:
					matched = memberbase[m_l_names.index(mid_match_l[0])]

		if not matched:
			await message.channel.send("Cannot recognize that user as someone in the server!")
			return
		
		added_info = message.content.split("\n")[1:]

		if len(added_info) == 0:
			await message.channel.send("Include warning information!")
			return

		data = {
			"name": f"{matched.name}#{matched.discriminator}",
			"id": str(matched.id),
			"count": None,
			"desc": None,
			"proof": None
		}

		for line in added_info:
			l_args = line.split(" ")
			l_args = [l for l in l_args if l != ""]

			if l_args[0].lower().startswith("count"):
				for i in l_args[1:]:
					if is_whole(i):
						data["count"] = int(i)
				
				if data["count"] == None:
					await message.channel.send(f"Invalid warning count `{' '.join(l_args[1:])}`!")
					return
			
			if l_args[0].lower().startswith("desc"):
				data["desc"] = ' '.join(l_args[1:])
			
			if l_args[0].lower().startswith("proof"):
				data["proof"] = ' '.join(l_args[1:])
		
		if data["count"] == None:
			await message.channel.send("Missing the warning count!")
			return
		if data["desc"] == None:
			await message.channel.send("Missing the warning description!")
			return
		if data["proof"] == None:
			await message.channel.send("Missing the warning proof!")
			return

		s = "" if data["count"] == 1 else "s"

		embed = discord.Embed(color=0x31D8B1)
		embed.title = f"{data['count']} warning{s}"
		embed.description = f"{data['name']}\n{data['id']}\n<@{data['id']}>"

		embed.add_field(name="Description", value=data['desc'], inline=False)
		embed.add_field(name="Proof", value=data['proof'])

		embed.set_thumbnail(url=matched.display_avatar.url)

		msg = await message.channel.send("**__Is this information correct?__**", embed=embed)
		await msg.add_reaction("🇾")
		await msg.add_reaction("🇳")

		def check(r, u):
			return (u == message.author
			and str(r.emoji) in ["🇾","🇳"]
			and r.message.id == msg.id)
		
		try:
			r, _ = await BRAIN.wait_for('reaction_add', timeout=30, check=check)
		
		except asyncio.TimeoutError:
			await message.channel.send("Warning command timed out.")
			return

		else:
			if str(r.emoji) == "🇳":
				await message.channel.send(f"Warning command cancelled.")
				return

		x = requests.post(WARNING_APP, data=data)

		if not x.ok:
			await message.channel.send("Something went wrong while sending the HTTP request!")
			raise ConnectionError(x.text)
		
		new_count = int(x.text)
		
		start = f"Successfully logged **{data['count']}** warning{s} for **{data['name']}**!\n"
		s = "" if new_count == 1 else "s"
		start += f"They now have a total of **{new_count}** warning{s}.\n\n"

		if new_count >= 6:
			start += "__This user has passed the warning ban threshold! **Do you wish to ban them?**__"

			msg = await message.channel.send(start)
			await msg.add_reaction("🇾")
			await msg.add_reaction("🇳")
			
			def check(r, u):
				return (u == message.author
				and str(r.emoji) in ["🇾","🇳"]
				and r.message.id == msg.id)
			
			try:
				r, _ = await BRAIN.wait_for('reaction_add', timeout=30, check=check)
			
			except asyncio.TimeoutError:
				await message.channel.send("Ban function timed out.")
				return
			
			else:
				if str(r.emoji) == "🇳":
					await message.channel.send(f"**{data['name']}** will not be banned.")
					return
				
				try:
					await SERVER["MAIN"].ban(matched, reason=f"Acquired a total of {new_count} warnings.",
					delete_message_days=0)
				except discord.Forbidden:
					await message.channel.send(f"No permission to ban **{data['name']}**.")
		
		else:
			await message.channel.send(start)
		return

from Config._functions import grammar_list, word_count
from Config._const import GAME_CHANNEL, PREFIX, ALPHABET, BRAIN
import discord, time
import numpy as np

HELP = {
	"MAIN": "Allows for playing and hosting MiniMiniTWOWs",
	"FORMAT": "[subcommand]",
	"CHANNEL": 3,
	"USAGE": f"""Available subcommands: `queue`, `create`, `start`, `spectate`, `join`, `prompt`, `respond`, `vote`. 
	Help pages for the subcommands are work in progress.""".replace("\n", "").replace("\t", "")
}

PERMS = 0
ALIASES = []
REQ = ["TWOW_CENTRAL", "EVENTS"]

async def MAIN(message, args, level, perms, TWOW_CENTRAL, EVENT):
	if not isinstance(message.channel, discord.DMChannel) and message.channel.id != GAME_CHANNEL:
		await message.channel.send(f"MiniMiniTWOW commands can only be used in <#{GAME_CHANNEL}>!")
		return
	
	if level == 1:
		await message.channel.send("Include a subcommand!")
		return
	
	mmt = EVENT["MMT"]

	if args[1].lower() == "end":
		if not mmt.RUNNING:
			await message.channel.send("There's no MiniMiniTWOW running right now!")
			return
		
		if mmt.info["GAME"]["PERIOD"] == 1:
			await message.channel.send("You can only end a MiniMiniTWOW that has already started!")
			return
		
		if message.author.id == mmt.info["GAME"]["HOST"]:
			await message.channel.send("**The current MiniMiniTWOW has been ended by the host! The queue moves on.**")
			mmt.force_skip()
			return
		
		if perms == 2:
			await message.channel.send("**The current MiniMiniTWOW has been ended by staff! The queue moves on.**")
			mmt.force_skip()
			return
		
		spect = len(mmt.info["SPECTATORS"])
		necessary = np.ceil(spect**(4/5) + 0.8)

		nec_seg = ""
		if necessary <= spect:
			nec_seg = f"/{necessary}"
		
		if message.author.id in mmt.info["GAME"]["ENDVOTES"]:
			mmt.info["GAME"]["ENDVOTES"] = [x for x in mmt.info["GAME"]["ENDVOTES"] if x != message.author.id]
			votes = len(mmt.info["GAME"]["ENDVOTES"])
			await message.channel.send(f"""🚪 {message.author.mention} removes their vote to end the MiniMiniTWOW. 
			There are now **{votes}{nec_seg}** votes.""")
			return
		
		mmt.info["GAME"]["ENDVOTES"].append(message.author.id)
		votes = len(mmt.info["GAME"]["ENDVOTES"])
		await message.channel.send(f"""🚪 **{message.author.mention} voted to end the MiniMiniTWOW!** 
		There are now **{votes}{nec_seg}** votes.""")

		if votes >= necessary:
			await message.channel.send("""**The current MiniMiniTWOW has been ended 
			by public vote! The queue moves on.**""".replace("\n", "").replace("\t", ""))
			mmt.force_skip()
		
		return
		

	if args[1].lower() == "transfer":
		if not mmt.RUNNING:
			await message.channel.send("There's no MiniMiniTWOW running right now!")
			return
		
		if mmt.info["GAME"]["PERIOD"] == 0:
			await message.channel.send("Host transfers can only occur with MiniMiniTWOWs that have been created.")
			return
		
		if mmt.info["GAME"]["HOST"] != message.author.id:
			await message.channel.send("Only the host can transfer the MiniMiniTWOW to someone else!")
			return
		
		if level == 2:
			await message.channel.send("Choose a user to transfer it to!")
			return

		mention = args[2]

		try:
			user_id = int(mention[2:-1])
		except:
			await message.channel.send("Invalid user! Ping the user you want to transfer the MiniMiniTWOW to!")
			return
		
		person = TWOW_CENTRAL.get_member(user_id)

		if person is None:
			await message.channel.send("Invalid user! Ping the user you want to transfer the MiniMiniTWOW to!")
			return
		
		await message.channel.send(f"""Are you sure you want to transfer the MiniMiniTWOW to **{person.name}**? Send 
		`confirm` to transfer.""".replace("\n", "").replace("\t", ""))
		
		msg = await BRAIN.wait_for('message', check=lambda m: (m.author == message.author and m.channel == message.channel))

		if msg.content.lower() != "confirm":
			await message.channel.send("Transfer command cancelled.")
			return
		
		msg_send = f"Successfully transfered host position to **{person.name}**!"

		mmt.info["GAME"]["HOST"] = user_id

		if mmt.info["GAME"]["PERIOD"] == 1 and mmt.info["GAME"]["PERIOD_START"] != 0:
			mmt.info["GAME"]["PERIOD_START"] = time.time()
			msg_send += f""" The timer to start the MiniMiniTWOW is reset. {mention} has {mmt.param["S_DEADLINE"]} 
			seconds to start it with `tc/mmt start`.""".replace("\n", "").replace("\t", "")
		
		if mmt.info["GAME"]["PERIOD"] == 2:
			mmt.info["GAME"]["PERIOD_START"] = time.time()
			msg_send += f""" The timer to set the prompt is reset. {mention} has {mmt.param["P_DEADLINE"]} 
			seconds to decide on the prompt with `tc/mmt prompt`.""".replace("\n", "").replace("\t", "")

		await message.channel.send(msg_send)
		return

	if args[1].lower() == "queue":
		if level == 2:
			if not mmt.RUNNING:
				mmt.start(TWOW_CENTRAL)
			
			if message.author.id in mmt.info["HOST_QUEUE"]:
				mmt.info["HOST_QUEUE"] = [x for x in mmt.info["HOST_QUEUE"] if x != message.author.id]
				await mmt.MMT_C.send(f"🎩 <@{message.author.id}> has been removed from queue.")
				return
			
			mmt.info["HOST_QUEUE"].append(message.author.id)
			await message.channel.send(
			f"🎩 <@{message.author.id}> has been added to queue at position **{len(mmt.info['HOST_QUEUE'])}**.")
			return
		
		if args[2].lower() == "list":
			if not mmt.RUNNING:
				await message.channel.send("The queue is empty!")
				return
		
			if len(mmt.info["HOST_QUEUE"]) == 0:
				await message.channel.send("The queue is empty!")
				return
			
			init = ["**This is the current MiniMiniTWOW hosting queue:**\n\n"]

			for person in mmt.info["HOST_QUEUE"]:
				member = TWOW_CENTRAL.get_member(person)

				if member is None:
					member = f"`{person}`"
				else:
					member = member.name
				
				line = f"🎩 [{mmt.info['HOST_QUEUE'].index(person) + 1}] - **{member}**"
				if len(init[-1] + line) > 1950:
					line.append("")
				init[-1] += line
			
			for z in init:
				await message.channel.send(z)
			return
	
	if args[1].lower() == "create":
		if not mmt.RUNNING:
			await message.channel.send(
			f"There's no host to create a MiniMiniTWOW! Join the queue with `{PREFIX}mmt queue` to host!")
			return
		
		if mmt.info["GAME"]["PERIOD"] != 0:
			await message.channel.send("There's already a MiniMiniTWOW running!")
			return
		
		if message.author.id != mmt.info["GAME"]["HOST"]:
			await message.channel.send("You can only create a MiniMiniTWOW if you're up on the queue!")
			return
		
		mmt.info["GAME"]["PERIOD"] = 1
		mmt.info["GAME"]["PERIOD_START"] = 0

		await message.channel.send(
		f"🎩 <@{message.author.id}> has created a MiniMiniTWOW! Use `{PREFIX}mmt join` to join it!")
		return
	
	if args[1].lower() == "spectate":
		if not mmt.RUNNING:
			await message.channel.send("There's no MiniMiniTWOW running right now!")
			return
		
		if mmt.info["GAME"]["PERIOD"] == 0:
			await message.channel.send("You can only spectate a MiniMiniTWOW that has been created!")
			return
		
		if message.author.id in mmt.info["SPECTATORS"]:
			mmt.info["SPECTATORS"] = [x for x in mmt.info["SPECTATORS"] if x != message.author.id]
			await mmt.MMT_C.send(f"👁️ <@{message.author.id}> is no longer spectating.")
			return
		
		mmt.info["SPECTATORS"].append(message.author.id)
		await mmt.MMT_C.send(f"""👁️ <@{message.author.id}> is now spectating, and will receive voting screens 
		for future rounds.""".replace("\n", "").replace("\t", ""))
		return
	
	if args[1].lower() == "join":
		if not mmt.RUNNING:
			await message.channel.send("There's no MiniMiniTWOW running right now!")
			return
		
		if mmt.info["GAME"]["PERIOD"] != 1:
			await message.channel.send("You can only join the MiniMiniTWOW if it's in signups!")
			return
		
		if message.author.id in mmt.info["PLAYERS"]:
			mmt.info["PLAYERS"] = [x for x in mmt.info["PLAYERS"] if x != message.author.id]
			mmt.info["SPECTATORS"] = [x for x in mmt.info["SPECTATORS"] if x != message.author.id]
			await mmt.MMT_C.send(
			f"🏁 <@{message.author.id}> left the MiniMiniTWOW. Our player count is {len(mmt.info['PLAYERS'])}.")

			if len(mmt.info['PLAYERS']) == 1:
				await mmt.MMT_C.send("🏁 We no longer have two players. The three minute start timer is now reset.")
			return
		
		mmt.info["PLAYERS"].append(message.author.id)
		if message.author.id not in mmt.info["SPECTATORS"]:
			mmt.info["SPECTATORS"].append(message.author.id)

		await mmt.MMT_C.send(
		f"🏁 **<@{message.author.id}> joined the MiniMiniTWOW!** Our player count is now {len(mmt.info['PLAYERS'])}!")
		if len(mmt.info['PLAYERS']) == 2:
			await mmt.MMT_C.send(f"""🏁 We have two players! <@{mmt.info["GAME"]["HOST"]}> has three minutes 
			to start the MiniMiniTWOW with `{PREFIX}mmt start`.""".replace("\n", "").replace("\t", ""))
			mmt.info["GAME"]["PERIOD_START"] = time.time()
		return
	
	if args[1].lower() == "start":
		if not mmt.RUNNING:
			await message.channel.send("There's no MiniMiniTWOW running right now!")
			return
		
		if mmt.info["GAME"]["PERIOD"] != 1:
			await message.channel.send("You can only start a MiniMiniTWOW if it's in signups!")
			return
		
		if message.author.id != mmt.info["GAME"]["HOST"]:
			await message.channel.send("Only the host can start a MiniMiniTWOW!")
			return
		
		if len(mmt.info["PLAYERS"]) < 2:
			await message.channel.send("You need at least two contestants to start a MiniMiniTWOW!")
			return
		
		mmt.info["GAME"]["PERIOD"] = 2
		mmt.info["GAME"]["PERIOD_START"] = time.time()

		await mmt.MMT_C.send(f"""🏁 <@{message.author.id}> has started the MiniMiniTWOW with 
		{len(mmt.info["PLAYERS"])} contestants. Nobody can sign up anymore.""".replace("\n", "").replace("\t", ""))
		
		return
	
	if args[1].lower() == "prompt":
		if not mmt.RUNNING:
			await message.channel.send("There's no MiniMiniTWOW running right now!")
			return
		
		if mmt.info["GAME"]["PERIOD"] != 2:
			await message.channel.send("You can only set a prompt inbetween rounds!")
			return
		
		if message.author.id != mmt.info["GAME"]["HOST"]:
			await message.channel.send("Only the host can set a prompt!")
			return
		
		if level == 2:
			await message.channel.send("You need to include a prompt!")
			return
		
		prompt = " ".join(args[2:]).replace("`", "").replace("\t", "").replace("\n", "")

		if len(prompt) > 200:
			await message.channel.send("That prompt is too long! It must be 200 characters at most.")
			return
		
		mmt.info["GAME"]["PERIOD"] = 3
		mmt.info["GAME"]["PERIOD_START"] = time.time()
		mmt.info["GAME"]["PROMPT"] = prompt
		mmt.info["RESPONSES"] = [""] * len(mmt.info["PLAYERS"])

		await mmt.MMT_C.send(f"""📝 **Round {mmt.info["GAME"]["ROUND"]} Responding** has started! The prompt is:
		```{prompt}```
		Our contestants have {mmt.param["R_DEADLINE"]} seconds to respond to it.""".replace("\n", "").replace("\t", ""))

		for player in mmt.info["PLAYERS"]:
			await TWOW_CENTRAL.get_member(player).send(f"""
			📝 **Round {mmt.info["GAME"]["ROUND"]} Responding** has started! The prompt is:
			```{prompt}```
			You must respond in {mmt.param["R_DEADLINE"]} seconds using `{PREFIX}mmt respond`!
			""".replace("\n", "").replace("\t", ""))
		return
	
	if args[1].lower() == "respond":
		if not isinstance(message.channel, discord.DMChannel):
			await mmt.MMT_C.send("This command can only be used in DMs!")
			return
		
		if not mmt.RUNNING:
			await message.channel.send("There's no MiniMiniTWOW running right now!")
			return
		
		if mmt.info["GAME"]["PERIOD"] != 3:
			await message.channel.send("You can only respond during a submission period!")
			return
		
		if message.author.id not in mmt.info["PLAYERS"]:
			await message.channel.send("Only alive contestants can respond!")
			return
		
		if level == 2:
			await message.channel.send("You need to include a response!")
			return

		response = " ".join(args[2:]).replace("`", "").replace("\t", "").replace("\n", "")

		if len(response) > 120:
			await message.channel.send("Your response is too long! It must be 120 characters at most.")
			return
		
		ind = mmt.info["PLAYERS"].index(message.author.id)
		new = not mmt.info["RESPONSES"][ind] == ""
		mmt.info["RESPONSES"][ind] = response

		await message.channel.send(f"""Your {'new ' if new else ''}response to the prompt has been recorded as:
		```{response}```> **Word count:** {word_count(response)}""".replace("\n", "").replace("\t", ""))
		return
	
	if args[1].lower() == "vote":
		if not isinstance(message.channel, discord.DMChannel):
			await mmt.MMT_C.send("This command can only be used in DMs!")
			return
		
		if not mmt.RUNNING:
			await message.channel.send("There's no MiniMiniTWOW running right now!")
			return
		
		if message.author.id not in mmt.info["VOTES"]["ID"]:
			await message.channel.send("You can only vote if you received a voting screen!")
			return
		
		if mmt.info["GAME"]["PERIOD"] != 4:
			await message.channel.send("You can only vote during a voting period!")
			return

		if level == 2:
			await message.channel.send("You need to include a vote!")
			return
		
		vote = args[2].upper()

		if sorted(list(vote)) != sorted(list(ALPHABET[:len(vote)])):
			await message.channel.send("""Your vote is invalid. Make sure you're not missing or repeating any letters, 
			or including any invalid characters.""".replace("\n", "").replace("\n", ""))
			return
		
		ind = mmt.info["VOTES"]["ID"].index(message.author.id)

		parsed_vote = []
		for z in range(len(vote)):
			score = (len(vote) - 1 - vote.find(ALPHABET[z])) / (len(vote) - 1)
			parsed_vote.append(str(score))

		new = not mmt.info["VOTES"]["VOTE"][ind] == ""
		mmt.info["VOTES"]["VOTE"][ind] = " ".join(parsed_vote)

		await message.channel.send(f"""Your {'new ' if new else ''}vote has been recorded as: 
		```{vote}```""".replace("\n", "").replace("\t", ""))
		return
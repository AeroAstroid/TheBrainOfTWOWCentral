import discord, time, asyncio, os, sys
from datetime import datetime, timedelta

from Config._const import *
from Config._functions import *

from Commands._commands import *
from Events._events import *

PARAMS = {} # This holds parameters that can be called to be used in commands

async def event_task():
	global EVENTS
	await BRAIN.wait_until_ready()
	TWOW_CENTRAL = discord.utils.get(BRAIN.guilds, id=TWOW_CENTRAL_ID)
	while not BRAIN.is_closed():
		loop_start = time.time()
		for event in EVENTS.keys():
			if not EVENTS[event].RUNNING:
				continue
			status = await EVENTS[event].on_two_second(TWOW_CENTRAL)
			if not status:
				EVENTS[event].end()
				continue
		await asyncio.sleep(loop_start + 2 - time.time())


@BRAIN.event
async def on_ready():
	# Define parameters that could be used in commands
	PARAMS["LOGIN"] = time.time()
	PARAMS["LOGIN_TIME"] = datetime.utcnow()
	PARAMS["BRAIN"] = BRAIN

	PARAMS["COMMANDS"] = COMMANDS
	PARAMS["EVENTS"] = EVENTS

	PARAMS["TWOW_CENTRAL"] = discord.utils.get(BRAIN.guilds, id=TWOW_CENTRAL_ID)
	PARAMS["STAFF"] = discord.utils.get(PARAMS["TWOW_CENTRAL"].roles, id=STAFF_ID)
	PARAMS["MEMBER"] = discord.utils.get(PARAMS["TWOW_CENTRAL"].roles, id=MEMBER_ID)
	PARAMS["PUBLIC_CHANNELS"] = PUBLIC_CHANNELS

	# By default, restart command restarts the script with extra sys arguments
	# This tells the bot to report the time it took to restart in the same channel the restart command was used
	if len(sys.argv) > 1:
		try:
			id_to_send = int(sys.argv[1])
			restart_time = float(sys.argv[2])
			channel_to_send = discord.utils.get(PARAMS["TWOW_CENTRAL"].channels, id=id_to_send)
			await channel_to_send.send(
			f"Successfully restarted in {round(time.time() - restart_time, 2)} second(s)!")

		except Exception:
			pass
	
	# Start all events that have been marked for starting by default right as the bot starts
	with open('Config/default.txt', 'r') as file:
		events = file.read().splitlines()
		try:
			for z in events:
				EVENTS[z.upper()].start(PARAMS["TWOW_CENTRAL"])
				print(f"Automatically started {z.upper()}")
		except Exception:
			pass

	# Notify that the bot is ready
	print(f"\nLogged in at {PARAMS['LOGIN_TIME']} ({PARAMS['LOGIN']})\n")

	@BRAIN.event
	async def on_message(message):
		# Ignore bot messages
		if message.author == BRAIN.user: return

		for event in EVENTS.keys():
			if not EVENTS[event].RUNNING:
				break
			
			await EVENTS[event].on_message(message)

		# Not bother with non-commands from here on
		if not message.content.startswith(PREFIX): return

		# Define the user's permissions: 2 = Staff; 1 = Member; 0 = Non-member
		perms = 2 if message.author in PARAMS["STAFF"].members else (
		        1 if message.author in PARAMS["MEMBER"].members else 0)

		if perms == 0: # Non-member commands are ignored
			return
		
		if perms == 1 and (not isinstance(message.channel, discord.DMChannel)
		and message.channel.id not in BOT_CHANNELS):
			return # Ignore commands from regular members that are not in bot channels

		print(f"""[COMMAND] {message.author.name} - {message.author.id} - 
		{'DMs' if isinstance(message.channel, discord.DMChannel) else message.guild.name} - 
		{'DMs' if isinstance(message.channel, discord.DMChannel) else message.channel.name}
		""".replace("\t", "").replace("\n", ""))

		print(f"\t{message.content}\n")

		args = message.content[len(PREFIX):].split(" ")
		command = args[0].upper()
		level = len(args)

		# If the command is not found, it checks if it's just an alias of any actual command
		if command not in COMMANDS.keys():
			alias = None
			for possible_alias in COMMANDS.keys(): # Check each command's aliases for a match
				if command in COMMANDS[possible_alias]['ALIASES']:
					alias = possible_alias
					break

			if alias is None: # If it's not an alias, it's an invalid command
				await message.channel.send("❌ Invalid command!")
				return
			else: # If it is an alias, specify the original command name
				command = alias

		if perms < COMMANDS[command]["PERMS"]: # Check if the permissions line up
			await message.channel.send("❌ You don't have permission to run this command!")
			return

		# List all the required parameters for the command's function. These are specified in each command's script
		requisites = [PARAMS[name] for name in COMMANDS[command]["REQ"]]

		# Run the command's main function, also specified in the command's script
		state = await COMMANDS[command]["MAIN"](message, args, level, perms, *requisites)

		if state is None: # Most commands return this
			return

		if state[0] == 0: # The restart command returns a [0] flag, signaling that the bot should be restarted
			os.execl(sys.executable, 'python', __file__, str(message.channel.id), str(time.time()))

		if state[0] == 1: # The event command returns a [1] flag, signaling to toggle the event
			if EVENTS[state[1]].RUNNING:
				EVENTS[state[1]].end()
			else:
				EVENTS[state[1]].start(PARAMS["TWOW_CENTRAL"])

BRAIN.loop.create_task(event_task())
BRAIN.run(TOKEN)

import discord, time, asyncio, os, sys, traceback, importlib
from datetime import datetime, timedelta

from Config._functions import *

from Commands._commands import *
from Events._events import *

if "debug" in sys.argv: # Run bot with all the debug constants
	from Config._debug_const import *
else: # Run bot normally
	from Config._const import *


PARAMS = {} # This holds parameters that can be called to be used in commands

async def event_task(): # This is an event handler for the time-based functions of various events
	global PARAMS
	await BRAIN.wait_until_ready()
	TWOW_CENTRAL = discord.utils.get(BRAIN.guilds, id=TWOW_CENTRAL_ID)
	await asyncio.sleep(2)

	while not BRAIN.is_closed():
		loop_start = time.time()

		day_function = False # Detect if the day just changed
		if datetime.utcnow().day != PARAMS["DAY"]:
			day_function = True
			PARAMS["DAY"] = datetime.utcnow().day

		for event in PARAMS["EVENTS"].keys():
			if not PARAMS["EVENTS"][event].RUNNING:
				continue # We only care about events that are currently running

			try:
				status = await PARAMS["EVENTS"][event].on_two_second(TWOW_CENTRAL)
				if status is False: # "return False"
					PARAMS["EVENTS"][event].end()
					continue
			except AttributeError:
				pass
			
			# If the day just changed, run the day function
			if day_function:
				try:
					await PARAMS["EVENTS"][event].on_one_day(TWOW_CENTRAL, PARAMS["DAY"])
				except AttributeError:
					pass

		# This results in more accurate intervals than using asyncio.sleep(2)
		await asyncio.sleep(loop_start + 2 - time.time())


@BRAIN.event
async def on_ready():
	# Define parameters that could be used in commands in the PARAMS dict
	PARAMS["LOGIN"] = time.time()
	PARAMS["LOGIN_TIME"] = datetime.utcnow()
	PARAMS["BRAIN"] = BRAIN
	
	PARAMS["DAY"] = CURRENT_DAY

	PARAMS["COMMANDS"] = COMMANDS
	PARAMS["EVENTS"] = EVENTS

	PARAMS["TWOW_CENTRAL"] = discord.utils.get(BRAIN.guilds, id=TWOW_CENTRAL_ID)
	PARAMS["STAFF"] = discord.utils.get(PARAMS["TWOW_CENTRAL"].roles, id=STAFF_ID)
	PARAMS["MEMBER"] = discord.utils.get(PARAMS["TWOW_CENTRAL"].roles, id=MEMBER_ID)
	PARAMS["PUBLIC_CHANNELS"] = PUBLIC_CHANNELS

	PARAMS["LOGS"] = discord.utils.get(PARAMS["TWOW_CENTRAL"].channels, id=LOG_CHANNEL)

	# By default, restart command restarts the script with extra sys arguments
	# This tells the bot to report the time it took to restart in the same channel the restart command was used
	if len(sys.argv) > 2:
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
				PARAMS["EVENTS"][z.upper()].start(PARAMS["TWOW_CENTRAL"])
				print(f"Automatically started {z.upper()}")

		except Exception:
			pass

	# Notify that the bot is ready
	print(f"\nLogged in at {PARAMS['LOGIN_TIME']} ({PARAMS['LOGIN']})\n")
	await PARAMS["LOGS"].send(f"> Logged in at {PARAMS['LOGIN_TIME']} ({PARAMS['LOGIN']})")

	@BRAIN.event
	async def on_message(message):
		# Ignore bot messages
		if message.author == BRAIN.user: return

		# Define the user's permissions: 2 = Staff; 1 = Member; 0 = Non-member
		perms = 2 if (message.author in PARAMS["STAFF"].members or message.author.id == 296389808815734794) else (
		        1 if message.author in PARAMS["MEMBER"].members else 0)
		
		try:
		
			# Run event on_message on every message
			for event in PARAMS["EVENTS"].keys():
				if not PARAMS["EVENTS"][event].RUNNING:
					break
				
				try:
					await PARAMS["EVENTS"][event].on_message(message, perms)
				except:
					pass
			
			# Not bother with non-commands from here on
			if not message.content.startswith(PREFIX): return
			
			if perms < 2 and (not isinstance(message.channel, discord.DMChannel)
			and message.channel.id not in BOT_CHANNELS):
				return # Ignore commands from non-staff that are not in bot channels

			print(f"""[COMMAND] {message.author.name} - {message.author.id} - 
			{'DMs' if isinstance(message.channel, discord.DMChannel) else message.guild.name} - 
			{'DMs' if isinstance(message.channel, discord.DMChannel) else message.channel.name}
			""".replace("\t", "").replace("\n", ""))

			print(f"\t{message.content}\n")

			args = message.content[len(PREFIX):].split(" ") # The arguments passed in the command
			command = args[0].upper() # The top-level command used
			level = len(args) # The number of arguments used in the command

			# If the command is not found, it checks if it's just an alias of any actual command
			if command not in PARAMS["COMMANDS"].keys():
				alias = None
				for possible_alias in PARAMS["COMMANDS"].keys(): # Check each command's aliases for a match
					if command in PARAMS["COMMANDS"][possible_alias]['ALIASES']:
						alias = possible_alias
						break

				if alias is None: # If it's not an alias, it's an invalid command
					await message.channel.send("❌ Invalid command!")
					return
				else: # If it is an alias, specify the original command name
					command = alias

			if perms < PARAMS["COMMANDS"][command]["PERMS"]: # Check if the permissions line up
				await message.channel.send("❌ You don't have permission to run this command!")
				return

			# List all the required parameters for the command's function. These are specified in each command's script
			requisites = [PARAMS[name] for name in PARAMS["COMMANDS"][command]["REQ"]]

			# Run the command's main function, also specified in the command's script
			state = await PARAMS["COMMANDS"][command]["MAIN"](message, args, level, perms, *requisites)

			if state is None: # Most commands return this
				return

			if state[0] == 0: # The restart command returns a [0] flag, signaling that the bot should be restarted
				os.execl(sys.executable, 'python', __file__, str(message.channel.id), str(time.time()))

			if state[0] == 1: # The event command returns a [1] flag, signaling to toggle the event
				if PARAMS["EVENTS"][state[1]].RUNNING:
					PARAMS["EVENTS"][state[1]].end()
				else:
					PARAMS["EVENTS"][state[1]].start(PARAMS["TWOW_CENTRAL"])
			
			if state[0] == 2: # The mmt command returns a [2] flag, triggering all updates to the event class
				PARAMS["EVENTS"][state[1]] = state[2]
			
			if state[0] == 3: # The reimport command returns a [3] flag, signaling to reimport commands
				global_vars = {}
				exec(open("Commands/_commands.py").read(), global_vars)
				PARAMS["COMMANDS"] = global_vars["COMMANDS"]

				for cfile in global_vars["file_list"]:
					cvars = {}
					exec(open(f"Commands/{cfile}.py", encoding='utf-8').read(), cvars)
					PARAMS["COMMANDS"][cfile.upper()]["MAIN"] = cvars["MAIN"]
				
				await message.channel.send(f"Reimported command files in {round(time.time() - state[1], 2)} seconds.")
			
			return

		except Exception: # Detect errors when commands are used
			traceback.print_exc() # Print the error

			try:
				await PARAMS["LOGS"].send(f"**Error occured!**```python\n{traceback.format_exc()}```")
			except:
				pass

BRAIN.loop.create_task(event_task()) # This is an event handler for the time-based functions of various events
BRAIN.run(TOKEN)

import discord, time, asyncio, os, sys, traceback, importlib, copy
from datetime import datetime, timedelta

from Config._functions import *

from Config._const import *

if "debug" in sys.argv: # Run bot with debug constants
	from Config._const_debug import *
else: # Run bot with production constants
	from Config._const_tc import *

SERVERS = {}
PARAMS = {} # This holds parameters that can be called to be used in commands

async def event_task(): # This is an event handler for the time-based functions of various events
	global PARAMS
	global SERVERS
	await BRAIN.wait_until_ready()
	await asyncio.sleep(2)

	while not BRAIN.is_closed():
		loop_start = time.time()

		hour_function = False # Detect if the hour just changed

		try:
			if datetime.utcnow().hour != PARAMS["HOUR"]:
				hour_function = True
				PARAMS["HOUR"] = datetime.utcnow().hour
			
			for server in SERVERS:
				for event in SERVERS[server]["EVENTS"].keys():
					if not SERVERS[server]["EVENTS"][event].RUNNING:
						continue # We only care about events that are currently running

					two_sec_func = None
					try:
						two_sec_func = SERVERS[server]["EVENTS"][event].on_two_second
					except AttributeError as e:
						pass

					if two_sec_func is not None:
						status = await two_sec_func()
						
						if status is False: # "return False"
							SERVERS[server]["EVENTS"][event].end()
							continue
					
					# If the hour just changed, run the hour function
					if hour_function:
						try:
							SERVERS[server]["EVENTS"][event].on_one_hour
						except AttributeError:
							continue
						
						try:
							print(f"Running {server} {event} one-hour function")
							await SERVERS[server]["EVENTS"][event].on_one_hour()
							print(f"Ran successfully.\n")
						except Exception as e:
							print(f"Error in {server} {event} one-hour function: {e}")
							traceback.print_exc()
							print("-----------------------------------------------------------\n")
			
			if len(SERVERS.keys()) != 0 and not PARAMS["EVENT_TASK"]:
				PARAMS["EVENT_TASK"] = True
				print("Event handler successfully loaded!")

		except NameError:
			traceback.print_exc()
			pass

		# This results in more accurate intervals than using asyncio.sleep(2)
		await asyncio.sleep(loop_start + 2 - time.time())


@BRAIN.event
async def on_ready():
	global SERVERS

	open("Config/_tr_gen.txt", "w").close()

	BRAIN.loop.create_task(event_task())

	from Config._servers import SERVERS, MAIN_SERVER

	from Commands._commands import COMMANDS
	from Events._events import EVENTS

	COOLDOWN = {}

	PARAMS["EVENT_TASK"] = False

	PARAMS["LOGIN"] = time.time()
	PARAMS["LOGIN_TIME"] = datetime.utcnow()
	PARAMS["BRAIN"] = BRAIN
	
	PARAMS["HOUR"] = CURRENT_HOUR

	PARAMS["MAIN_SERVER"] = MAIN_SERVER

	PARAMS["COMMANDS"] = COMMANDS

	PARAMS["UNO"] = UNO_INFO

	'''PARAMS["TWOW_CENTRAL"] = discord.utils.get(BRAIN.guilds, id=TWOW_CENTRAL_ID)
	PARAMS["STAFF"] = discord.utils.get(PARAMS["TWOW_CENTRAL"].roles, id=STAFF_ID)
	PARAMS["MEMBER"] = discord.utils.get(PARAMS["TWOW_CENTRAL"].roles, id=MEMBER_ID)
	PARAMS["BOT_ROLE"] = discord.utils.get(PARAMS["TWOW_CENTRAL"].roles, id=BOT_ROLE)
	PARAMS["PUBLIC_CHANNELS"] = PUBLIC_CHANNELS
	PARAMS["GAME_CHANNEL"] = GAME_CHANNEL
	PARAMS["BIRTHDAY_ROLE"] = BIRTHDAY_ROLE
	PARAMS["MEMES"] = MEMES'''

	server_name_list = []

	for server in SERVERS:
		server_name_list.append(SERVERS[server]["MAIN"].name)
		SERVERS[server]["EVENTS"] = copy.deepcopy(EVENTS)
	
	print(f"Servers tallied! Operational servers:\n\t{', '.join(server_name_list)}\n")

	# By default, restart command restarts the script with extra sys arguments
	# This tells the bot to report the time it took to restart in the same channel the restart command was used
	if len(sys.argv) > 3:
		try:
			server_id = sys.argv[1]
			id_to_send = int(sys.argv[2])
			restart_time = float(sys.argv[3])
			
			channel_to_send = discord.utils.get(SERVERS[server_id]["MAIN"].channels, id=id_to_send)
			await channel_to_send.send(
			f"Successfully restarted in {round(time.time() - restart_time, 2)} second(s)!")

		except Exception:
			pass
	
	# Start all events that have been marked for starting by default right as the bot starts
	with open('Config/default.txt', 'r') as file:
		events = file.read().splitlines()
		for z in events:
			try:
				event_name, event_server = z.split(" ")
				SERVERS[event_server]["EVENTS"][event_name.upper()].start(SERVERS[event_server])
				print(f"Automatically started {event_name.upper()} in {SERVERS[event_server]['MAIN'].name}")

			except Exception as e:
				print(f"Error starting {event_name} in {event_server}:", e)
				pass

	# Notify that the bot is ready
	print(f"\nLogged in at {PARAMS['LOGIN_TIME']} ({PARAMS['LOGIN']})\n")

	await MAIN_SERVER["LOGS"].send(f"> Logged in at {PARAMS['LOGIN_TIME']} ({PARAMS['LOGIN']})")
	
	@BRAIN.event
	async def on_member_join(member):
		if "twitter.com/h0nde" in member.name.lower():
			try:
				await member.ban(reason="Raid protection measure")
			except discord.Forbidden:
				pass
	
	@BRAIN.event
	async def on_message(message):
		
		# Ignore bot messages
		if message.author == BRAIN.user: return
		
		try:
			if message.guild is not None:
				msg_guild = SERVERS[str(message.guild.id)]
				
				# Run event on_message on every message
				for event in msg_guild["EVENTS"].keys():
					if not msg_guild["EVENTS"][event].RUNNING:
						continue

					try:
						on_msg_func = msg_guild["EVENTS"][event].on_message
					except AttributeError:
						continue

					await on_msg_func(message)

			elif message.guild is None:

				# Made for events in TWOW Central that are ran in DMs 
				tc_guild = None
				for server in list(SERVERS.keys()):
					if SERVERS[server]["MAIN"].id == PARAMS["MAIN_SERVER"]["ID"]: tc_guild = SERVERS[server]

				if tc_guild is not None:
					dm_events = ["DESCRIPTION_DETECTIVE", "RESPONDING", "SPEEDCOUNTER", "INVISIBLE_RULES"]

					for event in tc_guild["EVENTS"].keys():
						if event in dm_events and tc_guild["EVENTS"][event].RUNNING:
							try:
								on_msg_func = tc_guild["EVENTS"][event].on_message
							except AttributeError:
								continue

							await on_msg_func(message)
			
			# Not bother with non-commands from here on
			msg_guild = None
			for server in SERVERS:
				if not message.content.startswith(SERVERS[server]["PREFIX"]):
					continue
				
				if message.guild is None:
					msg_guild = SERVERS[server]
					break

				elif message.guild.id == int(server):
					msg_guild = SERVERS[server]
					break
			
			if msg_guild is None: return

			msg_PREFIX = msg_guild["PREFIX"]

			# Define the user's permissions: 3 = Developer; 2 = Staff; 1 = Member; 0 = Non-member
			if message.author.id in [184768535107469314, 183331874670641152, 179686717534502913]: perms = 3
			elif message.author in msg_guild["STAFF_ROLE"].members: perms = 2
			elif message.author in msg_guild["MEMBER_ROLE"].members: perms = 1
			else: perms = 0

			if perms == 3 and message.content == f"{msg_PREFIX}hourup":
				PARAMS["HOUR"] += 1
				return

			if perms < 2 and (message.guild is not None and message.channel not in msg_guild["BOT_CHANNELS"]):
				return # Ignore commands from non-staff that are not in bot channels'
			
			if message.author.id == 382925349144494080:
				await message.channel.send("Nice one, Bazboomer.")
				return
			
			if message.author.id == 155149108183695360:
				await message.channel.send("Act your age, Dynosaur.")
				return

			print(f"""[COMMAND] {message.author.name} - {message.author.id} - 
			{'DMs' if message.guild is None else msg_guild["MAIN"].name} - 
			{'DMs' if message.guild is None else message.channel.name}
			""".replace("\t", "").replace("\n", ""))

			print(f"\t{message.content}\n")

			args = message.content[len(msg_PREFIX):].split(" ") # The arguments passed in the command
			command = args[0].upper() # The top-level command used
			level = len(args) # The number of arguments used in the command

			# Check if command is either "respond" or "edit" and if so stop
			# This is for the RESPONDING event
			if command == "RESPOND" or command == "EDIT": return

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

			try:
				if COOLDOWN[message.author.id][command] > time.time():
					await message.add_reaction("💬")
					return
				else:
					del COOLDOWN[message.author.id][command]
					if len(list(COOLDOWN[message.author.id].keys())) == 0:
						del COOLDOWN[message.author.id]
			except KeyError:
				pass
			
			cooldown_time = PARAMS["COMMANDS"][command]["HELP"](msg_guild['PREFIX'])["COOLDOWN"]
			try:
				COOLDOWN[message.author.id][command] = time.time() + cooldown_time
			except KeyError:
				COOLDOWN[message.author.id] = {}
				COOLDOWN[message.author.id][command] = time.time() + cooldown_time
			
			# List all the required parameters for the command's function. These are specified in each command's script
			requisites = [PARAMS[name] for name in PARAMS["COMMANDS"][command]["REQ"]]

			# Run the command's main function, also specified in the command's script
			state = await PARAMS["COMMANDS"][command]["MAIN"](message, args, level, perms, msg_guild, *requisites)

			if state is not None:
				if state[0] == 0: # The restart command returns a [0] flag, signaling that the bot should be restarted
					extra_args = []
					if "debug" in sys.argv:
						extra_args = ["debug"] # If the bot is being run with debug, restart it with debug too

					if message.guild is not None:
						r_guild = str(message.guild.id)
					else:
						r_guild = str(message.author.id)
					
					os.execl(
						sys.executable, 'python', __file__, r_guild, str(message.channel.id), str(time.time()), *extra_args)

				if state[0] == 1: # The event command returns a [1] flag, signaling to toggle the event
					if msg_guild["EVENTS"][state[1]].RUNNING:
						msg_guild["EVENTS"][state[1]].end()
					else:
						msg_guild["EVENTS"][state[1]].start(msg_guild)
				
				if state[0] == 2: # The mmt command returns a [2] flag, triggering all updates to the event class
					msg_guild["EVENTS"][state[1]] = state[2]
				
				if state[0] == 3: # The reimport command returns a [3] flag, signaling to reimport commands
					global_vars = {}
					exec(open("Commands/_commands.py").read(), global_vars)
					PARAMS["COMMANDS"] = global_vars["COMMANDS"]

					for cfile in global_vars["file_list"]:
						cvars = {}
						exec(open(f"Commands/{cfile}.py", encoding='utf-8').read(), cvars)
						PARAMS["COMMANDS"][cfile.upper()]["MAIN"] = cvars["MAIN"]
					
					await message.channel.send(
						f"Reimported command files in {round(time.time() - state[1], 2)} seconds.")
				
				if state[0] == 4: # The uno command returns a [4] flag, editing a PARAMS entry
					PARAMS[state[1]] = state[2]
			
			try:
				if COOLDOWN[message.author.id][command] - time.time() > 0:
					await asyncio.sleep(COOLDOWN[message.author.id][command] - time.time())
					del COOLDOWN[message.author.id][command]
			except KeyError:
				pass
			
			return

		except Exception: # Detect errors when commands are used
			traceback.print_exc() # Print the error

			try:
				await MAIN_SERVER["LOGS"].send(
					f"**Error occured in {msg_guild['MAIN'].name}!**```python\n{traceback.format_exc()}```")
			except:
				pass
	
	
BRAIN.run(TOKEN)

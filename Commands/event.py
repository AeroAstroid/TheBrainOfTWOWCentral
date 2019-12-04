from Config._functions import grammar_list
from Config._const import PREFIX, BRAIN

HELP = {
	"MAIN": "Used to manage events or other bot actions",
	"FORMAT": "['list' / event] (subcommand) ('confirm')",
	"CHANNEL": 2, # Usable by staff in any channel
	
	"USAGE": f"""Using `{PREFIX}event ['list']` lists all available events, and whether they're on or off. 
	Specifying one of those events as `[event]` lets you toggle on/off that specific event, with a confirmation 
	message. Including `('confirm')` bypasses the confirmation message. You can use the subcommand 
	`{PREFIX}event [event] edit` to change parameters of an event that's currently running.
	""".replace("\n", "").replace("\t", "")
}

PERMS = 2 # Staff
ALIASES = []
REQ = ["EVENTS"]

async def MAIN(message, args, level, perms, EVENTS):
	if level == 1:
		await message.channel.send("Include events to call!")
		return
	
	if args[1].lower() == "list": # List the events from the dict
		event_list = [f'`{x}` - **{"ON" if EVENTS[x].RUNNING else "OFF"}**\n' for x in EVENTS.keys()]
		await message.channel.send(f"Here is a list of bot events:\n\n{''.join(event_list)}")
		return
	
	if args[1].upper() not in EVENTS.keys(): # Event doesn't exist
		await message.channel.send("Invalid event.")
		return

	event = args[1].upper()

	if level != 2: # If it's not just `tc/event [event_name]`, check for subcommands
		if args[2].lower() == "edit":
			if not EVENTS[event].RUNNING:
				await message.channel.send("You can only change an event that's currently running.")
				return
			
			parsing_index = 0 # Helps detect keywords and the brackets' boundaries
			config_dict = {} # Stores the values to be changed
			no_value = [] # Stores keywords that the user didn't provide values for, so they can be specified later

			while True: # Advances through the entire message until break is activated

				found = message.content[parsing_index + 1:].find("[")
				if found == -1: # If you can't find [ anymore, parsing is over
					break

				parsing_index += found + 2 # Brings parsing_index to the index of the character after [

				reach_index = parsing_index + message.content[parsing_index + 1:].find("]") + 1
				# Brings reach_index to the next ]

				# Contents of the brackets
				config_args = message.content[parsing_index:reach_index].split(" ")

				if len(config_args) == 0:
					continue # If it's just [], then there's nothing to do here

				key = config_args[0] # By default, the first word in the brackets is the parameter key

				if len(config_args) == 1: # If it's the *only* word, then no value was specified
					no_value.append(key)
					continue

				elif len(config_args) == 2: # If it's two words, the value is a string of the second word
					value = config_args[1]

				else: # If it's more than two words, the value is a list of all words past the first one
					value = config_args[1:]
				
				# Update the config_dict with the new value
				config_dict[key] = value
			
			if len(config_dict.keys()) == 0: # If no 
				await message.channel.send("Include parameters you want to edit!")
				return
			
			if len(no_value) > 0:
				await message.channel.send(f"Include the new value for {grammar_list(no_value)}!")
				return
			
			await EVENTS[event].edit_event(message, config_dict)
			return
	
	if EVENTS[event].RUNNING:
		action = "END"
	else:
		action = "START"

	if "confirm" not in [x.lower() for x in args]:
		await message.channel.send(f"""To confirm that you want to **{action} {event}**, send `confirm` in this channel.
		Send anything else to cancel the command.""".replace('\t', ''))

		msg = await BRAIN.wait_for('message', check=lambda m: (m.author == message.author and m.channel == message.channel))

		if msg.content.lower() != "confirm":
			await message.channel.send("Event command cancelled.")
			return

	await message.channel.send(f"{event} will now {action.lower()}.")
	return [1, event]
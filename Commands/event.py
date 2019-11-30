from Config._functions import grammar_list

HELP = "Starts, ends or edits an event or other bot behavior that spans more than one message"
PERMS = 2
ALIASES = []
REQ = ["BRAIN", "EVENTS"]

async def MAIN(message, args, level, perms, BRAIN, EVENTS):
	if level == 1:
		await message.channel.send("Include events to call!")
		return
	
	if args[1].lower() == "list":
		event_list = [f'`{x}` - **{"ON" if EVENTS[x].RUNNING else "OFF"}**\n' for x in EVENTS.keys()]
		await message.channel.send(f"Here is a list of bot events:\n\n{''.join(event_list)}")
		return
	
	if args[1].upper() not in EVENTS.keys():
		await message.channel.send("Invalid event.")
		return

	event = args[1].upper()

	if level != 2:
		if args[2].lower() == "edit":
			if not EVENTS[event].RUNNING:
				await message.channel.send("You can only change an event that's currently running.")
				return
			
			parsing_index = 0
			config_dict = {}
			no_value = []

			while True:
				found = message.content[parsing_index + 1:].find("[")
				if found == -1:
					break

				parsing_index += found + 2
				reach_index = parsing_index + message.content[parsing_index + 1:].find("]") + 1

				config_args = message.content[parsing_index:reach_index].split(" ")

				if len(config_args) == 0:
					continue

				key = config_args[0]
				if len(config_args) == 1:
					no_value.append(key)
					continue
				elif len(config_args) == 2:
					value = config_args[1]
				else:
					value = config_args[1:]
				
				config_dict[key] = value
			
			if len(config_dict.keys()) == 0:
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

		def check(m):
			return m.author == message.author and m.channel == message.channel

		msg = await BRAIN.wait_for('message', check=check)

		if msg.content.lower() != "confirm":
			await message.channel.send("Event command cancelled.")
			return

	await message.channel.send(f"{event} will now {action.lower()}.")
	return [1, event]
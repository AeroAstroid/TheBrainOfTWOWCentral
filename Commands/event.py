HELP = "Starts/ends an event or other bot behavior that spans more than one message"
PERMS = 2
ALIASES = []
REQ = ["BRAIN", "EVENTS"]

async def MAIN(message, args, level, perms, BRAIN, EVENTS):
	if level == 1:
		await message.channel.send("Include events to call!")
		return
	
	if args[1].lower() == "list":
		event_list = [f'`{x}` - **{"ON" if EVENTS[x].RUNNING else "OFF"}**' for x in EVENTS.keys()]
		await message.channel.send(f"Here is a list of bot events:\n\n{'\n'.join(event_list)}")
		return
	
	if args[1].upper() not in EVENTS.keys():
		await message.channel.send("Invalid event.")
		return

	event = args[1].upper()

	if EVENTS[event].RUNNING:
		action = "END"
	else:
		action = "START"

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
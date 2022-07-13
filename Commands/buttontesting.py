import random

# Import discord buttons
import discord
from discord.ui import Button, View


def HELP(PREFIX):
	return {
		"COOLDOWN": 1,
		"MAIN": "Testing command to test the functionality of Discord buttons.",
		"FORMAT": "",
		"CHANNEL": 0,
		"USAGE": f"""Using `{PREFIX}buttontesting` will show 4 buttons with emojis.
		""".replace("\n", "").replace("\t", ""),
		"CATEGORY" : "Fun"
	}

PERMS = 0 # Non-members
ALIASES = []
REQ = []

EMOJIS = ["😃", "😭", "😎", "😳"]

async def edit_original_message(interaction, reaction_dict, args_concat):
	
	msg_list = ["**"+args_concat+"**\n"]

	for user_in_dict in list(reaction_dict.keys()):

		msg_list.append(f"**{user_in_dict.name}**: {reaction_dict[user_in_dict]}")

	await interaction.response.edit_message(content = "\n".join(msg_list))

	return


async def MAIN(message, args, level, perms, SERVER):
	
	if len(args) == 1: args_concat = "How do you feel about Neonic?"
	else: args_concat = " ".join(args[1:])
	# Create buttons for changing things
	button_view = View()
	msg_to_edit = None
	list_of_reactions = {}

	# Functions for button pressing
	async def smiley_emoji(interaction):

		# Set button user
		button_user = interaction.user

		if button_user in list(list_of_reactions.keys()):
			list_of_reactions[button_user] = EMOJIS[0]
		elif len(list(list_of_reactions.keys())) < 10:
			list_of_reactions[button_user] = EMOJIS[0]
		await edit_original_message(interaction, list_of_reactions, args_concat)
		return

	async def sob_emoji(interaction):

		# Set button user
		button_user = interaction.user

		if button_user in list(list_of_reactions.keys()):
			list_of_reactions[button_user] = EMOJIS[1]
		elif len(list(list_of_reactions.keys())) < 10:
			list_of_reactions[button_user] = EMOJIS[1]
		await edit_original_message(interaction, list_of_reactions, args_concat)
		return

	async def sunglasses_emoji(interaction):

		# Set button user
		button_user = interaction.user
		
		if button_user in list(list_of_reactions.keys()):
			list_of_reactions[button_user] = EMOJIS[2]
		elif len(list(list_of_reactions.keys())) < 10:
			list_of_reactions[button_user] = EMOJIS[2]
		await edit_original_message(interaction, list_of_reactions, args_concat)
		return

	async def flushed_emoji(interaction):

		# Set button user
		button_user = interaction.user
		
		if button_user in list(list_of_reactions.keys()):
			list_of_reactions[button_user] = EMOJIS[3]
		elif len(list(list_of_reactions.keys())) < 10:
			list_of_reactions[button_user] = EMOJIS[3]
		await edit_original_message(interaction, list_of_reactions, args_concat)
		return

	# Create first button - smiley emoji button
	button_1 = Button(label = "", style = discord.ButtonStyle.secondary, emoji = EMOJIS[0])
	button_1.callback = smiley_emoji
	button_view.add_item(button_1)

	# Create second button - smiley emoji button
	button_2 = Button(label = "", style = discord.ButtonStyle.secondary, emoji = EMOJIS[1])
	button_2.callback = sob_emoji
	button_view.add_item(button_2)

	# Create third button - smiley emoji button
	button_3 = Button(label = "", style = discord.ButtonStyle.secondary, emoji = EMOJIS[2])
	button_3.callback = sunglasses_emoji
	button_view.add_item(button_3)

	# Create fourth button - smiley emoji button
	button_4 = Button(label = "", style = discord.ButtonStyle.secondary, emoji = EMOJIS[3])
	button_4.callback = flushed_emoji
	button_view.add_item(button_4)

	msg_to_edit = await message.channel.send("**"+args_concat+"**", view = button_view)
	return

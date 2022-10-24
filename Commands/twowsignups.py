from Helper.__comp import *

from functools import partial
from discord.ui import Modal, InputText
from discord import InputTextStyle

from Helper.__functions import command_user, m_line

import datetime, time

# Staff channels that all TWOWs sent using tc/twowsignups send will be sent to
tsignups_subs_id = 1027144900686393364

def setup(BOT):
	BOT.add_cog(Twowsignups(BOT))

class Twowsignups(cmd.Cog):
	'''
	[Write help description here!]
	'''

	# Extra arguments to be passed to the command
	FORMAT = "`[subcommand]`"
	CATEGORY = "BRAIN"
	EMOJI = CATEGORIES[CATEGORY]
	ALIASES = ['twowsinsignups', 'signups']

	def __init__(self, BRAIN):
		self.BRAIN = BRAIN

	@bridge.bridge_command(aliases=ALIASES)
	@cmd.cooldown(1, 1)
	async def twowsignups(self, ctx,
		subcommand):

		# Command code
		subcommands = ["send"]

		if subcommand not in subcommands:
			await ctx.respond("💀 **You must include a subcommand!**")
			return
		
		if subcommand == "send":

			# Create button for opening modal
			activator = Button(
				label = "Open form", style = dc.ButtonStyle.blurple,
				custom_id = "text box"
			)

			full_view = View(activator)

			msg = await ctx.respond(
				"Click the button to open the modal form to send your information for your TWOW!", 
				view = full_view
			)

			activator.callback = partial(self.button_funct, msg=msg, user=command_user(ctx))

		return

	async def button_funct(self, ctx, msg, user, name_value = None, host_value = None, 
		deadline_value = None, desc_value = None, invite_value = None):

		if ctx.user != user:
			await ctx.response.defer()
			return

		# Create modal form for sending TWOW
		twow_name_input = InputText(label="Name of TWOW", placeholder="eg. neonex miniTWOW S2", 
			max_length=100, custom_id="twow_name", value=name_value)

		twow_host_input = InputText(label="Host(s)", placeholder="eg. Neonic + Nonexistential", 
			max_length=150, custom_id="twow_host", value=host_value)

		twow_deadline_input = InputText(label="Deadline for signups in UTC", 
			placeholder="DD/MM/YYYY HH:MM", max_length=40, custom_id="twow_deadline", 
			value=deadline_value)

		twow_desc_input = InputText(label="Description of TWOW", placeholder="eg. dark dies", 
			style=InputTextStyle.long, max_length=1024, custom_id="twow_desc", value=desc_value)

		twow_invite_input = InputText(label="Permanent invite to TWOW", 
			placeholder="eg. https://discord.gg/uXknRqpenj", max_length=30, 
			custom_id="twow_invite", value=invite_value)

		modal = Modal(twow_name_input, twow_host_input, twow_deadline_input, 
			twow_desc_input, twow_invite_input, title="Submission for #twows-in-signups")

		modal.callback = partial(self.submit_twow, msg=msg, user=user)
		await ctx.response.send_modal(modal)
		
		return

	async def edit_modal(self, ctx, msg, user, error_msg, name_value = None, host_value = None,
		deadline_value = None, desc_value = None, invite_value = None):

		if ctx.user != user:
			await ctx.response.defer()
			return

		# Create button for opening modal
		activator = Button(
			label = "Open form", style = dc.ButtonStyle.blurple,
			custom_id = "text box"
		)

		full_view = View(activator)

		msg = await msg.edit(
			error_msg, view = full_view, embed = None
		)

		activator.callback = partial(self.button_funct, msg=msg, user=user, 
			name_value = name_value, host_value = host_value, deadline_value = deadline_value,
			desc_value = desc_value, invite_value = invite_value)
	
	async def submit_twow(self, ctx, msg, user):
		await ctx.response.defer()

		# Get all text inputs
		name_txt = ctx.data['components'][0]['components'][0]['value']
		host_txt = ctx.data['components'][1]['components'][0]['value']
		deadline_txt = ctx.data['components'][2]['components'][0]['value']
		desc_txt = ctx.data['components'][3]['components'][0]['value']
		invite_txt = ctx.data['components'][4]['components'][0]['value']

		# Check if the deadline format is correct
		deadline_timestamp = None

		try:
			deadline = datetime.datetime.strptime(deadline_txt, "%d/%m/%Y %H:%M")
			deadline_timestamp = int(round(deadline.replace(tzinfo=datetime.timezone.utc).timestamp()))
		except:
			pass

		if deadline_timestamp == None:

			await self.edit_modal(ctx, msg, user, "💀 **Your deadline is formatted wrong! Use the `DD/MM/YYYY HH:MM` format.**",
				name_txt, host_txt, deadline_txt, desc_txt, invite_txt)

		else:

			# Ask the user to confirm their information
			info_embed = dc.Embed(title="Is this information correct?",color=0x31D8B1)
			info_embed.add_field(name = "Name of TWOW", value = name_txt, inline = False)
			info_embed.add_field(name = "Host of TWOW", value = host_txt, inline = False)
			info_embed.add_field(name = "Deadline", value = f"<t:{deadline_timestamp}:F>", inline = False)
			info_embed.add_field(name = "Description", value = desc_txt, inline = False)
			info_embed.add_field(name = "Invite", value = invite_txt, inline = False)
			info_embed.set_footer(text = "tc/twowsignups command", icon_url = user.display_avatar.url)

			# Create buttons
			confirm_button = Button(emoji = "✅", label = "Confirm", style = dc.ButtonStyle.green,
				custom_id = "confirm_button")
			confirm_button.callback = partial(self.confirm_button_pressed, msg=msg, user=user,
				twow_data=[name_txt, host_txt, deadline_timestamp, desc_txt, invite_txt])

			edit_button = Button(emoji = "✏️", label = "Edit", style = dc.ButtonStyle.blurple,
				custom_id = "edit_button")
			edit_button.callback = partial(self.button_funct, msg=msg, user=user, 
				name_value = name_txt, host_value = host_txt, deadline_value = deadline_txt,
				desc_value = desc_txt, invite_value = invite_txt)

			cancel_button = Button(emoji = "❌", label = "Cancel", style = dc.ButtonStyle.red,
				custom_id = "cancel_button")
			cancel_button.callback = partial(self.cancel_button_pressed, msg=msg, user=user)

			button_view = View(confirm_button, edit_button, cancel_button)

			await msg.edit(content = "Please confirm the information using the buttons below.",
				embed = info_embed, view = button_view)

	async def cancel_button_pressed(self, ctx, msg, user):
		await ctx.response.defer()

		if ctx.user != user:
			return
		
		msg = await msg.edit("Cancelled TWOWs in signups submission form.")
		return

	async def confirm_button_pressed(self, ctx, msg, user, twow_data):
		await ctx.response.defer()

		if ctx.user != user:
			return

		# Get channel for TWOWS in signups submissions
		tsignups_subs = self.BRAIN.get_channel(tsignups_subs_id)

		# Create TWOW info embed
		info_embed = dc.Embed(title=twow_data[0],color=0x31D8B1)
		info_embed.add_field(name = "Host of TWOW", value = twow_data[1], inline = False)
		info_embed.add_field(name = "Deadline", value = f"<t:{twow_data[2]}:F>", inline = False)
		info_embed.add_field(name = "Description", value = twow_data[3], inline = False)
		info_embed.add_field(name = "Invite", value = twow_data[4], inline = False)
		info_embed.set_footer(text = f"TWOW submitted by {user.mention} - sent <t:{int(round(time.time()))}:R>", 
			icon_url = user.display_avatar.url)

		# Send embed to the signups submissions channel
		twow_info_msg = await tsignups_subs.send(content = "", embed = info_embed)
		twow_info_msg_id = twow_info_msg.id 
		
		# Edit embed to include its' message id in its own message
		info_embed.title += f" - {twow_info_msg_id}"
		twow_info_msg = await twow_info_msg.edit(content = "", embed = info_embed)

		# Edit message to tell user their TWOW has been submitted
		await msg.edit(m_line(f"""✅ **Your TWOW has been submitted!** ✅/n/If you wish to edit your submission, 
			use the command `tc/twowsignups edit {twow_info_msg_id}`. If you wish to revoke or delete your 
			submission, use the command `tc/twowsignups remove {twow_info_msg_id}`"""), embed = None, view = None)
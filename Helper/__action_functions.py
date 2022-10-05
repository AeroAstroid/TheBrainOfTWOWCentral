import discord as dc
from time import time
import random
from functools import partial

from discord.ui import View, Select

from Helper.__functions import command_user, smart_lookup
from Helper.__server_functions import member_servers, staff_servers
from Helper.__config import BRAIN

async def specify_server(ctx, return_var, create=False, msg_view=None, staff=False, 
membership=True):
	'''
	Prompts a menu to select the server to consider for a command when it's been left ambiguous, 
	using a return variable reference to salvage the user's input within a command's code. Serves 
	both as an initiator (create=True) AND a callback for the subsequent select menu (called by 
	the Discord API with the create=False default)
	'''

	if create:
		if staff:
			possible_servers = staff_servers(ctx)
		elif membership:
			possible_servers = member_servers(ctx)
		else:
			possible_servers = BRAIN.guilds
		
		if len(possible_servers) == 1:
			return_var[0] = possible_servers[0]
			return [None, None]

		elif len(possible_servers) == 0:
			raise dc.errors.CheckFailure()

		msg_view = View()

		options_list = [
			dc.SelectOption(label=s.name, value=str(s.id))
			for s in possible_servers
		]

		select_menu = Select(options=options_list, placeholder="Select a server!",
			custom_id=f"{command_user(ctx).id} {int(time()*1000)}")
		
		msg_view.add_item(select_menu)

		msg = await ctx.respond("⁉️ **Which server will you execute this command for?**",
			view=msg_view)
		
		# Pre-fill callback with this message view so that it can be referenced later
		select_menu.callback = partial(specify_server, return_var=return_var, msg_view=msg_view)

		return [msg, msg_view]
	
	else:
		u_id = ctx.data['custom_id'].split(" ")[0]

		if int(u_id) != ctx.user.id:
			await ctx.response.defer()
			return

		selected_id = int(ctx.data['values'][0])

		server_obj = dc.utils.get(BRAIN.guilds, id=selected_id)

		return_var[0] = server_obj
		await ctx.response.edit_message(content=f"📑 **Selected `{server_obj.name}`.**", view=None)
		msg_view.stop()
		return

async def confirm_action(ctx, return_var, create=False, msg_view=None):
	'''
	Prompts a confirmation menu for important/irreversible/risky actions, using a return variable 
	reference to salvage the user's input within a command's code. Serves as both an initiator 
	(create=True) AND a callback for the subsequent select menu (called by the Discord API with 
	the create=False default).
	'''

	if create:
		msg_view = View()

		# Make the user choose the confirmation between 5 options in a random order
		options_list = [
			dc.SelectOption(label="Confirm this action!", emoji="✅", value="Y"),
			dc.SelectOption(label="Don't confirm this action!", emoji="⛔", value="N0"),
			dc.SelectOption(label="Don't confirm this action!", emoji="⛔", value="N1"),
			dc.SelectOption(label="Don't confirm this action!", emoji="⛔", value="N2"),
			dc.SelectOption(label="Don't confirm this action!", emoji="⛔", value="N3"),
		]
		
		random.shuffle(options_list)

		select_menu = Select(options=options_list, placeholder="Do you confirm this command?",
			custom_id=f"{command_user(ctx).id} {int(time()*1000)}")
		
		msg_view.add_item(select_menu)

		msg = await ctx.respond(
			"⁉️ **Are you sure you want to execute this command?** Confirm below:",
			view=msg_view)
		
		# Pre-fill callback with this message view so that it can be referenced later, + return var
		select_menu.callback = partial(confirm_action, return_var=return_var, msg_view=msg_view)

		return [msg, msg_view]
	
	else:
		u_id = ctx.data['custom_id'].split(" ")[0]

		if int(u_id) != ctx.user.id:
			await ctx.response.defer()
			return
		
		selected = ctx.data['values'][0]

		if selected == "Y":
			await ctx.response.edit_message(content="⌛ **Command confirmed. Please wait...**",
			view=None)
			return_var[0] = True
			msg_view.stop()
			return
		
		else:
			await ctx.response.edit_message(content="⛔ **Command cancelled.**", view=None)
			return_var[0] = False
			msg_view.stop()
			return
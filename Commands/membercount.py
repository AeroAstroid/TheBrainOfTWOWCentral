from Helper.__comp import *

from Helper.__functions import plural, is_whole, smart_lookup, is_dm
from Helper.__action_functions import specify_server

def setup(BOT):
	BOT.add_cog(Membercount(BOT))

class Membercount(cmd.Cog):
	'''
	Returns the member count of the server this command was used in. If used in DMs, prompts 
	the user to specify a server through a dropdown menu. You must be a member in a server to 
	check its member count.
	'''

	# Extra arguments to be passed to the command
	FORMAT = "`(*server_args)`"
	CATEGORY = "SERVER"
	EMOJI = CATEGORIES[CATEGORY]
	ALIASES = ['members', 'member', 'serversize']

	def __init__(self, BRAIN):
		self.BRAIN = BRAIN

	# Slash version of the command due to function signature incompatibility
	@cmd.slash_command(name="membercount")
	@cmd.cooldown(1, 2)
	async def slash_membercount(self, ctx,
		server = ''):
		'''
		Returns the member count of the server this command was used in.
		'''

		server_args = server.split(" ")

		await self.membercount(ctx, *server_args)

		return
	
	@cmd.command(aliases=ALIASES)
	@cmd.cooldown(1, 2)
	async def membercount(self, ctx,
		*server_args):

		server_picked = [None]
		msg = None

		if len(server_args) > 0:
			server_search_term = " ".join(server_args)

			server_names = [g.name for g in self.BRAIN.guilds]

			if is_whole(server_search_term):
				match = dc.utils.get(self.BRAIN.guilds, id=int(server_search_term))
				
				if match is not None:
					server_picked = [match]
			
			elif (match := smart_lookup(server_search_term, server_names)):
				server_picked = [self.BRAIN.guilds[server_names.index(match[1])]]

		
		if server_picked[0] is None:
			if is_dm(ctx):
				msg, msg_view = await specify_server(ctx, server_picked, create=True)

				if msg_view is not None:
					await msg_view.wait()
				
				if server_picked[0] is None: # Happens if the view times out without an answer
					return
			
			else:
				server_picked = [ctx.guild]

		server_name = server_picked[0].name
		member_count = len(server_picked[0].members)

		response = f"📑 **{server_name}** has **{member_count}** member{plural(member_count)}."

		if msg is not None:
			await msg.edit(content=response)
		else:
			await ctx.respond(response)
		return
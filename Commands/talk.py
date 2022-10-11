from Helper.__comp import *

from Helper.__functions import is_dev, is_dm, is_slash_cmd
from Helper.__server_functions import is_staff, staff_servers

def setup(BOT):
	BOT.add_cog(Talk(BOT))

class Talk(cmd.Cog):
	'''
	Sends a message in an arbitrary channel through Brain
	'''

	# Extra arguments to be passed to the command
	FORMAT = "`[channel_id]` `[*message_content]`"
	CATEGORY = "BRAIN"
	EMOJI = CATEGORIES[CATEGORY]
	ALIASES = []

	def __init__(self, BRAIN):
		self.BRAIN = BRAIN

	# Slash version of the command due to function signature incompatibility
	@cmd.slash_command(name="talk")
	@cmd.cooldown(1, 1)
	@cmd.check(is_dev)
	@cmd.check(is_staff)
	async def slash_talk(self, ctx,
		channel_id,
		message_content):
		'''
		Sends a message in an arbitrary channel through Brain
		'''

		msg_args = message_content.split(" ")

		await self.talk(ctx, channel_id, *msg_args)

		return
	
	@cmd.command(aliases=ALIASES)
	@cmd.cooldown(1, 1)
	@cmd.check(is_dev)
	@cmd.check(is_staff)
	async def talk(self, ctx,
		channel_id,
		*msg_args):

		channel_id = int(channel_id)
		chosen_channel = None

		if is_dm(ctx):
			staff_s = staff_servers(ctx)
		else:
			staff_s = [ctx.guild]

		for s in staff_s:
			s_channel_ids = [c.id for c in s.channels]
			s_member_ids = [m.id for m in s.members]

			if channel_id in s_channel_ids: # Choose either a channel...
				chosen_channel = dc.utils.get(s.channels, id=channel_id)
				break
			
			if channel_id in s_member_ids: # ...or a member to DM
				chosen_channel = dc.utils.get(s.members, id=channel_id)
				break
		
		if chosen_channel is None:
			if is_dm(ctx):
				await ctx.respond(
				"💀 **This channel/member can't be found** in any servers you moderate!")
			
			else:
				await ctx.respond(
				"💀 **This channel/member can't be found** in this server!")
			
			return

		if is_slash_cmd(ctx):
			message_content = " ".join(msg_args).replace("\\n", "\n")
		else:
			message_content = ctx.message.content[ctx.message.content.find(msg_args[0]):]

		if len(message_content) == 0:
			await ctx.respond("💀 **The message to be sent cannot be empty!**")
			return

		await chosen_channel.send(message_content)
		await ctx.respond(
		f"✅ **Message successfully sent in `{channel_id}`:**\n> \t`{message_content}`")

		return
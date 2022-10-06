from Commands.__comp import *

from Helper.__functions import (is_whole, split_escape, is_dm, smart_lookup, is_slash_cmd, plural, 
	m_line)
from Helper.__server_functions import is_staff_here
from Helper.__action_functions import confirm_action

def setup(BOT):
	BOT.add_cog(Clean(BOT))

class Clean(cmd.Cog):
	'''
	Cleans out a channel of a certain amount of messages, using certain conditions.

	This command makes use of different keywords that change functionality in different ways.

	**`-within`**: specifies the range of messages to be searched for the conditions and 
	potentially deleted. Must be followed by a whole number between 1 and 1000.

	**`-since`**: specifies an upper bound of age for the messages to delete, in the form of an 
	ID. The command will delete all messages younger than the ID **__including the message with 
	the ID itself__**, if the ID points to one.

	The channel clean command must have at least one of the keywords `-within` or `-since`.

	</>

	Other keywords are:

	**`-from`**: specifies members to delete messages from. Supports multiple member names, member 
	IDs, role names and role IDs, in any combination, using a comma-separated format to separate 
	each identifier. If this keyword is omitted, the command deletes everyone's messages; if it's 
	included, it will only delete messages from the members named or members who have one of the 
	roles named.

	**`-silent`**: this keyword isn't followed by any values. Including it will make the command 
	"silent"; it will delete the user's command as well as its own confirmation message so as to 
	not leave a trace of the command's execution.

	</>

	Examples:

	> `{PREFIX}clean -within 50 -since 1026951126131691520` /n/
	> `{PREFIX}clean -within 100 -from Role 1, User 1, User 2 -silent` /n/
	> `{PREFIX}clean -since 1026951126131691520`
	'''

	# Extra arguments to be passed to the command
	FORMAT = "`[*'-within'/'-since']` `(*'-from')` `('-silent')`"
	CATEGORY = "SERVER"
	EMOJI = CATEGORIES[CATEGORY]
	ALIASES = ['clear', 'purge', 'prune']

	def __init__(self, BRAIN): self.BRAIN = BRAIN

	# Slash version of the command due to function signature incompatibility
	@cmd.slash_command(name="clean")
	@cmd.cooldown(1, 5)
	@cmd.check(is_staff_here)
	async def slash_clean(self, ctx,
		clean_command = ''):
		'''
		Cleans out a channel of a certain amount of messages, using certain conditions.
		'''

		clean_args = clean_command.split()

		await self.clean(ctx, *clean_args)

		return

	@cmd.command(aliases=ALIASES)
	@cmd.cooldown(1, 5)
	@cmd.check(is_staff_here)
	async def clean(self, ctx,
		*clean_args):

		if is_dm(ctx):
			await ctx.respond("💀 **This command is only usable in a server channel!**")
			return
		
		if is_slash_cmd(ctx):
			await ctx.interaction.response.defer()

		keyword_info = {
			"-within": "",
			"-since": "",
			"-from": "",
			"-silent": False
		}

		l_args = [a.lower() for a in clean_args]

		if "-within" not in l_args and "-since" not in l_args:
			await ctx.respond("💀 **You must include a `-within` keyword or an `-since` keyword!**")
			return
		
		current = ""
		for a in l_args:
			if a in keyword_info.keys():
				current = a

				if a == "-silent":
					keyword_info[current] = True

				continue
			
			try:
				keyword_info[current] += (" " if len(keyword_info[current]) > 0 else "") + a
			except IndexError:
				pass
		
		if keyword_info["-within"] and not is_whole(keyword_info["-within"]):
			await ctx.respond("💀 **The message limit (`-within`) must be a whole number!**")
			return
		
		if keyword_info["-within"]:
			within = int(keyword_info["-within"])

			if within > 1000:
				await ctx.respond("💀 **The message limit (`-within`) must be 1000 at most!**")
				return
		else:
			within = 1000
		
		if keyword_info["-since"] and not is_whole(keyword_info["-since"]):
			await ctx.respond("💀 **The `-since` parameter must be an ID!**")
			return
		
		if keyword_info["-since"]:
			since = int(keyword_info["-since"])
		else:
			since = None

		r_names = [r.name for r in ctx.guild.roles]
		r_ids = [[str(r.id)] for r in ctx.guild.roles]

		m_names = [m.name for m in ctx.guild.members]
		m_ids = [[str(m.id)] for m in ctx.guild.members]
		
		targets = None

		if keyword_info["-from"]:
			targets = []

			from_args = split_escape(keyword_info["-from"], ",")

			for indiv_r in from_args:
				m = smart_lookup(indiv_r, m_names, aliases=m_ids)

				if m:
					m = dc.utils.get(ctx.guild.members, name=m[1])
					targets.append(m)
					continue

				r = smart_lookup(indiv_r, r_names, aliases=r_ids)

				if r:
					role_obj = dc.utils.get(ctx.guild.roles, name=r[1])
					targets += role_obj.members
					continue
			
			targets = set(targets)
		
		action_confirmed = [None]
		c_msg, msg_view = await confirm_action(ctx, action_confirmed, create=True)

		await msg_view.wait()

		if not action_confirmed[0]:
			return
		
		within += 2

		def check(msg):
			status = True

			if not is_slash_cmd(ctx):
				if not keyword_info["-silent"] and msg.id in [c_msg.id, ctx.message.id]:
					status = False
			
			if since is not None:
				status = status and msg.id >= since
			
			if targets is not None:
				status = status and msg.author in targets
			
			return status
		
		deleted = await ctx.channel.purge(limit=within, check=check)

		if not keyword_info["-silent"]: 
			within -= 2 

			await c_msg.edit(content=m_line(f"""
			✅ **Successfully searched {within} message{plural(within)}, deleted {len(deleted)}!**
			"""))
		
		else:
			if is_slash_cmd(ctx):
				await ctx.send_followup(
				content=f"✅ **Successfully deleted {len(deleted)-2} messages!**",
				ephemeral=True)

		return
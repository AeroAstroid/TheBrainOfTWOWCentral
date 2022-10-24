from Helper.__comp import *

import random as rng

from Helper.__functions import (is_dm, smart_lookup, is_number, is_whole, is_slash_cmd, plural, 
	split_escape)
from Helper.__server_functions import is_staff
from Helper.__action_functions import specify_server

def setup(BOT):
	BOT.add_cog(Role(BOT))

class Role(cmd.Cog):
	'''
	Staff command for streamlined large-scale role management within a server.

	This command's syntax works using argument modes. You must include the `-add` or `-remove` 
	keywords followed by the role(s) to add/remove, separating multiple roles by commas. Quotation 
	marks around each role name are optional, but can be used to write role names that have commas 
	in them. Roles can be specified both by name and by their ID. For example: 
	/n/
	> `{PREFIX}role -remove Role 1, Role 2, Role 3` /n/
	> `{PREFIX}role -remove "This Role Has, A Comma", Role 2, Role 3`

	</>

	The other available keywords are:
	
	**`-to`**: mandatory when used with the `-add` keyword; specifies whom the role(s) will be 
	added to. Accepts member names, member IDs, role names, role IDs as well as an `everyone` 
	keyword for everyone in the server, using the same comma separation as described earlier. /n/
	> `{PREFIX}role -add Role 1 -to User 1, Role 2, User 2`
	> `{PREFIX}role -add Role 1 -to everyone`

	**`-from`**: optionally used with the `-remove` keyword; specifies whom the role(s) will be 
	removed from. If this is not included, the command will remove the roles from everyone that 
	has them. /n/
	> `{PREFIX}role -remove Role 1 -from Role 2`

	</>

	**`-except`**: used with both `-add` and `-remove`; specifies exceptions for people or roles 
	for which the command shouldn't apply. This always overrides the `-to` and `-from` keywords.
	/n/
	> `{PREFIX}role -add Role 1 -to Role 2 -except User 1`

	**`-count`**: specifies how many people the command should apply to. Can be expressed both as 
	a whole number of users, or as a percentage of the people the command would originally have 
	selected (the total number of people will be rounded once the percentage is applied). The 
	specific users the command is run on will then be chosen randomly. /n/
	> `{PREFIX}role -add Role 1 -to Role 2 -count 12` /n/
	> `{PREFIX}role -remove Role 1 -count 50%`

	**`-chance`**: for every person selected by the command, specifies a probability that the 
	command will actually be applied to them. Can be expressed both as a percentage or as a 
	decimal number (from 0% to 100%, or 0 to 1). /n/
	> `{PREFIX}role -add Role 1 -to Role 2 -chance 0.5` /n/
	> `{PREFIX}role -add Lottery Winner -to everyone -chance 0.000001%`
	'''

	# Extra arguments to be passed to the command
	FORMAT = "[-add/-remove] (-to/-from) (-count) (-chance)"
	CATEGORY = "SERVER"
	EMOJI = CATEGORIES[CATEGORY]
	ALIASES = ['roles', 'roledist']

	def __init__(self, BRAIN):
		self.BRAIN = BRAIN

	# Slash version of the command due to function signature incompatibility
	@cmd.slash_command(name="role")
	@cmd.cooldown(1, 5)
	@cmd.check(is_staff)
	async def slash_role(self, ctx,
		role_command = ''):
		'''
		Staff command for streamlined large-scale role management within a server.
		'''

		role_args = role_command.split()

		await self.role(ctx, *role_args)

		return

	@cmd.command(aliases=ALIASES)
	@cmd.cooldown(1, 5)
	@cmd.check(is_staff)
	async def role(self, ctx,
		*role_args):

		server_picked = [None]
		msg = None

		if is_dm(ctx):
			msg, msg_view = await specify_server(ctx, server_picked, staff=True, create=True)

			if msg_view is not None:
				await msg_view.wait()
			
			if server_picked[0] is None: # Happens if the view times out without an answer
				return
		
		else:
			server_picked = [ctx.guild]
		
		server_picked = server_picked[0]
		roles = server_picked.roles

		if len(roles) == 0:
			if msg is None:
				await ctx.respond(f"💀 **The server `{server_picked.name}` has no roles!**")
			else:
				await msg.edit(content=f"💀 **The server `{server_picked.name}` has no roles!**")
			return
		
		modes = ["-add", "-remove"]
		l_args = [a.lower() for a in role_args]

		mode_picked = None

		for m in modes:
			if m in l_args:
				mode_picked = m[1:]
				break
		
		if mode_picked is None:
			await ctx.respond(
			f"💀 **You must include one of the following keywords:**\n> {', '.join(modes)}")
			return
		
		if mode_picked == "add":
			modifiers = ["-add", "-to", "-except", "-count", "-chance"]
		if mode_picked == "remove":
			modifiers = ["-remove", "-from", "-except", "-count", "-chance"]
		
		modif_args = []

		for a in l_args:
			if a not in modifiers:
				if len(modif_args) == 0:
					await ctx.respond(
					f"💀 **You must start the command with the -{mode_picked} keyword!**")
					return
				
				modif_args[-1][1] += (" " if len(modif_args[-1][1]) > 0 else "") + a
			else:
				modif_args.append([a, ""])

		# Establish order of precedence
		modif_args = sorted(modif_args, key=lambda m: modifiers.index(m[0]))

		r_names = [r.name for r in roles]
		r_ids = [[str(r.id)] for r in roles]

		roles_picked = []
		highest_bot_role = server_picked.get_member(self.BRAIN.user.id).top_role

		for modif, spec in modif_args:
			if modif == "-" + mode_picked:
				s_roles = split_escape(spec, ",")

				for indiv_r in s_roles:
					r = smart_lookup(indiv_r, r_names, aliases=r_ids)
					r = dc.utils.get(server_picked.roles, name=r[1])

					if r is None:
						if msg is None:
							await ctx.respond(
							f"💀 **Could not narrow down `{indiv_r}` to a role!**")
						else:
							await msg.edit(
							content=f"💀 **Could not narrow down `{indiv_r}` to a role!**")
						return
					
					if r >= highest_bot_role:
						if msg is None:
							await ctx.respond(
							f"💀 **I don't have permission to assign the `{r.name}` role!**")
						else:
							await msg.edit(content=
							f"💀 **I don't have permission to assign the `{r.name}` role!**")
						return
					
					roles_picked.append(r)

		targets = []
		modifs_used = [m[0] for m in modif_args]

		# If there is no "remove from" provided, remove from every single person with the role
		if mode_picked == "remove" and "-from" not in modifs_used:
			for role in roles_picked:
				targets += role.members
			
			targets = set(targets) # Remove duplicates after everything is added
		
		count = None
		count_percent = False

		chance = None

		m_names = [m.name for m in server_picked.members]
		m_ids = [[str(m.id)] for m in server_picked.members]
		
		for modif, spec in modif_args:
			# Having multiple members/roles in a -to or -from combines them with OR logic
			if modif in ["-to", "-from"]:
				s_roles = split_escape(spec, ",")

				for indiv_r in s_roles:
					if indiv_r == "everyone":
						targets = server_picked.members
						break
					
					m = smart_lookup(indiv_r, m_names, aliases=m_ids)

					if m:
						m = dc.utils.get(server_picked.members, name=m[1])
						targets.append(m)
						continue

					r = smart_lookup(indiv_r, r_names, aliases=r_ids)

					if r:
						role_obj = dc.utils.get(server_picked.roles, name=r[1])
						targets += role_obj.members
						continue

					if msg is None:
						await ctx.respond(
						f"💀 **Could not narrow down `{indiv_r}` to a role or member!**")
					else:
						await msg.edit(content=
						f"💀 **Could not narrow down `{indiv_r}` to a role or member!**")
					return
			
			# Having multiple members/roles in an -except combines them with NOR logic
			if modif == "-except":
				s_roles = split_escape(spec, ",")

				for indiv_r in s_roles:
					r = smart_lookup(indiv_r, r_names, aliases=r_ids)

					if not r:
						if msg is None:
							await ctx.respond(
							f"💀 **Could not narrow down `{indiv_r}` to a role!**")
						else:
							await msg.edit(content=
							f"💀 **Could not narrow down `{indiv_r}` to a role!**")
						return
				
					role_obj = dc.utils.get(server_picked.roles, name=r[1])
					targets = [t for t in targets if t not in role_obj.members]
			
			if modif == "-count":
				count_percent = spec.endswith("%")
				value = spec[:-1] if count_percent else spec

				if not count_percent and not is_whole(value):
					if msg is None:
						await ctx.respond(f"💀 **Could not interpret `{spec}` as a whole number!**")
					else:
						await msg.edit(content=
						f"💀 **Could not interpret `{spec}` as a whole number!**")
					return
				
				if count_percent and not is_number(value):
					if msg is None:
						await ctx.respond(f"💀 **Could not interpret `{spec}` as a percentage!**")
					else:
						await msg.edit(content=
						f"💀 **Could not interpret `{spec}` as a percentage!**")
					return
				
				count = float(value) / (100 if count_percent else 1)
			
			if modif == "-chance":
				chance_percent = spec.endswith("%")
				value = spec[:-1] if chance_percent else spec
		
				if not is_number(value):
					if msg is None:
						await ctx.respond(f"💀 **Could not interpret `{spec}` as a number!**")
					else:
						await msg.edit(content=
						f"💀 **Could not interpret `{spec}` as a number!**")
					return
				
				chance = float(value) / (100 if chance_percent else 1)
		
		targets = set(targets)

		if count is not None:
			if count_percent:
				count = round(len(targets) * count)
			
			count = min(len(targets), max(0, count))

			targets = rng.sample(targets, k=int(count))
		
		if chance is not None:
			chance = min(1, max(0, chance))

			targets = [t for t in targets if rng.random() < chance]
		
		if len(targets) == 0:
			if msg is None:
				await ctx.respond("💀 **This role command selected 0 people!**")
			else:
				await msg.edit(content="💀 **This role command selected 0 people!**")
			return
		
		if is_slash_cmd(ctx):
			await ctx.interaction.response.defer()
		
		if mode_picked == "add":
			msg_text = f"⌛ **Adding roles to {len(targets)} member{plural(len(targets))}...**"
		if mode_picked == "remove":
			msg_text = f"⌛ **Removing roles from {len(targets)} member{plural(len(targets))}...**"
		
		if msg is None:
			msg = await ctx.respond(msg_text)
		else:
			await msg.edit(content=msg_text)
		
		if mode_picked == "add":
			for t in targets:
				await t.add_roles(*roles_picked)

		if mode_picked == "remove":
			for t in targets:
				await t.remove_roles(*roles_picked)
		
		await msg.edit(content=
		f"✅ **Role command successfully applied to {len(targets)} member{plural(len(targets))}!**")
		
		return
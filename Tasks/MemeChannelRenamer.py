from Helper.__comp import *
import inspect

import re

from Helper.__functions import is_dev, plural, m_line, is_number, is_whole, split_escape

def setup(BOT):
	BOT.add_cog(MemeChannelRenamer(BOT))

class MemeChannelRenamer(cmd.Cog):
	'''
	Task that changes the name of TWOW Central's #memes channel every hour
	'''

	###### BEGIN CUSTOM TASK PARAMETERS! ######

	CHANNEL_ID = 656641155869704205
	LETTERS = "éêèëĕẽēė"
	CHANNEL_NAME = "mem(.)s"

	####### END CUSTOM TASK PARAMETERS! #######

	def __init__(self, BRAIN):
		self.BRAIN = BRAIN

		for c in self.__cog_commands__:
			c.name = self.TASK_PREFIX + c.name
	
	TASK_PREFIX = "mcr/" # Secondary prefix for this this task's commands
	ON_BY_DEFAULT = True # If true, will get auto-started once the bot fully connects

	############ BEGIN TASK CODE! ############

	@tasks.loop(hours=1)
	async def change_channel_name(self):
		channel = self.BRAIN.get_channel(self.CHANNEL_ID)

		if not (m := re.match(self.CHANNEL_NAME, channel.name)):
			new_name = self.CHANNEL_NAME.replace("(.)", self.LETTERS[0])
		
		elif (i := self.LETTERS.find(m.groups()[0])) < 0:
			new_name = self.CHANNEL_NAME.replace("(.)", self.LETTERS[0])
		
		else:
			new_name = self.CHANNEL_NAME.replace("(.)", self.LETTERS[(i+1) % len(self.LETTERS)])
		
		await channel.edit(name=new_name)

	############# END TASK CODE! #############

	# Below is all boilerplate task code -- preferrably do not edit it at all

	@cmd.command()
	@cmd.check(is_dev)
	async def edit(self, ctx, parameter, *value):
		cog_attrs = [m[0] for m in inspect.getmembers(cmd.Cog)]
		task_attrs = [m for m in inspect.getmembers(self)]

		# Hardcoded here are default parameters that the command user shouldn't have access to
		attrs = [m for m in task_attrs if m[0] not in (cog_attrs + 
			["TASK_PREFIX", "BRAIN", "ON_BY_DEFAULT"]
		)]

		# Exclude functions, loops and commands from the attributes list
		attrs = [m for m in attrs if (
			not inspect.ismethod(m[1]) and
			not type(m[1]) == tasks.Loop and
			not type(m[1]) == cmd.core.Command
		)]

		param_list = [p[0] for p in attrs]

		if parameter.upper() not in param_list:
			await ctx.respond(m_line(f"""💀 **Invalid parameter `{parameter.upper()}`!** 
			Available parameters are: /n/> **`{", ".join(param_list)}`**"""))
			return
		
		i = param_list.index(parameter.upper())
		value = " ".join(value)

		try: # Prioritize keeping the same type as the original variable
			value = type(attrs[i][1])(value)

		except Exception: # If that's not possible...
			if is_whole(value):
				value = int(value)
			elif is_number(value):
				value = float(value)
			elif len(split_escape(value, ", ")) > 1:
				value = split_escape(value)
			
			# If all of these fail, keep it a string

		setattr(self, parameter.upper(), value)

		await ctx.respond(m_line(f"""
		**Successfully edited parameter `{parameter.upper()}`** to the value: /n/> **`{value}`**
		"""))
		return
	
	def get_loops(self):
		return [m for m in inspect.getmembers(self) if type(m[1]) == tasks.Loop]
	
	@cmd.command()
	@cmd.check(is_dev)
	async def status(self, ctx):
		loop_msgs = "\n".join([
			f"> **{l.upper()}** - {'Running' if obj.is_running() else 'Not Running'}"
			for l, obj in self.get_loops()])
		
		await ctx.respond(
			f"**Status report for loops in the `{self.qualified_name}` task:**\n{loop_msgs}")
		return
	
	def set_loop(self, start, loop_name=''):
		all_loops = self.get_loops()
		
		if not loop_name:
			for loop_tuple in all_loops:
				if start:
					loop_tuple[1].start()
				else:
					loop_tuple[1].cancel()
			return all_loops
		
		all_loop_names = [m[0] for m in all_loops]

		if loop_name.lower() not in all_loop_names:
			return False
		
		i = all_loop_names.index(loop_name.lower())

		if start:
			all_loops[i][1].start()
		else:
			all_loops[i][1].cancel()
		
		return all_loops[i]

	@cmd.command()
	@cmd.check(is_dev)
	async def start(self, ctx, loop_name=''):
		result = self.set_loop(True, loop_name=loop_name)

		if not result:
			await ctx.respond(f"💀 **Loop `{loop_name}` wasn't found in `{self.qualified_name}`!**")
			return
		
		if type(result) == list:
			await ctx.respond(f"**Successfully started {len(result)} loop{plural(len(result))}!**")
			return

		await ctx.respond(f"**Successfully started loop `{result[0]}`!**")
		return

	@cmd.command()
	@cmd.check(is_dev)
	async def end(self, ctx, loop_name=''):
		result = self.set_loop(False, loop_name=loop_name)

		if not result:
			await ctx.respond(f"💀 **Loop `{loop_name}` wasn't found in `{self.qualified_name}`!**")
			return
		
		if type(result) == list:
			await ctx.respond(f"**Successfully ended {len(result)} loop{plural(len(result))}!**")
			return

		await ctx.respond(f"**Successfully ended loop `{result[0]}`!**")
		return

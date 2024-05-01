from Helper.__comp import *

import os
from time import time

from Helper.__functions import m_line, is_dev

def setup(BOT):
	BOT.add_cog(Reimport(BOT))

class Reimport(cmd.Cog):
	'''
	Choose a bot command file to reload from disk using the `[command_name]` argument.

	Including a `(script_file)` attachment will replace the command script with the file 
	provided, saving a backup for security purposes. This will also create a new command under 
	the name `[command_name]` if it doesn't exist already. *This functionality is unavailable 
	if the command is triggered as a slash command.*

	Useful to test quick, temporary changes without having to wait for a full restart.
	'''

	# Extra arguments to be passed to the command
	FORMAT = "`[command_name]` `(script_file)`"
	CATEGORY = "BRAIN"
	EMOJI = CATEGORIES[CATEGORY]
	ALIASES = ['re', 'import']

	def __init__(self, BRAIN):
		self.BRAIN = BRAIN

	@cmd.command(aliases=ALIASES)
	@cmd.cooldown(1, 5)
	@cmd.check(is_dev)
	async def reimport(self, ctx,
		cmd_name):

		if cmd_name is None:
			await ctx.reply("💀 Include the name of the command to import.")
			return
		
		cmd_name = cmd_name.lower()

		if f"{cmd_name}.py" not in os.listdir("Commands"):
			if len(ctx.message.attachments) != 0:
				await ctx.message.attachments[0].save(f"Commands/{cmd_name}.py")

			else:
				await ctx.reply(
				"💀 That command does not exist. Include a script file to create it!"
				)
				return

			try:
				self.BRAIN.load_extension(f"Commands.{cmd_name}")

			except Exception as e:
				os.remove(f"Commands/{cmd_name}.py")

				await ctx.reply(m_line(f"""
				⚠️ **An error ({type(e).__name__}) occured with the new command script!** 
				The import command has been cancelled.
				"""))
				return

			await ctx.reply("✅ **Command file created successfully.**")
			return
		
		else:
			with open(f"Commands/{cmd_name}.py", "r", encoding="utf-8") as f:
				backup_cmd = f.read()

			if len(ctx.message.attachments) != 0:
				await ctx.message.attachments[0].save(f"Commands/{cmd_name}.py")

			try:
				self.BRAIN.unload_extension(f"Commands.{cmd_name}")
			except dc.errors.ExtensionNotLoaded:
				pass

			try:
				self.BRAIN.load_extension(f"Commands.{cmd_name}")

			except Exception as e:
				with open(f"Commands/{cmd_name}.py", "w", encoding="utf-8") as f:
					f.write(backup_cmd)

				self.BRAIN.load_extension(f"Commands.{cmd_name}")

				await ctx.reply(m_line(f"""
				⚠️ **An error ({type(e).__name__}) occured with the new command script!**
				The reimport command has been cancelled.
				"""))
				return
			
			f_name = f"Commands/BACKUP_{cmd_name}_{int(time())}.py"

			with open(f_name, 'w', encoding='utf-8') as f:
				f.write(backup_cmd)

			await ctx.reply(m_line("""✅ **Command file updated successfully.** 
			Below is a backup of its previous version."""), file=dc.File(f_name))

			os.remove(f_name)

		return
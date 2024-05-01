from Helper.__comp import *

import os
import sys
from time import time
from datetime import datetime

from Helper.__functions import m_line, is_dm, is_dev

def setup(BOT):
	BOT.add_cog(Restart(BOT))

class Restart(cmd.Cog):
	'''
	Forces a bot restart upon usage. The bot will report the amount of time it took to restart 
	in the channel this command was used in.

	Including the literal argument `('debug')` in the command will make the bot restart in debug 
	mode - by default, it restarts into the main Brain of TWOW Central.
	'''

	# Extra arguments to be passed to the command
	FORMAT = "`('debug')`"
	CATEGORY = "BRAIN"
	EMOJI = CATEGORIES[CATEGORY]
	ALIASES = ['r']

	def __init__(self, BRAIN):
		self.BRAIN = BRAIN

	@cmd.command(aliases=ALIASES)
	@cmd.cooldown(1, 5)
	@cmd.check(is_dev)
	async def restart(self, ctx,
		debug = ''):

		file_ref = sys.argv[0]

		debug_arg = 'debug' if debug == 'debug' else ''

		report_guild = f"1_report_guild:{'' if ctx.guild is None else ctx.guild.id}"

		report_chnl = m_line(f"""
		2_report_chnl:{ctx.message.author.id if is_dm(ctx) else ctx.channel.id}""")

		report_time = f"3_report_time:{int(time()*1000)}"

		await self.BRAIN.change_presence(status=dc.Status.idle)
		
		await ctx.reply("♻️ **Restarting the Brain of TWOW Central!**")
		print(f"Restarting on command from {ctx.message.author} at {datetime.utcnow()}")

		os.execl(
		sys.executable, 'python', file_ref, report_guild, report_chnl, report_time, debug_arg)

		return
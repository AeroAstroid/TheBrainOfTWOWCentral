from Helper.__comp import *

from time import time

from Helper.__config import STARTUP
from Helper.__functions import m_line

def setup(BOT):
	BOT.add_cog(Uptime(BOT))

class Uptime(cmd.Cog):
	'''
	Returns the amount of time since the bot was last started.
	'''

	# Extra arguments to be passed to the command
	FORMAT = ""
	CATEGORY = "BRAIN"
	EMOJI = CATEGORIES[CATEGORY]
	ALIASES = ['up']

	def __init__(self, BRAIN):
		self.BRAIN = BRAIN

	@cmd.command(aliases=ALIASES)
	@cmd.cooldown(1, 1)
	async def uptime(self, ctx):

		s = time() - STARTUP

		s_indiv = (
			int(s // 86400),
			int(s // 3600) % 24,
			int(s // 60) % 60,
			int(s) % 60,
			int(s * 1000) % 1000
		)

		await ctx.reply(m_line(f"""
		⏳ **The Brain of TWOW Central** has been online for 
		{s_indiv[0]}d {s_indiv[1]}h {s_indiv[2]}min {s_indiv[3]}s {s_indiv[4]}ms."""))

		return
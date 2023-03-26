import random, discord, datetime
from Helper.__comp import *
from Helper.__functions import get_dollar_strings, replace_dollar_strings, create_timestamped_embed


def setup(BOT):
	BOT.add_cog(Eightball(BOT))

class Eightball(cmd.Cog):
	'''
	[Write help description here!]
	'''

	# Extra arguments to be passed to the command
	FORMAT = "`[]`"
	CATEGORY = "BRAIN"
	EMOJI = CATEGORIES[CATEGORY]
	ALIASES = ['8ball']

	def __init__(self, BRAIN):
		self.BRAIN = BRAIN

	@bridge.bridge_command(aliases=ALIASES)
	@cmd.cooldown(1, 1)
	async def eightball(self, ctx):
		return_unparsed = random.choice(
			[
				"invest in $stock$",
				"create $item$"
			]
		)
		list_dollar_strings = get_dollar_strings()
		dollar_strings_return = []
		for element in list_dollar_strings:
			match element:
				case "stock":
					dollar_strings_return += random.choice(["apple stocks", "stonks", "stocks"])
				case "item":
					dollar_strings_return += random.choice(["TWOW Central 2", "Season Pentagon", "a b++ tag"])

		return_parsed = replace_dollar_strings(return_unparsed, dollar_strings_return)
		ctx.respond(Embed=create_timestamped_embed(title="The 8ball says:", description=return_parsed))
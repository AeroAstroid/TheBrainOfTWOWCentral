from Helper.__comp import *

from functools import partial
from discord.ui import Modal, InputText
from discord import InputTextStyle

from Helper.__functions import command_user, m_line

def setup(BOT):
	BOT.add_cog(Modaltest(BOT))

class Modaltest(cmd.Cog):
	'''
	Temporary command to help test Modal functionality.
	'''

	# Extra arguments to be passed to the command
	FORMAT = ""
	CATEGORY = "BRAIN"
	EMOJI = CATEGORIES[CATEGORY]
	ALIASES = ['']

	def __init__(self, BRAIN):
		self.BRAIN = BRAIN

	@bridge.bridge_command(aliases=ALIASES)
	@cmd.cooldown(1, 1)
	async def modaltest(self, ctx):
		activator = Button(
			label = "Text Box", emoji = "⬅️", style = dc.ButtonStyle.blurple,
			custom_id = "text box"
		)

		full_view = View(activator)

		msg = await ctx.respond("Press the button to open a Modal!", view=full_view)

		activator.callback = partial(self.button_funct, msg=msg, user=command_user(ctx))

		return
	
	async def button_funct(self, ctx, msg, user):
		box1 = InputText(label="First Box", placeholder="100 char. box", max_length=100, 
			custom_id="tb1")

		box2 = InputText(label="Second Box", placeholder="Box for long answers", 
			style=InputTextStyle.long, custom_id="tb2")

		modal = Modal(box1, box2, title="Modal Title")

		modal.callback = partial(self.modal_funct, msg=msg, user=user)

		await ctx.response.send_modal(modal)

		return
	
	async def modal_funct(self, ctx, msg, user):
		await ctx.response.defer()

		await msg.edit(content=m_line(f"""
		**This modal has been submitted to by {user.name}!**
		
		**Text 1:** `{ctx.data['components'][0]['components'][0]['value']}`
		
		**Text 2:** `{ctx.data['components'][1]['components'][0]['value']}`
		"""), view=None)

		return

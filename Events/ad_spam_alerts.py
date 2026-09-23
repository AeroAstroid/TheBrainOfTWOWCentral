from __future__ import annotations
from datetime import datetime, timedelta
import discord
from Config._functions import grammar_list
from Config._servers import MAIN_SERVER
import re


class EVENT:

	def __init__(self):
		self.RUNNING = False
		self.param = {}

	def start(self, SERVER):
		self.SERVER = SERVER
		self.AD_CHANNEL: discord.TextChannel = MAIN_SERVER["ADVERTISEMENTS"]
		self.ALERTS_CHANNEL: discord.TextChannel = MAIN_SERVER["STAFF_ALERTS"]
		self.ROLE_WHITELIST = [
			MAIN_SERVER["NOTABLE_HOST"]
		]
		self.param = {
			"CONSECUTIVE_AD_THRESHOLD": 5,
			"COOLDOWN_MIN": 60 * 2,
		}
		self.RUNNING = True

	def end(self):
		self.RUNNING = False

	ad_counts: dict[int, int] = {}
	last_ad_times: dict[int, datetime] = {}
	ad_msgs: dict[int, list[discord.Message]] = {}

	async def on_message(self, message: discord.Message):
		URL_REGEX = r"(?:https?:\/\/[^\s<>\"'`]+)|(?:discord.gg\/\w+)"
		has_url = re.search(URL_REGEX, message.content)

		if message.channel.id == self.AD_CHANNEL.id and has_url:
			if isinstance(message.author, discord.Member):
				for role in self.ROLE_WHITELIST:
					if role in message.author.roles:
						self.ad_counts.pop(message.author.id, None)
						return
			last_time = self.last_ad_times.get(message.author.id)
			if last_time and datetime.now() - last_time < timedelta(minutes=self.param["COOLDOWN_MIN"]):
				return
			self.last_ad_times[message.author.id] = datetime.now()
			self.ad_counts.setdefault(message.author.id, 0)
			if self.ad_counts[message.author.id] >= 0:
				self.ad_counts[message.author.id] += 1
				self.ad_msgs.setdefault(message.author.id, [])
				self.ad_msgs[message.author.id].append(message)

			if self.ad_counts[message.author.id] >= self.param["CONSECUTIVE_AD_THRESHOLD"]:
				await self.ad_spam_alert(message)
				self.ad_counts[message.author.id] = -1
				self.ad_msgs.pop(message.author.id, None)

		elif message.channel.id != self.AD_CHANNEL.id:
			self.ad_counts.pop(message.author.id, None)
			self.ad_msgs.pop(message.author.id, None)
	
	async def ad_spam_alert(self, message: discord.Message):
		embed = discord.Embed()
		embed.set_author(name=f"📢 Ad Spam Alert", icon_url=message.author.avatar and message.author.avatar.url)
		desc = f"<@{message.author.id}> sent **{self.param['CONSECUTIVE_AD_THRESHOLD']} ads** with no other messages in the server."
		assert message.guild
		desc += f"\nLatest ad: https://discord.com/channels/{message.guild.id}/{message.channel.id}/{message.id}"
		desc += f"\nSearch query: `from:{message.author.name}`"
		embed.description = desc

		view = discord.ui.View(timeout=None)
		button = discord.ui.Button(label=f"Kick {message.author.global_name or message.author.name}!", style=discord.ButtonStyle.danger, emoji="🔨")
		async def callback(interaction: discord.Interaction):
			assert isinstance(message.author, discord.Member)
			await message.author.kick()
			await interaction.response.send_message(f"Kicked <@{message.author.id}>.", ephemeral=True)
		button.callback = callback
		view.add_item(button)

		await self.ALERTS_CHANNEL.send(embed=embed, view=view, allowed_mentions=discord.AllowedMentions.none())

	# Change a parameter of the event
	async def edit_event(self, message, new_params):
		incorrect = []
		correct = []
		for parameter in new_params.keys():
			try:
				self.param[parameter] = new_params[parameter]
				correct.append(parameter)
			except KeyError:
				incorrect.append(parameter)
		
		if len(correct) > 0:
			await message.channel.send(f"Successfully changed the parameters: {grammar_list(correct)}")
		if len(incorrect) > 0:
			await message.channel.send(f"The following parameters are invalid: {grammar_list(incorrect)}")
		
		return

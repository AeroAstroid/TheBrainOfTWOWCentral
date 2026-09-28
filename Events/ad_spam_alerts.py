from __future__ import annotations
from datetime import datetime, timedelta, timezone
import discord
from Config._functions import grammar_list
from Config._servers import MAIN_SERVER
import re


def msg_url(msg: discord.Message):
	return f"https://discord.com/channels/{msg.guild.id if msg.guild else "@me"}/{msg.channel.id}/{msg.id}"


class EVENT:

	def __init__(self):
		self.RUNNING = False
		self.param = {}

	def start(self, SERVER):
		self.SERVER = SERVER
		self.AD_CHANNEL: discord.TextChannel = MAIN_SERVER["ADVERTISEMENTS"]
		self.ALERTS_CHANNEL: discord.TextChannel = MAIN_SERVER["MOD_ALERTS"]
		self.ROLE_WHITELIST = [
			MAIN_SERVER["NOTABLE_HOST"]
		]
		self.param = {
			"CONSECUTIVE_AD_THRESHOLD": 5,
			"AD_GRACE_MIN": 60 * 2,
			"AD_COOLDOWN_MIN": 60 * 12,
		}
		self.RUNNING = True

	def end(self):
		self.RUNNING = False

	ad_counts: dict[int, int] = {}
	last_ad_times: dict[int, datetime] = {}
	last_ad_msgs: dict[int, discord.Message] = {}
	ad_too_fast_alert_times: dict[int, datetime] = {}

	async def on_message(self, message: discord.Message):
		URL_REGEX = r"(?:https?:\/\/[^\s<>\"'`]+)|(?:discord.gg\/\w+)"
		has_url = re.search(URL_REGEX, message.content)

		if message.channel.id == self.AD_CHANNEL.id and has_url:
			last_time = self.last_ad_times.get(message.author.id)
			if last_time:
				if datetime.now() - last_time < timedelta(minutes=self.param["AD_GRACE_MIN"]):
					return
				if datetime.now() - last_time < timedelta(minutes=self.param["AD_COOLDOWN_MIN"] - 15):
					await self.ad_too_fast_alert(self.last_ad_msgs[message.author.id], message)

			if isinstance(message.author, discord.Member):
				for role in self.ROLE_WHITELIST:
					if role in message.author.roles:
						self.ad_counts.pop(message.author.id, None)
						return
			self.last_ad_times[message.author.id] = datetime.now()
			self.ad_counts.setdefault(message.author.id, 0)
			if self.ad_counts[message.author.id] >= 0:
				self.ad_counts[message.author.id] += 1
				self.last_ad_msgs[message.author.id] = message

			if self.ad_counts[message.author.id] >= self.param["CONSECUTIVE_AD_THRESHOLD"]:
				await self.ad_spam_alert(message)
				self.ad_counts[message.author.id] = -1

		elif message.channel.id != self.AD_CHANNEL.id:
			self.ad_counts.pop(message.author.id, None)
	
	async def ad_too_fast_alert(self, prev_ad: discord.Message, new_ad: discord.Message):
		ALERT_COOLDOWN = timedelta(days=7)
		last_alert = self.ad_too_fast_alert_times.get(new_ad.author.id)
		if last_alert and datetime.now(tz=timezone.utc) - last_alert < ALERT_COOLDOWN:
			return
		self.ad_too_fast_alert_times[new_ad.author.id] = datetime.now(tz=timezone.utc)
		embed = discord.Embed()
		embed.set_author(name="⏳ Ads too fast", icon_url=new_ad.author.avatar and new_ad.author.avatar.url)
		delta = round((new_ad.created_at - prev_ad.created_at).total_seconds() / (60 * 60), 1)
		desc = f"<@{new_ad.author.id}> sent two ads {delta} hours apart:"
		desc += f"\n- {msg_url(prev_ad)}"
		desc += f"\n- {msg_url(new_ad)}"
		embed.description = desc
		await self.ALERTS_CHANNEL.send(embed=embed, allowed_mentions=discord.AllowedMentions.none())
	
	async def ad_spam_alert(self, message: discord.Message):
		embed = discord.Embed()
		embed.set_author(name=f"📢 Ad spam alert", icon_url=message.author.avatar and message.author.avatar.url)
		desc = f"<@{message.author.id}> sent **{self.param['CONSECUTIVE_AD_THRESHOLD']} ads** with no other messages in the server."
		desc += f"\nLatest ad: {msg_url(message)}"
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

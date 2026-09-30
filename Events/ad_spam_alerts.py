from __future__ import annotations
from datetime import datetime, timedelta
from typing import NamedTuple
import re
import discord
from Config._db import Database
from Config._functions import grammar_list
from Config._servers import MAIN_SERVER


class AdEntry(NamedTuple):
    id: str
    adcount: int
    lasttime: int
    lastid: str
    lastalert: int


def msg_url(msg: discord.Message):
	return f"https://discord.com/channels/{msg.guild.id if msg.guild else '@me'}/{msg.channel.id}/{msg.id}"


class EVENT:
	# Cmd to initialize db table:
	# tc/db add tcadvertisements id-text adcount-integer lasttime-integer lastid-text lastalert-integer
	db = Database()

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
		self.advertisers_cache: set[int] = { int(row[0]) for row in self.db.get_entries("tcadvertisements") if row[1] > 0 }
		self.RUNNING = True

	def end(self):
		self.RUNNING = False
	
	advertisers_cache: set[int]

	def get_entry(self, user_id: int) -> AdEntry | None:
		rows = self.db.get_entries("tcadvertisements", conditions={"id": str(user_id)})
		return AdEntry(*rows[0]) if rows else None

	def set_entry(self, user_id: int, **columns: str | int):
		self.db.edit_entry("tcadvertisements", entry=columns, conditions={"id": str(user_id)})

	async def on_message(self, message: discord.Message):
		URL_REGEX = r"(?:https?:\/\/[^\s<>\"'`]+)|(?:discord.gg\/\w+)"
		has_url = re.search(URL_REGEX, message.content)

		if message.channel.id == self.AD_CHANNEL.id and has_url:
			stored = self.get_entry(message.author.id)
			entry = stored or AdEntry(str(message.author.id), 0, 0, "", 0)
			last_time = datetime.fromtimestamp(entry.lasttime) if entry.lasttime else None
			if last_time:
				if datetime.now() - last_time < timedelta(minutes=self.param["AD_GRACE_MIN"]):
					return
				if datetime.now() - last_time < timedelta(minutes=self.param["AD_COOLDOWN_MIN"] - 15):
					await self.ad_too_fast_alert(entry, message)

			if isinstance(message.author, discord.Member):
				for role in self.ROLE_WHITELIST:
					if role in message.author.roles:
						return

			ad_count, last_id = entry.adcount, entry.lastid
			ad_count += 1
			last_id = str(message.id)

			if ad_count >= self.param["CONSECUTIVE_AD_THRESHOLD"]:
				await self.ad_spam_alert(message)
				ad_count = -15

			new_time = int(datetime.now().timestamp())
			if stored:
				self.set_entry(message.author.id, adcount=ad_count, lasttime=new_time, lastid=last_id)
			else:
				self.db.add_entry("tcadvertisements", [str(message.author.id), ad_count, new_time, last_id, 0])
			if ad_count > 0:
				self.advertisers_cache.add(message.author.id)

		elif message.channel.id != self.AD_CHANNEL.id and message.author.id in self.advertisers_cache:
			self.set_entry(message.author.id, adcount=0)
			self.advertisers_cache.discard(message.author.id)
	
	async def ad_too_fast_alert(self, entry: AdEntry, new_ad: discord.Message):
		# ALERT_COOLDOWN = timedelta(days=7)
		# last_alert = datetime.fromtimestamp(entry.lastalert) if entry.lastalert else None
		# if last_alert and datetime.now() - last_alert < ALERT_COOLDOWN:
		# 	return
		# self.set_entry(message.author.id, lastalert=int(datetime.now().timestamp()))

		prev_ad = None
		if entry.lastid:
			try:
				prev_ad = await self.AD_CHANNEL.fetch_message(int(entry.lastid))
			except (discord.DiscordException, ValueError):
				pass

		embed = discord.Embed()
		embed.set_author(name="⏳ Ads too fast", icon_url=new_ad.author.avatar and new_ad.author.avatar.url)
		if prev_ad:
			delta = round((new_ad.created_at - prev_ad.created_at).total_seconds() / (60 * 60), 1)
		else:
			delta = f"less than {self.param['AD_COOLDOWN_MIN'] // 60}"
		desc = f"<@{new_ad.author.id}> sent two ads {delta} hours apart:"
		if prev_ad:
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
			await interaction.response.send_message(f"Kicked <@{message.author.id}>!", ephemeral=True)
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

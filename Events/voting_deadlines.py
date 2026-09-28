from __future__ import annotations
import asyncio
from datetime import datetime, timedelta, timezone
import discord
from Config._const import BRAIN
from Config._functions import grammar_list
from Config._servers import MAIN_SERVER
import re


class EVENT:

	def __init__(self):
		self.RUNNING = False
		self.param = {}

	def start(self, SERVER):
		self.SERVER: discord.Guild = SERVER
		self.CHANNEL: discord.TextChannel = MAIN_SERVER["VOTING"]
		self.param = {
			"REACTION_EMOJI": "⏰",
			"GRACE_HOURS": 24,
		}
		self.RUNNING = True

		asyncio.create_task(self.load_votings())

	def end(self):
		self.RUNNING = False

	votings: dict[int, datetime] = {}
	expired_votings: set[int] = set()

	async def on_one_hour(self):
		await self.check_expired_votings()
	
	async def check_expired_votings(self):
		now = datetime.now(tz=timezone.utc)
		expired = set()
		for msg_id, expiry_time in self.votings.items():
			if expiry_time < now:
				expired.add(msg_id)
		for msg_id in expired:
			self.expired_votings.add(msg_id)
			expiry_time = self.votings.pop(msg_id)
			msg: discord.Message = await self.CHANNEL.fetch_message(msg_id)
			await msg.add_reaction(self.param["REACTION_EMOJI"])

	async def load_votings(self):
		async for msg in self.CHANNEL.history():
			await self.scan_voting_msg(msg)
	
	async def on_message(self, message: discord.Message):
		await self.scan_voting_msg(message)
	
	async def on_raw_message_edit(self, payload: discord.RawMessageUpdateEvent):
		content = payload.data.get("content")
		if payload.channel_id != self.CHANNEL.id or not content:
			return
		message = await self.CHANNEL.fetch_message(payload.message_id)
		await self.scan_voting_msg(message)

	async def on_raw_reaction_add(self, payload: discord.RawReactionActionEvent):
		if (
			payload.message_id not in self.expired_votings
			or payload.channel_id != self.CHANNEL.id
			or payload.emoji.name != self.param["REACTION_EMOJI"]
		):
			return
		member = payload.member or await self.SERVER.fetch_member(payload.user_id)
		if member.bot or not self.CHANNEL.permissions_for(member).manage_messages:
			return
		msg: discord.Message = await self.CHANNEL.fetch_message(payload.message_id)
		await msg.delete()
	
	async def scan_voting_msg(self, msg: discord.Message):
		if msg.author.bot or msg.channel.id != self.CHANNEL.id:
			return

		TIMESTAMP_REGEX = r"<t:(\d+)(?::\w)?>"
		matches = re.findall(TIMESTAMP_REGEX, msg.content)
		if not matches:
			return

		timestamps = [datetime.fromtimestamp(int(s), tz=timezone.utc) for s in matches]
		deadline = max(timestamps)
		self.votings[msg.id] = deadline + timedelta(hours=self.param["GRACE_HOURS"])
		await self.check_expired_votings()

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

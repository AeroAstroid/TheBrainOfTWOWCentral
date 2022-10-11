from Helper.__comp import *
from Helper.__words import WORDS
from Helper.__functions import m_line, command_user, command_response_timestamp
import random

MIN_WORDS = 45
MAX_WORDS = 61

def setup(BOT):
	BOT.add_cog(Typingtest(BOT))

class Typingtest(cmd.Cog):
	'''
	[Write help description here!]
	'''

	# Extra arguments to be passed to the command
	FORMAT = "`[]`"
	CATEGORY = "BRAIN"
	EMOJI = CATEGORIES[CATEGORY]
	ALIASES = ['typetest', 'tt']

	def __init__(self, BRAIN):
		self.BRAIN = BRAIN

	@bridge.bridge_command(aliases=ALIASES)
	@cmd.cooldown(1, 1)
	async def typingtest(self, ctx,
		):

		user = command_user(ctx)

		# Command code
		to_type = " ".join(random.sample(WORDS, random.randint(MIN_WORDS, MAX_WORDS))) # creates list of words
		target_words = to_type.split(' ')
		count = len(target_words)

		# Adding zero - width spaces between words to prevent copy+paste
		spaced_text = ""
		for i in range(len(to_type)):
			spaced_text += to_type[i]
			if to_type[i] == " ":
				spaced_text += "\u200b"

		tt = await ctx.respond(f"**{user.mention} Type these {count} words in any order:**\n\n{spaced_text}")

		start_timestamp = await command_response_timestamp(ctx, tt)

		msg = await self.BRAIN.wait_for('message', check=(lambda m: m.channel == tt.channel and m.author == user))
		
		typed_words = msg.content.lower().split(' ')
		duration = round(msg.created_at.timestamp() - start_timestamp, 3)

		# Counting total successful characters typed
		success = 0
		chars = 0
		for word in typed_words:
			if word in target_words:
				success += 1
				chars += len(word) + 1
				target_words.remove(word)
		chars += -1
		wpm = chars / len(to_type) * chars / duration * 12 # WPM = CPM / 5
		if success < 10 or len(typed_words) > count + 10:
			await msg.reply("Typing test cancelled.") # cancel if there was no attempt
			return
		elif wpm >= 200:
			await msg.reply(f"Don't you think it's a bit obvious, with you going at {round(wpm, 2)} wpm?") # wr is generally said to be 216
			return
		else:
			# ^n is used because I want \n in the message but the dark-formatted string replaces \n with nothing
			await msg.reply(m_line(
				f"""**{user.mention} Typing test finished!**/n//n/
				Words typed correctly: {success} out of {count} ({round(100*(success/count), 1)}%)/n/
				Time: {duration}/n/
				WPM: **{round(wpm, 2)}**"""
			))

		return
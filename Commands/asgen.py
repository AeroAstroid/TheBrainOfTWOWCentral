from Config._const import BRAIN
from Config._asgen_functions import generate_all_slides, generate_slide_compilation
import discord
import csv
from PIL import Image

def HELP(PREFIX):
	return {
		"COOLDOWN": 1,
		"MAIN": "t",
		"FORMAT": "(command)",
		"CHANNEL": 0,
		"USAGE": f"""t
		t""".replace("\n", "").replace("\t", ""),
		"CATEGORY" : "Utility"
	}

PERMS = 2 # Staff
ALIASES = ["artshowdown"]
REQ = []

current_slides = []

async def MAIN(message, args, level, perms, SERVER):
	
	if level == 1:
		await message.channel.send("Include a subcommand!")
		return
	
	if args[0].lower() == "genround":
		# Generate images displaying the art for the round

		# Check if TSV is attached
		attachment = message.attachments[0]

		# Check if attachment is actually a TSV file
		attachment_url = attachment.url
			
		# This is a TSV file, now attempt to read it and if any errors come up just return
		try:

			# Save the attachment
			await attachment.save("art_showdown_round.tsv")

			# Read TSV and get round leaderboard
			round_leaderboard = []
			with open("art_showdown_round", 'r', encoding='UTF-8') as lb_file:

				reader = csv.reader(lb_file, delimiter="\t")

				for row in list(reader):

					# Check if there isn't a name in the first
					try:
						name = row[0]
						if name == "":
							continue
					except IndexError:
						continue

					# Add contestant to the round leaderboard list
					round_leaderboard.append(row)

			# Remove column titles
			round_leaderboard.pop(0)

			await message.channel.send(f"Generating {len(round_leaderboard)} art displays...")

			# Generate images
			slides, time = generate_all_slides(round_leaderboard, {}, Image.open("Images/asgen/rankgradient.png").convert("RGBA"))
			current_slides = slides

			await message.channel.send(f"Generated {len(slides)} in {time:.2f} seconds!")

			# Post first four
			slide_img = generate_slide_compilation(slides[:4])
			slide_img.save("Images/asgen/as_compilation.png")

			await message.channel.send("", file=discord.File("Images/asgen/as_compilation.png"))

		except Exception as e: 
			
			print(e)
			await message.channel.send(f"Error occured while generating slides!")
			return


	elif args[1].lower() == "postround":
		pass

	elif args[1].lower() == "genscoreboard":
		pass

	
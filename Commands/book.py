import os, discord
from Config._functions import make_book
from PIL import Image

def HELP(PREFIX):
	return {
		"COOLDOWN": 5,
		"MAIN": "Generate a booksona with the given name",
		"FORMAT": "",
		"CHANNEL": 0,
		"USAGE": f"""Using `{PREFIX}book` will generate a booksona image with colors taking into account the first 
		two letters of the name provided, as is customary for TWOW books.""".replace("\n", "").replace("\t", ""),
		"CATEGORY" : "Utility"
	}

PERMS = 1 # Non-members
ALIASES = []
REQ = []

async def MAIN(message, args, level, perms, SERVER):
	if level == 1:
		await message.channel.send("Provide a name to make a book with!")
		return
	
	book_names = " ".join(args[1:]).splitlines()

	if perms == 3:
		link_list = [[]]
		for book in book_names:
			book_image = make_book(book[:2])
			book_image.save(f"Images/Book/{book[:2]}.png")
			book_msg = await message.channel.send(f"**{book}**", file=discord.File(f"Images/Book/{book[:2]}.png"))

			if len("\n".join(link_list[-1])) + len(f"<{book_msg.attachments[0].url}>") > 1800:
				link_list.append([])
			link_list[-1].append(f"<{book_msg.attachments[0].url}>")

			os.remove(f"Images/Book/{book[:2]}.png")
		
		for z in link_list:
			await message.channel.send("\n".join(z))
	else:
		book_image = make_book(book_names[0][:2])
		book_image.save(f"Images/Book/{book_names[0][:2]}.png")
		await message.channel.send(f"**{book_names[0]}**", file=discord.File(f"Images/Book/{book_names[0][:2]}.png"))
		os.remove(f"Images/Book/{book_names[0][:2]}.png")

	return

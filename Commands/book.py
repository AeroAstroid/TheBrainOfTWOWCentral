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
		two letters of the name provided, as is customary for TWOW books.""".replace("\n", "").replace("\t", "")
	}

PERMS = 1 # Non-members
ALIASES = [""]
REQ = []

async def MAIN(message, args, level, perms, SERVER):
	if level == 1:
		await message.channel.send("Provide a name to make a book with!")
		return
	
	book_names = " ".join(args[1:]).splitlines()

	if perms == 3:
		for book in book_names:
			book_image = make_book(book[:2])
			book_image.save(f"Images/Book/{book[:2]}.png")
			await message.channel.send(f"**{book}**", file=discord.File(f"Images/Book/{book[:2]}.png"))
			os.remove(f"Images/Book/{book[:2]}.png")
	else:
		book_image = make_book(book[0][:2])
		book_image.save(f"Images/Book/{book[0][:2]}.png")
		await message.channel.send(f"**{book[0]}**", file=discord.File(f"Images/Book/{book[0][:2]}.png"))
		os.remove(f"Images/Book/{book[0][:2]}.png")

	return
import numpy as np
import os, discord, random, asyncio, math
from PIL import Image, ImageDraw, ImageFilter
from Config._functions import grammar_list

def HELP(PREFIX):
	return {
		"COOLDOWN": 5,
		"MAIN": "Generate a tr_ of random length and compare it to other objects",
		"FORMAT": "",
		"CHANNEL": 0,
		"USAGE": f"""Using `{PREFIX}tr_` will generate a tr_ of random length and draw it accordingly, while also 
		providing a scale reference in the form of an object or organism.""".replace("\n", "").replace("\t", ""),
		"CATEGORY" : "Fun"
	}

PERMS = 0 # Non-members
ALIASES = ["TR_"]
REQ = []

def to_nat(a):
	return max(1,int(a))

async def MAIN(message, args, level, perms, SERVER):
	if level != 1:
		if args[1].lower() == "queue" and perms == 2:
			await message.channel.send(open("Config/_image_gen.txt", "r").read())
			return
	
	tr_gen = open("Config/_image_gen.txt", "r").read()
	tr_gen += f" {message.id}"
	open("Config/_image_gen.txt", "w").write(tr_gen.strip())

	while not open("Config/_image_gen.txt", "r").read().startswith(str(message.id)):
		await asyncio.sleep(.1)

	pixel_count = 250 * np.power(10, np.power(np.e, random.uniform(0, 2.5)) - 1)
	image_pixels = 490 + 115 + pixel_count
	height = (0.2 / 860) * image_pixels

	await asyncio.sleep(min(8, 0.6*np.log(height)/2.5))

	if height > 10:
		image_pixels = 10 / (0.2 / 860)
		pixel_count = image_pixels - 115 - 490

	image_size = 2000
	ratio = image_size / image_pixels
	
	top = Image.open("Images/tr_ top.png").convert("RGBA")
	face = Image.open("Images/tr_ face.png").convert("RGBA")
	grad = Image.open("Images/tr_ gradient.png").convert("RGBA")
	bottom = Image.open("Images/tr_ bottom.png").convert("RGBA")

	top = top.resize((to_nat(top.size[0] * ratio), to_nat(top.size[1] * ratio)), Image.LANCZOS)
	bottom = bottom.resize((to_nat(bottom.size[0] * ratio), to_nat(bottom.size[1] * ratio)), Image.LANCZOS)	
	face = face.resize((to_nat(face.size[0] * ratio), to_nat(face.size[1] * ratio)), Image.LANCZOS)

	tr_base = Image.new("RGBA", (to_nat(1440 * ratio), image_size), (0, 0, 0, 0))
	tr_base.paste(top, (0, 0))
	grad = grad.resize((to_nat(1440 * ratio), to_nat(pixel_count * ratio)), Image.LANCZOS)
	tr_base.alpha_composite(grad, (0, int(115 * ratio)))
	tr_base.alpha_composite(bottom, (0, int(ratio * (image_pixels-611))-2))

	face_position = min(309, 
		int(image_pixels/2) - 312)
	
	tr_base.alpha_composite(face, (0, int(face_position*ratio)))

	image_size = 250
	ratio = image_size / image_pixels
	tr_base = tr_base.resize((to_nat(1440 * ratio), image_size), Image.LANCZOS)
		
	w = tr_base.size[0]
	h = tr_base.size[1]

	center_w = max(min(150, 150 / np.sqrt(height)), 35)

	to_post = Image.open("Images/tr_ background.png").convert("RGBA")
	to_post.paste(tr_base, (int(center_w - w/2), 290 - h), mask=tr_base)

	scale_objects = {
		"Tesla Cybertruck": 1.9,
		"Elephant": 3.2,
		"Basketball": 0.23,
		"Human Hand": 0.19,
		"Apple Pro Stand": 0.45,
		"Hummingbird": 0.1,
		"Robert Wadlow": 2.72,
		"Blue Whale": 4.5,
		"Bonsai Tree": 0.8,
		"Four Year Old Child": 1.1,
		"Aegislash": 1.7,
		"Purplegaze": 1.78,
		"Medium Dog House": 0.65,
		"Hedgehog": 0.12,
		"Pine Tree": 15,
		"All Diary of a Wimpy Kid Books Stacked on Top of Each Other": 0.3543,
		"Brazil": 4292000,
		"Earth": 12742000,
		"Empire State Building": 441,
		"Neutron Star": 10000,
		"The Three Pyramids of Giza Stacked on Top of Each Other": 348.1,
		"Giratina Origin Form": 6.9,
		"Eiffel Tower": 324,
		"Christ the Redeemer": 38,
		"Jupiter": 139822000,
		"Saturn's Rings": 357864000,
		"Mount Everest": 8848,
		"Hiroshima Mushroom Cloud": 18288,
		"Shimizu Mega-City Pyramid": 2000,
		"Kármán Line": 100000,
		"Birthday Cake": 0.11,
		"Regular Book": 0.3043,
		"The Sun": 1391000000,
		"Sirius": 2383470000,
		"Pollux": 12610000000,
		"Swartzchild Radius of Sagittarius A*": 25380000000
		"Polaris": 64380100000,
		"Cygnus OB2-12": 342300000000,
		"Betelgeuse": 1060000000000,
		"RSGC1-F01": 2129000000000,
		"The Solar System": 8996837420000
	}

	current_w = center_w * 1.65

	pixels_per_height = 250 / height

	references = []
	for scale in scale_objects.keys():
		scale_name = scale.replace("*","")
		if 0.2 * height < scale_objects[scale] < 1.15 * height:
			img = Image.open(f"Images/{scale_name}.png").convert("RGBA")
			ratio = (pixels_per_height * scale_objects[scale]) / img.height
			img = img.resize((int(img.width * ratio), int(img.height * ratio)))

			references.append([scale, img, img.width, img.height])
	
	to_scale = []

	while True:
		possible_ref = []

		for ref in references:
			if ref[2] + current_w <= 790:
				possible_ref.append(ref)
		
		if len(possible_ref) == 0:
			break

		ref = random.choice(possible_ref)

		to_post.paste(ref[1], (int(current_w), 290 - ref[3]), mask=ref[1])
		current_w += ref[2] + 35

		prefix = ""
		if scale_objects[ref[0]] > 1000:
			scale_objects[ref[0]] = scale_objects[ref[0]] / 1000
			prefix = "k"
		
		to_scale.append(f"**`{ref[0]}`** ({scale_objects[ref[0]]}{prefix}m tall)")
		references.remove(ref)

	if len(to_scale) != 0:
		to_scale = "To scale: " + grammar_list(to_scale)
	else:
		to_scale = ""

	to_post.save("Images/generated tr_.png")

	width_note = ""
	if height >= 10:
		width_note = "*(tr_ width not to scale)*"

	prefix = ""
	if height > 1000:
		height = height / 1000
		prefix = "k"
	await message.channel.send(
	f"""**<@{message.author.id}>, your generated tr_ is {round(height, 4)}{prefix}m tall!**
	{width_note}
	{to_scale}""".replace("\t", ""), file=discord.File("Images/generated tr_.png"))

	os.remove("Images/generated tr_.png")

	try:
		tr_gen = open("Config/_image_gen.txt", "r").read().split(" ")
		tr_gen.remove(str(message.id))
		open("Config/_image_gen.txt", "w").write(" ".join(tr_gen).strip())
	except ValueError:
		pass
	return

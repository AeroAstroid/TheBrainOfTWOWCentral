import os, discord

from PIL import Image, ImageDraw
import time

# Importing from const file
from Config._gl_img_const import *

PERMS = 3
ALIASES = []
REQ = []

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

def generate_image(midmove = False):

	# Calculating square sizes
	# Amount of space that can be taken up by the white squares
	square_space = GRID_MAX_WIDTH - (GRID_SIZE[0] - 1) * LINE_WIDTH
	square_size = round(square_space / GRID_SIZE[0])

	# Create image
	img = Image.new("RGBA", (IMAGE_WIDTH, IMAGE_HEIGHT), BACKGROUND_COLOR)
	img_draw = ImageDraw.Draw(img)

	# Calculating total grid bounding box
	total_grid_bound_x = square_size * GRID_SIZE[0] + LINE_WIDTH * (GRID_SIZE[0] - 1)
	total_grid_bound_y = square_size * GRID_SIZE[1] + LINE_WIDTH * (GRID_SIZE[1] - 1)

	# Draw the grid
	grid_left_x = GRID_CENTER[0] - round(total_grid_bound_x / 2)
	grid_top_y = GRID_CENTER[1] - round(total_grid_bound_y / 2)

	grid_right_x = GRID_CENTER[0] + round(total_grid_bound_x / 2)
	grid_bottom_y = GRID_CENTER[1] + round(total_grid_bound_y / 2)

	for row in range(GRID_SIZE[1]):
		for column in range(GRID_SIZE[0]):
			# Draw square
			x_left = grid_left_x + (square_size + LINE_WIDTH) * column
			x_right = grid_left_x + (LINE_WIDTH * column) + (square_size * (column + 1)) - 1
			y_top = grid_top_y + (square_size + LINE_WIDTH) * row
			y_bottom = grid_top_y + (LINE_WIDTH * row) + (square_size * (row + 1)) - 1

			rectangle_box = (x_left, y_top, x_right, y_bottom)
			img_draw.rectangle(rectangle_box, (255, 255, 255, 255))
		
	# Draw the text (A, B, 1, 2) on the end of the rows and columns
	for column in range(GRID_SIZE[0]):

		symbol = COLUMN_SYMBOLS[column]

		# X coordinate to draw both symbols on top and bottom -- this is the center of the text
		txt_x = grid_left_x + round((column + 0.5) * square_size) + LINE_WIDTH * column

		# Draw text on top
		txt_y = grid_top_y - COLUMN_TEXT_OFFSET
		img_draw.text((txt_x, txt_y), symbol, fill = (255, 255, 255, 255), font = ROW_COLUMN_FONT, anchor = "ms")

		# Draw text on bottom
		txt_y = grid_bottom_y + COLUMN_TEXT_OFFSET
		img_draw.text((txt_x, txt_y), symbol, fill = (255, 255, 255, 255), font = ROW_COLUMN_FONT, anchor = "mt")
		

	for row in range(GRID_SIZE[1]):
		
		symbol = ROW_SYMBOLS[row]

		# Y coordinate to draw both symbols on top and bottom -- this is the center of the text
		txt_y = grid_top_y + round((row + 0.5) * square_size) + LINE_WIDTH * row

		# Draw text on left
		txt_x = grid_left_x - ROW_TEXT_OFFSET
		img_draw.text((txt_x, txt_y), symbol, fill = (255, 255, 255, 255), font = ROW_COLUMN_FONT, anchor = "mm")

		# Draw text on right
		txt_x = grid_right_x + ROW_TEXT_OFFSET
		img_draw.text((txt_x, txt_y), symbol, fill = (255, 255, 255, 255), font = ROW_COLUMN_FONT, anchor = "mm")
	
	return img

async def MAIN(message, args, level, perms, SERVER):
	
	# Record start time
	start_time = time.time()

	tag = str(time.time()).split(".")[1]
	image = generate_image()
	image.save(f"Images/gl_img_{tag}.png")

	# Record end time
	end_time = time.time()

	await message.channel.send("Image generated in **{:.2f}s**!".format(end_time - start_time), # Send the image
			file=discord.File(f"Images/gl_img_{tag}.png"))
	
	os.remove(f"Images/gl_img_{tag}.png") # Then promptly delete it

	return

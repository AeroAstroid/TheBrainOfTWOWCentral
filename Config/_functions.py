import numpy as np
import random, string, re
from PIL import Image, ImageFont, ImageDraw, ImageChops

try:
	from Config._const import ALPHABET, OPTION_DESC, ORIGINAL_DECK
except ModuleNotFoundError:
	from _const import ALPHABET, OPTION_DESC, ORIGINAL_DECK

def alt_font(z): return ImageFont.truetype("Fonts/ARIALUNI.TTF", z)
def default(z): return ImageFont.truetype("Fonts/RobotoCondensed-Regular.ttf", z)
def font_italic(z): return ImageFont.truetype("Fonts/RobotoCondensed-Italic.ttf", z)
def font_bold(z): return ImageFont.truetype("Fonts/RobotoCondensed-Bold.ttf", z)
def font_boltalic(z): return ImageFont.truetype("Fonts/RobotoCondensed-BoldItalic.ttf", z)

# m_line : Command to parse multiline strings within the code more nicely
def m_line(line):
	return line.replace("\t", "").replace("\n\n", "/n/n").replace("\n", "").replace("/n", "\n")

# grammar_list : Simple function to properly list many strings
def grammar_list(listed, c_or=False):
	conjunction = f', {"or" if c_or else "and"} '

	if len(listed) > 2:
		first_list = ", ".join(listed[:-1])
		listed = first_list + conjunction + str(listed[-1])
	elif len(listed) == 2:
		listed = " and ".join(listed)
	elif len(listed) == 1:
		listed = "".join(listed)
	else:
		listed = "none"
	return listed


# make_letter_tint : Returns a color for a book depending on the letter
def make_letter_tint(char):
    char = char.upper()
    charcode = ord(char)
    if char >= "0" and char <= "9":
        hue1 = (charcode - ord("0")) / 10
    else:
        hue1 = (charcode - ord("A")) / 26 % 1
    hue360 = hue1 * 255
    return tuple((int(hue360), 153, 255))


# make_book : Generates a book image for a given contestant name
def make_book(name):
    if len(name) < 2:
        name += name

    left = Image.open("Images/Book/left.png").convert("RGBA")
    right = Image.open("Images/Book/right.png").convert("RGBA")
    face = Image.open("Images/Book/face.png").convert("RGBA")

    left = ImageChops.multiply(
        left, Image.new("HSV", left.size, make_letter_tint(name[0])).convert("RGBA")
    )
    right = ImageChops.multiply(
        right, Image.new("HSV", right.size, make_letter_tint(name[1])).convert("RGBA")
    )

    left.paste(right, (0, 0), right)
    left.paste(face, (0, 0), face)

    return left


# word_count : Returns a response's word count
def word_count(response):
	words = 0
	for piece in response.split(" "):
		for character in piece:
			if character.isalnum():
				words += 1
				break
	return words


# elim_prize : Returns how many contestants should prize and be eliminated (based on Dark's formulas)
def elim_prize(count, elim_rate=0.2):
	numbers = []

	if count == 2:
		numbers.append(1)
	else:
		numbers.append(round(count * elim_rate))
	
	numbers.append(np.floor(np.sqrt(count) * np.log(count) / 3.75))
	return numbers


# formatting_fix : Fixes weirdly formatted lines that might cause formatting problems
def formatting_fix(line):
	format_types = ["||", "~~", "__", "***", "**", "*", "_"]

	for r in format_types:
		if line.count(r) % 2 == 1:
			line = line.replace(r, "")
	
	return line


# is_whole : Detects integers
def is_whole(s):
	try:
		es = int(s)
		es2 = float(s)
		if es2 - es == 0:
			return True
		else:
			return False
	except:
		return False


# is_float : Detect numbers that have decimal components
def is_float(s):
	try:
		es = int(s)
		es2 = float(s)
		if es2 - es != 0:
			return True
		else:
			return False
	except:
		try:
			es2 = float(s)
			return True
		except:
			return False


# is_number : Simple detection for numbers
def is_number(s):
	try: float(s)
	except: return False
	return True


# key_generator : Generates a random alphanumeric string with variable length
def key_generator(n):
	return ''.join(random.SystemRandom().choice(string.ascii_uppercase + string.digits) for _ in range(n))


# number_key : Generates a random numeric string with variable length
def number_key(n):
	return ''.join(random.SystemRandom().choice(string.digits) for _ in range(n))


# strip_alpha : Strip a string to only alphabet characters
def strip_alpha(string, spaces=False):
	if spaces:
		return ''.join([x for x in list(string) if x.upper() in ALPHABET[:26] or x == " "])
	return ''.join([x for x in list(string) if x.upper() in ALPHABET[:26]])


# find_all : Find all instances of a substring in a string, even overlapping ones
def find_all(a_str, sub):
	start = 0

	while True:
		start = a_str.find(sub, start)
		if start == -1: return
		yield start
		start += 1


# find_multi : Find all instances of multiple substrings in a string
def find_multi(a_str, sstrlist):
	encounters = {}

	for sub in sstrlist:
		encounters[sub] = []
		start = 0

		while True:
			start = a_str.find(sub, start)
			if start == -1: break
			encounters[sub].append(start)
			start += 1

	return encounters

# overlap_match : Match a regex to a string and count how many times it matches
def match_count(pattern, search_string):
	total = 0
	start = 0
	there = re.compile(pattern)
	while True:
		mo = there.search(search_string, start)
		if mo is None: return total
		total += 1
		start = 1 + mo.start()

# strip_front : Removes all leading whitespace characters
def strip_front(string):
	return re.sub(r"^\s+", "", string, flags=re.UNICODE)

# uno_image : Handler for image generation for the UNO command
def uno_image(b_type, tag, PREFIX, hand=None, last=None, draw_c=None, name=None, config=None):
	background = Image.open("Images/Uno/Background.png") # Start with the background image
	draw = ImageDraw.Draw(background)

	if b_type in [0, 2]: # 0 or 2 displays a hand
		hand_size = len(hand) # Take the hand size and calculate its horizontal pixel length
		hand_range = ((hand_size - 1) * 90 * (0.95 ** hand_size)) if hand_size < 10 else 550

		for card in range(len(hand)): # Draw each card on the image. First, load the card and resize it properly
			card_image = Image.open("Images/Uno/{}.png".format(hand[card])).convert('RGBA').resize((119, 190))

			# Calculate the x coordinate for this card
			x_coord = (600 - hand_range) + hand_range * 2 * ((card / (hand_size - 1)) if hand_size != 1 else 0)
			sin_mod = np.sin(np.deg2rad(3 * x_coord / 20)) # Depending on the x coordinate it's lower down
			y_coord = 705 - 95 * sin_mod # Calculate the y coordinate

			angle = (np.rad2deg(np.arcsin(sin_mod)) - 90) / 3 # The x coordinate also affects angles

			card_image = card_image.rotate(angle if x_coord >= 600 else -angle, expand=1) # Rotate the card

			background.paste(card_image, # Paste the card in at the proper position
			(int(round(x_coord - card_image.width / 2)), int(round(y_coord - card_image.height / 2))),
			card_image)

			size_t = draw.textsize(str(card + 1), font_bold(40)) # Draw the card code above the card
			draw.text((x_coord - size_t[0] / 2, y_coord - 150), str(card + 1), (255, 255, 255), font_bold(40))
		
		# Paste the last card played
		last_played = Image.open("Images/Uno/{}.png".format(last)).convert('RGBA').resize((210, 337))
		background.paste(last_played, (495, 106), last_played)
	
		if b_type == 0: # Depending on the type, the text varies
			texty = f"""It's your turn! Use the [{PREFIX}uno play] command to play a card.
			Use [{PREFIX}uno play draw] to draw cards!""".replace("\t", "")
		else:
			texty = "This is your hand!"

		size_t = draw.textsize(texty, font_bold(40)) # Draw the text, centered
		draw.text((600 - size_t[0] / 2, 10),
		texty,
		(255, 255, 255),
		font_bold(40))
	
	if b_type in [1, 3]: # 1 and 3 are images containing just the last card - they're shared publicly
		# Paste the last card playeds
		last_played = Image.open("Images/Uno/{}.png".format(last)).convert('RGBA').resize((306, 490))
		background.paste(last_played, (447, 180), last_played)

		if b_type == 1:
			texty = f"It's {name}'s turn to play a card!"
		else:
			texty = f"{name} WINS THE GAME!"

		size_t = draw.textsize(texty, font_bold(50)) # Draw the text, centered
		draw.text((600 - size_t[0] / 2, 25),
		texty,
		(255, 255, 255),
		font_bold(50))
	
	if b_type == 4: # 4 is the config menu

		for option in range(len(config)): # Depending on the index of the option
			x_c = 50 + 580 * (option // 8) # Draw it at different x and y coordinates
			y_c = 130 + 85 * (option % 8)

			if type(list(config.values())[option]) is int: # If this setting is an integer, do the int visualization
				draw.ellipse((x_c + 20, y_c + 20, x_c + 50, y_c + 50), fill='white')

				for z in range(list(config.values())[option]): # Draw a number of lines corresponding to the int
					angle = 2 * np.pi / list(config.values())[option] * z
					draw.line((x_c + 35, y_c + 35, x_c + 35 * np.cos(angle) + 35, y_c + 35 * np.sin(angle) + 35),
					fill=(255, 255, 255), width=3)
				
				n_color = (0, 0, 0)

			else: # If it's a boolean, it's either a black or white circle
				draw.ellipse((x_c, y_c, x_c + 70, y_c + 70), fill='white')

				if not list(config.values())[option]:
					draw.ellipse((x_c + 2, y_c + 2, x_c + 66, y_c + 66), fill='black')
					n_color = (255, 255, 255)

				else:
					n_color = (0, 0, 0)

			draw.text((x_c + 90, y_c + 15),
			OPTION_DESC[list(config.keys())[option]].replace("$", str(list(config.values())[option])),
			(255, 255, 255), font_bold(30))
			x_size = draw.textsize(str(option + 1), font_bold(30))[0]
			draw.text((x_c - x_size / 2 + 35, y_c + 15), str(option + 1), n_color, font_bold(30))

		instruc = """The round host can change any of these options with [{PREFIX}uno config x y], 
		x being the option number, y being any complement necessary.""".replace("\n", "").replace("\t", "")
		x_size = draw.textsize(instruc, font_bold(30))[0]
		draw.text((600 - x_size / 2, 15), instruc, (255, 255, 255), font_bold(30))

	# Save the image with the tag provided
	background.save(f"Images/current_card_image_{tag}.png")
	return

# uno_skip : Sets the uno_info dict to normal
def uno_skip():
	uno_info = {
		"running": False,
		"status": 0,
		"players": [],
		"order": [],
		"hands": [],
		"host": 0,
		"current": 0,
		"deck": ORIGINAL_DECK,
		"last_card": "00",
		"carryover": 0,
		"channel": 0,
		"config": {"0-7": False, "d-skip": True, "start": 7, "no-cards": True}
	}
	return uno_info

# smart_lookup : Integrated lookup function that can look for substrings and altered case
def smart_lookup(needle, haystack, case_ins=True, startofstr=True, substr=True):
	if needle in haystack:
		return [haystack.index(needle), needle]
	
	if case_ins:
		l_needle = needle.lower()
		l_haystack = [hay.lower() for hay in haystack]

		if l_needle in l_haystack:
			l_ind = l_haystack.index(l_needle)
			return [l_ind, haystack[l_ind]]
	
	if startofstr:
		s_haystack = [hay for hay in haystack if hay.startswith(needle)]

		if len(s_haystack) == 1:
			s_ind = haystack.index(s_haystack[0])
			return [s_ind, s_haystack[0]]
	
		elif len(s_haystack) == 0 and substr:
			ss_haystack = [hay for hay in haystack if needle in haystack]

			if len(ss_haystack) == 1:
				ss_ind = haystack.index(ss_haystack[0])
				return [ss_ind, ss_haystack[0]]
	
	if case_ins and startofstr:
		sl_haystack = [hay for hay in l_haystack if hay.startswith(l_needle)]

		if len(s_haystack) == 1:
			sl_ind = l_haystack.index(sl_haystack[0])
			return [sl_ind, haystack[sl_ind]]
	
		elif len(s_haystack) == 0 and substr:
			ssl_haystack = [hay for hay in l_haystack if needle in haystack]

			if len(ssl_haystack) == 1:
				ssl_ind = l_haystack.index(ss_haystack[0])
				return [ssl_ind, haystack[ssl_ind]]

	return False
	
	
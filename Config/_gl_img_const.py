import PIL 
from PIL import Image, ImageDraw, ImageFont
import os

# FONTS
ROW_COLUMN_FONT = ImageFont.truetype("Fonts/Barlow-ExtraBoldItalic.ttf", 24)

# Symbols for rows and columns
COLUMN_SYMBOLS = ["A", "B", "C", "D", "E", "F", "G", "H", "I", "J", "K", "L", "M", "N", "O", "P", "Q", "R", "S", "T"]
ROW_SYMBOLS = ["1", "2", "3", "4", "5", "6", "7", "8", "9", "10", "11", "12", "13", "14", "15", "16", "17", "18", "19", "20"]

GRID_CENTER = [840, 470]

IMAGE_WIDTH = 1200
IMAGE_HEIGHT = 850

GRID_MAX_WIDTH = 560
GRID_MAX_HEIGHT = 560

LINE_WIDTH = 5

BACKGROUND_COLOR = (0, 0, 0, 255) # Black

GRID_SIZE = [14, 14]

COLUMN_TEXT_OFFSET = 10
ROW_TEXT_OFFSET = 18

FONT_SIZE_TO_SQUARE_SIZE = 2/3

# Showing all players
PLR_DISPLAY_MARGIN = 5
PLR_DISPLAY_SQR_SIZE = 31
PLR_DISPLAY_SQR_FONT = ImageFont.truetype("Fonts/Barlow-Bold.ttf", 19)

PLR_DISPLAY_SQR_LEFT = 65
PLR_DISPLAY_VERT_CENTER = 470

PLR_DISPLAY_NAME_FONT = ImageFont.truetype("Fonts/Archivo-Bold.ttf", 20)
PLR_DISPLAY_NAME_X_DIST = 12
PLR_DISPLAY_NAME_Y_DIST = 24
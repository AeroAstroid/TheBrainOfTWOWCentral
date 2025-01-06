import PIL
from PIL import ImageFont, Image, ImageDraw, ImageFilter, ImageEnhance
import requests
import time
import random

########### FONTS ###########
NOT_LOAD_FONT = ImageFont.truetype("Fonts/Poppins-ExtraBold.ttf", 64)
RANK_FONT = ImageFont.truetype("Fonts/Tharon.ttf", 128)
SCORE_FONT = ImageFont.truetype("Fonts/Tharon.ttf", 128)

# NAME FONTS - List of fonts to use for player's -- downsize depending on length of person's name
NAME_FONTS = []
NAME_FONT_SIZES = [96, 88, 80, 72, 64, 56, 48]
for name_font_size in NAME_FONT_SIZES:
    font = ImageFont.truetype("Fonts/Poppins-Bold.ttf", name_font_size)
    NAME_FONTS.append(font)

########### SIZES ###########
SLIDE_RESOLUTION = (1280, 720)

########### FUNCTIONS ###########
def get_art_image(image_link: str, display_img: bool = True):
    """Get the Image object that contains the art, in 1280x720 resolution"""

    # Resolution of image
    TARGET_RESOLUTION = (1031, 580)

    # Try to open image, and if not, don't display the image
    try:
        art_image = Image.open(requests.get(image_link, stream=True).raw).convert("RGBA")
    except Exception:
        display_img = False

    # Create new image
    new_image = Image.new("RGBA", TARGET_RESOLUTION, color=(0, 0, 0, 255))

    if display_img == False:
        # Draw text saying [Image could not be loaded]
        image_draw = ImageDraw.Draw(new_image)
        image_draw.text((TARGET_RESOLUTION[0] / 2, TARGET_RESOLUTION[1] / 2), text="[Image could not be loaded]", fill=(255, 255, 255, 255), font=NOT_LOAD_FONT, anchor="mm")
    else:

        # Resize and display image so it fits on the image
        # Calculate ratio of size of resized image to original image
        x_resize_ratio, y_resize_ratio = (TARGET_RESOLUTION[0] / art_image.size[0]), (TARGET_RESOLUTION[1] / art_image.size[1])
        resize_ratio = min(x_resize_ratio, y_resize_ratio)

        # Calculate sides of resized image
        x_size = round(art_image.size[0] * resize_ratio)
        y_size = round(art_image.size[1] * resize_ratio)

        # Resize image
        art_image = art_image.resize((x_size, y_size), Image.Resampling.BILINEAR)

        # Calculate pasting position
        x_pos = round((TARGET_RESOLUTION[0] / 2) - (x_size / 2))
        y_pos = round((TARGET_RESOLUTION[1] / 2) - (y_size / 2))

        new_image = art_image

    return new_image


def add_white_frame(art_image: Image.Image, thickness: Image.Image) -> Image.Image:
    """Adds white border around the image with a black dropshadow."""

    # Thickness of padding added to the art image
    BORDER_THICKNESS = 11

    # Create new image of the slide
    slide_image = Image.new("RGBA", SLIDE_RESOLUTION)

    # Calculate size of white rectangle and its positioning on the slide
    art_x_size = round(art_image.size[0])
    art_y_size = round(art_image.size[1])
    rect_x_size = art_x_size + BORDER_THICKNESS * 2
    rect_y_size = art_y_size + BORDER_THICKNESS * 2

    # Calculate position of top left of white rectangle - horizontally centered while allowing some space at bottom for text
    rect_x_left = round((SLIDE_RESOLUTION[0] - art_x_size) / 2)
    rect_y_top = round((SLIDE_RESOLUTION[1] - art_y_size) / 5)
    rect_shape = ((rect_x_left, rect_y_top), (rect_x_left + rect_x_size, rect_y_top + rect_y_size))

    # Draw dropshadow rectangle on new image
    slide_image_draw = ImageDraw.Draw(slide_image)
    slide_image_draw.rectangle(rect_shape, fill = (0, 0, 0, 255))
    slide_image = slide_image.filter(ImageFilter.GaussianBlur(radius=5))

    # Draw rectangle
    slide_image_draw = ImageDraw.Draw(slide_image)
    slide_image_draw.rectangle(rect_shape, fill = (255, 255, 255, 255))

    # Paste art image onto frame
    art_x_left = rect_x_left + BORDER_THICKNESS
    art_y_top = rect_y_top + BORDER_THICKNESS

    slide_image.alpha_composite(art_image, (art_x_left, art_y_top))

    return slide_image

def text_gradient(text_image: Image.Image, text_bbox: tuple, gradient: Image.Image):
    """Applies gradient onto text"""

    # Create new gradient image
    gradient_image = Image.new("RGBA", text_image.size)

    # Calculate position and size to paste gradient
    MARGIN = 5
    size_x = (text_bbox[2] - text_bbox[0]) + MARGIN * 2
    size_y = (text_bbox[3] - text_bbox[1]) + MARGIN * 2
    pos_x = text_bbox[0] - MARGIN
    pos_y = text_bbox[1] - MARGIN

    # Resize gradient to be within bounding box
    gradient = gradient.convert("RGBA")
    gradient = gradient.resize((round(size_x), round(size_y)))
    
    # Paste gradient onto gradient image
    gradient_image.paste(gradient, (round(pos_x), round(pos_y)), mask=gradient)

    # Put text on gradient
    gradient_image.putalpha(text_image)

    return gradient_image


def draw_number(text: str, image_resolution: tuple, font: ImageFont.ImageFont, gradient: Image.Image):
    """Get rank number with white outline"""

    # Draw text outline
    new_image = Image.new("RGBA", image_resolution)
    image_draw = ImageDraw.Draw(new_image)
    image_draw.text((image_resolution[0] / 2, image_resolution[1] / 2), text=text, fill=(255, 255, 255, 255), 
                    stroke_fill=(255, 255, 255, 255), stroke_width=7, font=font, anchor="mm")

    # Draw black and white solid text to use as alpha channel for gradient
    alpha = Image.new('L', image_resolution)
    alpha_draw = ImageDraw.Draw(alpha)
    alpha_draw.text((image_resolution[0] / 2, image_resolution[1] / 2), text=text, fill=255, 
                    stroke_fill=255, stroke_width=1, font=font, anchor="mm")
    
    text_bbox = alpha_draw.textbbox((image_resolution[0] / 2, image_resolution[1] / 2), text=text, stroke_width=1, font=font, anchor="mm")
    
    text_with_gradient = text_gradient(alpha, text_bbox, gradient)
    new_image.alpha_composite(text_with_gradient)
    
    # Rotate image
    new_image = new_image.rotate(6, resample=Image.Resampling.BICUBIC)

    return new_image


def draw_name(name: str, gradient: Image.Image):
    """Draw player's name with gradient and white outline applied"""

    TEXT_IMAGE_SIZE = (800, 150)
    TEXT_POSITION = (50, 75)
    TEXT_ANCHOR = "lm"

    # Draw text outline
    new_image = Image.new("RGBA", TEXT_IMAGE_SIZE)
    image_draw = ImageDraw.Draw(new_image)

    # Find a font size that will fit the player's name
    name_font = NAME_FONTS[-1]
    for font in NAME_FONTS:
        if image_draw.textlength(name, font) < 660:
            name_font = font
            break

    # Draw white outline of text
    image_draw.text(TEXT_POSITION, text=name, fill=(255, 255, 255, 255), 
                    stroke_fill=(255, 255, 255, 255), stroke_width=7, font=name_font, anchor=TEXT_ANCHOR)

    # Draw black and white solid text to use as alpha channel for gradient
    alpha = Image.new('L', TEXT_IMAGE_SIZE)
    alpha_draw = ImageDraw.Draw(alpha)
    alpha_draw.text(TEXT_POSITION, text=name, fill=255, stroke_fill=255, stroke_width=1, font=name_font, anchor=TEXT_ANCHOR)
    
    text_bbox = alpha_draw.textbbox(TEXT_POSITION, text=name, stroke_width=1, font=name_font, anchor=TEXT_ANCHOR)
    
    text_with_gradient = text_gradient(alpha, text_bbox, gradient)
    new_image.alpha_composite(text_with_gradient)

    return new_image


def get_circular_avatar(avatar: Image.Image):
    """Generates avatar in a circular mask"""

    # Open circular mask
    mask = Image.open("Images/asgen/avatarmask.png").convert("L")

    # Resize and rotate avatar
    new_avatar = avatar.copy().resize(mask.size, Image.Resampling.BICUBIC)

    # Apply circular mask to avatar
    new_avatar.putalpha(mask)

    return new_avatar


def generate_art_slide(rank: int, name: str, score: float, art_link: str, avatar_link: str, gradient: Image.Image):
    """Generates the art slide for the player, with their rank, name, score, art and profile picture displayed."""

    # Open art and resize correctly, then put onto slide image on top of the white art frame
    art_img = get_art_image(art_link)

    # Create slide
    slide_img = add_white_frame(art_img, 11)

    # Generate all text
    rank_img = draw_number("#{}".format(rank), (400, 400), RANK_FONT, gradient.copy())
    score_img = draw_number("{:.2f}".format(score), (350, 350), SCORE_FONT, gradient.copy())
    name_img = draw_name(name, gradient.copy())

    # Compile all text onto one image
    text_img = Image.new("RGBA", slide_img.size)
    text_img.alpha_composite(rank_img, (-30, -110))
    text_img.alpha_composite(score_img, (900, 450))
    text_img.alpha_composite(name_img, (170, 545))

    # Create black drop shadow by setting image to black
    drop_shadow = text_img.copy()
    new_pixel_data = []
    for i, pixel in enumerate(drop_shadow.getdata()):
        # Change color to black
        new_pixel_data.append((0, 0, 0, pixel[3]))
    drop_shadow.putdata(new_pixel_data)
    drop_shadow = drop_shadow.filter(ImageFilter.GaussianBlur(radius=8))

    # Paste drop shadow behind text image onto the final image
    slide_img.alpha_composite(drop_shadow)
    slide_img.alpha_composite(drop_shadow)
    slide_img.alpha_composite(drop_shadow)
    slide_img.alpha_composite(text_img)

    # Put profile picture on
    try:
        avatar = Image.open(requests.get(avatar_link, stream=True).raw).convert("RGBA")
        
        # Resize and put avatar in circular mask
        circular_avatar = get_circular_avatar(avatar)

        # Resize circular avatar again
        new_avatar = circular_avatar.resize((122, 122), Image.Resampling.BICUBIC)

        # Open white circular image and paste it onto final image
        white_circle = Image.open("Images/asgen/pfpcircle.png").convert("RGBA")
        slide_img.alpha_composite(white_circle, (0, 470))

        # Paste new avatar onto slide image
        slide_img.alpha_composite(new_avatar, (65, 536))

    except Exception:
        # Could not open profile picture, so don't draw the white circle
        pass

    return slide_img


def generate_all_slides(round_leaderboard: list, pfp_urls: dict, gradient: Image.Image) -> list:
    """Generate slides displaying the scores and art of an Artistic Showdown round."""

    start_time = time.time()

    # Store all generated slides
    slides_generated = []

    for contestant in round_leaderboard:

        # Get contestant information
        rank = contestant[0]
        name = contestant[1]
        art = contestant[2]
        score = contestant[3]

        # Check if score and rank are numbers
        try:
            rank = int(rank)
            score = float(score)
        except ValueError:
            # Continue in loop
            continue

        # Find user's avatar URL
        avatar_url = ""
        try:
            avatar_url = pfp_urls[name]
        except KeyError:
            pass

        contestant_slide = generate_art_slide(
            rank=rank,
            name=name,
            score=score,
            art_link=art,
            avatar_link=avatar_url,
            gradient=gradient
        )

        slides_generated.append(contestant_slide)

    end_time = time.time()
    print("Completed generating {} slides in {:.2f}!".format(len(slides_generated), end_time - start_time))

    # Return the slides and the time it took to generate those slides
    return slides_generated, (end_time - start_time)


def generate_slide_compilation(slide_list: list):
    """Generates one image with multiple displays of art on them (a maximum of 4)."""

    slide_amount = len(slide_list)

    # Can only handle a compilation of 4 slides
    if slide_amount > 4: return

    # Create compilation image
    compilation_image = Image.new("RGBA", (1280, 720))
    if slide_amount == 2:
        compilation_image = Image.new("RGBA", (1280, 360))

    for i, slide in enumerate(slide_list):

        # Paste slide onto new image downsized for rotation
        new_image = Image.new("RGBA", (1280, 720))
        resized_slide = slide.resize((640, 360))
        new_image.alpha_composite(resized_slide, (320, 180))
        new_image = new_image.rotate(random.randint(-20, 20) / 10, resample=Image.Resampling.BICUBIC)

        # Calculate position for pasting - left to right, up to down for rankings
        pos_x = (i % 2) * 640 - 320
        if slide_amount == 3 and i == 2:
            pos_x = 0

        pos_y = (i // 2) * 360 - 180

        compilation_image.alpha_composite(new_image, (pos_x, pos_y))

    return compilation_image
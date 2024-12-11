import os
from fontTools.ttLib import TTFont

font_path = os.path.join(
    os.path.dirname(os.path.dirname(__file__)), "style", "Clip.ttf"
)
default_font = TTFont(font_path)

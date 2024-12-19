import os
import sys

from fontmesher import default_font
from fontmesher.font_tools_3d import make_string_mesh3d

if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Usage: python demo.py <string>")
        sys.exit(1)

    string = sys.argv[1]
    assert string, "The input string cannot be empty"

    make_string_mesh3d(
        string=string,
        font=default_font,
        save_dir=os.getcwd(),
        lc=0.05,
        glyph_size=0.5,
        pad_y_start=0.25,
        pad_y_end=0.25,
        pad_x_start=0.8,
        pad_x_end=0.8,
        glyph_offset=0.5,
        pad_z = 0.2,
        dz_extrude = 0.4
    )

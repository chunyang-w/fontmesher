from fontTools.pens.recordingPen import RecordingPen


def get_font_boundaries(font):
    """
    Calculate the overall boundaries of the glyphs in a font.
    This function iterates through all the glyphs in the provided font and 
    calculates the minimum and maximum x and y coordinates that encompass 
    all the glyphs. It then returns the boundaries based on the larger 
    dimension (either width or height).
    Args:
        font: A font object that provides access to its glyph set.
    Returns:
        A tuple containing two values:
        - If the width (x dimension) is larger than the height (y dimension), 
          it returns (overall_x_min, overall_x_max).
        - Otherwise, it returns (overall_y_min, overall_y_max).
    """
    
    glyph_set = font.getGlyphSet()

    overall_x_min = float('inf')
    overall_y_min = float('inf')
    overall_x_max = float('-inf')
    overall_y_max = float('-inf')

    for glyph_name in glyph_set.keys():
        glyph = glyph_set[glyph_name]
        # Use a recording pen to capture the glyph outline
        pen = RecordingPen()
        glyph.draw(pen)

        for command, points in pen.value:
            if points:  # Some commands like `closePath` might not have points
                for point in points:
                    if len(point) == 2:  # Ensure the point has x and y
                        x, y = point
                        if isinstance(x, (int, float)) and isinstance(y, (int, float)):  # noqa
                            overall_x_min = min(overall_x_min, x)
                            overall_y_min = min(overall_y_min, y)
                            overall_x_max = max(overall_x_max, x)
                            overall_y_max = max(overall_y_max, y)

    x_scale = overall_x_max - overall_x_min
    y_scale = overall_y_max - overall_y_min

    if x_scale > y_scale:
        return overall_x_min, overall_x_max
    else:
        return overall_y_min, overall_y_max

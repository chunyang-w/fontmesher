import os
import gmsh

from fontmesher.font_pen import FontPen
from fontmesher import default_font
from fontmesher.utils import get_font_boundaries

from fontTools.pens.recordingPen import RecordingPen


def make_string_mesh(
    string,
    font=default_font,
    save_dir=".",
    lc=0.1,
    glyph_size=0.5,
    pad_y_start=0.25,
    pad_y_end=0.25,
    pad_x_start=0.8,
    pad_x_end=0.8,
    glyph_offset=0.5,
    extrude=False,
):
    """
    Generates a mesh for a given string using a specified font and saves it to a file.

    Parameters:
    string (str): The string to be meshed.
    font (Font): The font to be used for generating the mesh. Defaults to `default_font`.
    save_dir (str): The directory where the mesh file will be saved. Defaults to the current directory.
    lc (float): The characteristic length for the mesh elements. Defaults to 0.02.
    glyph_size (float): The size of each glyph in the mesh. Defaults to 0.5.
    pad_y_start (float): The padding at the start of the y-axis. Defaults to 0.25.
    pad_y_end (float): The padding at the end of the y-axis. Defaults to 0.25.
    pad_x_start (float): The padding at the start of the x-axis. Defaults to 0.8.
    pad_x_end (float): The padding at the end of the x-axis. Defaults to 0.8.
    glyph_offset (float): The offset between consecutive glyphs in the mesh. Defaults to 0.5.

    Returns:
    str: The path to the saved mesh file.
    """
    cmap = font.getBestCmap()
    glyphSet = font.getGlyphSet()
    min_val, max_val = get_font_boundaries(font)

    num_glyphs = len(string)

    domain_x_start = 0
    domain_x_end = glyph_offset*(num_glyphs) + (pad_x_start + pad_x_end)
    domain_y_start = 0
    domain_y_end = pad_y_start + glyph_size + pad_y_end

    gmsh.initialize()
    gmsh.model.add("font_mesh")

    # Initialise Domain
    p1 = gmsh.model.geo.addPoint(domain_x_start, domain_y_start, 0, lc)
    p2 = gmsh.model.geo.addPoint(domain_x_end, domain_y_start, 0, lc)
    p3 = gmsh.model.geo.addPoint(domain_x_end, domain_y_end, 0, lc)
    p4 = gmsh.model.geo.addPoint(domain_x_start, domain_y_end, 0, lc)

    l1 = gmsh.model.geo.addLine(p1, p2)
    l2 = gmsh.model.geo.addLine(p2, p3)
    l3 = gmsh.model.geo.addLine(p3, p4)
    l4 = gmsh.model.geo.addLine(p4, p1)

    domain_curves = [l1, l2, l3, l4]

    object_surface_loop = []
    object_curves = []
    for i in range(len(string)):
        pen = FontPen(
            geo=gmsh.model.geo,
            min_val=min_val,
            max_val=max_val,
            glyph_size=glyph_size,
            lc=lc
        )
        # r_pen = RecordingPen()
        glyph = string[i]
        g = glyphSet[cmap[ord(glyph)]]
        g.draw(pen)
        curves = pen.curves
        object_curves.extend(curves)
        gmsh.model.geo.translate([(1, curv) for curv in curves], i*glyph_offset + pad_x_start, pad_y_start, 0)  # noqa
        surface_loop = gmsh.model.geo.add_curve_loop(curves)
        gmsh.model.geo.addPhysicalGroup(1, curves, i + int(1e10), name=f"curves_of_{glyph}")
        object_surface_loop.append(surface_loop)

    domain_surface_loop = gmsh.model.geo.add_curve_loop(domain_curves)

    whole_surface = gmsh.model.geo.add_plane_surface([domain_surface_loop] + object_surface_loop)  # noqa

    gmsh.model.geo.addPhysicalGroup(1, [l1, l3], 1, name="wall")                            # noqa wall  
    gmsh.model.geo.addPhysicalGroup(1, [l4], 2, name="inflow")                              # noqa inflow
    gmsh.model.geo.addPhysicalGroup(1, [l2], 3, name="outflow")                             # noqa outflow
    gmsh.model.geo.addPhysicalGroup(1, object_curves, 4, name="object")                     # noqa object
    gmsh.model.geo.addPhysicalGroup(2, [whole_surface], 9, name="whole_domain")             # noqa whole domain surface

    gmsh.model.geo.synchronize()
    gmsh.model.mesh.generate(2) if not extrude else gmsh.model.mesh.generate(3)
    save_path = os.path.join(
        save_dir, f"{string}.msh"
    )
    gmsh.write(save_path)
    print(f"Mesh saved to {save_path}")
    return save_path

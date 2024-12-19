import os
import gmsh

from fontmesher.font_pen import FontPen
from fontmesher import default_font
from fontmesher.utils import get_font_boundaries

from fontTools.pens.recordingPen import RecordingPen


def make_string_mesh3d(
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
    dz_extrude=0.5,
    pad_z=0.2,
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

    domain_z_start = 0
    domain_z_end = domain_z_start + pad_z * 2 + dz_extrude

    # Physical entity group list
    #    Surface
    wall_list = []
    inflow_list = []
    outflow_list = []

    outter_surface_list = []

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
    domain_surface_loop = gmsh.model.geo.add_curve_loop(domain_curves)
    domain_surface = gmsh.model.geo.add_plane_surface([domain_surface_loop])
    domain_surface_extruded = gmsh.model.geo.extrude([[2, domain_surface]], 0, 0, domain_z_end)

    gmsh.model.geo.synchronize()

    print("domain_surface_extruded", domain_surface_extruded)
    print("original surface", domain_surface)

    for elem in domain_surface_extruded:
        tag, id = elem
        if tag == 3:
            gmsh.model.geo.remove([(tag, id)])
        else:
            box = gmsh.model.get_bounding_box(2, id)
            xmin, ymin, zmin, xmax, ymax, zmax = box
            if xmin == xmax:  # inlet or outlet
                if xmin == domain_x_start:
                    inflow_list.append(id)
                elif xmin == domain_x_end:
                    outflow_list.append(id)
            else:
                wall_list.append(id)
    wall_list.append(domain_surface)
        
    print(domain_surface_extruded)

    object_surface_list = []
    object_curves = []
    object_surface_loop_list = []
    for i in range(len(string)):
        pen = FontPen(
            geo=gmsh.model.geo,
            min_val=min_val,
            max_val=max_val,
            glyph_size=glyph_size,
            lc=lc,
            z=pad_z,
        )

        glyph = string[i]
        g = glyphSet[cmap[ord(glyph)]]
        g.draw(pen)

        curves = pen.curves
        object_curves.extend(curves)
        gmsh.model.geo.translate([(1, curv) for curv in curves], i*glyph_offset + pad_x_start, pad_y_start, 0)  # noqa
        surface_loop = gmsh.model.geo.add_curve_loop(curves)
        surface = gmsh.model.geo.add_plane_surface([surface_loop])
        surface_extruded = gmsh.model.geo.extrude([[2, surface]], 0, 0, dz_extrude)
        gmsh.model.geo.synchronize()
        surface_list = []
        for elem in surface_extruded:
            tag, id = elem
            if tag == 3:
                gmsh.model.geo.remove([(tag, id)])
            else:
                surface_list.append(id)
        surface_list.append(surface)
        object_surface_list.extend(surface_list)
        surface_loop_3d = gmsh.model.geo.add_surface_loop(surface_list)
        
        object_surface_loop_list.append(surface_loop_3d)

    outter_surface_list =  inflow_list + outflow_list + wall_list
    outter_surface_loop = gmsh.model.geo.addSurfaceLoop(outter_surface_list)
    print("outter_surface_loop", outter_surface_loop)

    domain_with_void = gmsh.model.geo.addVolume([outter_surface_loop] + object_surface_loop_list)

    gmsh.model.geo.addPhysicalGroup(2, wall_list, 1, name="wall")
    gmsh.model.geo.addPhysicalGroup(2, inflow_list, 2, name="inflow")
    gmsh.model.geo.addPhysicalGroup(2, outflow_list, 3, name="outflow")
    gmsh.model.geo.addPhysicalGroup(2, object_surface_list, 4, name="obj")
    gmsh.model.geo.addPhysicalGroup(3, [domain_with_void], 9, name="domain_with_void")


    gmsh.model.geo.synchronize()

    gmsh.model.mesh.generate(3)
    save_path = os.path.join(
        save_dir, f"{string}_3d.msh"
    )
    gmsh.write(save_path)
    print(f"Mesh saved to {save_path}")
    return save_path

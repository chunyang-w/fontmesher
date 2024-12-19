import gmsh

if __name__ == "__main__":
    gmsh.initialize()
    lc = 0.5
    
    domain_x_start = 0
    domain_y_start = 0
    
    domain_x_end = 1
    domain_y_end = 1

    
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

    domain_surface_extruded = gmsh.model.geo.extrude([[2, domain_surface]], 0, 0, 1)
    gmsh.model.geo.synchronize()

    box_x_start = 0.2
    box_x_end = 0.8
    box_y_start = 0.2
    box_y_end = 0.8

    p5 = gmsh.model.geo.addPoint(box_x_start, box_y_start, 0.2, lc)
    p6 = gmsh.model.geo.addPoint(box_x_end, box_y_start, 0.2, lc)
    p7 = gmsh.model.geo.addPoint(box_x_end, box_y_end, 0.2, lc)
    p8 = gmsh.model.geo.addPoint(box_x_start, box_y_end, 0.2, lc)


    l5 = gmsh.model.geo.addLine(p5, p6)
    l6 = gmsh.model.geo.addLine(p6, p7)
    l7 = gmsh.model.geo.addLine(p7, p8)
    l8 = gmsh.model.geo.addLine(p8, p5)

    box_curves = [l5, l6, l7, l8]
    box_surface_loop = gmsh.model.geo.add_curve_loop(box_curves)
    box_surface = gmsh.model.geo.add_plane_surface([box_surface_loop])

    box_surface_extruded = gmsh.model.geo.extrude([[2, box_surface]], 0, 0, 0.6)
    gmsh.model.geo.synchronize()

    domain_surface_list = []
    box_surface_list = []

    domain_vol_list = []
    box_vol_list = []

    for elem in domain_surface_extruded:
        tag, id = elem
        if tag == 3:
            gmsh.model.geo.remove([(tag, id)])
        else:
            domain_surface_list.append(id)
    domain_surface_list.append(domain_surface)

    for elem in box_surface_extruded:
        tag, id = elem
        if tag == 3:
            gmsh.model.geo.remove([(tag, id)])
        else:
            box_surface_list.append(id)
    box_surface_list.append(box_surface)
    gmsh.model.geo.synchronize()


    domain_surface_loop = gmsh.model.geo.add_surface_loop(domain_surface_list)
    box_surface_loop = gmsh.model.geo.add_surface_loop(box_surface_list)
    gmsh.model.geo.synchronize()
    

    domain_with_void = gmsh.model.geo.add_volume([domain_surface_loop, box_surface_loop])
    gmsh.model.geo.synchronize()


    gmsh.model.geo.add_physical_group(3, [domain_with_void], 1, name="domain_with_void")


    gmsh.model.geo.add_physical_group(2, domain_surface_list, 4, name="domain_surface_list")
    gmsh.model.geo.add_physical_group(2, box_surface_list, 5, name="box_surface_list")

    print("domain_vol_list", domain_vol_list)
    print("box_vol_list", box_vol_list)
    print("domain_with_void", domain_with_void)


    gmsh.model.geo.synchronize()
    # gmsh.fltk.run()
    gmsh.model.mesh.generate(3)
    gmsh.write("demo.msh")
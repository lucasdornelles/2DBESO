
# .txt mesh converter


def txt_mesh_converter(mesh_filename):

    # txt mesh converter, returns mesh variables

    with open(mesh_filename, 'r') as mesh_file:
        lines = mesh_file.readlines()

    # remove blank lines
    lines_list = []
    for line in lines:
        if line.strip():
            lines_list.append(line)

    surfaces_start = lines_list.index('$Surfaces\n')
    surfaces_end = lines_list.index('$EndSurfaces\n')
    surfaces_elements_start = lines_list.index('$SurfacesElements\n')
    surfaces_elements_end = lines_list.index('$EndSurfacesElements\n')
    boundaries_start = lines_list.index('$Boundaries\n')
    boundaries_end = lines_list.index('$EndBoundaries\n')
    boundaries_nodes_start = lines_list.index('$BoundariesNodes\n')
    boundaries_nodes_end = lines_list.index('$EndBoundariesNodes\n')
    nodes_start = lines_list.index('$Nodes\n')
    nodes_end = lines_list.index('$EndNodes\n')
    elements_start = lines_list.index('$Elements\n')
    elements_end = lines_list.index('$EndElements\n')

    surfaces = [lines_list[i] for i in range(surfaces_start + 1, surfaces_end)]
    surfaces_tags = []
    surfaces_names = []
    for i in range(len(surfaces)):
        surfaces[i] = surfaces[i].split()
        surfaces_tags.append(int(surfaces[i][0]))
        surfaces_names.append(surfaces[i][1])

    boundaries = [lines_list[i] for i in range(boundaries_start + 1, boundaries_end)]
    boundaries_tags = []
    boundaries_names = []
    for i in range(len(boundaries)):
        boundaries[i] = boundaries[i].split()
        boundaries_tags.append(int(boundaries[i][0]))
        boundaries_names.append(boundaries[i][1])

    nodes = [lines_list[i] for i in range(nodes_start + 1, nodes_end)]
    nodes_tags = []
    x_nodes_coordinates = []
    y_nodes_coordinates = []
    for i in range(len(nodes)):
        nodes[i] = nodes[i].split()
        nodes_tags.append(int(nodes[i][0]))
        x_nodes_coordinates.append(float(nodes[i][1]))
        y_nodes_coordinates.append(float(nodes[i][2]))

    elements = [lines_list[i] for i in range(elements_start + 1, elements_end)]
    elements_tags = []
    connectivity = []
    for i in range(1, len(elements)):
        elements[i] = elements[i].split()
        element_connectivity = [nodes_tags.index(int(elements[i][j])) for j in range(1, len(elements[i]))]
        if elements[0].lower() == 'c\n':
            tmp_element_connectivity = list(element_connectivity)
            element_connectivity = [tmp_element_connectivity[j] for j in [0, 3, 2, 1]]
        elements_tags.append(int(elements[i][0]))
        connectivity.append(element_connectivity)

    surfaces_elements_list = [lines_list[i] for i in range(surfaces_elements_start + 1, surfaces_elements_end)]
    number_of_surfaces = int(surfaces_elements_list[0])
    surface_elements = [i for i in range(number_of_surfaces)]
    for i in range(1, len(surfaces_elements_list), 2):
        surfaces_elements_list[i] = surfaces_elements_list[i][0].split()
        surfaces_elements_list[i + 1] = surfaces_elements_list[i + 1].split()
        index_ = surfaces_tags.index(int(surfaces_elements_list[i][0]))
        elements_list = [elements_tags.index(int(surfaces_elements_list[i + 1][j])) for j in
                         range(len(surfaces_elements_list[i + 1]))]
        surface_elements[index_] = list(elements_list)

    boundaries_nodes_list = [lines_list[i] for i in range(boundaries_nodes_start + 1, boundaries_nodes_end)]
    number_of_boundaries = int(boundaries_nodes_list[0])
    boundary_nodes = [i for i in range(number_of_boundaries)]
    for i in range(1, len(boundaries_nodes_list), 2):
        boundaries_nodes_list[i] = boundaries_nodes_list[i].split()
        boundaries_nodes_list[i + 1] = boundaries_nodes_list[i + 1].split()
        index_ = boundaries_tags.index(int(boundaries_nodes_list[i][0]))
        nodes_list = [nodes_tags.index(int(boundaries_nodes_list[i + 1][j])) for j in
                      range(len(boundaries_nodes_list[i + 1]))]
        boundary_nodes[index_] = list(nodes_list)

    return surfaces_names, boundaries_names, x_nodes_coordinates, y_nodes_coordinates, \
           connectivity, surface_elements, boundary_nodes


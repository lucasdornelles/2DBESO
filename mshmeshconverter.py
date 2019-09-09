
# gmsh .msh 4.0 converter


def msh_mesh_converter(mesh_filename):

    # reads .msh files and return the mesh variables

    with open(mesh_filename, 'r') as mesh_file:
        lines_list = mesh_file.readlines()

    physical_names_start = lines_list.index("$PhysicalNames\n")
    physical_names_end = lines_list.index("$EndPhysicalNames\n")
    entities_start = lines_list.index("$Entities\n")
    entities_end = lines_list.index("$EndEntities\n")
    nodes_start = lines_list.index("$Nodes\n")
    nodes_end = lines_list.index("$EndNodes\n")
    elements_start = lines_list.index("$Elements\n")
    elements_end = lines_list.index("$EndElements\n")

    physical_names = [lines_list[i] for i in range(physical_names_start + 2, physical_names_end)]
    for i in range(len(physical_names)):
        physical_names[i] = physical_names[i].split()
        physical_names[i][0] = int(physical_names[i][0])
        physical_names[i][1] = int(physical_names[i][1])

    entities = [lines_list[i] for i in range(entities_start + 1, entities_end)]
    for i in range(len(entities)):
        entities[i] = entities[i].split()
        entities[i][0] = int(entities[i][0])
        if i > 0:
            for j in range(1, 7):
                entities[i][j] = float(entities[i][j])
            for j in range(7, len(entities[i])):
                entities[i][j] = int(entities[i][j])
    entities[0][1] = int(entities[0][1])
    entities[0][2] = int(entities[0][2])
    entities[0][3] = int(entities[0][3])

    entities_nodes = [entities[i] for i in range(1, entities[0][0] + 1)]
    entities_curves = [entities[i] for i in range(entities[0][0] + 1, entities[0][0] + entities[0][1] + 1)]
    entities_surfaces = [entities[i] for i in range(entities[0][0] + entities[0][1] + 1,
                                                    entities[0][0] + entities[0][1] + entities[0][2] + 1)]

    nodes = [lines_list[i] for i in range(nodes_start + 1, nodes_end)]
    for i in range(len(nodes)):
        nodes[i] = nodes[i].split()
    step = 1
    nodes_list = []
    nodes_entitys_tag = []
    for i in range(int(nodes[0][0])):
        num_nodes = int(nodes[step][3])
        temp_nodes_list = [nodes[j] for j in range(step + 1, step + num_nodes + 1)]
        for j in range(len(temp_nodes_list)):
            temp_nodes_list[j][0] = int(temp_nodes_list[j][0])
            for k in range(1, 4):
                temp_nodes_list[j][k] = float(temp_nodes_list[j][k])
        nodes_list.append(temp_nodes_list)
        temp_nodes_entity_tag = [nodes[step][j] for j in [0, 1]]
        temp_nodes_entity_tag[0] = int(temp_nodes_entity_tag[0])
        temp_nodes_entity_tag[1] = int(temp_nodes_entity_tag[1])
        nodes_entitys_tag.append(temp_nodes_entity_tag)
        step = step + int(nodes[step][3]) + 1

    elements = [lines_list[i] for i in range(elements_start + 1, elements_end)]
    for i in range(len(elements)):
        elements[i] = elements[i].split()
        for j in range(len(elements[i])):
            elements[i][j] = int(elements[i][j])
    step = 1
    elements_list = []
    elements_entity_tag = []
    for i in range(elements[0][0]):
        num_elements = elements[step][3]
        temp_elements_list = [elements[j] for j in range(step + 1, step + num_elements + 1)]
        elements_list.append(temp_elements_list)
        temp_elements_entity_tag = [elements[step][j] for j in [0, 1, 2]]
        elements_entity_tag.append(temp_elements_entity_tag)
        step = step + elements[step][3] + 1

    x_nodes_coordinates = []
    nodes_tag = []
    for i in nodes_list:
        for j in i:
            x_nodes_coordinates.append(j[1])
            nodes_tag.append(j[0])

    y_nodes_coordinates = []
    for i in nodes_list:
        for j in i:
            y_nodes_coordinates.append(j[2])

    surface_names = []
    boundaries_names = []
    boundaries_tag = []
    surfaces_tag = []
    for i in physical_names:
        if i[0] == 0:
            boundaries_names.append(i[2].replace('"', ""))
            boundaries_tag.append(i[1])
        if i[0] == 1:
            boundaries_names.append(i[2].replace('"', ""))
            boundaries_tag.append(i[1])
        if i[0] == 2:
            surface_names.append(i[2].replace('"', ""))
            surfaces_tag.append(i[1])

    connectivity = []
    surfaces_elements = []
    surfaces_elements_tag = []
    boundary_nodes = []
    boundaries_nodes_tag = []
    step_start = 0
    for i in range(len(elements_entity_tag)):
        if elements_entity_tag[i][2] == 15:
            temp_boundary_nodes_list = []
            for j in range(len(elements_list[i])):
                temp_boundary_nodes = [nodes_tag.index(elements_list[i][j][1])]
                temp_boundary_nodes_list = temp_boundary_nodes_list + temp_boundary_nodes
            boundary_nodes.append(temp_boundary_nodes_list)
            boundaries_nodes_tag.append([elements_entity_tag[i][0], 15])
        if elements_entity_tag[i][2] == 1:
            temp_boundary_nodes_list = []
            for j in range(len(elements_list[i])):
                temp_boundary_nodes = [nodes_tag.index(elements_list[i][j][k]) for k in [1, 2]]
                temp_boundary_nodes_list = temp_boundary_nodes_list + temp_boundary_nodes
            boundary_nodes.append(list(set(temp_boundary_nodes_list)))
            boundaries_nodes_tag.append([elements_entity_tag[i][0], 1])

        if elements_entity_tag[i][2] == 3:
            step_end = step_start + len(elements_list[i])
            for j in range(len(elements_list[i])):
                temp_connectivity = [nodes_tag.index(elements_list[i][j][k]) for k in [1, 2, 3, 4]]
                connectivity.append(temp_connectivity)
            surfaces_elements.append([j for j in range(step_start, step_end)])
            step_start = step_end
            surfaces_elements_tag.append(elements_entity_tag[i][0])

    temp_boundary_nodes = list(boundary_nodes)
    boundary_nodes = []
    for i in range(len(boundaries_names)):
        temp_sum = []
        for j in range(len(entities_nodes)):
            if entities_nodes[j][7]:
                for k in range(entities_nodes[j][7]):
                    if entities_nodes[j][8 + k] == boundaries_tag[i]:
                        for l in range(len(boundaries_nodes_tag)):
                            if boundaries_nodes_tag[l] == [entities_nodes[j][0], 15]:
                                temp_sum = temp_sum + temp_boundary_nodes[l]
        if temp_sum:
            boundary_nodes.append(list(set(temp_sum)))
        temp_sum = []
        for j in range(len(entities_curves)):
            if entities_curves[j][7]:
                for k in range(entities_curves[j][7]):
                    if entities_curves[j][8 + k] == boundaries_tag[i]:
                        for l in range(len(boundaries_nodes_tag)):
                            if boundaries_nodes_tag[l] == [entities_curves[j][0], 1]:
                                temp_sum = temp_sum + temp_boundary_nodes[l]
        if temp_sum:
            boundary_nodes.append(list(set(temp_sum)))

    temp_surface_elements = list(surfaces_elements)
    surfaces_elements = []
    entities_surfaces_tags = [i[0] for i in entities_surfaces]
    for i in range(len(surfaces_tag)):
        temp_sum = []
        for j in range(len(surfaces_elements_tag)):
            index = entities_surfaces_tags.index(surfaces_elements_tag[j])
            if entities_surfaces[index][7]:
                for k in range(entities_surfaces[index][7]):
                    if entities_surfaces[index][8 + k] == surfaces_tag[i]:
                        temp_sum = temp_sum + temp_surface_elements[j]
        if temp_sum:
            surfaces_elements.append(temp_sum)

    return surface_names, surfaces_elements, x_nodes_coordinates, y_nodes_coordinates, \
           connectivity, boundaries_names, boundary_nodes


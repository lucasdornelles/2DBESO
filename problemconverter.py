# .txt problem converter


def problem_converter(problem_filename, surfaces_names, boundaries_names):

    # read a txt file and return problem parameters

    with open(problem_filename, 'r') as problem_file:
        lines = problem_file.readlines()

    # remove blank lines

    lines_list = []
    for line in lines:
        if line.strip():
            lines_list.append(line)

    for i in range(len(lines_list)):
        if '=' in lines_list[i]:
            lines_list[i] = lines_list[i].replace('=', ' ')
        if '[' in lines_list[i]:
            lines_list[i] = lines_list[i].replace('[', ' ')
        if ']' in lines_list[i]:
            lines_list[i] = lines_list[i].replace(']', ' ')
        lines_list[i] = lines_list[i].split()

    surfaces_index = [surfaces_names[i].lower() for i in range(len(surfaces_names))]

    boundaries_index = [boundaries_names[i].lower() for i in range(len(boundaries_names))]

    parameters_index = [lines_list[i][0].lower() for i in range(len(lines_list))]

    optimizer = lines_list[parameters_index.index('optimizer')][1].upper()
    evolutionary_rate = float(lines_list[parameters_index.index('evolutionaryrate')][1])
    minimum_density = float(lines_list[parameters_index.index('minimumdensity')][1])
    penalty = float(lines_list[parameters_index.index('penalty')][1])
    minimum_area_ratio = float(lines_list[parameters_index.index('minimumarearatio')][1])
    filter_radius = float(lines_list[parameters_index.index('filterradius')][1])

    plot_type = lines_list[parameters_index.index('plottype')][1].lower()
    print_all = bool(int(lines_list[parameters_index.index('printall')][1]))
    if not lines_list[parameters_index.index('dpi')][1].isalpha():
        dpi = int(lines_list[parameters_index.index('dpi')][1])
    else:
        dpi = None

    number_of_surfaces = len(surfaces_names)
    surface_type = list(range(number_of_surfaces))
    for i in range(1, number_of_surfaces + 1):
        lower_string = lines_list[parameters_index.index('surfaces')][i].lower()
        surface_type[surfaces_index.index(lower_string)] = int(lines_list[parameters_index.index('surfacestype')][i])

    number_of_boundaries = len(boundaries_names)
    boundary_type = list(range(number_of_boundaries))
    boundary_value = list(range(number_of_boundaries))
    for i in range(1, len(lines_list[parameters_index.index('boundariesvalues')])):
        if not lines_list[parameters_index.index('boundariesvalues')][i].isalpha():
            lines_list[parameters_index.index('boundariesvalues')][i] = float(
                lines_list[parameters_index.index('boundariesvalues')][i])

    temp_boundary_value = [[lines_list[parameters_index.index('boundariesvalues')][i],
                            lines_list[parameters_index.index('boundariesvalues')][i + 1]]
                           for i in range(1, len(lines_list[parameters_index.index('boundariesvalues')]), 2)]

    for i in range(1, number_of_boundaries + 1):
        lower_string = lines_list[parameters_index.index('boundaries')][i].lower()
        boundary_type[boundaries_index.index(lower_string)] = int(
            lines_list[parameters_index.index('boundariestype')][i])
        boundary_value[boundaries_index.index(lower_string)] = temp_boundary_value[i - 1]

    thickness = float(lines_list[parameters_index.index('thickness')][1])
    young_module = float(lines_list[parameters_index.index('youngmodule')][1])
    poisson_ratio = float(lines_list[parameters_index.index('poissonratio')][1])

    use_parallelism = bool(int(lines_list[parameters_index.index('useparalellism')][1]))
    if not lines_list[parameters_index.index('treads')][1].isalpha():
        treads = int(lines_list[parameters_index.index('treads')][1])
    else:
        treads = None

    if not lines_list[parameters_index.index('chuncksize')][1].isalpha():
        chuncksize = int(lines_list[parameters_index.index('chuncksize')][1])
    else:
        treads = None

    return evolutionary_rate, minimum_density, penalty, minimum_area_ratio, minimum_density, filter_radius, optimizer, \
           chuncksize, plot_type, print_all, dpi, surface_type, boundary_type, boundary_value, thickness, \
           young_module, poisson_ratio, use_parallelism, treads

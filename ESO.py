import numpy as np


def update_elements_density(averaged_sensibilities, last_elements_density, minimum_area, evolutionary_rate, areas,
                            surface_type, surface_elements):

    # update elements density using ESO softkill optimum criteria

    last_area = sum(list(np.array(last_elements_density) * np.array(areas)))
    new_area = max(minimum_area, last_area * (1 - evolutionary_rate))

    design_elements = []
    for i in range(len(surface_type)):
        if surface_type[i]:
            design_elements = design_elements + surface_elements[i]

    design_sensibilities = [averaged_sensibilities[i] for i in design_elements]

    low = min(design_sensibilities)
    high = max(design_sensibilities)
    residue = 10 ** (-5)
    new_elements_density = []
    while ((high - low) / high) > residue:
        new_elements_density = list(last_elements_density)
        threshold = (high + low) / 2

        for i in range(len(design_sensibilities)):
            if design_sensibilities[i] < threshold:
                new_elements_density[i] = 0

        area = sum(list(np.array(new_elements_density) * np.array(areas)))

        if area > new_area:
            low = threshold
        else:
            high = threshold

    new_area = area

    return new_elements_density, new_area


def check_convergence(elements_density, areas, minimum_area):

    # check ESO algorithm convergence

    iteration_area = sum(list(np.array(areas) * np.array(elements_density)))
    convergence = bool(iteration_area <= minimum_area)

    return convergence

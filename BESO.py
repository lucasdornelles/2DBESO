import numpy as np
from FEM import get_element_dof
from tqdm import tqdm
from scipy.spatial.distance import pdist


def get_elements_sensibilities(local_matrix, minimum_density, elements_density,
                               displacements, penalty, connectivity, nodes_dof):

    # calculate elements sensibilities

    sensibilities = []
    for i in tqdm(range(len(connectivity))):
        element_dof = get_element_dof(connectivity[i], nodes_dof)
        element_displacements = displacements[element_dof]

        element_sensibility = np.matmul(element_displacements,
                                        np.matmul(local_matrix[i],
                                                  np.transpose(np.asmatrix(element_displacements))))
        if elements_density[i] == 1:
            sensibilities.append(element_sensibility[0, 0])

        else:
            element_sensibility[0, 0] = element_sensibility[0, 0] * (minimum_density ** (penalty - 1))
            sensibilities.append(element_sensibility[0, 0])

    return sensibilities


def get_elements_on_filtering_radius(centers, element_index, filter_radius):

    # identify elements index on filtering radius of element_index element

    element_center = centers[element_index]

    elements_on_filtering_radius = []
    for i in range(len(centers)):
        if (element_center[0] - filter_radius) <= centers[i][0] <= (element_center[0] + filter_radius) and \
            (element_center[1] - filter_radius) <= centers[i][1] <= (element_center[1] + filter_radius) and \
                pdist([centers[i], element_center]) <= filter_radius:
            elements_on_filtering_radius = elements_on_filtering_radius + [i]

    return elements_on_filtering_radius


def get_filtering_weights(centers, filter_radius, all_elements_on_filtering_radius):

    # calculate filtering weights for all elements

    filtering_weights = []
    for element_index in range(len(centers)):
        element_weights = []
        element_center = centers[element_index]
        elements_on_filtering_radius = all_elements_on_filtering_radius[element_index]
        for elements in elements_on_filtering_radius:
            center = centers[elements]
            weight = filter_radius - pdist([element_center, center])
            element_weights = element_weights + [weight]
        filtering_weights.append(element_weights)

    return filtering_weights


def filter_sensibilities(sensibilities, all_elements_on_filtering_radius, filtering_weights):

    # filter sensibilities using filtering weights and elements on filtering radius

    filtered_sensibilities = []
    for element_index in range(len(sensibilities)):
        element_sensibilitie = 0
        elements_on_filtering_radius = all_elements_on_filtering_radius[element_index]
        element_filtering_weights = filtering_weights[element_index]
        for index in range(len(elements_on_filtering_radius)):
            sensibilitie_index = elements_on_filtering_radius[index]
            element_sensibilitie = element_sensibilitie + element_filtering_weights[index] * sensibilities[sensibilitie_index]
        element_sensibilitie = element_sensibilitie / sum(element_filtering_weights)
        filtered_sensibilities.append(element_sensibilitie[0])

    return filtered_sensibilities


def average_sensibilities(last_sensibilities, filtered_sensibilities):

    # average sensibilities with last iteration sensibilities

    averaged_sensibilities = []

    for element_index in range(len(filtered_sensibilities)):
        element_sensibilitie = (last_sensibilities[element_index] + filtered_sensibilities[element_index]) / 2
        averaged_sensibilities.append(element_sensibilitie)

    return averaged_sensibilities


def update_elements_density(averaged_sensibilities, last_elements_density, minimum_area, evolutionary_rate, areas,
                            surface_type, surface_elements):

    # update elements density using BESO softkill optimum criteria

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
            else:
                new_elements_density[i] = 1

        area = sum(list(np.array(new_elements_density) * np.array(areas)))

        if area > new_area:
            low = threshold
        else:
            high = threshold

    new_area = area

    return new_elements_density, new_area


def get_minimum_area(areas, minimum_area_ratio):

    # get minimum area for optimization

    minimum_area = sum(areas) * minimum_area_ratio
    return minimum_area


def check_convergence(compliances_list, iteration):

    # check BESO algorithm convergence

    compliance_diference = (sum(compliances_list[(iteration - 5): iteration]) -
                            sum(compliances_list[(iteration - 10): (iteration - 5)]))

    residue = 0.001
    convergence = bool(abs(compliance_diference) <= residue)

    return convergence, compliance_diference

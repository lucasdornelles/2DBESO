import numpy as np
from scipy.sparse.linalg import spsolve
from tqdm import tqdm
from scipy.sparse import lil_matrix

# Finite Elements Method Module


def get_local_matrix(x_nodes_coordinates, y_nodes_coordinates, connectivity, poisson_ratio, young_module, thickness):
    
    # returns a list of elements local matrix and a list of elements tensor matrix
    
    local_matrix = []
    tensor_matrix = []

    xi = np.array([-(1 / np.sqrt(3)), 1 / np.sqrt(3)])
    neta = np.array([-(1 / np.sqrt(3)), 1 / np.sqrt(3)])

    m_young = (young_module / (1 - (poisson_ratio ** 2))) * (np.array([[1, poisson_ratio, 0],
                                                                       [poisson_ratio, 1, 0],
                                                                       [0, 0, (1 - poisson_ratio) / 2]]))
    
    for i in tqdm(range(len(connectivity))):
        element_connectivity = connectivity[i]
        x_nodes = [x_nodes_coordinates[j] for j in element_connectivity]
        y_nodes = [y_nodes_coordinates[j] for j in element_connectivity]
        
        element_local_matrix = np.zeros((8, 8))
        element_tensor_matrix = np.zeros((3, 8))
        
        for j in range(2):
            for l in range(2):
                jacobian = np.array(
                    [[((1 / 4) * ((x_nodes[1] - x_nodes[0]) * (1 - neta[l]) + (x_nodes[2] - x_nodes[3]) * (1 + neta[l]))),
                      ((1 / 4) * ((y_nodes[1] - y_nodes[0]) * (1 - neta[l]) + (y_nodes[2] - y_nodes[3]) * (1 + neta[l])))],
                     [((1 / 4) * ((x_nodes[3] - x_nodes[0]) * (1 - xi[j]) + (x_nodes[2] - x_nodes[1]) * (1 + xi[j]))),
                      ((1 / 4) * ((y_nodes[3] - y_nodes[0]) * (1 - xi[j]) + (y_nodes[2] - y_nodes[1]) * (1 + xi[j])))]]
                )

                m_d = np.array(
                    [[(-(1 / 4) * (1 - neta[l])), ((1 / 4) * (1 - neta[l])), ((1 / 4) * (1 + neta[l])),
                      (-(1 / 4) * (1 + neta[l]))],
                     [(-(1 / 4) * (1 - xi[j])), (-(1 / 4) * (1 + xi[j])), ((1 / 4) * (1 + xi[j])),
                      ((1 / 4) * (1 - xi[j]))]]
                )

                inverse_jacobian = np.linalg.inv(jacobian)

                m_d[(0, 1), (0, 0)] = np.matmul(inverse_jacobian, m_d[(0, 1), (0, 0)])
                m_d[(0, 1), (1, 1)] = np.matmul(inverse_jacobian, m_d[(0, 1), (1, 1)])
                m_d[(0, 1), (2, 2)] = np.matmul(inverse_jacobian, m_d[(0, 1), (2, 2)])
                m_d[(0, 1), (3, 3)] = np.matmul(inverse_jacobian, m_d[(0, 1), (3, 3)])

                m_b = np.array([[m_d[0, 0], 0, m_d[0, 1], 0, m_d[0, 2], 0, m_d[0, 3], 0],
                                [0, m_d[1, 0], 0, m_d[1, 1], 0, m_d[1, 2], 0, m_d[1, 3]],
                                [m_d[1, 0], m_d[0, 0], m_d[1, 1], m_d[0, 1], m_d[1, 2], m_d[0, 2], m_d[1, 3],
                                 m_d[0, 3]]])

                element_tensor_matrix = element_tensor_matrix + m_b

                element_local_matrix = element_local_matrix + thickness * np.matmul((np.matmul(m_b.transpose(), m_young)),
                                                                                    m_b) * np.linalg.det(jacobian)

        element_tensor_matrix = (1/4) * np.matmul(m_young, element_tensor_matrix)

        local_matrix.append(element_local_matrix)
        tensor_matrix.append(element_tensor_matrix)

    return local_matrix, tensor_matrix


def get_element_dof(element_connectivity, nodes_dof):

    # returns the element degrees of freedom

    element_dof = []
    for i in element_connectivity:
        element_dof = element_dof + nodes_dof[i]
    return element_dof


def get_global_matrix(local_matrix, connectivity, nodes_dof):

    # returns the global matrix

    global_matrix = lil_matrix((len(nodes_dof)*2, len(nodes_dof)*2))
    for i in tqdm(range(len(connectivity))):
        element_connectivity = connectivity[i]
        element_dof = get_element_dof(element_connectivity, nodes_dof)

        global_matrix[np.ix_(element_dof, element_dof)] = global_matrix[np.ix_(element_dof, element_dof)] + local_matrix[i]

    return global_matrix


def apply_boundary_conditions(global_matrix, load_vector, boundary_type, boundary_nodes, boundary_value, nodes_dof):

    # apply boundary conditions to global matrix and load vector

    for i in range(len(boundary_type)):
        if boundary_type[i] == 0:
            for j in boundary_nodes[i]:
                if not boundary_value[i][0] == 'null':
                    load_vector[nodes_dof[j][0]] = boundary_value[i][0]
                if not boundary_value[i][1] == 'null':
                    load_vector[nodes_dof[j][1]] = boundary_value[i][1]

    for i in range(len(boundary_type)):
        if boundary_type[i] == 1:
            for j in boundary_nodes[i]:
                if not boundary_value[i][0] == 'null':
                    load_vector[nodes_dof[j][0]] = boundary_value[i][0] * (10 ** 50)
                    global_matrix[nodes_dof[j][0], nodes_dof[j][0]] = global_matrix[nodes_dof[j][0], nodes_dof[j][0]] + (10 ** 50)
                if not boundary_value[i][1] == 'null':
                    load_vector[nodes_dof[j][1]] = boundary_value[i][1] * (10 ** 50)
                    global_matrix[nodes_dof[j][1], nodes_dof[j][1]] = global_matrix[nodes_dof[j][1], nodes_dof[j][1]] + (10 ** 50)


def solve_fem(global_matrix, load_vector):

    # solves the set of linear equations and returns the nodes displacements (uses umfpack)
    # global matrix is formatted to csr and indices and indptr dtypes to int64 to use 64bits umfpack

    csr_global_matrix = global_matrix.tocsr()
    #csr_global_matrix.indices, csr_global_matrix.indptr = csr_global_matrix.indices.astype('int64'), \
    #                                                      csr_global_matrix.indptr.astype('int64')

    displacements = spsolve(csr_global_matrix, load_vector, use_umfpack=True)

    return displacements


def update_global_matrix(global_matrix, elements_density, last_elements_density,
                         local_matrix, nodes_dof, penalty, minimum_density, connectivity):

    # updates the global matrix to the new design

    for i in range(len(elements_density)):
        if not elements_density[i] == last_elements_density[i]:
            element_dof = get_element_dof(connectivity[i], nodes_dof)
            if elements_density[i] == 1:
                global_matrix[np.ix_(element_dof, element_dof)] = global_matrix[np.ix_(element_dof, element_dof)] - (local_matrix[i] * (minimum_density ** penalty)) + local_matrix[i]
            if elements_density[i] == 0:
                global_matrix[np.ix_(element_dof, element_dof)] = global_matrix[np.ix_(element_dof, element_dof)] - local_matrix[i] + (local_matrix[i] * (minimum_density ** penalty))


def get_elements_vonmises(tensor_matrix, displacements, nodes_dof, connectivity):

    # return a list of elements von Mises stress

    vonmises = []
    for i in range(len(connectivity)):
        element_dof = get_element_dof(connectivity[i], nodes_dof)
        element_displacements = displacements[element_dof]
        element_stress = np.matmul(tensor_matrix[i], element_displacements)
        element_vonmises = np.sqrt((((element_stress[0] ** 2) - (element_stress[0] * element_stress[1]) + (element_stress[1] ** 2) + (3 * (element_stress[2] ** 2)))/2))

        vonmises.append(element_vonmises)

    return vonmises


def get_elements_area(x_nodes_coordinates, y_nodes_coordinates, connectivity):

    # return a list of elements area calculated through Gauss's shoelace formula

    areas = []
    for i in range(len(connectivity)):
        x1 = x_nodes_coordinates[connectivity[i][0]]
        x2 = x_nodes_coordinates[connectivity[i][1]]
        x3 = x_nodes_coordinates[connectivity[i][2]]
        x4 = x_nodes_coordinates[connectivity[i][3]]
        y1 = y_nodes_coordinates[connectivity[i][0]]
        y2 = y_nodes_coordinates[connectivity[i][1]]
        y3 = y_nodes_coordinates[connectivity[i][2]]
        y4 = y_nodes_coordinates[connectivity[i][3]]
        element_area = ((x1 * y2) + (x2 * y3) + (x3 * y4) + (x4 * y1) - (x2 * y1) - (x3 * y2) - (x4 * y3) - (x1 * y4)) / 2
        areas.append(element_area)

    return areas


def get_total_compliance(global_matrix, displacements):

    # return design total compliance

    total_compliance = np.matmul(np.asmatrix((np.transpose(displacements))), global_matrix.dot(displacements))
    return total_compliance[0, 0]


def get_elements_center(x_nodes_coordinates, y_nodes_coordinates, connectivity):

    # return a list of elements centers

    centers = []
    for i in range(len(connectivity)):
        x1 = x_nodes_coordinates[connectivity[i][0]]
        x2 = x_nodes_coordinates[connectivity[i][1]]
        x3 = x_nodes_coordinates[connectivity[i][2]]
        x4 = x_nodes_coordinates[connectivity[i][3]]
        y1 = y_nodes_coordinates[connectivity[i][0]]
        y2 = y_nodes_coordinates[connectivity[i][1]]
        y3 = y_nodes_coordinates[connectivity[i][2]]
        y4 = y_nodes_coordinates[connectivity[i][3]]
        centers.append([(x1 + x2 + x3 + x4) / 4, (y1 + y2 + y3 + y4) / 4])

    return centers


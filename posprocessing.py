from itertools import cycle, islice
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.tri as tri


def roundrobin(*iterables):
    "roundrobin('ABC', 'D', 'EF') --> A D E B F C"
    # Recipe credited to George Sakkis
    num_active = len(iterables)
    nexts = cycle(iter(it).__next__ for it in iterables)
    while num_active:
        try:
            for next in nexts:
                yield next()
        except StopIteration:
            # Remove the iterator we just exhausted from the cycle.
            num_active -= 1
            nexts = cycle(islice(nexts, num_active))

            # create a new elementsstate list with doubled elements with
            # roundrobin(elementsstate, elementsstate)
            # and use it as c in plt.tripcolor with cmap="Blues"
            # use same method for vom mises but 0 elements must be masked


def get_triangulation(connectivity):

    # return elements triangulation order for use in tri.Triangulation()

    number_of_elements = len(connectivity)
    triangulation = np.zeros((2*number_of_elements, 3))
    correction = -1
    for i in range(number_of_elements):
        correction = correction + 1
        triangulation[i + correction, :] = np.array([connectivity[i][0], connectivity[i][1], connectivity[i][3]])
        triangulation[i + correction + 1, :] = np.array([connectivity[i][3], connectivity[i][1], connectivity[i][2]])

    return triangulation


def get_mask(elements_density):

    # return a elements density mask for use on tri.Triangulatio()

    mask = list(roundrobin(elements_density, elements_density))
    for i in range(len(mask)):
        mask[i] = bool(mask[i] == 0)

    return mask


def get_triangles(triangulation, x_nodes_coordinates, y_nodes_coordinates, mask):

    # return design triangles plot with elements with density 0 masked

    x = list(x_nodes_coordinates)
    y = list(y_nodes_coordinates)
    triangles = tri.Triangulation(x, y, triangulation, mask=mask)

    return triangles


def draw_triangles_contour(triangles):

    # not used

    plt.gca().set_aspect('equal')
    plt.triplot(triangles)


def draw_interior(triangles, elements_density):

    # not used

    c = list(roundrobin(elements_density, elements_density))
    cmap = 'Blues'
    plt.gca().set_aspect('equal')
    plt.tripcolor(triangles, c, cmap=cmap)


def draw_results(triangles, color_map):

    # plot design with selected color map

    c = list(roundrobin(color_map, color_map))
    cmap = 'jet'
    plt.gca().set_aspect('equal')
    plt.tripcolor(triangles, c, cmap=cmap, vmin=0)
    plt.colorbar(orientation='horizontal')


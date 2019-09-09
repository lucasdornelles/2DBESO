from mshmeshconverter import msh_mesh_converter
from txtmeshconverter import txt_mesh_converter
from problemconverter import problem_converter
import tkinter as tk
from tkinter import filedialog
import sys


def import_files():

    # uses tkinter filedialog to import files and return mesh variables and problem parameters

    print('Please select mesh file')
    root = tk.Tk()
    root.filename = filedialog.askopenfilename(initialdir='/', title='Select mesh file',
                                               filetypes=(('Gmsh 4.0 mesh file', '*.msh'), ('txt mesh file', '*.txt')))

    mesh_filename = root.filename
    root.destroy()
    if mesh_filename.lower().endswith('.msh'):
        surfaces_names, surface_elements, x_nodes_coordinates, y_nodes_coordinates, \
            connectivity, boundaries_names, boundary_nodes = msh_mesh_converter(mesh_filename)

    elif mesh_filename.lower().endswith('.txt'):
        surfaces_names, boundaries_names, x_nodes_coordinates, y_nodes_coordinates, \
            connectivity, surface_elements, boundary_nodes = txt_mesh_converter(mesh_filename)

    else:
        print('File type not supported')
        input()
        sys.exit()

    # generate nodes degrees of freedom

    konedd = list(range(0, len(x_nodes_coordinates) * 2))
    koned = list()
    for i in range(0, len(x_nodes_coordinates) * 2, 2):
        koned.append(konedd[i:i+2])

    nodes_dof = list(koned)

    print('Please select problem file')
    root = tk.Tk()
    root.filename = filedialog.askopenfilename(initialdir='/', title='Select problem file',
                                               filetypes=(('txt problem file', '*.txt'), ('all files', '*.*')))

    problem_filename = root.filename
    root.destroy()

    evolutionary_rate, minimum_density, penalty, minimum_area_ratio, minimum_density, filter_radius, optimizer, \
        chuncksize, plot_type, print_all, dpi, surface_type, boundary_type, boundary_value, thickness, young_module, \
        poisson_ratio, use_parallelism, treads = problem_converter(problem_filename, surfaces_names, boundaries_names)

    return surfaces_names, surface_elements, x_nodes_coordinates, y_nodes_coordinates, optimizer, \
        connectivity, boundaries_names, boundary_nodes, evolutionary_rate, minimum_density, \
        penalty, minimum_area_ratio, minimum_density, filter_radius, plot_type, print_all, \
        dpi, surface_type, boundary_type, boundary_value, thickness, young_module, \
        poisson_ratio, use_parallelism, treads, nodes_dof, chuncksize

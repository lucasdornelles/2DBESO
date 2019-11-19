import BESO
import ESO
import FEM
import posprocessing
from filesimporter import import_files
import numpy as np
import matplotlib.pyplot as plt
import time
import datetime
import os
from tqdm import tqdm
from multiprocessing import Pool


if __name__ == '__main__':
    print('2D Bidirectional Evolutionary Structural Optimization')
    date_and_time = datetime.datetime.today()
    result_path = 'Results/%i-%i-%i--%i-%i-%i' % (date_and_time.day, date_and_time.month, date_and_time.year,
                                                  date_and_time.hour, date_and_time.minute, date_and_time.second)
    if not os.path.exists(result_path):
        os.mkdir(result_path)
    
    console_output = open(result_path + '/' + 'console output.txt', 'w+')
    console_output.write('2D Bidirectional Evolutionary Structural Optimization\n')
    console_output.write('Initializing\n')
    console_output.write('Importing files\n')

    surfaces_names, surface_elements, x_nodes_coordinates, y_nodes_coordinates, optimizer, \
        connectivity, boundaries_names, boundary_nodes, evolutionary_rate, minimum_density, \
        penalty, minimum_area_ratio, minimum_density, filter_radius, plot_type, print_all, \
        dpi, surface_type, boundary_type, boundary_value, thickness, young_module, poisson_ratio, \
        use_parallelism, treads, nodes_dof, chuncksize = import_files()

    console_output.write('done\n')

    #plt.ioff()
    complete_start_time = time.time()
    print('Getting proprieties, this will take a while')
    console_output.write('Getting proprieties\n')

    print('Getting elements area')
    console_output.write('Getting elements area\n')
    start_time = time.time()
    areas = FEM.get_elements_area(x_nodes_coordinates, y_nodes_coordinates, connectivity)
    end_time = time.time()
    print('Process time: %f seconds' % (end_time - start_time))
    console_output.write('Process time: %f seconds\n' % (end_time - start_time))

    print('Getting elements centers')
    console_output.write('Getting elements centers\n')
    start_time = time.time()
    centers = FEM.get_elements_center(x_nodes_coordinates, y_nodes_coordinates, connectivity)
    end_time = time.time()

    print('Getting elements on filtering radius')
    console_output.write('Getting elements on filtering radius\n')
    start_time = time.time()

    if use_parallelism:
        arg = [(centers, i, filter_radius) for i in range(len(centers))]
        with Pool(treads) as pool:
            elements_on_filtering_radius = pool.starmap(BESO.get_elements_on_filtering_radius, tqdm(arg),chunksize=chuncksize)
    else:
        elements_on_filtering_radius = []
        for i in tqdm(range(len(centers))):
            elements_on_filtering_radius.append(BESO.get_elements_on_filtering_radius(centers, i, filter_radius))

    end_time = time.time()
    print('Process time: %f seconds' % (end_time - start_time))
    console_output.write('Process time: %f seconds\n' % (end_time - start_time))

    print('Getting filtering weights')
    console_output.write('Getting filtering weights\n')
    start_time = time.time()
    filtering_weights = BESO.get_filtering_weights(centers, filter_radius, elements_on_filtering_radius)
    end_time = time.time()
    print('Process time: %f seconds' % (end_time - start_time))
    console_output.write('Process time: %f seconds\n' % (end_time - start_time))

    print('Getting minimum area')
    console_output.write('Getting minimum area\n')
    start_time = time.time()
    minimum_area = BESO.get_minimum_area(areas, minimum_area_ratio)
    end_time = time.time()
    print('Process time: %f seconds' % (end_time - start_time))
    console_output.write('Process time: %f seconds\n' % (end_time - start_time))

    print('Getting plot triangulation')
    console_output.write('Getting plot triangulation')
    start_time = time.time()
    triangulation = posprocessing.get_triangulation(connectivity)
    end_time = time.time()
    print('Process time: %f seconds' % (end_time - start_time))
    console_output.write('Process time: %f seconds\n' % (end_time - start_time))

    print('Proprieties done')
    console_output.write('Proprieties done')
    console_output.write('\n')

    print('Getting local matrix list')
    console_output.write('Getting local matrix list\n')
    start_time = time.time()
    local_matrix, tensor_matrix = FEM.get_local_matrix(x_nodes_coordinates, y_nodes_coordinates, connectivity,
                                                       poisson_ratio, young_module, thickness)
    if not plot_type == 'mises':
        tensor_matrix = 0
    end_time = time.time()
    print('Process time: %f seconds' % (end_time - start_time))
    console_output.write('Process time: %f seconds\n' % (end_time - start_time))
    console_output.write('\n')

    print('Getting global matrix')
    console_output.write('Getting global matrix\n')
    start_time = time.time()
    global_matrix = FEM.get_global_matrix(local_matrix, connectivity, nodes_dof)
    end_time = time.time()
    print('Process time: %f seconds' % (end_time - start_time))
    console_output.write('Process time: %f seconds\n' % (end_time - start_time))
    console_output.write('\n')

    print('Applying boundary conditions')
    console_output.write('Applying boundary conditions\n')
    start_time = time.time()
    load_vector = np.zeros((len(nodes_dof) * 2, 1))
    FEM.apply_boundary_conditions(global_matrix, load_vector, boundary_type, boundary_nodes,
                                  boundary_value, nodes_dof)
    end_time = time.time()
    print('Process time: %f seconds' % (end_time - start_time))
    console_output.write('Process time: %f seconds\n' % (end_time - start_time))
    console_output.write('\n')

    print('Solving FEM')
    console_output.write('Solving FEM\n')
    start_time = time.time()
    displacements = FEM.solve_fem(global_matrix, load_vector)
    compliance_list = [FEM.get_total_compliance(global_matrix, displacements)]
    von_mises = []
    if plot_type == 'mises':
        von_mises = FEM.get_elements_vonmises(tensor_matrix, displacements, nodes_dof, connectivity)
    elements_density = list(np.ones(len(connectivity)))
    end_time = time.time()
    print('Process time: %f seconds' % (end_time - start_time))
    console_output.write('Process time: %f seconds\n' % (end_time - start_time))
    console_output.write('\n')

    print('Solving sensibilities')
    console_output.write('Solving sensibilities\n')
    start_time = time.time()
    sensibilities = BESO.get_elements_sensibilities(local_matrix, minimum_density, elements_density,
                                                    displacements, penalty, connectivity, nodes_dof)
    end_time = time.time()
    print('Process time: %f seconds' % (end_time - start_time))
    console_output.write('Process time: %f seconds\n' % (end_time - start_time))
    console_output.write('\n')

    print('Filtering sensibilities')
    console_output.write('Filtering sensibilities\n')
    start_time = time.time()
    filtered_sensibilities = BESO.filter_sensibilities(sensibilities, elements_on_filtering_radius, filtering_weights)
    averaged_sensibilities = list(filtered_sensibilities)
    end_time = time.time()
    print('Process time: %f seconds' % (end_time - start_time))
    console_output.write('Process time: %f seconds\n' % (end_time - start_time))
    console_output.write('\n')

    print('Plotting initial design')
    console_output.write('Plotting initial design')
    start_time = time.time()
    plt.figure()
    mask = posprocessing.get_mask(elements_density)
    triangles = posprocessing.get_triangles(triangulation, x_nodes_coordinates, y_nodes_coordinates, mask)
    if plot_type == 'mises':
        color_map = von_mises
    elif plot_type == 'sensibilities':
        color_map = averaged_sensibilities
    posprocessing.draw_results(triangles, color_map)
    plt.savefig(result_path + '/' + 'iteration-0', dpi=dpi, orientation='portrait')
    end_time = time.time()
    print('Process time: %f seconds' % (end_time - start_time))
    console_output.write('Process time: %f seconds\n' % (end_time - start_time))
    console_output.write('\n')

    print('Initializing iterations')
    console_output.write('Initializing iterations\n')
    iteration = -1
    convergence = False
    iteration_time = []

    while not convergence:
        start_iteration_time = time.time()
        iteration = iteration + 1
        last_elements_density = list(elements_density)
        last_sensibilities = averaged_sensibilities
        console_output.write('\n')
        console_output.write('-------------------------------------------------------------------')
        console_output.write('\n')
        console_output.write('Iteration %i\n' % (iteration+1))
        console_output.write('\n')

        print('Updating elements density')
        console_output.write('Updating elements density\n')
        start_time = time.time()
        if optimizer == 'BESO':
            elements_density, new_area = BESO.update_elements_density(averaged_sensibilities, last_elements_density,
                                                                      minimum_area, evolutionary_rate, areas,
                                                                      surface_type, surface_elements)
        elif optimizer == 'ESO':
            elements_density, new_area = ESO.update_elements_density(averaged_sensibilities, last_elements_density,
                                                                     minimum_area, evolutionary_rate, areas,
                                                                     surface_type, surface_elements)

        end_time = time.time()
        print('Process time: %f seconds' % (end_time - start_time))
        console_output.write('Process time: %f seconds\n' % (end_time - start_time))
        console_output.write('\n')

        print('Updating global matrix')
        console_output.write('Updating global matrix\n')
        start_time = time.time()
        FEM.update_global_matrix(global_matrix, elements_density, last_elements_density, local_matrix,
                                 nodes_dof, penalty, minimum_density, connectivity)
        end_time = time.time()
        print('Process time: %f seconds' % (end_time - start_time))
        console_output.write('Process time: %f seconds\n' % (end_time - start_time))
        console_output.write('\n')

        print('Solving FEM')
        console_output.write('Solving FEM\n')
        start_time = time.time()
        displacements = FEM.solve_fem(global_matrix, load_vector)
        compliance_list.append(FEM.get_total_compliance(global_matrix, displacements))
        von_mises = []
        if plot_type == 'mises':
            von_mises = FEM.get_elements_vonmises(tensor_matrix, displacements, nodes_dof, connectivity)
        end_time = time.time()
        print('Process time: %f seconds' % (end_time - start_time))
        console_output.write('Process time: %f seconds\n' % (end_time - start_time))
        console_output.write('\n')

        print('Solving sensibilities')
        console_output.write('Solving sensibilities\n')
        start_time = time.time()
        sensibilities = BESO.get_elements_sensibilities(local_matrix, minimum_density, elements_density,
                                                        displacements, penalty, connectivity, nodes_dof)
        end_time = time.time()
        print('Process time: %f seconds' % (end_time - start_time))
        console_output.write('Process time: %f seconds\n' % (end_time - start_time))
        console_output.write('\n')

        print('Filtering sensibilities')
        console_output.write('Filtering sensibilities\n')
        start_time = time.time()
        filtered_sensibilities = BESO.filter_sensibilities(sensibilities, elements_on_filtering_radius,
                                                           filtering_weights)
        averaged_sensibilities = BESO.average_sensibilities(last_sensibilities, filtered_sensibilities)
        end_time = time.time()
        print('Process time: %f seconds' % (end_time - start_time))
        console_output.write('Process time: %f seconds\n' % (end_time - start_time))
        console_output.write('\n')

        if print_all:
            print('Plotting results')
            console_output.write('Plotting results')
            start_time = time.time()
            plt.clf()
            mask = posprocessing.get_mask(elements_density)
            triangles = posprocessing.get_triangles(triangulation, x_nodes_coordinates, y_nodes_coordinates, mask)
            if plot_type == 'mises':
                color_map = von_mises
            elif plot_type == 'sensibilities':
                color_map = averaged_sensibilities
            posprocessing.draw_results(triangles, color_map)
            figname = result_path + '/' + 'iteration-%i' % (iteration+1)
            plt.draw()
            plt.savefig(figname, dpi=dpi, orientation='portrait')
            end_time = time.time()
            print('Process time: %f seconds' % (end_time - start_time))
            console_output.write('Process time: %f seconds\n' % (end_time - start_time))
            console_output.write('\n')

        print('Compliance: %f' % compliance_list[iteration + 1])
        console_output.write('Compliance: %f\n' % compliance_list[iteration + 1])

        if iteration > 10:
            if optimizer == 'BESO':
                convergence, convergence_value = BESO.check_convergence(compliance_list, iteration)
                console_output.write('Convergence: %f\n' % convergence_value)
            if optimizer == 'ESO':
                convergence = ESO.check_convergence(elements_density, areas, minimum_area)
        console_output.write('New area: %f\n' % new_area)

        end_iteration_time = time.time()
        iteration_time.append((end_iteration_time - start_iteration_time))
        print('Iteration %i time: %f' % (iteration + 1, iteration_time[iteration]))
        console_output.write('Iteration %i time: %f\n' % (iteration + 1, iteration_time[iteration]))
        console_output.write('\n')

    if not print_all:
        print('Plotting results')
        console_output.write('Plotting results')
        start_time = time.time()
        plt.clf()
        mask = posprocessing.get_mask(elements_density)
        triangles = posprocessing.get_triangles(triangulation, x_nodes_coordinates, y_nodes_coordinates, mask)
        if plot_type == 'mises':
            color_map = von_mises
        elif plot_type == 'sensibilities':
            color_map = averaged_sensibilities
        posprocessing.draw_results(triangles, color_map)
        figname = result_path + '/' + 'iteration-%i' % (iteration + 1)
        plt.draw()
        plt.savefig(figname, dpi=dpi, orientation='portrait')
        end_time = time.time()
        print('Process time: %f seconds' % (end_time - start_time))
        console_output.write('Process time: %f seconds\n' % (end_time - start_time))
        console_output.write('\n')

    plt.clf()
    plt.plot(compliance_list)
    plt.draw()
    figname = result_path + '/' + 'compliance-plot'
    plt.savefig(figname, dpi=dpi)
    complete_end_time = time.time()
    complete_time = complete_end_time - complete_start_time
    average_iteration_time = sum(iteration_time) / (len(iteration_time))
    print('Total time: %f seconds' % complete_time)
    console_output.write('Total time: %f seconds\n' % complete_time)
    print('Average iteration time: %f seconds' % average_iteration_time)
    console_output.write('Average iteration time: %f seconds\n' % average_iteration_time)
    print('foldername: ' + result_path)
    console_output.close()
    input()


# Tremuri_Input_func.py
# Author : Arash Askari
# Start Date: 11.01.2019
# Project: Masonry Interface Modeling and Analysis Software
# Place: EESD-ENAC-EPFL
# Supervision and Collaboration: Prof. Katrin Beyer, Francesco Vanin
# ## Description: ## #
# Reading a Tremuri file as input is one of the primary options to generate the 3D model of a masonry building.
# The procedure is performed using the file module named **Tremuri_Input_func.py**.
# Below, you can find the guideline, through which you can find how the Tremuri input file is interpreted.
# This function calls nothing
# This function is called by the "convertTremuriToOpenSees_func.py" file

# Import required packages
import numpy as np
import pandas as pd
import math
from numpy.linalg import inv
import time

completeFileLocation1 = ""  # The location of the Tremuri file that is going to be read


# The function checks if there is a blank line when going through the lines and jumps over it
# to prevent errors from happening.
def check_empty(f_lines, f_inside_counter):
    while 1:
        if not f_lines[f_inside_counter]:
            f_inside_counter = f_inside_counter + 1
        else:
            break
    return f_inside_counter


def TRIfunc():
    # The variables that are going to be used by higher level functions are defined as global variables
    global wall, n2d, poly2d, n3d, poly3d1, poly3d2, max_node_number, element, elastic_beam, nl_beam, floor_level, floor, \
        material, nodal_mass, restraint, analysis
    start_time = time.time()  # just to track the time passed for going through each module
    open_file = open(completeFileLocation1, "r")  # Open the Tremuri file
    input_file = open_file.read()  # Read the Tremuri file

    # read the lines of the input file
    lines = input_file.splitlines()  # split the lines of the input file
    open_file.close()  # close the input file after reading its data

    max_node_number = 0  # initialize max_node_number to store the largest node tag
    # ## initialize model DataFrames: tmp_*** : temporary DataFrame for individual items ## #
    # ## ***: DataFrame for storing all the individuals ## #
    # ## tmp_***_list: list for storage of all the individuals before converting to the final DataFrame
    # ## empty_tmp_***: defined to clear all the data presented in the tmp_***
    # initiate wall data frame
    tmp_wall = pd.DataFrame(columns=['No', 'x0', 'y0', 'angle'], index=['0'])
    wall = pd.DataFrame(columns=['No', 'x0', 'y0', 'angle'], index=['0'])
    tmp_wall_list = []
    # initiate material data frame
    tmp_material = pd.DataFrame(
        columns=['No', 'E', 'G', 'rho', 'fc', 'tau0', 'verification', 'shear_model', 'drift_S', 'drift_F', 'mu', 'Gc',
                 'beta'], index=['0'])
    material = pd.DataFrame(
        columns=['No', 'E', 'G', 'rho', 'fc', 'tau0', 'verification', 'shear_model', 'drift_S', 'drift_F', 'mu', 'Gc',
                 'beta'], index=['0'])
    tmp_material_list = []
    empty_tmp_material = pd.DataFrame(
        columns=['No', 'E', 'G', 'rho', 'fc', 'tau0', 'verification', 'shear_model', 'drift_S', 'drift_F', 'mu', 'Gc',
                 'beta'], index=['0'])
    # initiate floor data frame
    tmp_floor = pd.DataFrame(columns=['No', 'nI', 'nJ', 'nK', 'nL', 'thickness', 'E1', 'E2', 'Poisson', 'G', 'angle'],
                             index=['0'])
    floor = pd.DataFrame(columns=['No', 'nI', 'nJ', 'nK', 'nL', 'thickness', 'E1', 'E2', 'Poisson', 'G', 'angle'],
                         index=['0'])
    tmp_floor_list = []
    # inititate restraints data frame
    tmp_restraint = pd.DataFrame(columns=['Node', 'x', 'y', 'z', 'rx', 'ry'], index=['0'])
    restraint = pd.DataFrame(columns=['Node', 'x', 'y', 'z', 'rx', 'ry'], index=['0'])
    tmp_restraint_list = []
    # initiate floor number data
    tmp_floor_level = pd.DataFrame(columns=['h', 'zAxis1', 'zAxis2', 'zAxis3'], index=['0'])
    floor_level = pd.DataFrame(columns=['h', 'zAxis1', 'zAxis2', 'zAxis3'], index=['0'])
    tmp_floor_level_list = []
    # initiate the data for 2D nodes
    tmp_n2d = pd.DataFrame(
        columns=['Node', 'wall', 'x_loc', 'z', 'type', 'rho', 'thickness', 'offsetXloc1', 'offsetXloc2', 'offsetZ1',
                 'offsetZ2', 'repartition1', 'repartition2', 'x', 'y', 'offsetX1', 'offsetX2', 'offsetY1', 'offsetY2'],
        index=['0'])
    n2d = pd.DataFrame(
        columns=['Node', 'wall', 'x_loc', 'z', 'type', 'rho', 'thickness', 'offsetXloc1', 'offsetXloc2', 'offsetZ1',
                 'offsetZ2', 'repartition1', 'repartition2', 'x', 'y', 'offsetX1', 'offsetX2', 'offsetY1', 'offsetY2'],
        index=['0'])
    tmp_n2d_list = []
    empty_tmp_n2d = pd.DataFrame(
        columns=['Node', 'wall', 'x_loc', 'z', 'type', 'rho', 'thickness', 'offsetXloc1', 'offsetXloc2', 'offsetZ1',
                 'offsetZ2', 'repartition1', 'repartition2', 'x', 'y', 'offsetX1', 'offsetX2', 'offsetY1', 'offsetY2'],
        index=['0'])
    # initiate the data for 3D nodes
    tmp_n3d = pd.DataFrame(
        columns=['Node', 'n_wall2', 'wall1', 'wall2', 'z', 'type', 'rho1', 'thickness1', 'offsetXloc11', 'offsetXloc12',
                 'offsetZ11', 'offsetZ12', 'rho2', 'thickness2', 'offsetXloc21', 'offsetXloc22', 'offsetZ21',
                 'offsetZ22', 'x', 'y', 'offsetX11', 'offsetX12', 'offsetY11', 'offsetY12', 'offsetX21', 'offsetX22',
                 'offsetY21', 'offsetY22'], index=['0'])
    n3d = pd.DataFrame(
        columns=['Node', 'n_wall2', 'wall1', 'wall2', 'z', 'type', 'rho1', 'thickness1', 'offsetXloc11', 'offsetXloc12',
                 'offsetZ11', 'offsetZ12', 'rho2', 'thickness2', 'offsetXloc21', 'offsetXloc22', 'offsetZ21',
                 'offsetZ22', 'x', 'y', 'offsetX11', 'offsetX12', 'offsetY11', 'offsetY12', 'offsetX21', 'offsetX22',
                 'offsetY21', 'offsetY22'], index=['0'])
    tmp_n3d_list = []
    empty_tmp_n3d = pd.DataFrame(
        columns=['Node', 'n_wall2', 'wall1', 'wall2', 'z', 'type', 'rho1', 'thickness1', 'offsetXloc11', 'offsetXloc12',
                 'offsetZ11', 'offsetZ12', 'rho2', 'thickness2', 'offsetXloc21', 'offsetXloc22', 'offsetZ21',
                 'offsetZ22', 'x', 'y', 'offsetX11', 'offsetX12', 'offsetY11', 'offsetY12', 'offsetX21', 'offsetX22',
                 'offsetY21', 'offsetY22'], index=['0'])
    # indicate the data for the 2d node polygons
    tmp_poly2d = pd.DataFrame(
        columns=['Node - Global', 'Node - Local', 'rho', 'thickness', 'offsetXloc1', 'offsetXloc2', 'offsetZ1',
                 'offsetZ2', 'offsetX1', 'offsetX2', 'offsetY1', 'offsetY2'], index=['0', '1', '2', '3'])
    poly2d = pd.DataFrame(
        columns=['Node - Global', 'Node - Local', 'rho', 'thickness', 'offsetXloc1', 'offsetXloc2', 'offsetZ1',
                 'offsetZ2', 'offsetX1', 'offsetX2', 'offsetY1', 'offsetY2'], index=['0', '1', '2', '3'])
    tmp_poly2d_list = []
    empty_tmp_poly2d = pd.DataFrame(
        columns=['Node - Global', 'Node - Local', 'rho', 'thickness', 'offsetXloc1', 'offsetXloc2', 'offsetZ1',
                 'offsetZ2', 'offsetX1', 'offsetX2', 'offsetY1', 'offsetY2'], index=['0', '1', '2', '3'])
    for item in np.arange(4):  # assign the local node numbers for the 2d node polygons : 1, 2, 3, 4
        tmp_poly2d['Node - Local'].iat[item] = item + 1
        empty_tmp_poly2d['Node - Local'].iat[item] = item + 1
    # indicate the data for the 3d node polygons (1 & 2)
    tmp_poly3d1 = pd.DataFrame(
        columns=['Node - Global', 'Node - Local', 'rho', 'thickness', 'offsetXloc1', 'offsetXloc2', 'offsetZ1', 
                 'offsetZ2', 'offsetX1', 'offsetX2', 'offsetY1', 'offsetY2'], index=['0', '1', '2', '3'])
    poly3d1 = pd.DataFrame(
        columns=['Node - Global', 'Node - Local', 'rho', 'thickness', 'offsetXloc1', 'offsetXloc2', 'offsetZ1', 
                 'offsetZ2', 'offsetX1', 'offsetX2', 'offsetY1', 'offsetY2'], index=['0', '1', '2', '3'])
    tmp_poly3d1_list = []
    empty_tmp_poly3d1 = pd.DataFrame(
        columns=['Node - Global', 'Node - Local', 'rho', 'thickness', 'offsetXloc1', 'offsetXloc2', 'offsetZ1', 
                 'offsetZ2', 'offsetX1', 'offsetX2', 'offsetY1', 'offsetY2'], index=['0', '1', '2', '3'])
    tmp_poly3d2 = pd.DataFrame(
        columns=['Node - Global', 'Node - Local', 'rho', 'thickness', 'offsetXloc1', 'offsetXloc2', 'offsetZ1', 
                 'offsetZ2', 'offsetX1', 'offsetX2', 'offsetY1', 'offsetY2'], index=['0', '1', '2', '3'])
    poly3d2 = pd.DataFrame(
        columns=['Node - Global', 'Node - Local', 'rho', 'thickness', 'offsetXloc1', 'offsetXloc2', 'offsetZ1', 
                 'offsetZ2', 'offsetX1', 'offsetX2', 'offsetY1', 'offsetY2'], index=['0', '1', '2', '3'])
    tmp_poly3d2_list = []
    empty_tmp_poly3d2 = pd.DataFrame(
        columns=['Node - Global', 'Node - Local', 'rho', 'thickness', 'offsetXloc1', 'offsetXloc2', 'offsetZ1', 
                 'offsetZ2', 'offsetX1', 'offsetX2', 'offsetY1', 'offsetY2'], index=['0', '1', '2', '3'])
    for item in np.arange(4):  # assign the local node numbers for the 2d node polygons : 1, 2, 3, 4
        tmp_poly3d1['Node - Local'].iat[item] = item + 1
        tmp_poly3d2['Node - Local'].iat[item] = item + 1
        empty_tmp_poly3d1['Node - Local'].iat[item] = item + 1
        empty_tmp_poly3d2['Node - Local'].iat[item] = item + 1
    # initiate elastic beam data frame
    tmp_elastic_beam = pd.DataFrame(
        columns=['No', 'wall', 'nodeI', 'nodeJ', 'mat', 'area', 'J', 'deformIn', 'type', 'offXloc_I', 'offZ_I', 
                 'offXloc_J', 'offZ_J'], index=['0'])
    elastic_beam = pd.DataFrame(
        columns=['No', 'wall', 'nodeI', 'nodeJ', 'mat', 'area', 'J', 'deformIn', 'type', 'offXloc_I', 'offZ_I', 
                 'offXloc_J', 'offZ_J'], index=['0'])
    tmp_elastic_beam_list = []
    # initiate nonlinear beam data frame
    tmp_nl_beam = pd.DataFrame(
        columns=['No', 'wall', 'nodeI', 'nodeJ', 'mat', 'area', 'J', 'offXloc_I', 'offZ_I', 'offXloc_J', 'offZ_J', 
                 'type', 'deformIn', 'Wpl'], index=['0'])
    nl_beam = pd.DataFrame(
        columns=['No', 'wall', 'nodeI', 'nodeJ', 'mat', 'area', 'J', 'offXloc_I', 'offZ_I', 'offXloc_J', 'offZ_J', 
                 'type', 'deformIn', 'Wpl'], index=['0'])
    tmp_nl_beam_list = []
    # initiate element data frame
    element_number = 0
    tmp_element = pd.DataFrame(
        columns=['No', 'wall', 'nodeI', 'nodeJ', 'xBar', 'zBar', 'L', 'H', 't', 'mat', 'type', 'angle', 'nI1', 'nI2', 
                 'nI3', 'nJ1', 'nJ2', 'nJ3'], index=['0'])
    element = pd.DataFrame(
        columns=['No', 'wall', 'nodeI', 'nodeJ', 'xBar', 'zBar', 'L', 'H', 't', 'mat', 'type', 'angle', 'nI1', 'nI2', 
                 'nI3', 'nJ1', 'nJ2', 'nJ3'], index=['0'])
    tmp_element_list = []
    # initiate analysis number data
    analysis_number = 0
    last_analysis_number = 0
    tmp_analysis = pd.DataFrame(columns=['analysisNumber', 'type', 'nSteps', 'tol', 'maxStep', 'accVec1', 'accVec2',
                                         'accVec3', 'dt', 'nModes', 'rayleigh1', 'rayleigh2', 'subd', 'controlNode',
                                         'DOF', 'maxDisp', 'forceDrop', 'loadedNode', 'load1', 'load2', 'load3',
                                         'load4', 'load5', 'groundMotion', 'PGA'], index=['0'])
    analysis = pd.DataFrame(columns=['analysisNumber', 'type', 'nSteps', 'tol', 'maxStep', 'accVec1', 'accVec2',
                                     'accVec3', 'dt', 'nModes', 'rayleigh1', 'rayleigh2', 'subd', 'controlNode', 'DOF',
                                     'maxDisp', 'forceDrop', 'loadedNode', 'load1', 'load2', 'load3', 'load4', 'load5',
                                     'groundMotion', 'PGA'], index=['0'])
    tmp_analysis_list = []
    empty_tmp_analysis = pd.DataFrame(columns=['analysisNumber', 'type', 'nSteps', 'tol', 'maxStep', 'accVec1',
                                               'accVec2', 'accVec3', 'dt', 'nModes', 'rayleigh1', 'rayleigh2', 'subd',
                                               'controlNode', 'DOF', 'maxDisp', 'forceDrop', 'loadedNode', 'load1',
                                               'load2', 'load3', 'load4', 'load5', 'groundMotion', 'PGA'], index=['0'])
    # initiate nodal mass data frame
    tmp_nodal_mass = pd.DataFrame(columns=['node', 'mass', 'ecc_x', 'ecc_z'], index=['0'])
    nodal_mass = pd.DataFrame(columns=['node', 'mass', 'ecc_x', 'ecc_z'], index=['0'])
    tmp_nodal_mass_list = []
    # initiate distributed mass data frame
    tmp_distr_mass = pd.DataFrame(columns=['node', 'V', 'M', 'Vr', 'Mr', 'el'], index=['0'])
    distr_mass = pd.DataFrame(columns=['node', 'V', 'M', 'Vr', 'Mr', 'el'], index=['0'])
    tmp_distr_mass_list = []

    # and store the data in a Microsoft Excel workbook for further usages
    writer = pd.ExcelWriter('tremuri_input_parameters.xlsx', engine='xlsxwriter')

    # go through the lines to find each of the desired sections
    for lineCounter in np.arange(len(lines)):
        # find the parameters for walls
        if (("pareti" in lines[lineCounter]) or ("walls" in lines[lineCounter])) and ("!" not in lines[lineCounter]):
            # the inside_counter parameter is defined so the data blocks for each parameter can be dealt with
            inside_counter = lineCounter + 1
            inside_counter = check_empty(lines, inside_counter)
            while lines[inside_counter][0] != '/':
                # jump over the commented and empty lines
                while (lines[inside_counter][0] == '!') or (lines[inside_counter][0:1] == '\t'):
                    inside_counter = inside_counter + 1
                    inside_counter = check_empty(lines, inside_counter)
                    if lines[inside_counter][0] == '/':
                        break
                if lines[inside_counter][0] == '/':
                    break
                # separate, extract and store the wall parameters in each line using "SPACE" in a list
                params = lines[inside_counter].split()
                for paramCounter in np.arange(len(params)):
                    # In some cases, the lines are followed by a number of empty values.
                    # Therefore, the number of parameters are calculated to prevent any errors
                    # using the extracted data.
                    if params[paramCounter] == "":
                        last_item = paramCounter - 1
                        break
                    elif paramCounter == len(params) - 1:
                        last_item = len(params) - 1
                params = params[0:last_item + 1]  # params variable is updated to store only the non-empty arguments
                for item in np.arange(last_item + 1):
                    # if the presented angle values are in degrees, change them to radians
                    if "°" in params[item]:
                        params[item] = (float(params[item][0:len(params[item]) - 1]) / 180) * math.pi
                    tmp_wall.iat[0, item] = params[item]  # store all the parameters in the temporary DataFrame
                tmp_wall_list.append(tmp_wall.values.tolist()[0])  # store all the individual items in a list
                inside_counter = inside_counter + 1
                inside_counter = check_empty(lines, inside_counter)

            # convert the list of all individuals to a DataFrame
            wall = pd.DataFrame(tmp_wall_list, columns=['No', 'x0', 'y0', 'angle'])
            wall = wall.astype(float)  # convert all the variables to float
            wall['No'] = wall['No'].astype(int)  # the wall numbers should be integers
            wall = wall.set_index('No')  # set the wall number as the index
            # Convert the dataframe to an XlsxWriter Excel object.
            wall.to_excel(writer, sheet_name='wall')

        # find the parameters for materials
        if (("Materiali" in lines[lineCounter]) or ("Material_properties" in lines[lineCounter])) and (
                "!" not in lines[lineCounter]):
            # the inside_counter parameter is defined so the data blocks for each parameter can be dealt with
            inside_counter = lineCounter + 1
            inside_counter = check_empty(lines, inside_counter)
            while lines[inside_counter][0] != '/':
                # jump over the commented and empty lines
                while (lines[inside_counter][0] == '!') or (lines[inside_counter][0:1] == '\t'):
                    inside_counter = inside_counter + 1
                    inside_counter = check_empty(lines, inside_counter)
                    if lines[inside_counter][0] == '/':
                        break
                if lines[inside_counter][0] == '/':
                    break
                # separate, extract and store the material parameters in each line using "SPACE" in a list
                params = lines[inside_counter].split()
                for paramCounter in np.arange(len(params)):
                    # In some cases, the lines are followed by a number of empty values.
                    # Therefore, the number of parameters are calculated to prevent any errors
                    # using the extracted data.
                    if params[paramCounter] == "":
                        last_item = paramCounter - 1
                        break
                    elif paramCounter == len(params) - 1:
                        last_item = len(params) - 1
                params = params[0:last_item + 1]  # params variable is updated to store only the non-empty arguments
                for item in np.arange(last_item + 1):
                    tmp_material.iat[0, item] = params[item]  # store all the parameters in the temporary DataFrame
                tmp_material_list.append(tmp_material.values.tolist()[0])  # store all the individual items in a list
                inside_counter = inside_counter + 1
                inside_counter = check_empty(lines, inside_counter)
                tmp_material = empty_tmp_material.copy(deep=True)  # clear the temporary dataframe to store next items

            # convert the list of all individuals to a DataFrame
            material = pd.DataFrame(tmp_material_list, columns=['No', 'E', 'G', 'rho', 'fc', 'tau0', 'verification',
                                                                'shear_model', 'drift_S', 'drift_F', 'mu', 'Gc',
                                                                'beta'])
            material = material.astype(float)  # convert all the variables to float
            material['No'] = material['No'].astype(int)  # the material numbers should be integers
            material = material.set_index('No')  # set the material number as the index
            # Convert the dataframe to an XlsxWriter Excel object.
            material.to_excel(writer, sheet_name='material')

        # find the parameters for floors
        if (("solaio" in lines[lineCounter]) or ("floors" in lines[lineCounter])) and ("!" not in lines[lineCounter]):
            # the inside_counter parameter is defined so the data blocks for each parameter can be dealt with
            inside_counter = lineCounter + 1
            inside_counter = check_empty(lines, inside_counter)
            while lines[inside_counter][0] != '/':
                # jump over the commented and empty lines
                while (lines[inside_counter][0] == '!') or (lines[inside_counter][0:1] == '\t'):
                    inside_counter = inside_counter + 1
                    inside_counter = check_empty(lines, inside_counter)
                    if lines[inside_counter][0] == '/':
                        break
                if lines[inside_counter][0] == '/':
                    break
                # separate, extract and store the floor parameters in each line using "SPACE" in a list
                params = lines[inside_counter].split()
                for paramCounter in np.arange(len(params)):
                    # In some cases, the lines are followed by a number of empty values.
                    # Therefore, the number of parameters are calculated to prevent any errors
                    # using the extracted data.
                    if params[paramCounter] == "":
                        last_item = paramCounter - 1
                        break
                    elif paramCounter == len(params) - 1:
                        last_item = len(params) - 1
                params = params[0:last_item + 1]  # params variable is updated to store only the non-empty arguments
                for item in np.arange(last_item + 1):
                    if "°" in params[item]:
                        params[item] = (float(params[item][0:len(params[item]) - 1]) / 180) * math.pi
                    tmp_floor.iat[0, item] = params[item]  # store all the parameters in the temporary DataFrame
                tmp_floor_list.append(tmp_floor.values.tolist()[0])  # store all the individual items in a list
                inside_counter = inside_counter + 1
                inside_counter = check_empty(lines, inside_counter)

            # convert the list of all individuals to a DataFrame
            floor = pd.DataFrame(tmp_floor_list, columns=['No', 'nI', 'nJ', 'nK', 'nL', 'thickness', 'E1', 'E2',
                                                          'Poisson', 'G', 'angle'])
            floor = floor.astype(float)  # convert all the variables to float
            # the floor and node numbers should be integers
            floor[['No', 'nI', 'nJ', 'nK', 'nL']] = floor[['No', 'nI', 'nJ', 'nK', 'nL']].astype(int)
            floor = floor.set_index('No')  # set the floor number as the index
            # Convert the dataframe to an XlsxWriter Excel object.
            floor.to_excel(writer, sheet_name='floor')

        # find the parameters for restraints
        if (("vincoli" in lines[lineCounter]) or ("Restraints" in lines[lineCounter])) and ("!" not in lines[lineCounter]):
            # the inside_counter parameter is defined so the data blocks for each parameter can be dealt with
            inside_counter = lineCounter + 1
            inside_counter = check_empty(lines, inside_counter)
            while lines[inside_counter][0] != '/':
                # jump over the commented and empty lines
                while (lines[inside_counter][0] == '!') or (lines[inside_counter][0:1] == '\t'):
                    inside_counter = inside_counter + 1
                    inside_counter = check_empty(lines, inside_counter)
                    if lines[inside_counter][0] == '/':
                        break
                if lines[inside_counter][0] == '/':
                    break
                # separate, extract and store the restraint parameters in each line using "SPACE" in a list
                params = lines[inside_counter].split()
                for paramCounter in np.arange(len(params)):
                    # In some cases, the lines are followed by a number of empty values.
                    # Therefore, the number of parameters are calculated to prevent any errors
                    # using the extracted data.
                    if params[paramCounter] == "":
                        last_item = paramCounter - 1
                        break
                    elif paramCounter == len(params) - 1:
                        last_item = len(params) - 1
                params = params[0:last_item + 1]  # params variable is updated to store only the non-empty arguments
                # ## the 2D case
                if len(params) == 4:
                    for item in np.arange(last_item + 1):
                        # just put the node number in its place in the temporary DataFrame
                        if item == 0:
                            tmp_restraint.iat[0, item] = params[item]
                        elif item == 1:
                            # just put the DOF restraints in their places in the temporary DataFrame
                            if params[item] == 'V' or params[item] == '1' or params[item] == 'v':
                                tmp_restraint.iat[0, 2 * item - 1] = '1'
                                tmp_restraint.iat[0, 2 * item] = '1'
                            else:
                                tmp_restraint.iat[0, 2 * item - 1] = '0'
                                tmp_restraint.iat[0, 2 * item] = '0'
                        elif item == 2:
                            if params[item] == 'V' or params[item] == '1' or params[item] == 'v':
                                tmp_restraint.iat[0, 2 * item - 1] = '1'
                            else:
                                tmp_restraint.iat[0, 2 * item - 1] = '0'
                        elif item == 3:
                            if params[item] == 'V' or params[item] == '1' or params[item] == 'v':
                                tmp_restraint.iat[0, 2 * item - 2] = '1'
                                tmp_restraint.iat[0, 2 * item - 1] = '1'
                            else:
                                tmp_restraint.iat[0, 2 * item - 2] = '0'
                                tmp_restraint.iat[0, 2 * item - 1] = '0'
                # ## the 3D case
                else:
                    for item in np.arange(last_item + 1):
                        # just put the node number in its place
                        if item == 0:
                            tmp_restraint.iat[0, item] = params[item]
                        else:
                            # just put the DOF restraints in their places in the temporary DataFrame
                            if params[item] == 'V' or params[item] == '1' or params[item] == 'v':
                                tmp_restraint.iat[0, item] = '1'
                            else:
                                tmp_restraint.iat[0, item] = '0'
                tmp_restraint_list.append(tmp_restraint.values.tolist()[0])  # store all the individual items in a list
                inside_counter = inside_counter + 1
                inside_counter = check_empty(lines, inside_counter)

            # convert the list of all individuals to a DataFrame
            restraint = pd.DataFrame(tmp_restraint_list, columns=['Node', 'x', 'y', 'z', 'rx', 'ry'])
            restraint = restraint.astype(int)  # convert all the variables to integer
            restraint = restraint.set_index('Node')  # set the node number as the index
            # Convert the dataframe to an XlsxWriter Excel object.
            restraint.to_excel(writer, sheet_name='restraints')

        # find the parameters for floor levels
        if ("Piani" in lines[lineCounter]) and ("!" not in lines[lineCounter]):
            # the inside_counter parameter is defined so the data blocks for each parameter can be dealt with
            inside_counter = lineCounter
            inside_counter = check_empty(lines, inside_counter)
            while (lines[inside_counter][0] == '!') or (lines[inside_counter][0:1] == '\t'):
                inside_counter = inside_counter + 1
            # separate, extract and store the floor level parameters in each line using "SPACE" in a list
            params = lines[inside_counter].split()
            for paramCounter in np.arange(len(params)):
                # In some cases, the lines are followed by a number of empty values.
                # Therefore, the number of parameters are calculated to prevent any errors
                # using the extracted data.
                if params[paramCounter] == "":
                    last_item = paramCounter - 1
                    break
                elif paramCounter == len(params) - 1:
                    last_item = len(params) - 1
            params = params[1:last_item + 1]  # params variable is updated to store only the non-empty arguments
            for item in np.arange(last_item):
                # store all the parameters in the temporary DataFrame
                tmp_floor_level.iat[0, 0] = params[item]
                tmp_floor_level.iat[0, 1] = "0"
                tmp_floor_level.iat[0, 2] = "0"
                tmp_floor_level.iat[0, 3] = "1"
                # store all the individual items in a list
                tmp_floor_level_list.append(tmp_floor_level.values.tolist()[0])

            # convert the list of all individuals to a DataFrame
            floor_level = pd.DataFrame(tmp_floor_level_list, columns=['h', 'zAxis1', 'zAxis2', 'zAxis3'])
            floor_level = floor_level.astype(float)  # convert all the variables to float
            # convert the variables related to the zAxes to integer
            floor_level[['zAxis1', 'zAxis2', 'zAxis3']] = floor_level[['zAxis1', 'zAxis2', 'zAxis3']].astype(int)
            floor_level = floor_level.set_index('h')  # set the story level as the index
            # Convert the dataframe to an XlsxWriter Excel object.
            floor_level.to_excel(writer, sheet_name='floor levels')

        # find the parameters for 2D nodes
        if (("nodi2d" in lines[lineCounter]) or ("nodes_2d" in lines[lineCounter])) and ("!" not in lines[lineCounter]):
            # the inside_counter parameter is defined so the data blocks for each parameter can be dealt with
            inside_counter = lineCounter + 1
            inside_counter = check_empty(lines, inside_counter)
            while lines[inside_counter][0] != '/':
                # jump over the commented and empty lines
                while (lines[inside_counter][0] == '!') or (lines[inside_counter][0:1] == '\t'):
                    inside_counter = inside_counter + 1
                    inside_counter = check_empty(lines, inside_counter)
                    if lines[inside_counter][0] == '/':
                        break
                if lines[inside_counter][0] == '/':
                    break
                # separate, extract and store the 2D node parameters in each line using "SPACE" in a list
                params = lines[inside_counter].split()
                for paramCounter in np.arange(len(params)):
                    # In some cases, the lines are followed by a number of empty values.
                    # Therefore, the number of parameters are calculated to prevent any errors
                    # using the extracted data.
                    if params[paramCounter] == "":
                        last_item = paramCounter - 1
                        break
                    elif paramCounter == len(params) - 1:
                        last_item = len(params) - 1
                params = params[0:last_item + 1]  # params variable is updated to store only the non-empty arguments
                # find the maximum node number tag for future usages
                if max_node_number < int(params[0]):
                    max_node_number = int(params[0])
                for item in np.arange(5):
                    tmp_n2d.iat[0, item] = params[item]  # store all the parameters in the temporary DataFrame
                    if "P" in params[item]:
                        tmp_n2d.iat[0, item] = "P"  # store the node shape(R: Rectangular, P: Polygonal, N: None)
                # convert the Node and Wall number variables to integer
                tmp_n2d[['Node', 'wall']] = tmp_n2d[['Node', 'wall']].astype(int)
                # convert the x_loc and z variables to float
                tmp_n2d[['x_loc', 'z']] = tmp_n2d[['x_loc', 'z']].astype(float)

                tmp_n2d.at['0', 'x'] = wall.at[tmp_n2d.at['0', 'wall'], 'x0'] + tmp_n2d.at['0', 'x_loc'] * math.cos(
                    wall.at[tmp_n2d.at['0', 'wall'], 'angle'])
                tmp_n2d.at['0', 'y'] = wall.at[tmp_n2d.at['0', 'wall'], 'y0'] + tmp_n2d.at['0', 'x_loc'] * math.sin(
                    wall.at[tmp_n2d.at['0', 'wall'], 'angle'])
                if params[4] == 'R':
                    for item in np.arange(5, 11):
                        # store the parameters of rectangular nodes in the temporary DataFrame
                        tmp_n2d.iat[0, item] = params[item]
                    # convert the corresponding variables to float
                    tmp_n2d[['rho', 'thickness', 'offsetXloc1', 'offsetXloc2', 'offsetZ1', 'offsetZ2']] = \
                        tmp_n2d[['rho', 'thickness', 'offsetXloc1', 'offsetXloc2', 'offsetZ1', 'offsetZ2']].astype(float)

                    tmp_n2d.at['0', 'offsetXloc1'] = -1 * tmp_n2d.at['0', 'offsetXloc1']
                    tmp_n2d.at['0', 'offsetZ2'] = -1 * tmp_n2d.at['0', 'offsetZ2']
                    tmp_n2d.at['0', 'offsetX1'] = tmp_n2d.at['0', 'x'] + tmp_n2d.at['0', 'offsetXloc1'] * math.cos(
                        wall.at[tmp_n2d.at['0', 'wall'], 'angle'])
                    tmp_n2d['offsetX2'].at['0'] = tmp_n2d.at['0', 'x'] + tmp_n2d.at['0', 'offsetXloc2'] * math.cos(
                        wall.at[tmp_n2d.at['0', 'wall'], 'angle'])
                    tmp_n2d['offsetY1'].at['0'] = tmp_n2d.at['0', 'y'] + tmp_n2d.at['0', 'offsetXloc1'] * math.sin(
                        wall.at[tmp_n2d.at['0', 'wall'], 'angle'])
                    tmp_n2d['offsetY2'].at['0'] = tmp_n2d.at['0', 'y'] + tmp_n2d.at['0', 'offsetXloc2'] * math.sin(
                        wall.at[tmp_n2d.at['0', 'wall'], 'angle'])
                elif 'P' in params[4]:
                    poly_index = 4
                    while poly_index < last_item:
                        # store the parameters of polygonal nodes in the temporary DataFrame
                        for nodeItem in np.arange(4):
                            tmp_poly2d['Node - Global'].iat[nodeItem] = int(params[0])
                        tmp_index = params[poly_index]
                        tmp_index = str(int(tmp_index[1]) - 1)
                        tmp_poly2d.at[tmp_index, 'rho'] = float(params[poly_index + 1])
                        tmp_poly2d.at[tmp_index, 'thickness'] = float(params[poly_index + 2])
                        tmp_poly2d.at[tmp_index, 'offsetXloc1'] = min(float(params[poly_index + 3]),
                                                                      float(params[poly_index + 5]),
                                                                      float(params[poly_index + 7]),
                                                                      float(params[poly_index + 9]))
                        tmp_poly2d.at[tmp_index, 'offsetXloc2'] = max(float(params[poly_index + 3]),
                                                                      float(params[poly_index + 5]),
                                                                      float(params[poly_index + 7]),
                                                                      float(params[poly_index + 9]))
                        tmp_poly2d.at[tmp_index, 'offsetZ1'] = max(float(params[poly_index + 4]),
                                                                   float(params[poly_index + 6]),
                                                                   float(params[poly_index + 8]),
                                                                   float(params[poly_index + 10]))
                        tmp_poly2d.at[tmp_index, 'offsetZ2'] = min(float(params[poly_index + 4]),
                                                                   float(params[poly_index + 6]),
                                                                   float(params[poly_index + 8]),
                                                                   float(params[poly_index + 10]))
                        tmp_poly2d.at[tmp_index, 'offsetX1'] = tmp_n2d.at['0', 'x'] + tmp_poly2d.at[
                            tmp_index, 'offsetXloc1'] * math.cos(wall.at[tmp_n2d.at['0', 'wall'], 'angle'])
                        tmp_poly2d.at[tmp_index, 'offsetX2'] = tmp_n2d.at['0', 'x'] + tmp_poly2d.at[
                            tmp_index, 'offsetXloc2'] * math.cos(wall.at[tmp_n2d.at['0', 'wall'], 'angle'])
                        tmp_poly2d.at[tmp_index, 'offsetY1'] = tmp_n2d.at['0', 'y'] + tmp_poly2d.at[
                            tmp_index, 'offsetXloc1'] * math.sin(wall.at[tmp_n2d.at['0', 'wall'], 'angle'])
                        tmp_poly2d.at[tmp_index, 'offsetY2'] = tmp_n2d.at['0', 'y'] + tmp_poly2d.at[
                            tmp_index, 'offsetXloc2'] * math.sin(wall.at[tmp_n2d.at['0', 'wall'], 'angle'])
                        poly_index = poly_index + 11

                if "P" in params[4]:
                    for polyItem in np.arange(4):
                        # store all the individual items in a list
                        tmp_poly2d_list.append(tmp_poly2d.values.tolist()[polyItem])
                tmp_n2d_list.append(tmp_n2d.values.tolist()[0])  # store all the individual items in a list
                inside_counter = inside_counter + 1
                inside_counter = check_empty(lines, inside_counter)
                tmp_n2d = empty_tmp_n2d.copy(deep=True)  # clear the temporary dataframe to store next items
                tmp_poly2d = empty_tmp_poly2d.copy(deep=True)  # clear the temporary dataframe to store next items

            # convert the list of all individuals to a DataFrame
            n2d = pd.DataFrame(tmp_n2d_list, columns=['Node', 'wall', 'x_loc', 'z', 'type', 'rho', 'thickness',
                                                      'offsetXloc1', 'offsetXloc2', 'offsetZ1', 'offsetZ2',
                                                      'repartition1', 'repartition2', 'x', 'y', 'offsetX1', 'offsetX2',
                                                      'offsetY1', 'offsetY2'])
            # set the node number as the index
            n2d = n2d.set_index('Node')
            # convert the list of all individuals to a DataFrame
            poly2d = pd.DataFrame(tmp_poly2d_list, columns=['Node - Global', 'Node - Local', 'rho', 'thickness',
                                                            'offsetXloc1', 'offsetXloc2', 'offsetZ1', 'offsetZ2',
                                                            'offsetX1', 'offsetX2', 'offsetY1', 'offsetY2'])
            # set the global node number as the index
            poly2d = poly2d.set_index('Node - Global')
            # Convert the dataframe to an XlsxWriter Excel object.
            poly2d.to_excel(writer, sheet_name='polygon 2d')

        # find the repartition properties for 2d nodes
        if (("ripartizione" in lines[lineCounter]) or ("2D_mass_sharing" in lines[lineCounter])) and (
                "!" not in lines[lineCounter]):
            # the inside_counter parameter is defined so the data blocks for each parameter can be dealt with
            inside_counter = lineCounter + 1
            inside_counter = check_empty(lines, inside_counter)
            while lines[inside_counter][0] != '/':
                # jump over the commented and empty lines
                while (lines[inside_counter][0] == '!') or (lines[inside_counter][0:1] == '\t'):
                    inside_counter = inside_counter + 1
                    inside_counter = check_empty(lines, inside_counter)
                    if lines[inside_counter][0] == '/':
                        break
                if lines[inside_counter][0] == '/':
                    break
                # separate, extract and store the 2d mass sharing parameters in each line using "SPACE" in a list
                params = lines[inside_counter].split()
                for paramCounter in np.arange(len(params)):
                    # In some cases, the lines are followed by a number of empty values.
                    # Therefore, the number of parameters are calculated to prevent any errors
                    # using the extracted data.
                    if params[paramCounter] == "":
                        last_item = paramCounter - 1
                        break
                    elif paramCounter == len(params) - 1:
                        last_item = len(params) - 1
                params = params[0:last_item + 1]  # params variable is updated to store only the non-empty arguments
                inside_counter = inside_counter + 1
                inside_counter = check_empty(lines, inside_counter)
                # convert the mass sharing parameters to integer
                n2d.at[int(params[0]), 'repartition1'] = int(params[1])
                n2d.at[int(params[0]), 'repartition2'] = int(params[2])
            # Convert the dataframe to an XlsxWriter Excel object.
            n2d.to_excel(writer, sheet_name='node 2d')

        # find the parameters for 3D nodes
        if (("nodi3d" in lines[lineCounter]) or ("nodes_3d" in lines[lineCounter])) and ("!" not in lines[lineCounter]):
            # the inside_counter parameter is defined so the data blocks for each parameter can be dealt with
            inside_counter = lineCounter + 1
            inside_counter = check_empty(lines, inside_counter)
            while lines[inside_counter][0] != '/':
                # jump over the commented and empty lines
                while (lines[inside_counter][0] == '!') or (lines[inside_counter][0:1] == '\t'):
                    inside_counter = inside_counter + 1
                    inside_counter = check_empty(lines, inside_counter)
                    if lines[inside_counter][0] == '/':
                        break
                if lines[inside_counter][0] == '/':
                    break
                # separate, extract and store the 3D node parameters in each line using "SPACE" in a list
                params = lines[inside_counter].split()
                for paramCounter in np.arange(len(params)):
                    # In some cases, the lines are followed by a number of empty values.
                    # Therefore, the number of parameters are calculated to prevent any errors
                    # using the extracted data.
                    if params[paramCounter] == "":
                        last_item = paramCounter - 1
                        break
                    elif paramCounter == len(params) - 1:
                        last_item = len(params) - 1
                params = params[0:last_item + 1]  # params variable is updated to store only the non-empty arguments
                # find the maximum node number tag for future usages
                if max_node_number < int(params[0]):
                    max_node_number = int(params[0])
                for item in np.arange(6):
                    tmp_n3d.iat[0, item] = params[item]  # store all the parameters in the temporary DataFrame
                # convert the Node and Wall number variables to integer
                tmp_n3d[['Node', 'n_wall2', 'wall1', 'wall2']] = \
                    tmp_n3d[['Node', 'n_wall2', 'wall1', 'wall2']].astype(int)
                # convert the z variable to float
                tmp_n3d['z'] = tmp_n3d['z'].astype(float)
                # store the 3D node shapes (R: Rectangular, P: Polygonal, N: None)
                if "N" in tmp_n3d.at['0', 'type']:
                    if "P" in params[6]:
                        tmp_n3d.at['0', 'type'] = tmp_n3d.at['0', 'type'] + "P"
                    else:
                        tmp_n3d.at['0', 'type'] = tmp_n3d.at['0', 'type'] + params[6]
                        if "R" in params[6]:
                            tmp_index = 12
                            for item in np.arange(7, 13):
                                # store the parameters of none/rectangular nodes in the temporary DataFrame
                                tmp_n3d.iat[0, tmp_index] = float(params[item])
                                tmp_index = tmp_index + 1
                            tmp_n3d.at['0', 'offsetXloc21'] = -1 * tmp_n3d.at['0', 'offsetXloc21']
                            tmp_n3d.at['0', 'offsetZ22'] = -1 * tmp_n3d.at['0', 'offsetZ22']
                elif "R" in tmp_n3d.at['0', 'type']:
                    for item in np.arange(6, 12):
                        # store the parameters of rectangular nodes in the temporary DataFrame
                        tmp_n3d.iat[0, item] = float(params[item])
                    tmp_n3d.at['0', 'offsetXloc11'] = -1 * tmp_n3d.at['0', 'offsetXloc11']
                    tmp_n3d.at['0', 'offsetZ12'] = -1 * tmp_n3d.at['0', 'offsetZ12']
                    # store the 3D node shapes (R: Rectangular, P: Polygonal, N: None)
                    if "P" in params[12]:
                        tmp_n3d.at['0', 'type'] = tmp_n3d.at['0', 'type'] + "P"
                    else:
                        tmp_n3d.at['0', 'type'] = tmp_n3d.at['0', 'type'] + params[12]
                        if "R" in params[12]:
                            for item in np.arange(13, 19):
                                # store the parameters of rectangular/rectangular nodes in the temporary DataFrame
                                tmp_n3d.iat[0, item - 1] = float(params[item])
                            tmp_n3d.at['0', 'offsetXloc21'] = -1 * tmp_n3d.at['0', 'offsetXloc21']
                            tmp_n3d.at['0', 'offsetZ22'] = -1 * tmp_n3d.at['0', 'offsetZ22']
                elif "P" in tmp_n3d.at['0', 'type']:
                    loc_index = params.index('|')
                    # store the 3D node shapes (R: Rectangular, P: Polygonal, N: None)
                    if "P" in params[loc_index + 1]:
                        tmp_n3d.at['0', 'type'] = "PP"
                    else:
                        tmp_n3d.at['0', 'type'] = "P" + params[loc_index + 1]
                        if "R" in params[loc_index + 1]:
                            for item in np.arange(loc_index + 2, loc_index + 8):
                                tmp_index = 12
                                # store the parameters of polygonal/rectangular nodes in the temporary DataFrame
                                tmp_n3d.iat[0, tmp_index] = float(params[item])
                                tmp_index = tmp_index + 1
                            tmp_n3d.at['0', 'offsetXloc21'] = -1 * tmp_n3d.at['0', 'offsetXloc21']
                            tmp_n3d.at['0', 'offsetZ22'] = -1 * tmp_n3d.at['0', 'offsetZ22']
                # initialize A and b matrices
                A = np.zeros((2, 2))
                b = np.zeros((2, 1))
                A[0][0] = math.cos(wall.at[tmp_n3d.at['0', 'wall1'], 'angle'])
                A[0][1] = -1 * math.cos(wall.at[tmp_n3d.at['0', 'wall2'], 'angle'])
                A[1][0] = math.sin(wall.at[tmp_n3d.at['0', 'wall1'], 'angle'])
                A[1][1] = -1 * math.sin(wall.at[tmp_n3d.at['0', 'wall2'], 'angle'])
                b[0][0] = wall.at[tmp_n3d.at['0', 'wall2'], 'x0'] - wall.at[tmp_n3d.at['0', 'wall1'], 'x0']
                b[1][0] = wall.at[tmp_n3d.at['0', 'wall2'], 'y0'] - wall.at[tmp_n3d.at['0', 'wall1'], 'y0']
                x = inv(np.matrix(A)).dot(b)
                tmp_n3d.at['0', 'x'] = float(wall.at[tmp_n3d.at['0', 'wall1'], 'x0'] + x[0][0] * math.cos(
                    wall.at[tmp_n3d.at['0', 'wall1'], 'angle']))
                tmp_n3d.at['0', 'y'] = float(wall.at[tmp_n3d.at['0', 'wall1'], 'y0'] + x[0][0] * math.sin(
                    wall.at[tmp_n3d.at['0', 'wall1'], 'angle']))

                tmp_type = tmp_n3d.at['0', 'type']
                if "R" in tmp_type[0]:  # if the node shape for the 1st wall is rectangular
                    # store the parameters of rectangular nodes in the temporary DataFrame
                    tmp_n3d.at['0', 'offsetX11'] = tmp_n3d.at['0', 'x'] + tmp_n3d.at['0', 'offsetXloc11'] * math.cos(
                        wall.at[tmp_n3d.at['0', 'wall1'], 'angle'])
                    tmp_n3d.at['0', 'offsetX12'] = tmp_n3d.at['0', 'x'] + tmp_n3d.at['0', 'offsetXloc12'] * math.cos(
                        wall.at[tmp_n3d.at['0', 'wall1'], 'angle'])
                    tmp_n3d.at['0', 'offsetY11'] = tmp_n3d.at['0', 'y'] + tmp_n3d.at['0', 'offsetXloc11'] * math.sin(
                        wall.at[tmp_n3d.at['0', 'wall1'], 'angle'])
                    tmp_n3d.at['0', 'offsetY12'] = tmp_n3d.at['0', 'y'] + tmp_n3d.at['0', 'offsetXloc12'] * math.sin(
                        wall.at[tmp_n3d.at['0', 'wall1'], 'angle'])
                if "R" in tmp_type[1]:  # if the node shape for the 2nd wall is rectangular
                    # store the parameters of rectangular nodes in the temporary DataFrame
                    tmp_n3d.at['0', 'offsetX21'] = tmp_n3d.at['0', 'x'] + tmp_n3d.at['0', 'offsetXloc21'] * math.cos(
                        wall.at[tmp_n3d.at['0', 'wall2'], 'angle'])
                    tmp_n3d.at['0', 'offsetX22'] = tmp_n3d.at['0', 'x'] + tmp_n3d.at['0', 'offsetXloc22'] * math.cos(
                        wall.at[tmp_n3d.at['0', 'wall2'], 'angle'])
                    tmp_n3d.at['0', 'offsetY21'] = tmp_n3d.at['0', 'y'] + tmp_n3d.at['0', 'offsetXloc21'] * math.sin(
                        wall.at[tmp_n3d.at['0', 'wall2'], 'angle'])
                    tmp_n3d.at['0', 'offsetY22'] = tmp_n3d.at['0', 'y'] + tmp_n3d.at['0', 'offsetXloc22'] * math.sin(
                        wall.at[tmp_n3d.at['0', 'wall2'], 'angle'])
                if "P" in tmp_type[0]:  # if the node shape for the 1st wall is polygonal
                    # store the parameters of polygonal nodes in the temporary DataFrame
                    for nodeItem in np.arange(4):
                        tmp_poly3d1['Node - Global'].iat[nodeItem] = int(params[0])
                    loc_index = params.index('|')
                    for item in np.arange(5, loc_index):
                        if "P" in params[item]:
                            tmp_index = params[item]
                            tmp_index = str(int(tmp_index[1]) - 1)
                            tmp_poly3d1.at[tmp_index, 'rho'] = float(params[item + 1])
                            tmp_poly3d1.at[tmp_index, 'thickness'] = float(params[item + 2])
                            tmp_poly3d1.at[tmp_index, 'offsetXloc1'] = min(float(params[item + 3]),
                                                                           float(params[item + 5]),
                                                                           float(params[item + 7]),
                                                                           float(params[item + 9]))
                            tmp_poly3d1.at[tmp_index, 'offsetXloc2'] = max(float(params[item + 3]),
                                                                           float(params[item + 5]),
                                                                           float(params[item + 7]),
                                                                           float(params[item + 9]))
                            tmp_poly3d1.at[tmp_index, 'offsetZ1'] = min(float(params[item + 4]),
                                                                        float(params[item + 6]),
                                                                        float(params[item + 8]),
                                                                        float(params[item + 10]))
                            tmp_poly3d1.at[tmp_index, 'offsetZ2'] = max(float(params[item + 4]),
                                                                        float(params[item + 6]),
                                                                        float(params[item + 8]),
                                                                        float(params[item + 10]))
                            tmp_poly3d1.at[tmp_index, 'offsetX1'] = tmp_n3d.at['0', 'x'] + tmp_poly3d1.at[
                                tmp_index, 'offsetXloc1'] * math.cos(wall.at[tmp_n3d.at['0', 'wall1'], 'angle'])
                            tmp_poly3d1.at[tmp_index, 'offsetX2'] = tmp_n3d.at['0', 'x'] + tmp_poly3d1.at[
                                tmp_index, 'offsetXloc2'] * math.cos(wall.at[tmp_n3d.at['0', 'wall1'], 'angle'])
                            tmp_poly3d1.at[tmp_index, 'offsetY1'] = tmp_n3d.at['0', 'y'] + tmp_poly3d1.at[
                                tmp_index, 'offsetXloc1'] * math.sin(wall.at[tmp_n3d.at['0', 'wall1'], 'angle'])
                            tmp_poly3d1.at[tmp_index, 'offsetY2'] = tmp_n3d.at['0', 'y'] + tmp_poly3d1.at[
                                tmp_index, 'offsetXloc2'] * math.sin(wall.at[tmp_n3d.at['0', 'wall1'], 'angle'])
                if "P" in tmp_type[1]:
                    # store the parameters of polygonal nodes in the temporary DataFrame
                    for nodeItem in np.arange(4):
                        tmp_poly3d2['Node - Global'].iat[nodeItem] = int(params[0])
                    if "N" in tmp_type[0]:
                        loc_index = 6
                    elif "R" in tmp_type[0]:
                        loc_index = 12
                    elif "P" in tmp_type[0]:
                        loc_index = params.index('|') + 1
                    for item in np.arange(loc_index, len(params)):
                        if "P" in params[item]:
                            tmp_index = params[item]
                            tmp_index = str(int(tmp_index[1]) - 1)
                            tmp_poly3d2.at[tmp_index, 'rho'] = float(params[item + 1])
                            tmp_poly3d2.at[tmp_index, 'thickness'] = float(params[item + 2])
                            tmp_poly3d2.at[tmp_index, 'offsetXloc1'] = min(float(params[item + 3]),
                                                                           float(params[item + 5]),
                                                                           float(params[item + 7]),
                                                                           float(params[item + 9]))
                            tmp_poly3d2.at[tmp_index, 'offsetXloc2'] = max(float(params[item + 3]),
                                                                           float(params[item + 5]),
                                                                           float(params[item + 7]),
                                                                           float(params[item + 9]))
                            tmp_poly3d2.at[tmp_index, 'offsetZ1'] = min(float(params[item + 4]), 
                                                                        float(params[item + 6]),
                                                                        float(params[item + 8]),
                                                                        float(params[item + 10]))
                            tmp_poly3d2.at[tmp_index, 'offsetZ2'] = max(float(params[item + 4]),
                                                                        float(params[item + 6]),
                                                                        float(params[item + 8]),
                                                                        float(params[item + 10]))
                            tmp_poly3d2.at[tmp_index, 'offsetX1'] = tmp_n3d.at['0', 'x'] + tmp_poly3d2.at[
                                tmp_index, 'offsetXloc1'] * math.cos(wall.at[tmp_n3d.at['0', 'wall2'], 'angle'])
                            tmp_poly3d2.at[tmp_index, 'offsetX2'] = tmp_n3d.at['0', 'x'] + tmp_poly3d2.at[
                                tmp_index, 'offsetXloc2'] * math.cos(wall.at[tmp_n3d.at['0', 'wall2'], 'angle'])
                            tmp_poly3d2.at[tmp_index, 'offsetY1'] = tmp_n3d.at['0', 'y'] + tmp_poly3d2.at[
                                tmp_index, 'offsetXloc1'] * math.sin(wall.at[tmp_n3d.at['0', 'wall2'], 'angle'])
                            tmp_poly3d2.at[tmp_index, 'offsetY2'] = tmp_n3d.at['0', 'y'] + tmp_poly3d2.at[
                                tmp_index, 'offsetXloc2'] * math.sin(wall.at[tmp_n3d.at['0', 'wall2'], 'angle'])
                tmp_n3d_list.append(tmp_n3d.values.tolist()[0])  # store all the individual items in a list
                if "P" in tmp_type[0]:
                    for polyItem in np.arange(4):
                        tmp_poly3d1_list.append(tmp_poly3d1.values.tolist()[polyItem])
                if "P" in tmp_type[1]:
                    for polyItem in np.arange(4):
                        tmp_poly3d2_list.append(tmp_poly3d2.values.tolist()[polyItem])
                inside_counter = inside_counter + 1
                inside_counter = check_empty(lines, inside_counter)
                tmp_n3d = empty_tmp_n3d.copy(deep=True)  # clear the temporary dataframe to store next items
                tmp_poly3d1 = empty_tmp_poly3d1.copy(deep=True)  # clear the temporary dataframe to store next items
                tmp_poly3d2 = empty_tmp_poly3d2.copy(deep=True)  # clear the temporary dataframe to store next items

            # convert the list of all individuals to a DataFrame
            n3d = pd.DataFrame(tmp_n3d_list, columns=['Node', 'n_wall2', 'wall1', 'wall2', 'z', 'type', 'rho1',
                                                      'thickness1', 'offsetXloc11', 'offsetXloc12', 'offsetZ11',
                                                      'offsetZ12', 'rho2', 'thickness2', 'offsetXloc21', 'offsetXloc22',
                                                      'offsetZ21', 'offsetZ22', 'x', 'y', 'offsetX11', 'offsetX12',
                                                      'offsetY11', 'offsetY12', 'offsetX21', 'offsetX22', 'offsetY21',
                                                      'offsetY22'])
            n3d = n3d.set_index('Node')  # set the node number as the index
            # convert the list of all individuals to a DataFrame
            poly3d1 = pd.DataFrame(tmp_poly3d1_list, columns=['Node - Global', 'Node - Local', 'rho', 'thickness',
                                                              'offsetXloc1', 'offsetXloc2', 'offsetZ1', 'offsetZ2',
                                                              'offsetX1', 'offsetX2', 'offsetY1', 'offsetY2'])
            # convert the list of all individuals to a DataFrame
            poly3d2 = pd.DataFrame(tmp_poly3d2_list, columns=['Node - Global', 'Node - Local', 'rho', 'thickness',
                                                              'offsetXloc1', 'offsetXloc2', 'offsetZ1', 'offsetZ2',
                                                              'offsetX1', 'offsetX2', 'offsetY1', 'offsetY2'])
            poly3d1 = poly3d1.set_index('Node - Global')  # set the global node number as the index
            poly3d2 = poly3d2.set_index('Node - Global')  # set the global node number as the index
            # Convert the dataframe to an XlsxWriter Excel object.
            n3d.to_excel(writer, sheet_name='node 3d')
            poly3d1.to_excel(writer, sheet_name='polygon 3d - 1')
            poly3d2.to_excel(writer, sheet_name='polygon 3d - 2')

        # find the parameters for elastic beams
        if (("traveElastica" in lines[lineCounter]) or ("Beam_elastic" in lines[lineCounter])) and (
                "!" not in lines[lineCounter]):
            # the inside_counter parameter is defined so the data blocks for each parameter can be dealt with
            inside_counter = lineCounter + 1
            inside_counter = check_empty(lines, inside_counter)
            while lines[inside_counter][0] != '/':
                # jump over the commented and empty lines
                while (lines[inside_counter][0] == '!') or (lines[inside_counter][0:1] == '\t'):
                    inside_counter = inside_counter + 1
                    inside_counter = check_empty(lines, inside_counter)
                    if lines[inside_counter][0] == '/':
                        break
                if lines[inside_counter][0] == '/':
                    break
                # separate, extract and store the elastic beam parameters in each line using "SPACE" in a list
                params = lines[inside_counter].split()
                for paramCounter in np.arange(len(params)):
                    # In some cases, the lines are followed by a number of empty values.
                    # Therefore, the number of parameters are calculated to prevent any errors
                    # using the extracted data.
                    if params[paramCounter] == "":
                        last_item = paramCounter - 1
                        break
                    elif paramCounter == len(params) - 1:
                        last_item = len(params) - 1
                params = params[0:last_item + 1]  # params variable is updated to store only the non-empty arguments
                for item in np.arange(last_item + 1):
                    tmp_elastic_beam.iat[0, item] = params[item]  # store all the parameters in the temporary DataFrame
                # store all the individual items in a list
                tmp_elastic_beam_list.append(tmp_elastic_beam.values.tolist()[0])
                inside_counter = inside_counter + 1
                inside_counter = check_empty(lines, inside_counter)
            # convert the list of all individuals to a DataFrame
            elastic_beam = pd.DataFrame(tmp_elastic_beam_list, columns=['No', 'wall', 'nodeI', 'nodeJ', 'mat', 'area',
                                                                       'J', 'deformIn', 'type', 'offXloc_I', 'offZ_I', 
                                                                       'offXloc_J', 'offZ_J'])
            elastic_beam = elastic_beam.astype(float)  # convert all the variables to float
            # convert the beam, wall, node, material, and beam type variables to integer
            elastic_beam[['No', 'wall', 'nodeI', 'nodeJ', 'mat', 'type']] = elastic_beam[['No', 'wall', 'nodeI', 'nodeJ',
                                                                                        'mat', 'type']].astype(int)
            elastic_beam = elastic_beam.set_index('No')  # set the beam number as the index
            # Convert the dataframe to an XlsxWriter Excel object.
            elastic_beam.to_excel(writer, sheet_name='elastic beam')

        # find the parameters for nonlinear beams
        if (("traveNonLineare" in lines[lineCounter]) or ("Beam_nonlinear" in lines[lineCounter])) and (
                "!" not in lines[lineCounter]):
            # the inside_counter parameter is defined so the data blocks for each parameter can be dealt with
            inside_counter = lineCounter + 1
            inside_counter = check_empty(lines, inside_counter)
            while lines[inside_counter][0] != '/':
                # jump over the commented and empty lines
                while (lines[inside_counter][0] == '!') or (lines[inside_counter][0:1] == '\t'):
                    inside_counter = inside_counter + 1
                    inside_counter = check_empty(lines, inside_counter)
                    if lines[inside_counter][0] == '/':
                        break
                if lines[inside_counter][0] == '/':
                    break
                # separate, extract and store the nonlinear beam parameters in each line using "SPACE" in a list
                params = lines[inside_counter].split()
                for paramCounter in np.arange(len(params)):
                    # In some cases, the lines are followed by a number of empty values.
                    # Therefore, the number of parameters are calculated to prevent any errors
                    # using the extracted data.
                    if params[paramCounter] == "":
                        last_item = paramCounter - 1
                        break
                    elif paramCounter == len(params) - 1:
                        last_item = len(params) - 1
                params = params[0:last_item + 1]  # params variable is updated to store only the non-empty arguments
                for item in np.arange(last_item + 1):
                    tmp_nl_beam.iat[0, item] = params[item]  # store all the parameters in the temporary DataFrame
                tmp_nl_beam_list.append(tmp_nl_beam.values.tolist()[0])  # store all the individual items in a list
                inside_counter = inside_counter + 1
                inside_counter = check_empty(lines, inside_counter)
            # convert the list of all individuals to a DataFrame
            nl_beam = pd.DataFrame(tmp_nl_beam_list, columns=['No', 'wall', 'nodeI', 'nodeJ', 'mat', 'area', 'J',
                                                             'offXloc_I', 'offZ_I', 'offXloc_J', 'offZ_J', 'type', 
                                                             'deformIn', 'Wpl'])
            nl_beam = nl_beam.astype(float)  # convert all the variables to float
            # convert the beam, wall, node, material, and beam type variables to integer
            nl_beam[['No', 'wall', 'nodeI', 'nodeJ', 'mat', 'type']] = nl_beam[['No', 'wall', 'nodeI', 'nodeJ', 'mat',
                                                                              'type']].astype(int)
            nl_beam = nl_beam.set_index('No')  # set the beam number as the index
            # Convert the dataframe to an XlsxWriter Excel object.
            nl_beam.to_excel(writer, sheet_name='nonlinear beam')

        # find the parameters for elements
        if (("macroelementoCalibrato" in lines[lineCounter]) or ("macroelemento" in lines[lineCounter]) or (
                "elementi" in lines[lineCounter]) or ("elementoOPCM3274" in lines[lineCounter]) or (
                    "macroelements" in lines[lineCounter]) or ("bilinear" in lines[lineCounter])) and (
                "!" not in lines[lineCounter]):
            # the inside_counter parameter is defined so the data blocks for each parameter can be dealt with
            inside_counter = lineCounter + 1
            inside_counter = check_empty(lines, inside_counter)
            while lines[inside_counter][0] != '/':
                # jump over the commented and empty lines
                while (lines[inside_counter][0] == '!') or (lines[inside_counter][0:1] == '\t'):
                    inside_counter = inside_counter + 1
                    inside_counter = check_empty(lines, inside_counter)
                    if lines[inside_counter][0] == '/':
                        break
                if lines[inside_counter][0] == '/':
                    break
                element_number = element_number + 1
                # separate, extract and store the macroelement parameters in each line using "SPACE" in a list
                params = lines[inside_counter].split()
                for paramCounter in np.arange(len(params)):
                    # In some cases, the lines are followed by a number of empty values.
                    # Therefore, the number of parameters are calculated to prevent any errors
                    # using the extracted data.
                    if params[paramCounter] == "":
                        last_item = paramCounter - 1
                        break
                    elif paramCounter == len(params) - 1:
                        last_item = len(params) - 1
                params = params[0:last_item + 1]  # params variable is updated to store only the non-empty arguments
                for item in np.arange(last_item + 1):
                    tmp_element.iat[0, item] = params[item]  # store all the parameters in the temporary DataFrame
                # convert the beam, wall, node, material, and beam type variables to integer
                tmp_element[['No', 'wall', 'nodeI', 'nodeJ', 'mat', 'type']] = tmp_element[
                    ['No', 'wall', 'nodeI', 'nodeJ', 'mat', 'type']].astype(int)
                # convert the other values to float
                tmp_element[['xBar', 'zBar', 'L', 'H', 't']] = \
                    tmp_element[['xBar', 'zBar', 'L', 'H', 't']].astype(float)
                tmp_element_list.append(tmp_element.values.tolist()[0])  # store all the individual items in a list
                inside_counter = inside_counter + 1
                inside_counter = check_empty(lines, inside_counter)
            # convert the list of all individuals to a DataFrame
            element = pd.DataFrame(tmp_element_list, columns=['No', 'wall', 'nodeI', 'nodeJ', 'xBar', 'zBar', 'L', 'H',
                                                              't', 'mat', 'type', 'angle', 'nI1', 'nI2', 'nI3', 'nJ1',
                                                              'nJ2', 'nJ3'])
            for item in np.arange(element_number):
                # assign orientations to the elements
                if element['type'].iat[item] == 0:
                    element['angle'].iat[item] = 0.5 * math.pi
                elif element['type'].iat[item] == 1:
                    element['angle'].iat[item] = 0.0
                # assign offset to the elements
                nwall = element['wall'].iat[item]
                x0 = wall.at[nwall, 'x0']
                y0 = wall.at[nwall, 'y0']

                x_loc = float(element['xBar'].iat[item]) - 0.5 * float(element['H'].iat[item]) * math.cos(
                    element['angle'].iat[item])  # x in local coordinates
                z_loc = float(element['zBar'].iat[item]) - 0.5 * float(element['H'].iat[item]) * math.sin(
                    element['angle'].iat[item])  # z in local coordinates
                x_glob = x0 + x_loc * math.cos(wall.at[nwall, 'angle'])  # x in global coordinates
                y_glob = y0 + x_loc * math.sin(wall.at[nwall, 'angle'])  # y in global coordinates
                element['nI1'].iat[item] = x_glob
                element['nI2'].iat[item] = y_glob
                element['nI3'].iat[item] = z_loc

                x_loc = element['xBar'].iat[item] + 0.5 * element['H'].iat[item] * math.cos(
                    element['angle'].iat[item])  # x in local coordinates
                z_loc = element['zBar'].iat[item] + 0.5 * element['H'].iat[item] * math.sin(
                    element['angle'].iat[item])  # z in local coordinates
                x_glob = x0 + x_loc * math.cos(wall.at[nwall, 'angle'])  # x in global coordinates
                y_glob = y0 + x_loc * math.sin(wall.at[nwall, 'angle'])  # y in global coordinates
                element['nJ1'].iat[item] = x_glob
                element['nJ2'].iat[item] = y_glob
                element['nJ3'].iat[item] = z_loc
            element = element.set_index('No')  # set the element number as the index
            # Convert the dataframe to an XlsxWriter Excel object.
            element.to_excel(writer, sheet_name='elements')

        # find the parameters for different analysis types
        if ("/pp" in lines[lineCounter]) and ("!" not in lines[lineCounter]):  # static analysis
            # the inside_counter parameter is defined so the data blocks for each parameter can be dealt with
            inside_counter = lineCounter
            inside_counter = check_empty(lines, inside_counter)
            while (lines[inside_counter][0] == '!') or (lines[inside_counter][0:1] == '\t'):
                inside_counter = inside_counter + 1
            analysis_number = analysis_number + 1
            check = lines[inside_counter]
            # separate, extract and store the analysis parameters in each line using "SPACE" in a list
            params = lines[inside_counter].split()
            for paramCounter in np.arange(len(params)):
                # In some cases, the lines are followed by a number of empty values.
                # Therefore, the number of parameters are calculated to prevent any errors
                # using the extracted data.
                if params[paramCounter] == "":
                    last_item = paramCounter - 1
                    break
                elif paramCounter == len(params) - 1:
                    last_item = len(params) - 1
            params = params[1:last_item + 1]  # params variable is updated to store only the non-empty arguments
            tmp_analysis.at['0', 'analysisNumber'] = analysis_number  # analysis number
            tmp_analysis.at['0', 'type'] = 'selfWeight'  # analysis type
            tmp_analysis.at['0', 'nSteps'] = int(params[0])  # number of analysis steps
            tmp_analysis.at['0', 'tol'] = float(params[1])  # convergence tolerance
            tmp_analysis.at['0', 'maxStep'] = int(params[2])  # maximum analysis step size
            tmp_analysis.at['0', 'accVec1'] = float(params[3])  # acceleration in X direction
            tmp_analysis.at['0', 'accVec2'] = float(params[4])  # acceleration in Y direction
            tmp_analysis.at['0', 'accVec3'] = float(params[5])  # acceleration in Z direction
            tmp_analysis_list.append(tmp_analysis.values.tolist()[0])  # store all the individual items in a list
            tmp_analysis = empty_tmp_analysis.copy(deep=True)  # clear the temporary dataframe to store next items
        elif ("/am" in lines[lineCounter]) and ("!" not in lines[lineCounter]):  # modal analysis
            # the inside_counter parameter is defined so the data blocks for each parameter can be dealt with
            inside_counter = lineCounter
            inside_counter = check_empty(lines, inside_counter)
            while (lines[inside_counter][0] == '!') or (lines[inside_counter][0:1] == '\t'):
                inside_counter = inside_counter + 1
            analysis_number = analysis_number + 1
            check = lines[inside_counter]
            # separate, extract and store the analysis parameters in each line using "SPACE" in a list
            params = lines[inside_counter].split()
            for paramCounter in np.arange(len(params)):
                # In some cases, the lines are followed by a number of empty values.
                # Therefore, the number of parameters are calculated to prevent any errors
                # using the extracted data.
                if params[paramCounter] == "":
                    last_item = paramCounter - 1
                    break
                elif paramCounter == len(params) - 1:
                    last_item = len(params) - 1
            params = params[1:last_item + 1]  # params variable is updated to store only the non-empty arguments
            tmp_analysis.at['0', 'analysisNumber'] = analysis_number  # analysis number
            tmp_analysis.at['0', 'type'] = 'modal'  # analysis type
            tmp_analysis.at['0', 'nModes'] = int(params[0])  # number of modes
            tmp_analysis_list.append(tmp_analysis.values.tolist()[0])  # store all the individual items in a list
            tmp_analysis = empty_tmp_analysis.copy(deep=True)  # clear the temporary dataframe to store next items
        # triangular or rectangular pushover analysis
        elif (("/pomas" in lines[lineCounter]) or ("/pomaz" in lines[lineCounter])) and ("!" not in lines[lineCounter]):
            # the inside_counter parameter is defined so the data blocks for each parameter can be dealt with
            inside_counter = lineCounter
            inside_counter = check_empty(lines, inside_counter)
            while (lines[inside_counter][0] == '!') or (lines[inside_counter][0:1] == '\t'):
                inside_counter = inside_counter + 1
            analysis_number = analysis_number + 1
            check = lines[inside_counter]
            # separate, extract and store the analysis parameters in each line using "SPACE" in a list
            params = lines[inside_counter].split()
            for paramCounter in np.arange(len(params)):
                # In some cases, the lines are followed by a number of empty values.
                # Therefore, the number of parameters are calculated to prevent any errors
                # using the extracted data.
                if params[paramCounter] == "":
                    last_item = paramCounter - 1
                    break
                elif paramCounter == len(params) - 1:
                    last_item = len(params) - 1
            params = params[1:last_item + 1]  # params variable is updated to store only the non-empty arguments
            tmp_analysis.at['0', 'analysisNumber'] = analysis_number  # analysis number
            if "/pomas" in lines[lineCounter]:
                tmp_analysis.at['0', 'type'] = 'pushoverRectangular'  # analysis type
            elif "/pomaz" in lines[lineCounter]:
                tmp_analysis.at['0', 'type'] = 'pushoverTriangular'  # analysis type
            tmp_analysis.at['0', 'nSteps'] = int(params[0])  # number of analysis steps
            tmp_analysis.at['0', 'tol'] = float(params[1])  # convergence tolerance
            tmp_analysis.at['0', 'maxStep'] = int(params[2])  # maximum analysis step size
            tmp_analysis.at['0', 'controlNode'] = int(params[3])  # control node of the analysis
            tmp_analysis.at['0', 'DOF'] = int(params[4])  # degree of freedom of the control node
            tmp_analysis.at['0', 'maxDisp'] = float(params[5])  # maximum displacement of the control node
            tmp_analysis.at['0', 'forceDrop'] = float(params[6])
            tmp_analysis_list.append(tmp_analysis.values.tolist()[0])  # store all the individual items in a list
            tmp_analysis = empty_tmp_analysis.copy(deep=True)  # clear the temporary dataframe to store next items
        elif ("/po" in lines[lineCounter]) and ("!" not in lines[lineCounter]):  # generic pushover analysis
            # the inside_counter parameter is defined so the data blocks for each parameter can be dealt with
            inside_counter = lineCounter
            inside_counter = check_empty(lines, inside_counter)
            while (lines[inside_counter][0] == '!') or (lines[inside_counter][0:1] == '\t'):
                inside_counter = inside_counter + 1
            analysis_number = analysis_number + 1
            check = lines[inside_counter]
            # separate, extract and store the analysis parameters in each line using "SPACE" in a list
            params = lines[inside_counter].split()
            for paramCounter in np.arange(len(params)):
                # In some cases, the lines are followed by a number of empty values.
                # Therefore, the number of parameters are calculated to prevent any errors
                # using the extracted data.
                if params[paramCounter] == "":
                    last_item = paramCounter - 1
                    break
                elif paramCounter == len(params) - 1:
                    last_item = len(params) - 1
            params = params[1:last_item + 1]  # params variable is updated to store only the non-empty arguments
            tmp_analysis.at['0', 'analysisNumber'] = analysis_number  # analysis number
            tmp_analysis.at['0', 'type'] = 'pushoverGeneric'  # analysis type
            tmp_analysis.at['0', 'nSteps'] = int(params[0])  # number of analysis steps
            tmp_analysis.at['0', 'tol'] = float(params[1])  # convergence tolerance
            tmp_analysis.at['0', 'maxStep'] = int(params[2])  # maximum analysis step size
            tmp_analysis.at['0', 'controlNode'] = int(params[3])  # control node of the analysis
            tmp_analysis.at['0', 'DOF'] = int(params[4])  # degree of freedom of the control node
            tmp_analysis.at['0', 'maxDisp'] = float(params[5])  # maximum displacement of the control node
            tmp_analysis.at['0', 'forceDrop'] = float(params[6])
            tmp_analysis_list.append(tmp_analysis.values.tolist()[0])  # store all the individual items in a list
            tmp_analysis = empty_tmp_analysis.copy(deep=True)  # clear the temporary dataframe to store next items
            inside_counter = inside_counter + 1
            load_number = 0

            while lines[inside_counter][0] != '/':
                # jump over the commented and empty lines
                while (lines[inside_counter][0] == '!') or (lines[inside_counter][0:1] == '\t'):
                    inside_counter = inside_counter + 1
                    inside_counter = check_empty(lines, inside_counter)
                    if lines[inside_counter][0] == '/':
                        break
                if lines[inside_counter][0] == '/':
                    break
                load_number = load_number + 1
                # separate, extract and store the analysis parameters in each line using "SPACE" in a list
                params = lines[inside_counter].split()
                for paramCounter in np.arange(len(params)):
                    # In some cases, the lines are followed by a number of empty values.
                    # Therefore, the number of parameters are calculated to prevent any errors
                    # using the extracted data.
                    if params[paramCounter] == "":
                        last_item = paramCounter - 1
                        break
                    elif paramCounter == len(params) - 1:
                        last_item = len(params) - 1
                params = params[0:last_item + 1]  # params variable is updated to store only the non-empty arguments
                tmp_analysis.at['0', 'analysisNumber'] = analysis_number  # analysis number
                tmp_analysis.at['0', 'loadedNode'] = int(params[0])  # loaded node
                tmp_analysis.at['0', 'load1'] = float(params[1])  # load in X direction
                tmp_analysis.at['0', 'load2'] = float(params[2])  # load in Y direction
                tmp_analysis.at['0', 'load3'] = float(params[3])  # load in Z direction
                if last_item == 3:
                    tmp_analysis.at['0', 'load4'] = 0  # load in MX direction
                    tmp_analysis.at['0', 'load5'] = 0  # load in MY direction
                elif last_item == 5:
                    tmp_analysis.at['0', 'load4'] = float(params[4])  # load in MX direction
                    tmp_analysis.at['0', 'load5'] = float(params[5])  # load in MY direction
                tmp_analysis_list.append(tmp_analysis.values.tolist()[0])  # store all the individual items in a list
                tmp_analysis = empty_tmp_analysis.copy(deep=True)  # clear the temporary dataframe to store next items
                inside_counter = inside_counter + 1
                inside_counter = check_empty(lines, inside_counter)
        elif ("/ad" in lines[lineCounter]) and ("!" not in lines[lineCounter]):  # dynamic analysis
            # the inside_counter parameter is defined so the data blocks for each parameter can be dealt with
            inside_counter = lineCounter
            inside_counter = check_empty(lines, inside_counter)
            while (lines[inside_counter][0] == '!') or (lines[inside_counter][0:1] == '\t'):
                inside_counter = inside_counter + 1
            analysis_number = analysis_number + 1
            check = lines[inside_counter]
            # separate, extract and store the analysis parameters in each line using "SPACE" in a list
            params = lines[inside_counter].split()
            for paramCounter in np.arange(len(params)):
                # In some cases, the lines are followed by a number of empty values.
                # Therefore, the number of parameters are calculated to prevent any errors
                # using the extracted data.
                if params[paramCounter] == "":
                    last_item = paramCounter - 1
                    break
                elif paramCounter == len(params) - 1:
                    last_item = len(params) - 1
            params = params[1:last_item + 1]  # params variable is updated to store only the non-empty arguments
            tmp_analysis.at['0', 'analysisNumber'] = analysis_number  # analysis number
            tmp_analysis.at['0', 'type'] = 'Dynamic'  # analysis type
            tmp_analysis.at['0', 'nSteps'] = int(params[0])  # number of analysis steps
            tmp_analysis.at['0', 'tol'] = float(params[1])  # convergence tolerance
            tmp_analysis.at['0', 'maxStep'] = int(params[2])  # maximum analysis step size
            tmp_analysis.at['0', 'dt'] = float(params[3])  # time increment
            tmp_analysis.at['0', 'rayleigh1'] = float(params[4])  # mass proportional rayleigh damping
            tmp_analysis.at['0', 'rayleigh2'] = float(params[5])  # stiffness proportional rayleigh damping
            tmp_analysis.at['0', 'subd'] = float(params[6])
            inside_counter = inside_counter + 1
            load_number = 0
            while lines[inside_counter][0] != '/':
                # jump over the commented and empty lines
                while (lines[inside_counter][0] == '!') or (lines[inside_counter][0:1] == '\t'):
                    inside_counter = inside_counter + 1
                    inside_counter = check_empty(lines, inside_counter)
                    if lines[inside_counter][0] == '/':
                        break
                if lines[inside_counter][0] == '/':
                    break
                load_number = load_number + 1
                # separate, extract and store the analysis parameters in each line using "SPACE" in a list
                params = lines[inside_counter].split()
                for paramCounter in np.arange(len(params)):
                    # In some cases, the lines are followed by a number of empty values.
                    # Therefore, the number of parameters are calculated to prevent any errors
                    # using the extracted data.
                    if params[paramCounter] == "":
                        last_item = paramCounter - 1
                        break
                    elif paramCounter == len(params) - 1:
                        last_item = len(params) - 1
                params = params[0:last_item + 1]  # params variable is updated to store only the non-empty arguments
                tmp_analysis.at['0', 'DOF'] = str(params[0])
                tmp_analysis.at['0', 'groundMotion'] = str(params[1])  # ground motion record used
                if last_item == 1:
                    tmp_analysis.at['0', 'PGA'] = -1  # PGA of the GM not specified
                else:
                    tmp_analysis.at['0', 'PGA'] = float(params[2])  # PGA of the GM specified

                tmp_analysis_list.append(tmp_analysis.values.tolist()[0])  # store all the individual items in a list
                tmp_analysis = empty_tmp_analysis.copy(deep=True)  # clear the temporary dataframe to store next items
                inside_counter = inside_counter + 1
                inside_counter = check_empty(lines, inside_counter)

        if analysis_number > 1 and analysis_number > last_analysis_number:
            # convert the list of all individuals to a DataFrame
            analysis = pd.DataFrame(tmp_analysis_list, columns=['analysisNumber', 'type', 'nSteps', 'tol', 'maxStep',
                                                                'accVec1', 'accVec2', 'accVec3', 'dt', 'nModes',
                                                                'rayleigh1', 'rayleigh2', 'subd', 'controlNode', 'DOF',
                                                                'maxDisp', 'forceDrop', 'loadedNode', 'load1', 'load2',
                                                                'load3', 'load4', 'load5', 'groundMotion', 'PGA'])
        last_analysis_number = analysis_number
        # find the parameters for nodal masses
        if (("masse" in lines[lineCounter]) or ("mass" in lines[lineCounter])) and ("!" not in lines[lineCounter]):
            # the inside_counter parameter is defined so the data blocks for each parameter can be dealt with
            inside_counter = lineCounter + 1
            inside_counter = check_empty(lines, inside_counter)
            while lines[inside_counter][0] != '/':
                # jump over the commented and empty lines
                while (lines[inside_counter][0] == '!') or (lines[inside_counter][0:1] == '\t'):
                    inside_counter = inside_counter + 1
                    inside_counter = check_empty(lines, inside_counter)
                    if lines[inside_counter][0] == '/':
                        break
                if lines[inside_counter][0] == '/':
                    break
                # separate, extract and store the nodal mass parameters in each line using "SPACE" in a list
                params = lines[inside_counter].split()
                for paramCounter in np.arange(len(params)):
                    # In some cases, the lines are followed by a number of empty values.
                    # Therefore, the number of parameters are calculated to prevent any errors
                    # using the extracted data.
                    if params[paramCounter] == "":
                        last_item = paramCounter - 1
                        break
                    elif paramCounter == len(params) - 1:
                        last_item = len(params) - 1
                # params variable is updated to store only the non-empty arguments
                params = params[0:min(last_item + 1, 4)]
                for item in np.arange(last_item + 1):
                    tmp_nodal_mass.iat[0, item] = params[item]
                if last_item < 3:
                    tmp_nodal_mass.at['0', 'ecc_z'] = 0
                    if last_item < 2:
                        tmp_nodal_mass.at['0', 'ecc_x'] = 0
                # store all the individual items in a list
                tmp_nodal_mass_list.append(tmp_nodal_mass.values.tolist()[0])
                inside_counter = inside_counter + 1
                inside_counter = check_empty(lines, inside_counter)
            # convert the list of all individuals to a DataFrame
            nodal_mass = pd.DataFrame(tmp_nodal_mass_list, columns=['node', 'mass', 'ecc_x', 'ecc_z'])
            nodal_mass = nodal_mass.set_index('node')  # set the node number as the index
            # Convert the dataframe to an XlsxWriter Excel object.
            nodal_mass.to_excel(writer, sheet_name='nodal mass')

        # find the parameters for distributed masses
        if (("massedistr" in lines[lineCounter]) or ("massdistr" in lines[lineCounter])) and ("!" not in lines[lineCounter]):
            # the inside_counter parameter is defined so the data blocks for each parameter can be dealt with
            inside_counter = lineCounter + 1
            inside_counter = check_empty(lines, inside_counter)
            while lines[inside_counter][0] != '/':
                # jump over the commented and empty lines
                while (lines[inside_counter][0] == '!') or (lines[inside_counter][0:1] == '\t'):
                    inside_counter = inside_counter + 1
                    inside_counter = check_empty(lines, inside_counter)
                    if lines[inside_counter][0] == '/':
                        break
                if lines[inside_counter][0] == '/':
                    break
                # separate, extract and store the distributed mass parameters in each line using "SPACE" in a list
                params = lines[inside_counter].split()
                for paramCounter in np.arange(len(params)):
                    # In some cases, the lines are followed by a number of empty values.
                    # Therefore, the number of parameters are calculated to prevent any errors
                    # using the extracted data.
                    if params[paramCounter] == "":
                        last_item = paramCounter - 1
                        break
                    elif paramCounter == len(params) - 1:
                        last_item = len(params) - 1
                params = params[0:last_item + 1]  # params variable is updated to store only the non-empty arguments
                tmp_distr_mass.at['0', 'node'] = params[0]
                tmp_distr_mass.at['0', 'V'] = params[1]
                tmp_distr_mass.at['0', 'M'] = params[2]
                tmp_distr_mass.at['0', 'Vr'] = params[3]
                tmp_distr_mass.at['0', 'Mr'] = params[4]
                tmp_distr_mass.at['0', 'el'] = params[7]
                # store all the individual items in a list
                tmp_distr_mass_list.append(tmp_distr_mass.values.tolist()[0])
                inside_counter = inside_counter + 1
                inside_counter = check_empty(lines, inside_counter)
            # convert the list of all individuals to a DataFrame
            distr_mass = pd.DataFrame(tmp_distr_mass_list, columns=['node', 'V', 'M', 'Vr', 'Mr', 'el'])
            distr_mass = distr_mass.set_index('node')  # set the node number as the index
            # Convert the dataframe to an XlsxWriter Excel object.
            distr_mass.to_excel(writer, sheet_name='distributed mass')
    print("Tremuri_Input completed in --- %s seconds ---" % (time.time() - start_time))

    if analysis_number > 0:
        analysis = analysis.set_index('analysisNumber')  # set the analysis number as the index
        # Convert the dataframe to an XlsxWriter Excel object.
        analysis.to_excel(writer, sheet_name='analysis')

    # Close the Pandas Excel writer and output the Excel file.
    writer.save()

    return wall, n2d, poly2d, n3d, poly3d1, poly3d2, max_node_number, element, elastic_beam, nl_beam, floor_level, floor, \
           material, nodal_mass, restraint, analysis

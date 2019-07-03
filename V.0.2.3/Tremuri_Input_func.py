# This code reads the input file of Tremuri
from os.path import join
import numpy as np
import pandas as pd
import math
from numpy.linalg import inv
import time

# first import the file into a variable
# tfilePath = "C:/Model Processing/tremuri_model_processing/basel_models_Pavia/"
# tfileName = "basilea_ALLdynamics.txt"
# completeFileLocation = join(tfilePath, tfileName)
completeFileLocation1 = ""


def checkEmpty(f_lines, f_insideCounter):
    while 1:
        if not f_lines[f_insideCounter]:
            f_insideCounter = f_insideCounter + 1
        else:
            break
    return f_insideCounter

def TRIfunc():
    global wall, n2d, poly2d, n3d, poly3d1, poly3d2, maxNodeNumber, element, elasticBeam, nlBeam, floorLevel, floor, \
        material, nodalMass, restraint, analysis
    startTime = time.time()
    openFile = open(completeFileLocation1, "r")
    inputFile = openFile.read()

    # read the lines of the input file
    lines = inputFile.splitlines()
    openFile.close()


    def dataConcat(number, tmp, full):
        if number == 1:
            full = tmp.copy(deep=True)
        else:
            full = pd.concat([full, tmp])
        return full


    # initialize maxNodeNumber to store the largest node tag
    maxNodeNumber = 0
    # initiate wall data frame
    wallNumber = 0
    tmp_wall = pd.DataFrame(columns=['No', 'x0', 'y0', 'angle'], index=['0'])
    wall = pd.DataFrame(columns=['No', 'x0', 'y0', 'angle'], index=['0'])
    tmp_wall_list = []
    # initiate material data frame
    materialNumber = 0
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
    floorNumber = 0
    tmp_floor = pd.DataFrame(columns=['No', 'nI', 'nJ', 'nK', 'nL', 'thickness', 'E1', 'E2', 'Poisson', 'G', 'angle'],
                             index=['0'])
    floor = pd.DataFrame(columns=['No', 'nI', 'nJ', 'nK', 'nL', 'thickness', 'E1', 'E2', 'Poisson', 'G', 'angle'],
                             index=['0'])
    tmp_floor_list = []
    # inititate restraints data frame
    restraintNumber = 0
    tmp_restraint = pd.DataFrame(columns=['Node', 'x', 'y', 'z', 'rx', 'ry'], index=['0'])
    restraint = pd.DataFrame(columns=['Node', 'x', 'y', 'z', 'rx', 'ry'], index=['0'])
    tmp_restraint_list = []
    # initiate floor number data
    floorLevelNumber = 0
    tmp_floorLevel = pd.DataFrame(columns=['h', 'zAxis1', 'zAxis2', 'zAxis3'], index=['0'])
    floorLevel = pd.DataFrame(columns=['h', 'zAxis1', 'zAxis2', 'zAxis3'], index=['0'])
    tmp_floorLevel_list = []
    # initiate the data for 2D nodes
    n2dNumber = 0
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
    n3dNumber = 0
    tmp_n3d = pd.DataFrame(
        columns=['Node', 'n_wall2', 'wall1', 'wall2', 'z', 'type', 'rho1', 'thickness1', 'offsetXloc11', 'offsetXloc12',
                 'offsetZ11', 'offsetZ12', 'rho2', 'thickness2', 'offsetXloc21', 'offsetXloc22', 'offsetZ21', 'offsetZ22',
                 'x', 'y', 'offsetX11', 'offsetX12', 'offsetY11', 'offsetY12', 'offsetX21', 'offsetX22', 'offsetY21',
                 'offsetY22'], index=['0'])
    n3d = pd.DataFrame(
        columns=['Node', 'n_wall2', 'wall1', 'wall2', 'z', 'type', 'rho1', 'thickness1', 'offsetXloc11', 'offsetXloc12',
                 'offsetZ11', 'offsetZ12', 'rho2', 'thickness2', 'offsetXloc21', 'offsetXloc22', 'offsetZ21', 'offsetZ22',
                 'x', 'y', 'offsetX11', 'offsetX12', 'offsetY11', 'offsetY12', 'offsetX21', 'offsetX22', 'offsetY21',
                 'offsetY22'], index=['0'])
    tmp_n3d_list = []
    empty_tmp_n3d = pd.DataFrame(
        columns=['Node', 'n_wall2', 'wall1', 'wall2', 'z', 'type', 'rho1', 'thickness1', 'offsetXloc11', 'offsetXloc12',
                 'offsetZ11', 'offsetZ12', 'rho2', 'thickness2', 'offsetXloc21', 'offsetXloc22', 'offsetZ21', 'offsetZ22',
                 'x', 'y', 'offsetX11', 'offsetX12', 'offsetY11', 'offsetY12', 'offsetX21', 'offsetX22', 'offsetY21',
                 'offsetY22'], index=['0'])
    # indicate the data for the 2d node polygons
    firstItem = 0
    poly2dNumber = 0
    tmp_poly2d = pd.DataFrame(
        columns=['Node - Global', 'Node - Local', 'rho', 'thickness', 'offsetXloc1', 'offsetXloc2', 'offsetZ1', 'offsetZ2',
                 'offsetX1', 'offsetX2', 'offsetY1', 'offsetY2'], index=['0', '1', '2', '3'])
    poly2d = pd.DataFrame(
        columns=['Node - Global', 'Node - Local', 'rho', 'thickness', 'offsetXloc1', 'offsetXloc2', 'offsetZ1', 'offsetZ2',
                 'offsetX1', 'offsetX2', 'offsetY1', 'offsetY2'], index=['0', '1', '2', '3'])
    tmp_poly2d_list = []
    empty_tmp_poly2d = pd.DataFrame(
        columns=['Node - Global', 'Node - Local', 'rho', 'thickness', 'offsetXloc1', 'offsetXloc2', 'offsetZ1', 'offsetZ2',
                 'offsetX1', 'offsetX2', 'offsetY1', 'offsetY2'], index=['0', '1', '2', '3'])
    for item in np.arange(4):
        tmp_poly2d['Node - Local'].iat[item] = item + 1
        empty_tmp_poly2d['Node - Local'].iat[item] = item + 1
    # indicate the data for the 3d node polygons (1 & 2)
    firstItem3d1 = 0
    firstItem3d2 = 0
    poly3dNumber1 = 0
    poly3dNumber2 = 0
    tmp_poly3d1 = pd.DataFrame(
        columns=['Node - Global', 'Node - Local', 'rho', 'thickness', 'offsetXloc1', 'offsetXloc2', 'offsetZ1', 'offsetZ2',
                 'offsetX1', 'offsetX2', 'offsetY1', 'offsetY2'], index=['0', '1', '2', '3'])
    poly3d1 = pd.DataFrame(
        columns=['Node - Global', 'Node - Local', 'rho', 'thickness', 'offsetXloc1', 'offsetXloc2', 'offsetZ1', 'offsetZ2',
                 'offsetX1', 'offsetX2', 'offsetY1', 'offsetY2'], index=['0', '1', '2', '3'])
    tmp_poly3d1_list = []
    empty_tmp_poly3d1 = pd.DataFrame(
        columns=['Node - Global', 'Node - Local', 'rho', 'thickness', 'offsetXloc1', 'offsetXloc2', 'offsetZ1', 'offsetZ2',
                 'offsetX1', 'offsetX2', 'offsetY1', 'offsetY2'], index=['0', '1', '2', '3'])
    tmp_poly3d2 = pd.DataFrame(
        columns=['Node - Global', 'Node - Local', 'rho', 'thickness', 'offsetXloc1', 'offsetXloc2', 'offsetZ1', 'offsetZ2',
                 'offsetX1', 'offsetX2', 'offsetY1', 'offsetY2'], index=['0', '1', '2', '3'])
    poly3d2 = pd.DataFrame(
        columns=['Node - Global', 'Node - Local', 'rho', 'thickness', 'offsetXloc1', 'offsetXloc2', 'offsetZ1', 'offsetZ2',
                 'offsetX1', 'offsetX2', 'offsetY1', 'offsetY2'], index=['0', '1', '2', '3'])
    tmp_poly3d2_list = []
    empty_tmp_poly3d2 = pd.DataFrame(
        columns=['Node - Global', 'Node - Local', 'rho', 'thickness', 'offsetXloc1', 'offsetXloc2', 'offsetZ1', 'offsetZ2',
                 'offsetX1', 'offsetX2', 'offsetY1', 'offsetY2'], index=['0', '1', '2', '3'])
    for item in np.arange(4):
        tmp_poly3d1['Node - Local'].iat[item] = item + 1
        tmp_poly3d2['Node - Local'].iat[item] = item + 1
        empty_tmp_poly3d1['Node - Local'].iat[item] = item + 1
        empty_tmp_poly3d2['Node - Local'].iat[item] = item + 1
    # initiate elastic beam data frame
    elasticBeamNumber = 0
    tmp_elasticBeam = pd.DataFrame(
        columns=['No', 'wall', 'nodeI', 'nodeJ', 'mat', 'area', 'J', 'deformIn', 'type', 'offXloc_I', 'offZ_I', 'offXloc_J',
                 'offZ_J'], index=['0'])
    elasticBeam = pd.DataFrame(
        columns=['No', 'wall', 'nodeI', 'nodeJ', 'mat', 'area', 'J', 'deformIn', 'type', 'offXloc_I', 'offZ_I', 'offXloc_J',
                 'offZ_J'], index=['0'])
    tmp_elasticBeam_list = []
    # initiate nonlinear beam data frame
    nlBeamNumber = 0
    tmp_nlBeam = pd.DataFrame(
        columns=['No', 'wall', 'nodeI', 'nodeJ', 'mat', 'area', 'J', 'offXloc_I', 'offZ_I', 'offXloc_J', 'offZ_J', 'type',
                 'deformIn', 'Wpl'], index=['0'])
    nlBeam = pd.DataFrame(
        columns=['No', 'wall', 'nodeI', 'nodeJ', 'mat', 'area', 'J', 'offXloc_I', 'offZ_I', 'offXloc_J', 'offZ_J', 'type',
                 'deformIn', 'Wpl'], index=['0'])
    tmp_nlBeam_list = []
    # initiate element data frame
    elementNumber = 0
    tmp_element = pd.DataFrame(
        columns=['No', 'wall', 'nodeI', 'nodeJ', 'xBar', 'zBar', 'L', 'H', 't', 'mat', 'type', 'angle', 'nI1', 'nI2', 'nI3',
                 'nJ1', 'nJ2', 'nJ3'], index=['0'])
    element = pd.DataFrame(
        columns=['No', 'wall', 'nodeI', 'nodeJ', 'xBar', 'zBar', 'L', 'H', 't', 'mat', 'type', 'angle', 'nI1', 'nI2', 'nI3',
                 'nJ1', 'nJ2', 'nJ3'], index=['0'])
    tmp_element_list = []
    # initiate analysis number data
    analysisNumber = 0
    lastAnalysisNumber = 0
    tmp_analysis = pd.DataFrame(columns=['analysisNumber', 'type', 'nSteps', 'tol', 'maxStep', 'accVec1', 'accVec2',
                                         'accVec3', 'dt', 'nModes', 'rayleigh1', 'rayleigh2', 'subd', 'controlNode', 'DOF',
                                         'maxDisp', 'forceDrop', 'loadedNode', 'load1', 'load2', 'load3', 'load4', 'load5',
                                         'groundMotion', 'PGA'], index=['0'])
    analysis = pd.DataFrame(columns=['analysisNumber', 'type', 'nSteps', 'tol', 'maxStep', 'accVec1', 'accVec2',
                                         'accVec3', 'dt', 'nModes', 'rayleigh1', 'rayleigh2', 'subd', 'controlNode', 'DOF',
                                         'maxDisp', 'forceDrop', 'loadedNode', 'load1', 'load2', 'load3', 'load4', 'load5',
                                         'groundMotion', 'PGA'], index=['0'])
    tmp_analysis_list = []
    empty_tmp_analysis = pd.DataFrame(columns=['analysisNumber', 'type', 'nSteps', 'tol', 'maxStep', 'accVec1', 'accVec2',
                                         'accVec3', 'dt', 'nModes', 'rayleigh1', 'rayleigh2', 'subd', 'controlNode', 'DOF',
                                         'maxDisp', 'forceDrop', 'loadedNode', 'load1', 'load2', 'load3', 'load4', 'load5',
                                         'groundMotion', 'PGA'], index=['0'])
    # initiate nodal mass data frame
    nodalMassNumber = 0
    tmp_nodalMass = pd.DataFrame(columns=['node', 'mass', 'ecc_x', 'ecc_z'], index=['0'])
    nodalMass = pd.DataFrame(columns=['node', 'mass', 'ecc_x', 'ecc_z'], index=['0'])
    tmp_nodalMass_list = []
    # initiate distributed mass data frame
    distrMassNumber = 0
    tmp_distrMass = pd.DataFrame(columns=['node', 'V', 'M', 'Vr', 'Mr', 'el'], index=['0'])
    distrMass = pd.DataFrame(columns=['node', 'V', 'M', 'Vr', 'Mr', 'el'], index=['0'])
    tmp_distrMass_list = []

    # go through the lines to find each of the desired sections
    for lineCounter in np.arange(len(lines)):
        # find the parameters for walls
        if (("pareti" in lines[lineCounter]) or ("walls" in lines[lineCounter])) and ("!" not in lines[lineCounter]):
            insideCounter = lineCounter + 1
            insideCounter = checkEmpty(lines, insideCounter)
            while lines[insideCounter][0] != '/':
                while (lines[insideCounter][0] == '!') or (lines[insideCounter][0:1] == '\t'):
                    insideCounter = insideCounter + 1
                    insideCounter = checkEmpty(lines, insideCounter)
                    if lines[insideCounter][0] == '/':
                        break
                if lines[insideCounter][0] == '/':
                    break
                wallNumber = wallNumber + 1
                # params = lines[insideCounter].split('\t')
                # params = re.split('\t| ', lines[insideCounter])
                params = lines[insideCounter].split()
                for paramCounter in np.arange(len(params)):
                    if params[paramCounter] == "":
                        lastItem = paramCounter - 1
                        break
                    elif paramCounter == len(params) - 1:
                        lastItem = len(params) - 1
                params = params[0:lastItem + 1]
                for item in np.arange(lastItem + 1):
                    if "°" in params[item]:
                        params[item] = (float(params[item][0:len(params[item]) - 1]) / 180) * math.pi
                    tmp_wall.iat[0, item] = params[item]
                tmp_wall_list.append(tmp_wall.values.tolist()[0])
                insideCounter = insideCounter + 1
                insideCounter = checkEmpty(lines, insideCounter)

            wall = pd.DataFrame(tmp_wall_list, columns=['No', 'x0', 'y0', 'angle'])
            wall = wall.astype(float)  # convert all the variables to float
            wall['No'] = wall['No'].astype(int)  # the wall numbers could be integers
            wall = wall.set_index('No')  # set the wall number as the index
            writer = pd.ExcelWriter('tremuri_input_parameters.xlsx', engine='xlsxwriter')
            # Convert the dataframe to an XlsxWriter Excel object.
            wall.to_excel(writer, sheet_name='wall')

        # find the parameters for materials
        if (("Materiali" in lines[lineCounter]) or ("Material_properties" in lines[lineCounter])) and (
                "!" not in lines[lineCounter]):
            insideCounter = lineCounter + 1
            insideCounter = checkEmpty(lines, insideCounter)
            while lines[insideCounter][0] != '/':
                while (lines[insideCounter][0] == '!') or (lines[insideCounter][0:1] == '\t'):
                    insideCounter = insideCounter + 1
                    insideCounter = checkEmpty(lines, insideCounter)
                    if lines[insideCounter][0] == '/':
                        break
                if lines[insideCounter][0] == '/':
                    break
                materialNumber = materialNumber + 1
                params = lines[insideCounter].split()
                for paramCounter in np.arange(len(params)):
                    if params[paramCounter] == "":
                        lastItem = paramCounter - 1
                        break
                    elif paramCounter == len(params) - 1:
                        lastItem = len(params) - 1
                params = params[0:lastItem + 1]
                for item in np.arange(lastItem + 1):
                    tmp_material.iat[0, item] = params[item]
                tmp_material_list.append(tmp_material.values.tolist()[0])
                insideCounter = insideCounter + 1
                insideCounter = checkEmpty(lines, insideCounter)
                tmp_material = empty_tmp_material.copy(deep=True)

            material = pd.DataFrame(tmp_material_list, columns=['No', 'E', 'G', 'rho', 'fc', 'tau0', 'verification',
                                                                'shear_model', 'drift_S', 'drift_F', 'mu', 'Gc', 'beta'])
            material = material.astype(float)  # convert all the variables to float
            material['No'] = material['No'].astype(int)  # the material numbers could be integers
            material = material.set_index('No')
            # Convert the dataframe to an XlsxWriter Excel object.
            material.to_excel(writer, sheet_name='material')

        # find the parameters for floors
        if (("solaio" in lines[lineCounter]) or ("floors" in lines[lineCounter])) and ("!" not in lines[lineCounter]):
            insideCounter = lineCounter + 1
            insideCounter = checkEmpty(lines, insideCounter)
            while lines[insideCounter][0] != '/':
                while (lines[insideCounter][0] == '!') or (lines[insideCounter][0:1] == '\t'):
                    insideCounter = insideCounter + 1
                    insideCounter = checkEmpty(lines, insideCounter)
                    if lines[insideCounter][0] == '/':
                        break
                if lines[insideCounter][0] == '/':
                    break
                floorNumber = floorNumber + 1
                params = lines[insideCounter].split()
                for paramCounter in np.arange(len(params)):
                    if params[paramCounter] == "":
                        lastItem = paramCounter - 1
                        break
                    elif paramCounter == len(params) - 1:
                        lastItem = len(params) - 1
                params = params[0:lastItem + 1]
                for item in np.arange(lastItem + 1):
                    if "°" in params[item]:
                        params[item] = (float(params[item][0:len(params[item]) - 1]) / 180) * math.pi
                    tmp_floor.iat[0, item] = params[item]
                tmp_floor_list.append(tmp_floor.values.tolist()[0])
                insideCounter = insideCounter + 1
                insideCounter = checkEmpty(lines, insideCounter)

            floor = pd.DataFrame(tmp_floor_list, columns=['No', 'nI', 'nJ', 'nK', 'nL', 'thickness', 'E1', 'E2', 'Poisson',
                                                          'G', 'angle'])
            floor = floor.astype(float)  # convert all the variables to float
            floor[['No', 'nI', 'nJ', 'nK', 'nL']] = floor[['No', 'nI', 'nJ', 'nK', 'nL']].astype(int)
            floor = floor.set_index('No')
            # Convert the dataframe to an XlsxWriter Excel object.
            floor.to_excel(writer, sheet_name='floor')

        # find the parameters for restraints
        if (("vincoli" in lines[lineCounter]) or ("Restraints" in lines[lineCounter])) and ("!" not in lines[lineCounter]):
            insideCounter = lineCounter + 1
            insideCounter = checkEmpty(lines, insideCounter)
            while lines[insideCounter][0] != '/':
                while (lines[insideCounter][0] == '!') or (lines[insideCounter][0:1] == '\t'):
                    insideCounter = insideCounter + 1
                    insideCounter = checkEmpty(lines, insideCounter)
                    if lines[insideCounter][0] == '/':
                        break
                if lines[insideCounter][0] == '/':
                    break
                restraintNumber = restraintNumber + 1
                params = lines[insideCounter].split()
                for paramCounter in np.arange(len(params)):
                    if params[paramCounter] == "":
                        lastItem = paramCounter - 1
                        break
                    elif paramCounter == len(params) - 1:
                        lastItem = len(params) - 1
                params = params[0:lastItem + 1]
                # the 2D case
                if len(params) == 4:
                    for item in np.arange(lastItem + 1):
                        # just put the node number in its place
                        if item == 0:
                            tmp_restraint.iat[0, item] = params[item]
                        elif item == 1:
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
                # the 3D case
                else:
                    for item in np.arange(lastItem + 1):
                        # just put the node number in its place
                        if item == 0:
                            tmp_restraint.iat[0, item] = params[item]
                        else:
                            if params[item] == 'V' or params[item] == '1' or params[item] == 'v':
                                tmp_restraint.iat[0, item] = '1'
                            else:
                                tmp_restraint.iat[0, item] = '0'
                tmp_restraint_list.append(tmp_restraint.values.tolist()[0])
                insideCounter = insideCounter + 1
                insideCounter = checkEmpty(lines, insideCounter)

            restraint = pd.DataFrame(tmp_restraint_list, columns=['Node', 'x', 'y', 'z', 'rx', 'ry'])
            restraint = restraint.astype(int)  # convert all the variables to integer
            restraint = restraint.set_index('Node')
            # Convert the dataframe to an XlsxWriter Excel object.
            restraint.to_excel(writer, sheet_name='restraints')

        # find the parameters for floor levels
        if ("Piani" in lines[lineCounter]) and ("!" not in lines[lineCounter]):
            insideCounter = lineCounter
            insideCounter = checkEmpty(lines, insideCounter)
            while (lines[insideCounter][0] == '!') or (lines[insideCounter][0:1] == '\t'):
                insideCounter = insideCounter + 1
            floorLevelNumber = floorLevelNumber + 1
            check = lines[insideCounter]
            params = lines[insideCounter].split()
            for paramCounter in np.arange(len(params)):
                if params[paramCounter] == "":
                    lastItem = paramCounter - 1
                    break
                elif paramCounter == len(params) - 1:
                    lastItem = len(params) - 1
            params = params[1:lastItem + 1]
            for item in np.arange(lastItem):
                tmp_floorLevel.iat[0, 0] = params[item]
                tmp_floorLevel.iat[0, 1] = "0"
                tmp_floorLevel.iat[0, 2] = "0"
                tmp_floorLevel.iat[0, 3] = "1"
                tmp_floorLevel_list.append(tmp_floorLevel.values.tolist()[0])

            floorLevel = pd.DataFrame(tmp_floorLevel_list, columns=['h', 'zAxis1', 'zAxis2', 'zAxis3'])
            floorLevel = floorLevel.astype(float)  # convert all the variables to float
            floorLevel[['zAxis1', 'zAxis2', 'zAxis3']] = floorLevel[['zAxis1', 'zAxis2', 'zAxis3']].astype(int)
            floorLevel = floorLevel.set_index('h')
            # Convert the dataframe to an XlsxWriter Excel object.
            floorLevel.to_excel(writer, sheet_name='floor levels')

        # find the parameters for 2D nodes
        if (("nodi2d" in lines[lineCounter]) or ("nodes_2d" in lines[lineCounter])) and ("!" not in lines[lineCounter]):
            insideCounter = lineCounter + 1
            insideCounter = checkEmpty(lines, insideCounter)
            while lines[insideCounter][0] != '/':
                while (lines[insideCounter][0] == '!') or (lines[insideCounter][0:1] == '\t'):
                    insideCounter = insideCounter + 1
                    insideCounter = checkEmpty(lines, insideCounter)
                    if lines[insideCounter][0] == '/':
                        break
                if lines[insideCounter][0] == '/':
                    break
                n2dNumber = n2dNumber + 1
                params = lines[insideCounter].split()
                for paramCounter in np.arange(len(params)):
                    if params[paramCounter] == "":
                        lastItem = paramCounter - 1
                        break
                    elif paramCounter == len(params) - 1:
                        lastItem = len(params) - 1
                params = params[0:lastItem + 1]
                if maxNodeNumber < int(params[0]):
                    maxNodeNumber = int(params[0])
                for item in np.arange(5):
                    tmp_n2d.iat[0, item] = params[item]
                    if "P" in params[item]:
                        tmp_n2d.iat[0, item] = "P"
                tmp_n2d[['Node', 'wall']] = tmp_n2d[['Node', 'wall']].astype(int)
                tmp_n2d[['x_loc', 'z']] = tmp_n2d[['x_loc', 'z']].astype(float)

                tmp_n2d.at['0', 'x'] = wall.at[tmp_n2d.at['0', 'wall'], 'x0'] + tmp_n2d.at['0', 'x_loc'] * math.cos(
                    wall.at[tmp_n2d.at['0', 'wall'], 'angle'])
                tmp_n2d.at['0', 'y'] = wall.at[tmp_n2d.at['0', 'wall'], 'y0'] + tmp_n2d.at['0', 'x_loc'] * math.sin(
                    wall.at[tmp_n2d.at['0', 'wall'], 'angle'])
                if params[4] == 'R':
                    for item in np.arange(5, 11):
                        tmp_n2d.iat[0, item] = params[item]
                    tmp_n2d[['rho', 'thickness', 'offsetXloc1', 'offsetXloc2', 'offsetZ1', 'offsetZ2']] = \
                        tmp_n2d[['rho', 'thickness', 'offsetXloc1', 'offsetXloc2', 'offsetZ1', 'offsetZ2']].astype(float)

                    tmp_n2d.at['0', 'offsetXloc1'] = -1 * tmp_n2d.at['0', 'offsetXloc1']
                    tmp_n2d.at['0', 'offsetZ2'] = -1 * tmp_n2d.at['0', 'offsetZ2']
                    tmp_n2d.at['0', 'offsetX1'] = tmp_n2d.at['0', 'x'] + tmp_n2d.at['0', 'offsetXloc1'] * \
                                                  math.cos(wall.at[tmp_n2d.at['0', 'wall'], 'angle'])
                    tmp_n2d['offsetX2'].at['0'] = tmp_n2d.at['0', 'x'] + tmp_n2d.at['0', 'offsetXloc2'] * \
                                                  math.cos(wall.at[tmp_n2d.at['0', 'wall'], 'angle'])
                    tmp_n2d['offsetY1'].at['0'] = tmp_n2d.at['0', 'y'] + tmp_n2d.at['0', 'offsetXloc1'] * \
                                                  math.sin(wall.at[tmp_n2d.at['0', 'wall'], 'angle'])
                    tmp_n2d['offsetY2'].at['0'] = tmp_n2d.at['0', 'y'] + tmp_n2d.at['0', 'offsetXloc2'] * \
                                                  math.sin(wall.at[tmp_n2d.at['0', 'wall'], 'angle'])
                elif 'P' in params[4]:
                    polyIndex = 4
                    firstItem = firstItem + 1
                    while polyIndex < lastItem:
                        for nodeItem in np.arange(4):
                            tmp_poly2d['Node - Global'].iat[nodeItem] = int(params[0])
                        tmp_index = params[polyIndex]
                        tmp_index = str(int(tmp_index[1]) - 1)
                        tmp_poly2d.at[tmp_index, 'rho'] = float(params[polyIndex + 1])
                        tmp_poly2d.at[tmp_index, 'thickness'] = float(params[polyIndex + 2])
                        tmp_poly2d.at[tmp_index, 'offsetXloc1'] = min(float(params[polyIndex + 3]),
                                                                      float(params[polyIndex + 5]),
                                                                      float(params[polyIndex + 7]),
                                                                      float(params[polyIndex + 9]))
                        tmp_poly2d.at[tmp_index, 'offsetXloc2'] = max(float(params[polyIndex + 3]),
                                                                      float(params[polyIndex + 5]),
                                                                      float(params[polyIndex + 7]),
                                                                      float(params[polyIndex + 9]))
                        tmp_poly2d.at[tmp_index, 'offsetZ1'] = max(float(params[polyIndex + 4]),
                                                                   float(params[polyIndex + 6]),
                                                                   float(params[polyIndex + 8]),
                                                                   float(params[polyIndex + 10]))
                        tmp_poly2d.at[tmp_index, 'offsetZ2'] = min(float(params[polyIndex + 4]),
                                                                   float(params[polyIndex + 6]),
                                                                   float(params[polyIndex + 8]),
                                                                   float(params[polyIndex + 10]))
                        tmp_poly2d.at[tmp_index, 'offsetX1'] = tmp_n2d.at['0', 'x'] + tmp_poly2d.at[
                            tmp_index, 'offsetXloc1'] * math.cos(wall.at[tmp_n2d.at['0', 'wall'], 'angle'])
                        tmp_poly2d.at[tmp_index, 'offsetX2'] = tmp_n2d.at['0', 'x'] + tmp_poly2d.at[
                            tmp_index, 'offsetXloc2'] * math.cos(wall.at[tmp_n2d.at['0', 'wall'], 'angle'])
                        tmp_poly2d.at[tmp_index, 'offsetY1'] = tmp_n2d.at['0', 'y'] + tmp_poly2d.at[
                            tmp_index, 'offsetXloc1'] * math.sin(wall.at[tmp_n2d.at['0', 'wall'], 'angle'])
                        tmp_poly2d.at[tmp_index, 'offsetY2'] = tmp_n2d.at['0', 'y'] + tmp_poly2d.at[
                            tmp_index, 'offsetXloc2'] * math.sin(wall.at[tmp_n2d.at['0', 'wall'], 'angle'])
                        polyIndex = polyIndex + 11

                if "P" in params[4]:
                    for polyItem in np.arange(4):
                        tmp_poly2d_list.append(tmp_poly2d.values.tolist()[polyItem])
                tmp_n2d_list.append(tmp_n2d.values.tolist()[0])
                insideCounter = insideCounter + 1
                insideCounter = checkEmpty(lines, insideCounter)
                tmp_n2d = empty_tmp_n2d.copy(deep=True)
                tmp_poly2d = empty_tmp_poly2d.copy(deep=True)

            n2d = pd.DataFrame(tmp_n2d_list, columns=['Node', 'wall', 'x_loc', 'z', 'type', 'rho', 'thickness',
                                                      'offsetXloc1', 'offsetXloc2', 'offsetZ1', 'offsetZ2', 'repartition1',
                                                      'repartition2', 'x', 'y', 'offsetX1', 'offsetX2', 'offsetY1',
                                                      'offsetY2'])
            n2d = n2d.set_index('Node')
            poly2d = pd.DataFrame(tmp_poly2d_list, columns=['Node - Global', 'Node - Local', 'rho', 'thickness',
                                                            'offsetXloc1', 'offsetXloc2', 'offsetZ1', 'offsetZ2',
                                                            'offsetX1', 'offsetX2', 'offsetY1', 'offsetY2'])
            poly2d = poly2d.set_index('Node - Global')
            # Convert the dataframe to an XlsxWriter Excel object.
            poly2d.to_excel(writer, sheet_name='polygon 2d')

        # find the repartition properties for 2d nodes
        if (("ripartizione" in lines[lineCounter]) or ("2D_mass_sharing" in lines[lineCounter])) and (
                "!" not in lines[lineCounter]):
            insideCounter = lineCounter + 1
            insideCounter = checkEmpty(lines, insideCounter)
            while lines[insideCounter][0] != '/':
                while (lines[insideCounter][0] == '!') or (lines[insideCounter][0:1] == '\t'):
                    insideCounter = insideCounter + 1
                    insideCounter = checkEmpty(lines, insideCounter)
                    if lines[insideCounter][0] == '/':
                        break
                if lines[insideCounter][0] == '/':
                    break
                params = lines[insideCounter].split()
                for paramCounter in np.arange(len(params)):
                    if params[paramCounter] == "":
                        lastItem = paramCounter - 1
                        break
                    elif paramCounter == len(params) - 1:
                        lastItem = len(params) - 1
                params = params[0:lastItem + 1]
                insideCounter = insideCounter + 1
                insideCounter = checkEmpty(lines, insideCounter)
                n2d.at[int(params[0]), 'repartition1'] = int(params[1])
                n2d.at[int(params[0]), 'repartition2'] = int(params[2])
            # Convert the dataframe to an XlsxWriter Excel object.
            n2d.to_excel(writer, sheet_name='node 2d')

        # find the parameters for 3D nodes
        if (("nodi3d" in lines[lineCounter]) or ("nodes_3d" in lines[lineCounter])) and ("!" not in lines[lineCounter]):
            insideCounter = lineCounter + 1
            node3DLine = insideCounter
            insideCounter = checkEmpty(lines, insideCounter)
            while lines[insideCounter][0] != '/':
                while (lines[insideCounter][0] == '!') or (lines[insideCounter][0:1] == '\t'):
                    insideCounter = insideCounter + 1
                    insideCounter = checkEmpty(lines, insideCounter)
                    if lines[insideCounter][0] == '/':
                        break
                if lines[insideCounter][0] == '/':
                    break
                n3dNumber = n3dNumber + 1
                params = lines[insideCounter].split()
                for paramCounter in np.arange(len(params)):
                    if params[paramCounter] == "":
                        lastItem = paramCounter - 1
                        break
                    elif paramCounter == len(params) - 1:
                        lastItem = len(params) - 1
                params = params[0:lastItem + 1]
                if maxNodeNumber < int(params[0]):
                    maxNodeNumber = int(params[0])
                for item in np.arange(6):
                    tmp_n3d.iat[0, item] = params[item]
                tmp_n3d[['Node', 'n_wall2', 'wall1', 'wall2']] = tmp_n3d[['Node', 'n_wall2', 'wall1', 'wall2']].astype(int)
                tmp_n3d['z'] = tmp_n3d['z'].astype(float)
                if "N" in tmp_n3d.at['0', 'type']:
                    if "P" in params[6]:
                        tmp_n3d.at['0', 'type'] = tmp_n3d.at['0', 'type'] + "P"
                    else:
                        tmp_n3d.at['0', 'type'] = tmp_n3d.at['0', 'type'] + params[6]
                        if "R" in params[6]:
                            tmp_index = 12
                            for item in np.arange(7, 13):
                                tmp_n3d.iat[0, tmp_index] = float(params[item])
                                tmp_index = tmp_index + 1
                            tmp_n3d.at['0', 'offsetXloc21'] = -1 * tmp_n3d.at['0', 'offsetXloc21']
                            tmp_n3d.at['0', 'offsetZ22'] = -1 * tmp_n3d.at['0', 'offsetZ22']
                elif "R" in tmp_n3d.at['0', 'type']:
                    for item in np.arange(6, 12):
                        tmp_n3d.iat[0, item] = float(params[item])
                    tmp_n3d.at['0', 'offsetXloc11'] = -1 * tmp_n3d.at['0', 'offsetXloc11']
                    tmp_n3d.at['0', 'offsetZ12'] = -1 * tmp_n3d.at['0', 'offsetZ12']
                    if "P" in params[12]:
                        tmp_n3d.at['0', 'type'] = tmp_n3d.at['0', 'type'] + "P"
                    else:
                        tmp_n3d.at['0', 'type'] = tmp_n3d.at['0', 'type'] + params[12]
                        if "R" in params[12]:
                            for item in np.arange(13, 19):
                                tmp_n3d.iat[0, item - 1] = float(params[item])
                            tmp_n3d.at['0', 'offsetXloc21'] = -1 * tmp_n3d.at['0', 'offsetXloc21']
                            tmp_n3d.at['0', 'offsetZ22'] = -1 * tmp_n3d.at['0', 'offsetZ22']
                elif "P" in tmp_n3d.at['0', 'type']:
                    loc_index = params.index('|')
                    if "P" in params[loc_index + 1]:
                        tmp_n3d.at['0', 'type'] = "PP"
                    else:
                        tmp_n3d.at['0', 'type'] = "P" + params[loc_index + 1]
                        if "R" in params[loc_index + 1]:
                            for item in np.arange(loc_index + 2, loc_index + 8):
                                tmp_index = 12
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
                if "R" in tmp_type[0]:
                    tmp_n3d.at['0', 'offsetX11'] = tmp_n3d.at['0', 'x'] + tmp_n3d.at['0', 'offsetXloc11'] * \
                                                   math.cos(wall.at[tmp_n3d.at['0', 'wall1'], 'angle'])
                    tmp_n3d.at['0', 'offsetX12'] = tmp_n3d.at['0', 'x'] + tmp_n3d.at['0', 'offsetXloc12'] * \
                                                   math.cos(wall.at[tmp_n3d.at['0', 'wall1'], 'angle'])
                    tmp_n3d.at['0', 'offsetY11'] = tmp_n3d.at['0', 'y'] + tmp_n3d.at['0', 'offsetXloc11'] * \
                                                   math.sin(wall.at[tmp_n3d.at['0', 'wall1'], 'angle'])
                    tmp_n3d.at['0', 'offsetY12'] = tmp_n3d.at['0', 'y'] + tmp_n3d.at['0', 'offsetXloc12'] * \
                                                   math.sin(wall.at[tmp_n3d.at['0', 'wall1'], 'angle'])
                if "R" in tmp_type[1]:
                    tmp_n3d.at['0', 'offsetX21'] = tmp_n3d.at['0', 'x'] + tmp_n3d.at['0', 'offsetXloc21'] * \
                                                   math.cos(wall.at[tmp_n3d.at['0', 'wall2'], 'angle'])
                    tmp_n3d.at['0', 'offsetX22'] = tmp_n3d.at['0', 'x'] + tmp_n3d.at['0', 'offsetXloc22'] * \
                                                   math.cos(wall.at[tmp_n3d.at['0', 'wall2'], 'angle'])
                    tmp_n3d.at['0', 'offsetY21'] = tmp_n3d.at['0', 'y'] + tmp_n3d.at['0', 'offsetXloc21'] * \
                                                   math.sin(wall.at[tmp_n3d.at['0', 'wall2'], 'angle'])
                    tmp_n3d.at['0', 'offsetY22'] = tmp_n3d.at['0', 'y'] + tmp_n3d.at['0', 'offsetXloc22'] *\
                                                   math.sin(wall.at[tmp_n3d.at['0', 'wall2'], 'angle'])
                if "P" in tmp_type[0]:
                    poly3dNumber1 = poly3dNumber1 + 1
                    for nodeItem in np.arange(4):
                        tmp_poly3d1['Node - Global'].iat[nodeItem] = int(params[0])
                    loc_index = params.index('|')
                    for item in np.arange(5, loc_index):
                        if "P" in params[item]:
                            tmp_index = params[item]
                            tmp_index = str(int(tmp_index[1]) - 1)
                            tmp_poly3d1.at[tmp_index, 'rho'] = float(params[item + 1])
                            tmp_poly3d1.at[tmp_index, 'thickness'] = float(params[item + 2])
                            tmp_poly3d1.at[tmp_index, 'offsetXloc1'] = min(float(params[item + 3]), float(params[item + 5]),
                                                                           float(params[item + 7]), float(params[item + 9]))
                            tmp_poly3d1.at[tmp_index, 'offsetXloc2'] = max(float(params[item + 3]), float(params[item + 5]),
                                                                           float(params[item + 7]), float(params[item + 9]))
                            tmp_poly3d1.at[tmp_index, 'offsetZ1'] = min(float(params[item + 4]), float(params[item + 6]),
                                                                        float(params[item + 8]), float(params[item + 10]))
                            tmp_poly3d1.at[tmp_index, 'offsetZ2'] = max(float(params[item + 4]), float(params[item + 6]),
                                                                        float(params[item + 8]), float(params[item + 10]))
                            tmp_poly3d1.at[tmp_index, 'offsetX1'] = tmp_n3d.at['0', 'x'] + tmp_poly3d1.at[
                                tmp_index, 'offsetXloc1'] * math.cos(wall.at[tmp_n3d.at['0', 'wall1'], 'angle'])
                            tmp_poly3d1.at[tmp_index, 'offsetX2'] = tmp_n3d.at['0', 'x'] + tmp_poly3d1.at[
                                tmp_index, 'offsetXloc2'] * math.cos(wall.at[tmp_n3d.at['0', 'wall1'], 'angle'])
                            tmp_poly3d1.at[tmp_index, 'offsetY1'] = tmp_n3d.at['0', 'y'] + tmp_poly3d1.at[
                                tmp_index, 'offsetXloc1'] * math.sin(wall.at[tmp_n3d.at['0', 'wall1'], 'angle'])
                            tmp_poly3d1.at[tmp_index, 'offsetY2'] = tmp_n3d.at['0', 'y'] + tmp_poly3d1.at[
                                tmp_index, 'offsetXloc2'] * math.sin(wall.at[tmp_n3d.at['0', 'wall1'], 'angle'])
                if "P" in tmp_type[1]:
                    poly3dNumber2 = poly3dNumber2 + 1
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
                            tmp_poly3d2.at[tmp_index, 'offsetXloc1'] = min(float(params[item + 3]), float(params[item + 5]),
                                                                           float(params[item + 7]), float(params[item + 9]))
                            tmp_poly3d2.at[tmp_index, 'offsetXloc2'] = max(float(params[item + 3]), float(params[item + 5]),
                                                                           float(params[item + 7]), float(params[item + 9]))
                            tmp_poly3d2.at[tmp_index, 'offsetZ1'] = min(float(params[item + 4]), float(params[item + 6]),
                                                                        float(params[item + 8]), float(params[item + 10]))
                            tmp_poly3d2.at[tmp_index, 'offsetZ2'] = max(float(params[item + 4]), float(params[item + 6]),
                                                                        float(params[item + 8]), float(params[item + 10]))
                            tmp_poly3d2.at[tmp_index, 'offsetX1'] = tmp_n3d.at['0', 'x'] + tmp_poly3d2.at[
                                tmp_index, 'offsetXloc1'] * math.cos(wall.at[tmp_n3d.at['0', 'wall2'], 'angle'])
                            tmp_poly3d2.at[tmp_index, 'offsetX2'] = tmp_n3d.at['0', 'x'] + tmp_poly3d2.at[
                                tmp_index, 'offsetXloc2'] * math.cos(wall.at[tmp_n3d.at['0', 'wall2'], 'angle'])
                            tmp_poly3d2.at[tmp_index, 'offsetY1'] = tmp_n3d.at['0', 'y'] + tmp_poly3d2.at[
                                tmp_index, 'offsetXloc1'] * math.sin(wall.at[tmp_n3d.at['0', 'wall2'], 'angle'])
                            tmp_poly3d2.at[tmp_index, 'offsetY2'] = tmp_n3d.at['0', 'y'] + tmp_poly3d2.at[
                                tmp_index, 'offsetXloc2'] * math.sin(wall.at[tmp_n3d.at['0', 'wall2'], 'angle'])
                tmp_n3d_list.append(tmp_n3d.values.tolist()[0])
                if "P" in tmp_type[0]:
                    for polyItem in np.arange(4):
                        tmp_poly3d1_list.append(tmp_poly3d1.values.tolist()[polyItem])
                if "P" in tmp_type[1]:
                    for polyItem in np.arange(4):
                        tmp_poly3d2_list.append(tmp_poly3d2.values.tolist()[polyItem])
                insideCounter = insideCounter + 1
                insideCounter = checkEmpty(lines, insideCounter)
                tmp_n3d = empty_tmp_n3d.copy(deep=True)
                tmp_poly3d1 = empty_tmp_poly3d1.copy(deep=True)
                tmp_poly3d2 = empty_tmp_poly3d2.copy(deep=True)

            n3d = pd.DataFrame(tmp_n3d_list, columns=['Node', 'n_wall2', 'wall1', 'wall2', 'z', 'type', 'rho1',
                                                      'thickness1', 'offsetXloc11', 'offsetXloc12', 'offsetZ11',
                                                      'offsetZ12', 'rho2', 'thickness2', 'offsetXloc21', 'offsetXloc22',
                                                      'offsetZ21', 'offsetZ22', 'x', 'y', 'offsetX11', 'offsetX12',
                                                      'offsetY11', 'offsetY12', 'offsetX21', 'offsetX22', 'offsetY21',
                                                      'offsetY22'])
            n3d = n3d.set_index('Node')
            poly3d1 = pd.DataFrame(tmp_poly3d1_list, columns=['Node - Global', 'Node - Local', 'rho', 'thickness',
                                                              'offsetXloc1', 'offsetXloc2', 'offsetZ1', 'offsetZ2',
                                                              'offsetX1', 'offsetX2', 'offsetY1', 'offsetY2'])
            poly3d2 = pd.DataFrame(tmp_poly3d2_list, columns=['Node - Global', 'Node - Local', 'rho', 'thickness',
                                                              'offsetXloc1', 'offsetXloc2', 'offsetZ1', 'offsetZ2',
                                                              'offsetX1', 'offsetX2', 'offsetY1', 'offsetY2'])
            poly3d1 = poly3d1.set_index('Node - Global')
            poly3d2 = poly3d2.set_index('Node - Global')
            # Convert the dataframe to an XlsxWriter Excel object.
            n3d.to_excel(writer, sheet_name='node 3d')
            poly3d1.to_excel(writer, sheet_name='polygon 3d - 1')
            poly3d2.to_excel(writer, sheet_name='polygon 3d - 2')

        # find the parameters for elastic beams
        if (("traveElastica" in lines[lineCounter]) or ("Beam_elastic" in lines[lineCounter])) and (
                "!" not in lines[lineCounter]):
            insideCounter = lineCounter + 1
            insideCounter = checkEmpty(lines, insideCounter)
            while lines[insideCounter][0] != '/':
                while (lines[insideCounter][0] == '!') or (lines[insideCounter][0:1] == '\t'):
                    insideCounter = insideCounter + 1
                    insideCounter = checkEmpty(lines, insideCounter)
                    if lines[insideCounter][0] == '/':
                        break
                if lines[insideCounter][0] == '/':
                    break
                elasticBeamNumber = elasticBeamNumber + 1
                params = lines[insideCounter].split()
                for paramCounter in np.arange(len(params)):
                    if params[paramCounter] == "":
                        lastItem = paramCounter - 1
                        break
                    elif paramCounter == len(params) - 1:
                        lastItem = len(params) - 1
                params = params[0:lastItem + 1]
                for item in np.arange(lastItem + 1):
                    tmp_elasticBeam.iat[0, item] = params[item]
                tmp_elasticBeam_list.append(tmp_elasticBeam.values.tolist()[0])
                insideCounter = insideCounter + 1
                insideCounter = checkEmpty(lines, insideCounter)
            elasticBeam = pd.DataFrame(tmp_elasticBeam_list, columns=['No', 'wall', 'nodeI', 'nodeJ', 'mat', 'area', 'J',
                                                                      'deformIn', 'type', 'offXloc_I', 'offZ_I',
                                                                      'offXloc_J', 'offZ_J'])
            elasticBeam = elasticBeam.astype(float)  # convert all the variables to float
            elasticBeam[['No', 'wall', 'nodeI', 'nodeJ', 'mat', 'type']] = elasticBeam[['No', 'wall', 'nodeI', 'nodeJ', 'mat', 'type']].astype(int)
            elasticBeam = elasticBeam.set_index('No')
            # Convert the dataframe to an XlsxWriter Excel object.
            elasticBeam.to_excel(writer, sheet_name='elastic beam')

        # find the parameters for nonlinear beams
        if (("traveNonLineare" in lines[lineCounter]) or ("Beam_nonlinear" in lines[lineCounter])) and (
                "!" not in lines[lineCounter]):
            insideCounter = lineCounter + 1
            insideCounter = checkEmpty(lines, insideCounter)
            while lines[insideCounter][0] != '/':
                while (lines[insideCounter][0] == '!') or (lines[insideCounter][0:1] == '\t'):
                    insideCounter = insideCounter + 1
                    insideCounter = checkEmpty(lines, insideCounter)
                    if lines[insideCounter][0] == '/':
                        break
                if lines[insideCounter][0] == '/':
                    break
                nlBeamNumber = nlBeamNumber + 1
                params = lines[insideCounter].split()
                for paramCounter in np.arange(len(params)):
                    if params[paramCounter] == "":
                        lastItem = paramCounter - 1
                        break
                    elif paramCounter == len(params) - 1:
                        lastItem = len(params) - 1
                params = params[0:lastItem + 1]
                for item in np.arange(lastItem + 1):
                    tmp_nlBeam.iat[0, item] = params[item]
                tmp_nlBeam_list.append(tmp_nlBeam.values.tolist()[0])
                insideCounter = insideCounter + 1
                insideCounter = checkEmpty(lines, insideCounter)
            nlBeam = pd.DataFrame(tmp_nlBeam_list, columns=['No', 'wall', 'nodeI', 'nodeJ', 'mat', 'area', 'J',
                                                            'offXloc_I', 'offZ_I', 'offXloc_J', 'offZ_J', 'type',
                                                            'deformIn', 'Wpl'])
            nlBeam = nlBeam.astype(float)  # convert all the variables to float
            nlBeam[['No', 'wall', 'nodeI', 'nodeJ', 'mat', 'type']] = nlBeam[['No', 'wall', 'nodeI', 'nodeJ', 'mat', 'type']].astype(int)
            nlBeam = nlBeam.set_index('No')
            # Convert the dataframe to an XlsxWriter Excel object.
            nlBeam.to_excel(writer, sheet_name='nonlinear beam')

        # find the parameters for elements
        if (("macroelementoCalibrato" in lines[lineCounter]) or ("macroelemento" in lines[lineCounter]) or (
                "elementi" in lines[lineCounter]) or ("elementoOPCM3274" in lines[lineCounter]) or (
                    "macroelements" in lines[lineCounter]) or ("bilinear" in lines[lineCounter])) and (
                "!" not in lines[lineCounter]):
            insideCounter = lineCounter + 1
            insideCounter = checkEmpty(lines, insideCounter)
            while lines[insideCounter][0] != '/':
                while (lines[insideCounter][0] == '!') or (lines[insideCounter][0:1] == '\t'):
                    insideCounter = insideCounter + 1
                    insideCounter = checkEmpty(lines, insideCounter)
                    if lines[insideCounter][0] == '/':
                        break
                if lines[insideCounter][0] == '/':
                    break
                elementNumber = elementNumber + 1
                params = lines[insideCounter].split()
                for paramCounter in np.arange(len(params)):
                    if params[paramCounter] == "":
                        lastItem = paramCounter - 1
                        break
                    elif paramCounter == len(params) - 1:
                        lastItem = len(params) - 1
                params = params[0:lastItem + 1]
                for item in np.arange(lastItem + 1):
                    tmp_element.iat[0, item] = params[item]
                tmp_element[['No', 'wall', 'nodeI', 'nodeJ', 'mat', 'type']] = tmp_element[
                    ['No', 'wall', 'nodeI', 'nodeJ', 'mat', 'type']].astype(int)
                tmp_element[['xBar', 'zBar', 'L', 'H', 't']] = tmp_element[['xBar', 'zBar', 'L', 'H', 't']].astype(float)
                tmp_element_list.append(tmp_element.values.tolist()[0])
                insideCounter = insideCounter + 1
                insideCounter = checkEmpty(lines, insideCounter)
            element = pd.DataFrame(tmp_element_list, columns=['No', 'wall', 'nodeI', 'nodeJ', 'xBar', 'zBar', 'L', 'H',
                                                              't', 'mat', 'type', 'angle', 'nI1', 'nI2', 'nI3', 'nJ1',
                                                              'nJ2', 'nJ3'])
            for item in np.arange(elementNumber):
                if element['type'].iat[item] == 0:
                    element['angle'].iat[item] = 0.5 * math.pi
                elif element['type'].iat[item] == 1:
                    element['angle'].iat[item] = 0.0
                # assign offset to elements
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
            element = element.set_index('No')
            # Convert the dataframe to an XlsxWriter Excel object.
            element.to_excel(writer, sheet_name='elements')

        # find the parameters for different analysis types
        if ("/pp" in lines[lineCounter]) and ("!" not in lines[lineCounter]):  # static analysis
            insideCounter = lineCounter
            insideCounter = checkEmpty(lines, insideCounter)
            while (lines[insideCounter][0] == '!') or (lines[insideCounter][0:1] == '\t'):
                insideCounter = insideCounter + 1
            analysisNumber = analysisNumber + 1
            check = lines[insideCounter]
            params = lines[insideCounter].split()
            for paramCounter in np.arange(len(params)):
                if params[paramCounter] == "":
                    lastItem = paramCounter - 1
                    break
                elif paramCounter == len(params) - 1:
                    lastItem = len(params) - 1
            params = params[1:lastItem + 1]
            tmp_analysis.at['0', 'analysisNumber'] = analysisNumber
            tmp_analysis.at['0', 'type'] = 'selfWeight'
            tmp_analysis.at['0', 'nSteps'] = int(params[0])
            tmp_analysis.at['0', 'tol'] = float(params[1])
            tmp_analysis.at['0', 'maxStep'] = int(params[2])
            tmp_analysis.at['0', 'accVec1'] = float(params[3])
            tmp_analysis.at['0', 'accVec2'] = float(params[4])
            tmp_analysis.at['0', 'accVec3'] = float(params[5])
            tmp_analysis_list.append(tmp_analysis.values.tolist()[0])
            tmp_analysis = empty_tmp_analysis.copy(deep=True)
        elif ("/am" in lines[lineCounter]) and ("!" not in lines[lineCounter]):
            insideCounter = lineCounter
            insideCounter = checkEmpty(lines, insideCounter)
            while (lines[insideCounter][0] == '!') or (lines[insideCounter][0:1] == '\t'):
                insideCounter = insideCounter + 1
            analysisNumber = analysisNumber + 1
            check = lines[insideCounter]
            params = lines[insideCounter].split()
            for paramCounter in np.arange(len(params)):
                if params[paramCounter] == "":
                    lastItem = paramCounter - 1
                    break
                elif paramCounter == len(params) - 1:
                    lastItem = len(params) - 1
            params = params[1:lastItem + 1]
            tmp_analysis.at['0', 'analysisNumber'] = analysisNumber
            tmp_analysis.at['0', 'type'] = 'modal'
            tmp_analysis.at['0', 'nModes'] = int(params[0])
            tmp_analysis_list.append(tmp_analysis.values.tolist()[0])
            tmp_analysis = empty_tmp_analysis.copy(deep=True)
        elif (("/pomas" in lines[lineCounter]) or ("/pomaz" in lines[lineCounter])) and ("!" not in lines[lineCounter]):
            insideCounter = lineCounter
            insideCounter = checkEmpty(lines, insideCounter)
            while (lines[insideCounter][0] == '!') or (lines[insideCounter][0:1] == '\t'):
                insideCounter = insideCounter + 1
            analysisNumber = analysisNumber + 1
            check = lines[insideCounter]
            params = lines[insideCounter].split()
            for paramCounter in np.arange(len(params)):
                if params[paramCounter] == "":
                    lastItem = paramCounter - 1
                    break
                elif paramCounter == len(params) - 1:
                    lastItem = len(params) - 1
            params = params[1:lastItem + 1]
            tmp_analysis.at['0', 'analysisNumber'] = analysisNumber
            if "/pomas" in lines[lineCounter]:
                tmp_analysis.at['0', 'type'] = 'pushoverRectangular'
            elif "/pomaz" in lines[lineCounter]:
                tmp_analysis.at['0', 'type'] = 'pushoverTriangular'
            tmp_analysis.at['0', 'nSteps'] = int(params[0])
            tmp_analysis.at['0', 'tol'] = float(params[1])
            tmp_analysis.at['0', 'maxStep'] = int(params[2])
            tmp_analysis.at['0', 'controlNode'] = int(params[3])
            tmp_analysis.at['0', 'DOF'] = int(params[4])
            tmp_analysis.at['0', 'maxDisp'] = float(params[5])
            tmp_analysis.at['0', 'forceDrop'] = float(params[6])
            tmp_analysis_list.append(tmp_analysis.values.tolist()[0])
            tmp_analysis = empty_tmp_analysis.copy(deep=True)
        elif ("/po" in lines[lineCounter]) and ("!" not in lines[lineCounter]):
            insideCounter = lineCounter
            insideCounter = checkEmpty(lines, insideCounter)
            while (lines[insideCounter][0] == '!') or (lines[insideCounter][0:1] == '\t'):
                insideCounter = insideCounter + 1
            analysisNumber = analysisNumber + 1
            check = lines[insideCounter]
            params = lines[insideCounter].split()
            for paramCounter in np.arange(len(params)):
                if params[paramCounter] == "":
                    lastItem = paramCounter - 1
                    break
                elif paramCounter == len(params) - 1:
                    lastItem = len(params) - 1
            params = params[1:lastItem + 1]
            tmp_analysis.at['0', 'analysisNumber'] = analysisNumber
            tmp_analysis.at['0', 'type'] = 'pushoverGeneric'
            tmp_analysis.at['0', 'nSteps'] = int(params[0])
            tmp_analysis.at['0', 'tol'] = float(params[1])
            tmp_analysis.at['0', 'maxStep'] = int(params[2])
            tmp_analysis.at['0', 'controlNode'] = int(params[3])
            tmp_analysis.at['0', 'DOF'] = int(params[4])
            tmp_analysis.at['0', 'maxDisp'] = float(params[5])
            tmp_analysis.at['0', 'forceDrop'] = float(params[6])
            tmp_analysis_list.append(tmp_analysis.values.tolist()[0])
            tmp_analysis = empty_tmp_analysis.copy(deep=True)
            insideCounter = insideCounter + 1
            loadNumber = 0

            while lines[insideCounter][0] != '/':
                while (lines[insideCounter][0] == '!') or (lines[insideCounter][0:1] == '\t'):
                    insideCounter = insideCounter + 1
                    insideCounter = checkEmpty(lines, insideCounter)
                    if lines[insideCounter][0] == '/':
                        break
                if lines[insideCounter][0] == '/':
                    break
                loadNumber = loadNumber + 1
                params = lines[insideCounter].split()
                for paramCounter in np.arange(len(params)):
                    if params[paramCounter] == "":
                        lastItem = paramCounter - 1
                        break
                    elif paramCounter == len(params) - 1:
                        lastItem = len(params) - 1
                params = params[0:lastItem + 1]
                tmp_analysis.at['0', 'analysisNumber'] = analysisNumber
                tmp_analysis.at['0', 'loadedNode'] = int(params[0])
                tmp_analysis.at['0', 'load1'] = float(params[1])
                tmp_analysis.at['0', 'load2'] = float(params[2])
                tmp_analysis.at['0', 'load3'] = float(params[3])
                if lastItem == 3:
                    tmp_analysis.at['0', 'load4'] = 0
                    tmp_analysis.at['0', 'load5'] = 0
                elif lastItem == 5:
                    tmp_analysis.at['0', 'load4'] = float(params[4])
                    tmp_analysis.at['0', 'load5'] = float(params[5])
                tmp_analysis_list.append(tmp_analysis.values.tolist()[0])
                tmp_analysis = empty_tmp_analysis.copy(deep=True)
                insideCounter = insideCounter + 1
                insideCounter = checkEmpty(lines, insideCounter)
        elif ("/ad" in lines[lineCounter]) and ("!" not in lines[lineCounter]):
            insideCounter = lineCounter
            insideCounter = checkEmpty(lines, insideCounter)
            while (lines[insideCounter][0] == '!') or (lines[insideCounter][0:1] == '\t'):
                insideCounter = insideCounter + 1
            analysisNumber = analysisNumber + 1
            check = lines[insideCounter]
            params = lines[insideCounter].split()
            for paramCounter in np.arange(len(params)):
                if params[paramCounter] == "":
                    lastItem = paramCounter - 1
                    break
                elif paramCounter == len(params) - 1:
                    lastItem = len(params) - 1
            params = params[1:lastItem + 1]
            tmp_analysis.at['0', 'analysisNumber'] = analysisNumber
            tmp_analysis.at['0', 'type'] = 'Dynamic'
            tmp_analysis.at['0', 'nSteps'] = int(params[0])
            tmp_analysis.at['0', 'tol'] = float(params[1])
            tmp_analysis.at['0', 'maxStep'] = int(params[2])
            tmp_analysis.at['0', 'dt'] = float(params[3])
            tmp_analysis.at['0', 'rayleigh1'] = float(params[4])
            tmp_analysis.at['0', 'rayleigh2'] = float(params[5])
            tmp_analysis.at['0', 'subd'] = float(params[6])
            insideCounter = insideCounter + 1
            loadNumber = 0
            while lines[insideCounter][0] != '/':
                while (lines[insideCounter][0] == '!') or (lines[insideCounter][0:1] == '\t'):
                    insideCounter = insideCounter + 1
                    insideCounter = checkEmpty(lines, insideCounter)
                    if lines[insideCounter][0] == '/':
                        break
                if lines[insideCounter][0] == '/':
                    break
                loadNumber = loadNumber + 1
                params = lines[insideCounter].split()
                for paramCounter in np.arange(len(params)):
                    if params[paramCounter] == "":
                        lastItem = paramCounter - 1
                        break
                    elif paramCounter == len(params) - 1:
                        lastItem = len(params) - 1
                params = params[0:lastItem + 1]
                tmp_analysis.at['0', 'DOF'] = str(params[0])
                tmp_analysis.at['0', 'groundMotion'] = str(params[1])
                if lastItem == 1:
                    tmp_analysis.at['0', 'PGA'] = -1
                else:
                    tmp_analysis.at['0', 'PGA'] = float(params[2])

                tmp_analysis_list.append(tmp_analysis.values.tolist()[0])
                tmp_analysis = empty_tmp_analysis.copy(deep=True)
                insideCounter = insideCounter + 1
                insideCounter = checkEmpty(lines, insideCounter)

        if analysisNumber > 1 and analysisNumber > lastAnalysisNumber:
            analysis = pd.DataFrame(tmp_analysis_list, columns=['analysisNumber', 'type', 'nSteps', 'tol', 'maxStep',
                                                                'accVec1', 'accVec2', 'accVec3', 'dt', 'nModes',
                                                                'rayleigh1', 'rayleigh2', 'subd', 'controlNode', 'DOF',
                                                                'maxDisp', 'forceDrop', 'loadedNode', 'load1', 'load2',
                                                                'load3', 'load4', 'load5', 'groundMotion', 'PGA'])
        lastAnalysisNumber = analysisNumber
        # find the parameters for nodal masses
        if (("masse" in lines[lineCounter]) or ("mass" in lines[lineCounter])) and ("!" not in lines[lineCounter]):
            insideCounter = lineCounter + 1
            insideCounter = checkEmpty(lines, insideCounter)
            while lines[insideCounter][0] != '/':
                while (lines[insideCounter][0] == '!') or (lines[insideCounter][0:1] == '\t'):
                    insideCounter = insideCounter + 1
                    insideCounter = checkEmpty(lines, insideCounter)
                    if lines[insideCounter][0] == '/':
                        break
                if lines[insideCounter][0] == '/':
                    break
                nodalMassNumber = nodalMassNumber + 1
                params = lines[insideCounter].split()
                for paramCounter in np.arange(len(params)):
                    if params[paramCounter] == "":
                        lastItem = paramCounter - 1
                        break
                    elif paramCounter == len(params) - 1:
                        lastItem = len(params) - 1
                params = params[0:min(lastItem + 1, 4)]
                for item in np.arange(lastItem + 1):
                    tmp_nodalMass.iat[0, item] = params[item]
                if lastItem < 3:
                    tmp_nodalMass.at['0', 'ecc_z'] = 0
                    if lastItem < 2:
                        tmp_nodalMass.at['0', 'ecc_x'] = 0
                tmp_nodalMass_list.append(tmp_nodalMass.values.tolist()[0])
                insideCounter = insideCounter + 1
                insideCounter = checkEmpty(lines, insideCounter)
            nodalMass = pd.DataFrame(tmp_nodalMass_list, columns=['node', 'mass', 'ecc_x', 'ecc_z'])
            nodalMass = nodalMass.set_index('node')
            # Convert the dataframe to an XlsxWriter Excel object.
            nodalMass.to_excel(writer, sheet_name='nodal mass')

        # find the parameters for distributed masses
        if (("massedistr" in lines[lineCounter]) or ("massdistr" in lines[lineCounter])) and ("!" not in lines[lineCounter]):
            insideCounter = lineCounter + 1
            insideCounter = checkEmpty(lines, insideCounter)
            while lines[insideCounter][0] != '/':
                while (lines[insideCounter][0] == '!') or (lines[insideCounter][0:1] == '\t'):
                    insideCounter = insideCounter + 1
                    insideCounter = checkEmpty(lines, insideCounter)
                    if lines[insideCounter][0] == '/':
                        break
                if lines[insideCounter][0] == '/':
                    break
                distrMassNumber = distrMassNumber + 1
                params = lines[insideCounter].split()
                for paramCounter in np.arange(len(params)):
                    if params[paramCounter] == "":
                        lastItem = paramCounter - 1
                        break
                    elif paramCounter == len(params) - 1:
                        lastItem = len(params) - 1
                params = params[0:lastItem + 1]
                tmp_distrMass.at['0', 'node'] = params[0]
                tmp_distrMass.at['0', 'V'] = params[1]
                tmp_distrMass.at['0', 'M'] = params[2]
                tmp_distrMass.at['0', 'Vr'] = params[3]
                tmp_distrMass.at['0', 'Mr'] = params[4]
                tmp_distrMass.at['0', 'el'] = params[7]
                tmp_distrMass_list.append(tmp_distrMass.values.tolist()[0])
                insideCounter = insideCounter + 1
                insideCounter = checkEmpty(lines, insideCounter)
            distrMass = pd.DataFrame(tmp_distrMass_list, columns=['node', 'V', 'M', 'Vr', 'Mr', 'el'])
            distrMass = distrMass.set_index('node')
            # Convert the dataframe to an XlsxWriter Excel object.
            distrMass.to_excel(writer, sheet_name='distributed mass')
    print("Tremuri_Input completed in --- %s seconds ---" % (time.time() - startTime))

    if analysisNumber > 0:
        analysis = analysis.set_index('analysisNumber')
        # Convert the dataframe to an XlsxWriter Excel object.
        analysis.to_excel(writer, sheet_name='analysis')

    # Close the Pandas Excel writer and output the Excel file.
    writer.save()

    return wall, n2d, poly2d, n3d, poly3d1, poly3d2, maxNodeNumber, element, elasticBeam, nlBeam, floorLevel, floor, \
           material, nodalMass, restraint, analysis

import Tremuri_Input_func
import numpy as np
import pandas as pd
import math
from numpy import linalg
from os.path import join
import time


def dataConcat(number, tmp, full):
    if number == 1:
        full = tmp.copy(deep=True)
    else:
        full = pd.concat([full, tmp])
    return full


def rotate3D(f_vec, f_angles):
    gamma = linalg.norm(f_angles)
    if gamma == 0:
        rotated = f_vec
    else:
        f_angles = f_angles/gamma
        T = np.zeros((3, 3))
        c = math.cos(gamma)
        s = math.sin(gamma)
        T[0][0] = c + (1 - c) * f_angles[0] ** 2
        T[0][1] = f_angles[2] * s + (1 - c) * f_angles[0] * f_angles[1]
        T[0][2] = -1 * f_angles[1] * s + (1 - c) * f_angles[0] * f_angles[2]
        T[1][0] = -1 * f_angles[2] * s + (1 - c) * f_angles[0] * f_angles[1]
        T[1][1] = c + (1 - c) * f_angles[1] ** 2
        T[1][2] = f_angles[0] * s + (1 - c) * f_angles[1] * f_angles[2]
        T[2][0] = f_angles[1] * s + (1 - c) * f_angles[0] * f_angles[2]
        T[2][1] = -1 * f_angles[0] * s + (1 - c) * f_angles[1] * f_angles[2]
        T[2][2] = c + (1 - c) * f_angles[2] ** 2
        rotated = np.dot(T.transpose(), f_vec)
    return rotated


def nodeSplit(nIJ, doubleNodes, tempEl, Tremuri3D):
    f_nI = nIJ
    if (doubleNodes['original'] == nIJ).any():
        if tempEl.at['0', 'wall'] == Tremuri3D.at[nIJ, 'wall2']:
            f_nI = doubleNodes.at[doubleNodes[doubleNodes['original'] == nIJ].index[0], 'copy']
    return f_nI


completeFileLocation2 = ""


def CONVtriOPSfunc():
    global element, node, wall, floor, polygon, material, analysis, restraint, fixconstraint, w2wconstraint, f2wconstraint
    startTime = time.time()
    Tremuri_Input_func.completeFileLocation1 = completeFileLocation2
    Tremuri_Input_func.TRIfunc()

    # assign the required objects to variables
    impWall = Tremuri_Input_func.wall.copy(deep=True)
    impN2d = Tremuri_Input_func.n2d.copy(deep=True)
    impPoly2d = Tremuri_Input_func.poly2d.copy(deep=True)
    impN3d = Tremuri_Input_func.n3d.copy(deep=True)
    impPoly3d1 = Tremuri_Input_func.poly3d1.copy(deep=True)
    impPoly3d2 = Tremuri_Input_func.poly3d2.copy(deep=True)
    impMaxNodeNumber = Tremuri_Input_func.maxNodeNumber
    impElement = Tremuri_Input_func.element.copy(deep=True)
    impElasticBeam = Tremuri_Input_func.elasticBeam.copy(deep=True)
    impNlBeam = Tremuri_Input_func.nlBeam.copy(deep=True)
    impFloorLevel = Tremuri_Input_func.floorLevel.copy(deep=True)
    impFloor = Tremuri_Input_func.floor.copy(deep=True)
    impMaterial = Tremuri_Input_func.material.copy(deep=True)
    impNodalMass = Tremuri_Input_func.nodalMass.copy(deep=True)
    impRestraint = Tremuri_Input_func.restraint.copy(deep=True)
    impAnalysis = Tremuri_Input_func.analysis.copy(deep=True)

    writer = pd.ExcelWriter('opensees_input_parameters.xlsx', engine='xlsxwriter')
    # initiate wall data frame for OpenSees model
    wallNumber = 0
    tmp_wall = pd.DataFrame(columns=['No', 'origin', 'xAxis', 'yAxis', 'zAxis'], index=['0'])
    tmp_wall_list = []
    wall = pd.DataFrame(columns=['No', 'origin', 'xAxis', 'yAxis', 'zAxis'], index=['0'])
    # initiate node data frame for OpenSees model
    nodeNumber = 0
    tmp_node = pd.DataFrame(columns=['No', 'x', 'y', 'z', 'pos', 'wall', 'addedMass', 'addedMassEcc', 'repartition'],
                            index=['0'])
    tmp_node_list = []
    node = pd.DataFrame(columns=['No', 'x', 'y', 'z', 'pos', 'wall', 'addedMass', 'addedMassEcc', 'repartition'],
                        index=['0'])
    empty_tmp_node = pd.DataFrame(columns=['No', 'x', 'y', 'z', 'pos', 'wall', 'addedMass', 'addedMassEcc', 'repartition'],
                                  index=['0'])
    # initiate element data frame for OpenSees model
    elementNumber = 0
    tmp_element = pd.DataFrame(columns=['No', 'wall', 'nodeI', 'nodeJ', 'nodeE', 'nodeVec', 'xAxis', 'h', 'b', 't', 'type',
                                        'area', 'floor', 'mat', 'J', 'propVec', 'offsetI', 'offsetJ', 'Wpl', 'nodeK',
                                        'nodeL', 'properties'], index=['0'])
    tmp_element_list = []
    empty_tmp_element = pd.DataFrame(columns=['No', 'wall', 'nodeI', 'nodeJ', 'nodeE', 'nodeVec', 'xAxis', 'h', 'b', 't',
                                              'type', 'area', 'floor', 'mat', 'J', 'propVec', 'offsetI', 'offsetJ', 'Wpl',
                                              'nodeK', 'nodeL', 'properties'], index=['0'])
    element = pd.DataFrame(columns=['No', 'wall', 'nodeI', 'nodeJ', 'nodeE', 'nodeVec', 'xAxis', 'h', 'b', 't', 'type',
                                    'area', 'floor', 'mat', 'J', 'propVec', 'offsetI', 'offsetJ', 'Wpl', 'nodeK', 'nodeL',
                                    'properties'], index=['0'])
    # initiate node data frame for OpenSees model
    polygonNumber = 0
    tmp_polygon = pd.DataFrame(columns=['Node - Global', 'xDim', 'yDim', 'area', 'blCorner', 't', 'rho'], index=['0'])
    tmp_polygon_list = []
    polygon = pd.DataFrame(columns=['Node - Global', 'xDim', 'yDim', 'area', 'blCorner', 't', 'rho'], index=['0'])
    # initiate wall to wall constraint data frame for OpenSees model
    w2wTag = 0
    w2wconstraintNumber = 0
    tmp_w2wconstraint = pd.DataFrame(columns=['master', 'slave', 'dofs'], index=['0'])
    tmp_w2wconstraint_list = []
    w2wconstraint = pd.DataFrame(columns=['master', 'slave', 'dofs'], index=['0'])
    # initiate floor to wall constraint data frame for OpenSees model
    f2wTag = 0
    f2wconstraintNumber = 0
    tmp_f2wconstraint = pd.DataFrame(columns=['master', 'slave', 'dofs'], index=['0'])
    tmp_f2wconstraint_list = []
    f2wconstraint = pd.DataFrame(columns=['master', 'slave', 'dofs'], index=['0'])
    # initiate fix constraint data frame for OpenSees model
    newFix = 0
    fixconstraintNumber = 0
    tmp_fixconstraint = pd.DataFrame(columns=['node', 'dofs'], index=['0'])
    tmp_fixconstraint_list = []
    fixconstraint = pd.DataFrame(columns=['node', 'dofs'], index=['0'])
    # initiate doubled 3D nodes data frame for OpenSees model to keep a record of copied nodes
    double3DNodesNumber = 0
    tmp_double3DNodes = pd.DataFrame(columns=['original', 'copy'], index=['0'])
    tmp_double3DNodes_list = []
    double3DNodes = pd.DataFrame(columns=['original', 'copy'], index=['0'])
    # initiate floor data frame for OpenSees model
    floorNumber = 0
    tmp_floor = pd.DataFrame(columns=['h', 'zAxis'], index=['0'])
    tmp_floor_list = []
    floor = pd.DataFrame(columns=['h', 'zAxis'], index=['0'])
    # initiate material data frame for OpenSees model
    materialNumber = 0
    tmp_material = pd.DataFrame(
        columns=['No', 'E', 'G', 'rho', 'fc', 'tau0', 'verification', 'shear_model', 'drift_S', 'drift_F', 'mu', 'Gc',
                 'beta', 'muR'], index=['0'])
    material = pd.DataFrame(
        columns=['No', 'E', 'G', 'rho', 'fc', 'tau0', 'verification', 'shear_model', 'drift_S', 'drift_F', 'mu', 'Gc',
                 'beta', 'muR'], index=['0'])

    # Create OpenSees model for the walls
    totalWalls = impWall['angle'].count()
    for item in np.arange(totalWalls):
        wallNumber = wallNumber + 1
        tmp_wall.at['0', 'No'] = wallNumber
        tmp_wall.at['0', 'origin'] = np.round([impWall['x0'].iat[item],
                                      impWall['y0'].iat[item], 0], decimals=4)
        tmp_wall.at['0', 'xAxis'] = np.round([math.cos(impWall['angle'].iat[item]),
                                              math.sin(impWall['angle'].iat[item]), 0], decimals=4)
        tmp_wall.at['0', 'yAxis'] = [0, 0, 1]
        tmp_wall.at['0', 'zAxis'] = np.round(np.cross(tmp_wall.at['0', 'xAxis'], tmp_wall.at['0', 'yAxis']), decimals=4)
        tmp_wall_list.append(tmp_wall.values.tolist()[0])
    wall = pd.DataFrame(tmp_wall_list, columns=['No', 'origin', 'xAxis', 'yAxis', 'zAxis'])
    wall = wall.set_index('No')
    wall.to_excel(writer, sheet_name='walls')

    # Create OpenSees model for 2D nodes
    total2DNodes = impN2d['wall'].count()
    for item in np.arange(total2DNodes):
        nodeNumber = nodeNumber + 1
        tmp_node = empty_tmp_node.copy(deep=True)
        tmp_node.at['0', 'No'] = impN2d.index[item]
        tmp_node.at['0', 'x'] = np.round(impN2d['x'].iat[item], decimals=4)
        tmp_node.at['0', 'y'] = np.round(impN2d['y'].iat[item], decimals=4)
        tmp_node.at['0', 'z'] = np.round(impN2d['z'].iat[item], decimals=4)
        tmp_node.at['0', 'pos'] = [tmp_node.at['0', 'x'], tmp_node.at['0', 'y'], tmp_node.at['0', 'z']]
        tmp_node.at['0', 'wall'] = impN2d['wall'].iat[item]
        tmp_node.at['0', 'repartition'] = [impN2d['repartition1'].iat[item], impN2d[
            'repartition2'].iat[item]]
        tmp_node_list.append(tmp_node.values.tolist()[0])
        if impN2d['type'].iat[item] == "R":
            polygonNumber = polygonNumber + 1
            tmp_polygon.at['0', 'Node - Global'] = tmp_node.at['0', 'No']
            tmp_polygon.at['0', 'xDim'] = abs(impN2d['offsetXloc2'].iat[item] -
                impN2d['offsetXloc1'].iat[item])
            tmp_polygon.at['0', 'yDim'] = abs(impN2d['offsetZ2'].iat[item] -
                impN2d['offsetZ1'].iat[item])
            tmp_polygon.at['0', 'area'] = tmp_polygon.at['0', 'xDim'] * tmp_polygon.at['0', 'yDim']
            tmp_polygon.at['0', 'blCorner'] = np.round([min(impN2d['offsetX1'].iat[item],
                                                            impN2d['offsetX2'].iat[item]),
                                                        min(impN2d['offsetY1'].iat[item],
                                                            impN2d['offsetY2'].iat[item]),
                                                        tmp_node.at['0', 'z'] +
                                                        min(impN2d['offsetZ1'].iat[item],
                                                            impN2d['offsetZ2'].iat[item])], decimals=4)
            tmp_polygon.at['0', 't'] = impN2d['thickness'].iat[item]
            tmp_polygon.at['0', 'rho'] = impN2d['rho'].iat[item]
            tmp_polygon_list.append(tmp_polygon.values.tolist()[0])
        elif impN2d['type'].iat[item] == "P":
            # extract the polygon data for current node
            sub_polygon = impPoly2d.groupby(impPoly2d.index).get_group(tmp_node.at['0', 'No'])
            for localNodeCounter in np.arange(4):
                polygonNumber = polygonNumber + 1
                if not pd.isnull(sub_polygon['rho'].iat[localNodeCounter]):
                    tmp_polygon.at['0', 'Node - Global'] = tmp_node.at['0', 'No']
                    tmp_polygon.at['0', 'xDim'] = abs(sub_polygon['offsetXloc2'].iat[localNodeCounter] - sub_polygon[
                        'offsetXloc1'].iat[localNodeCounter])
                    tmp_polygon.at['0', 'yDim'] = abs(sub_polygon['offsetZ2'].iat[localNodeCounter] - sub_polygon[
                        'offsetZ1'].iat[localNodeCounter])
                    tmp_polygon.at['0', 'area'] = tmp_polygon.at['0', 'xDim'] * tmp_polygon.at['0', 'yDim']
                    tmp_polygon.at['0', 'blCorner'] = np.round([min(sub_polygon['offsetX1'].iat[localNodeCounter],
                                                                    sub_polygon['offsetX2'].iat[localNodeCounter]),
                                                                min(sub_polygon['offsetY1'].iat[localNodeCounter],
                                                                    sub_polygon['offsetY2'].iat[localNodeCounter]),
                                                                tmp_node.at['0', 'z'] +
                                                                min(sub_polygon['offsetZ1'].iat[localNodeCounter],
                                                                    sub_polygon['offsetZ2'].iat[localNodeCounter])], decimals=4)
                    tmp_polygon.at['0', 't'] = sub_polygon['thickness'].iat[localNodeCounter]
                    tmp_polygon.at['0', 'rho'] = sub_polygon['rho'].iat[localNodeCounter]
                    tmp_polygon_list.append(tmp_polygon.values.tolist()[0])

    # Create OpenSees model for 3D nodes
    total3DNodes = impN3d['wall1'].count()
    for item in np.arange(total3DNodes):
        nodeNumber = nodeNumber + 1
        tmp_node = empty_tmp_node.copy(deep=True)
        tmp_node.at['0', 'No'] = impN3d.index[item]
        tmp_node.at['0', 'x'] = np.round(impN3d['x'].iat[item], decimals=4)
        tmp_node.at['0', 'y'] = np.round(impN3d['y'].iat[item], decimals=4)
        tmp_node.at['0', 'z'] = np.round(impN3d['z'].iat[item], decimals=4)
        tmp_node.at['0', 'pos'] = [tmp_node.at['0', 'x'], tmp_node.at['0', 'y'], tmp_node.at['0', 'z']]
        tmp_node.at['0', 'wall'] = impN3d['wall1'].iat[item]
        tmp_node_list.append(tmp_node.values.tolist()[0])
        if impN3d['type'].iat[item][0] == "R":
            polygonNumber = polygonNumber + 1
            tmp_polygon.at['0', 'Node - Global'] = tmp_node.at['0', 'No']
            tmp_polygon.at['0', 'xDim'] = abs(impN3d['offsetXloc12'].iat[item] - impN3d[
                'offsetXloc11'].iat[item])
            tmp_polygon.at['0', 'yDim'] = abs(impN3d['offsetZ12'].iat[item] - impN3d[
                'offsetZ11'].iat[item])
            tmp_polygon.at['0', 'area'] = tmp_polygon.at['0', 'xDim'] * tmp_polygon.at['0', 'yDim']
            tmp_polygon.at['0', 'blCorner'] = np.round([min(impN3d['offsetX11'].iat[item],
                                                            impN3d['offsetX12'].iat[item]),
                                                        min(impN3d['offsetY11'].iat[item],
                                                            impN3d['offsetY12'].iat[item]),
                                                        tmp_node.at['0', 'z'] +
                                                        min(impN3d['offsetZ11'].iat[item],
                                                            impN3d['offsetZ12'].iat[item])], decimals=4)
            tmp_polygon.at['0', 't'] = impN3d['thickness1'].iat[item]
            tmp_polygon.at['0', 'rho'] = impN3d['rho1'].iat[item]
            tmp_polygon_list.append(tmp_polygon.values.tolist()[0])
        elif impN3d['type'].iat[item][0] == "P":
            # extract the polygon data for current node
            sub_polygon = impPoly3d1.groupby(impPoly3d1.index).get_group(
                tmp_node.at['0', 'No'])
            for localNodeCounter in np.arange(4):
                polygonNumber = polygonNumber + 1
                if not pd.isnull(sub_polygon['rho'].iat[localNodeCounter]):
                    tmp_polygon.at['0', 'Node - Global'] = tmp_node.at['0', 'No']
                    tmp_polygon.at['0', 'xDim'] = abs(sub_polygon['offsetXloc2'].iat[localNodeCounter] - sub_polygon[
                        'offsetXloc1'].iat[localNodeCounter])
                    tmp_polygon.at['0', 'yDim'] = abs(sub_polygon['offsetZ2'].iat[localNodeCounter] - sub_polygon[
                        'offsetZ1'].iat[localNodeCounter])
                    tmp_polygon.at['0', 'area'] = tmp_polygon.at['0', 'xDim'] * tmp_polygon.at['0', 'yDim']
                    tmp_polygon.at['0', 'blCorner'] = np.round([min(sub_polygon['offsetX1'].iat[localNodeCounter],
                                                                    sub_polygon['offsetX2'].iat[localNodeCounter]),
                                                                min(sub_polygon['offsetY1'].iat[localNodeCounter],
                                                                    sub_polygon['offsetY2'].iat[localNodeCounter]),
                                                                tmp_node.at['0', 'z'] +
                                                                min(sub_polygon['offsetZ1'].iat[localNodeCounter],
                                                                    sub_polygon['offsetZ2'].iat[localNodeCounter])], decimals=4)
                    tmp_polygon.at['0', 't'] = sub_polygon['thickness'].iat[localNodeCounter]
                    tmp_polygon.at['0', 'rho'] = sub_polygon['rho'].iat[localNodeCounter]
                    tmp_polygon_list.append(tmp_polygon.values.tolist()[0])

    node = pd.DataFrame(tmp_node_list, columns=['No', 'x', 'y', 'z', 'pos', 'wall', 'addedMass', 'addedMassEcc', 'repartition'])
    # Generate copies of the 3D nodes on the second wall and keep track of the connections
    newNodeTag = impMaxNodeNumber
    for item in np.arange(total3DNodes):
        newNodeTag = newNodeTag + 1
        nodeCount = node['No'].count()
        w2wTag = w2wTag + 1
        w2wconstraintNumber = w2wconstraintNumber + 1
        tmp_w2wconstraint.at['0', 'master'] = impN3d.index[item]
        tmp_w2wconstraint.at['0', 'slave'] = newNodeTag
        tmp_w2wconstraint.at['0', 'dofs'] = [1, 2]
        tmp_w2wconstraint_list.append(tmp_w2wconstraint.values.tolist()[0])
        double3DNodesNumber = double3DNodesNumber + 1
        tmp_double3DNodes.at['0', 'original'] = tmp_w2wconstraint.at['0', 'master']
        tmp_double3DNodes.at['0', 'copy'] = tmp_w2wconstraint.at['0', 'slave']
        tmp_double3DNodes_list.append(tmp_double3DNodes.values.tolist()[0])
        subNode = node.groupby(node['No']).get_group(impN3d.index[item])
        node = dataConcat(nodeNumber, subNode, node)
        node['No'].iat[nodeCount] = newNodeTag
        node['wall'].iat[nodeCount] = impN3d['wall2'].iat[item]
        if impN3d['type'].iat[item][1] == "R":
            polygonNumber = polygonNumber + 1
            tmp_polygon.at['0', 'Node - Global'] = node['No'].iat[nodeCount]
            tmp_polygon.at['0', 'xDim'] = abs(impN3d['offsetXloc22'].iat[item] - impN3d[
                'offsetXloc21'].iat[item])
            tmp_polygon.at['0', 'yDim'] = abs(impN3d['offsetZ22'].iat[item] - impN3d[
                'offsetZ21'].iat[item])
            tmp_polygon.at['0', 'area'] = tmp_polygon.at['0', 'xDim'] * tmp_polygon.at['0', 'yDim']
            tmp_polygon.at['0', 'blCorner'] = np.round([min(impN3d['offsetX21'].iat[item],
                                                            impN3d['offsetX22'].iat[item]),
                                                        min(impN3d['offsetY21'].iat[item],
                                                            impN3d['offsetY22'].iat[item]),
                                                        node['z'].iat[nodeCount] +
                                                        min(impN3d['offsetZ21'].iat[item],
                                                            impN3d['offsetZ22'].iat[item])], decimals=4)
            tmp_polygon.at['0', 't'] = impN3d['thickness2'].iat[item]
            tmp_polygon.at['0', 'rho'] = impN3d['rho2'].iat[item]
            tmp_polygon_list.append(tmp_polygon.values.tolist()[0])
        elif impN3d['type'].iat[item][1] == "P":
            # extract the polygon data for current node
            sub_polygon = impPoly3d2.groupby(impPoly3d2.index).get_group(tmp_w2wconstraint.at['0', 'master'])
            for localNodeCounter in np.arange(4):
                polygonNumber = polygonNumber + 1
                if not pd.isnull(sub_polygon['rho'].iat[localNodeCounter]):
                    tmp_polygon.at['0', 'Node - Global'] = node['No'].iat[nodeCount]
                    tmp_polygon.at['0', 'xDim'] = abs(sub_polygon['offsetXloc2'].iat[localNodeCounter] - sub_polygon[
                        'offsetXloc1'].iat[localNodeCounter])
                    tmp_polygon.at['0', 'yDim'] = abs(sub_polygon['offsetZ2'].iat[localNodeCounter] - sub_polygon[
                        'offsetZ1'].iat[localNodeCounter])
                    tmp_polygon.at['0', 'area'] = tmp_polygon.at['0', 'xDim'] * tmp_polygon.at['0', 'yDim']
                    tmp_polygon.at['0', 'blCorner'] = np.round([min(sub_polygon['offsetX1'].iat[localNodeCounter],
                                                                    sub_polygon['offsetX2'].iat[localNodeCounter]),
                                                                min(sub_polygon['offsetY1'].iat[localNodeCounter],
                                                                    sub_polygon['offsetY2'].iat[localNodeCounter]),
                                                                node['z'].iat[nodeCount] +
                                                                min(sub_polygon['offsetZ1'].iat[localNodeCounter],
                                                                    sub_polygon['offsetZ2'].iat[localNodeCounter])], decimals=4)
                    tmp_polygon.at['0', 't'] = sub_polygon['thickness'].iat[localNodeCounter]
                    tmp_polygon.at['0', 'rho'] = sub_polygon['rho'].iat[localNodeCounter]
                    tmp_polygon_list.append(tmp_polygon.values.tolist()[0])

    polygon = pd.DataFrame(tmp_polygon_list, columns=['Node - Global', 'xDim', 'yDim', 'area', 'blCorner', 't', 'rho'])
    w2wconstraint = pd.DataFrame(tmp_w2wconstraint_list, columns=['master', 'slave', 'dofs'])
    double3DNodes = pd.DataFrame(tmp_double3DNodes_list, columns=['original', 'copy'])
    double3DNodes.reset_index(inplace=True, drop=True)
    w2wconstraint.reset_index(inplace=True, drop=True)

    # Create OpenSees model for the elements : macro-elements
    totalElements = impElement['wall'].count()
    for item in np.arange(totalElements):
        elementNumber = elementNumber + 1
        tmp_element.at['0', 'No'] = elementNumber
        tmp_element.at['0', 'wall'] = impElement['wall'].iat[item]
        # Check if node I was split
        nI = impElement['nodeI'].iat[item]
        nI = nodeSplit(nI, double3DNodes, tmp_element, impN3d)
        tmp_element.at['0', 'nodeI'] = nI
        # Check if node J was split
        nJ = impElement['nodeJ'].iat[item]
        nJ = nodeSplit(nJ, double3DNodes, tmp_element, impN3d)
        tmp_element.at['0', 'nodeJ'] = nJ
        # Create element nodes
        newNodeTag = newNodeTag + 1
        posVec = wall.at[impElement['wall'].iat[item], 'origin'] + \
                 np.multiply(wall.at[impElement['wall'].iat[item], 'xAxis'], impElement['xBar'].iat[item])
        tmp_node = empty_tmp_node.copy(deep=True)
        tmp_node.at['0', 'No'] = newNodeTag
        tmp_node.at['0', 'x'] = posVec[0]
        tmp_node.at['0', 'y'] = posVec[1]
        tmp_node.at['0', 'z'] = impElement['zBar'].iat[item]
        tmp_node.at['0', 'pos'] = [tmp_node.at['0', 'x'], tmp_node.at['0', 'y'], tmp_node.at['0', 'z']]
        tmp_node.at['0', 'wall'] = impElement['wall'].iat[item]
        node = dataConcat(nodeNumber, tmp_node, node)

        tmp_element.at['0', 'nodeE'] = newNodeTag
        tmp_element.at['0', 'nodeVec'] = [tmp_element.at['0', 'nodeI'], tmp_element.at['0', 'nodeJ'],
                                            tmp_element.at['0', 'nodeE']]
        angles = impElement['angle'].iat[item] * wall.at[impElement['wall'].iat[item], 'zAxis']
        axisVec = rotate3D(wall.at[impElement['wall'].iat[item], 'xAxis'], angles)
        tmp_element.at['0', 'xAxis'] = np.round(axisVec, decimals=4)
        tmp_element.at['0', 'h'] = impElement['H'].iat[item]
        tmp_element.at['0', 'b'] = impElement['L'].iat[item]
        tmp_element.at['0', 't'] = impElement['t'].iat[item]
        tmp_element.at['0', 'type'] = "Macroelement3d"
        tmp_element.at['0', 'mat'] = impElement['mat'].iat[item]
        tmp_element_list.append(tmp_element.values.tolist()[0])

    node.reset_index(inplace=True, drop=True)

    # Create OpenSees model for the elements : elastic beams
    totalelasticBeam = impElasticBeam['wall'].count()
    for item in np.arange(totalelasticBeam):
        elementNumber = elementNumber + 1
        tmp_element = empty_tmp_element.copy(deep=True)
        tmp_element.at['0', 'No'] = elementNumber
        tmp_element.at['0', 'wall'] = impElasticBeam['wall'].iat[item]
        # Check if node I was split
        nI = impElasticBeam['nodeI'].iat[item]
        nI = nodeSplit(nI, double3DNodes, tmp_element, impN3d)
        tmp_element.at['0', 'nodeI'] = nI
        # Check if node J was split
        nJ = impElasticBeam['nodeJ'].iat[item]
        nJ = nodeSplit(nJ, double3DNodes, tmp_element, impN3d)
        tmp_element.at['0', 'nodeJ'] = nJ
        tmp_element.at['0', 'mat'] = impElasticBeam['mat'].iat[item]
        tmp_element.at['0', 'area'] = impElasticBeam['area'].iat[item]
        tmp_element.at['0', 'J'] = impElasticBeam['J'].iat[item]
        tmp_element.at['0', 'propVec'] = [impElasticBeam['deformIn'].iat[item],
                                          impElasticBeam['type'].iat[item],
                                          impElasticBeam['offXloc_I'].iat[item],
                                          impElasticBeam['offZ_I'].iat[item],
                                          impElasticBeam['offXloc_J'].iat[item],
                                          impElasticBeam['offZ_J'].iat[item]]
        tmp_element.at['0', 'type'] = "ElasticBeam"
        # Calculate offsets
        xAxis = wall.at[impElasticBeam['wall'].iat[item], 'xAxis']
        yAxis = wall.at[impElasticBeam['wall'].iat[item], 'yAxis']
        zAxis = wall.at[impElasticBeam['wall'].iat[item], 'zAxis']
        tmp_element.at['0', 'offsetI'] = np.multiply(xAxis, impElasticBeam['offXloc_I'].iat[item]) + \
                                         np.multiply(yAxis, impElasticBeam['offZ_I'].iat[item])
        tmp_element.at['0', 'offsetJ'] = np.multiply(xAxis, impElasticBeam['offXloc_J'].iat[item]) + \
                                         np.multiply(yAxis, impElasticBeam['offZ_J'].iat[item])
        tmp_element_list.append(tmp_element.values.tolist()[0])

    # Create OpenSees model for the elements : nonlinear beams
    totalNlBeam = impNlBeam['wall'].count()
    for item in np.arange(totalNlBeam):
        elementNumber = elementNumber + 1
        tmp_element = empty_tmp_element.copy(deep=True)
        tmp_element.at['0', 'No'] = elementNumber
        tmp_element.at['0', 'wall'] = impNlBeam['wall'].iat[item]
        # Check if node I was split
        nI = impNlBeam['nodeI'].iat[item]
        nI = nodeSplit(nI, double3DNodes, tmp_element, impN3d)
        tmp_element.at['0', 'nodeI'] = nI
        # Check if node J was split
        nJ = impNlBeam['nodeJ'].iat[item]
        nJ = nodeSplit(nJ, double3DNodes, tmp_element, impN3d)
        tmp_element.at['0', 'nodeJ'] = nJ
        tmp_element.at['0', 'mat'] = impNlBeam['mat'].iat[item]
        tmp_element.at['0', 'area'] = impNlBeam['area'].iat[item]
        tmp_element.at['0', 'J'] = impNlBeam['J'].iat[item]
        tmp_element.at['0', 'Wpl'] = impNlBeam['Wpl'].iat[item]
        tmp_element.at['0', 'propVec'] = [impNlBeam['deformIn'].iat[item],
                                          impNlBeam['type'].iat[item],
                                          impNlBeam['offXloc_I'].iat[item],
                                          impNlBeam['offZ_I'].iat[item],
                                          impNlBeam['offXloc_J'].iat[item],
                                          impNlBeam['offZ_J'].iat[item]]
        tmp_element.at['0', 'type'] = "NonlinearBeam"
        # Calculate offsets
        xAxis = wall.at[impNlBeam['wall'].iat[item], 'xAxis']
        yAxis = wall.at[impNlBeam['wall'].iat[item], 'yAxis']
        zAxis = wall.at[impNlBeam['wall'].iat[item], 'zAxis']
        tmp_element.at['0', 'offsetI'] = np.multiply(xAxis, impNlBeam['offXloc_I'].iat[item]) + \
                                         np.multiply(yAxis, impNlBeam['offZ_I'].iat[item])
        tmp_element.at['0', 'offsetJ'] = np.multiply(xAxis, impNlBeam['offXloc_J'].iat[item]) + \
                                         np.multiply(yAxis, impNlBeam['offZ_J'].iat[item])
        tmp_element_list.append(tmp_element.values.tolist()[0])

    # Create OpenSees model for the floors
    totalFloors = impFloor['nI'].count()
    totalFloorLevels = impFloorLevel['zAxis1'].count()
    for item in np.arange(totalFloorLevels):
        floorNumber = floorNumber + 1
        tmp_floor.at['0', 'h'] = impFloorLevel.index[item]
        tmp_floor.at['0', 'zAxis'] = [impFloorLevel['zAxis1'].iat[item],
                                      impFloorLevel['zAxis2'].iat[item],
                                      impFloorLevel['zAxis3'].iat[item]]
        tmp_floor_list.append(tmp_floor.values.tolist()[0])
    floor = pd.DataFrame(tmp_floor_list, columns=['h', 'zAxis'])
    floor.reset_index(inplace=True, drop=True)

    for item in np.arange(totalFloors):
        # Create nodes to connect it to the structure with possible sliding
        floorNodes = [impFloor['nI'].iat[item], impFloor['nJ'].iat[item],
                      impFloor['nK'].iat[item], impFloor['nL'].iat[item]]
        for nodeItem in np.arange(4):
            tmp_node = empty_tmp_node.copy(deep=True)
            newNodeTag = newNodeTag + 1
            oldNode = floorNodes[nodeItem]
            tmp_node.at['0', 'No'] = newNodeTag
            tmp_node.at['0', 'x'] = node['x'].iat[node[node['No'] == oldNode].index[0]]
            tmp_node.at['0', 'y'] = node['y'].iat[node[node['No'] == oldNode].index[0]]
            tmp_node.at['0', 'z'] = node['z'].iat[node[node['No'] == oldNode].index[0]]
            tmp_node.at['0', 'pos'] = [tmp_node.at['0', 'x'], tmp_node.at['0', 'y'], tmp_node.at['0', 'z']]
            tmp_node.at['0', 'wall'] = node.at[node[node['No'] == oldNode].index[0], 'wall']
            node = dataConcat(nodeNumber, tmp_node, node)
            node.reset_index(inplace=True, drop=True)
            # Remember the constraint
            f2wTag = f2wTag + 1
            f2wconstraintNumber = f2wconstraintNumber + 1
            tmp_f2wconstraint.at['0', 'master'] = oldNode
            tmp_f2wconstraint.at['0', 'slave'] = newNodeTag
            tmp_f2wconstraint.at['0', 'dofs'] = [1, 2, 3, 4, 5, 6]
            tmp_f2wconstraint_list.append(tmp_f2wconstraint.values.tolist()[0])
        # Create floor shell
        elementNumber = elementNumber + 1
        tmp_element = empty_tmp_element.copy(deep=True)
        tmp_element.at['0', 'No'] = elementNumber
        tmp_element.at['0', 't'] = impFloor['thickness'].iat[item]
        tmp_element.at['0', 'nodeI'] = newNodeTag - 3
        tmp_element.at['0', 'nodeJ'] = newNodeTag - 2
        tmp_element.at['0', 'nodeK'] = newNodeTag - 1
        tmp_element.at['0', 'nodeL'] = newNodeTag
        tmp_element.at['0', 'nodeVec'] = [tmp_element.at['0', 'nodeI'], tmp_element.at['0', 'nodeJ'],
                                          tmp_element.at['0', 'nodeK'], tmp_element.at['0', 'nodeL']]
        # Calculate area (Useful for applying loads)
        area = 0
        vecAB = np.subtract((node['pos'].iat[node[node['No'] == tmp_element.at['0', 'nodeJ']].index.tolist()[0]])
                            , (node['pos'].iat[node[node['No'] == tmp_element.at['0', 'nodeI']].index.tolist()[0]]))
        vecAC = np.subtract((node['pos'].iat[node[node['No'] == tmp_element.at['0', 'nodeL']].index.tolist()[0]])
                            , (node['pos'].iat[node[node['No'] == tmp_element.at['0', 'nodeI']].index.tolist()[0]]))
        area = area + 0.5 * linalg.norm(np.cross(vecAB, vecAC))

        vecAB = np.subtract((node['pos'].iat[node[node['No'] == tmp_element.at['0', 'nodeJ']].index.tolist()[0]])
                            , (node['pos'].iat[node[node['No'] == tmp_element.at['0', 'nodeK']].index.tolist()[0]]))
        vecAC = np.subtract((node['pos'].iat[node[node['No'] == tmp_element.at['0', 'nodeL']].index.tolist()[0]])
                            , (node['pos'].iat[node[node['No'] == tmp_element.at['0', 'nodeK']].index.tolist()[0]]))
        area = area + 0.5 * linalg.norm(np.cross(vecAB, vecAC))

        tmp_element.at['0', 'area'] = area
        tmp_element.at['0', 'properties'] = [impFloor['E1'].iat[item], impFloor['E2'].iat[item],
                                             impFloor['Poisson'].iat[item], impFloor['G'].iat[item]]
        tmp_element.at['0', 'type'] = "FloorShell"
        # Assign floor number
        heightVec = [node['z'].iat[node[node['No'] == tmp_element.at['0', 'nodeI']].index.tolist()[0]],
                     node['z'].iat[node[node['No'] == tmp_element.at['0', 'nodeJ']].index.tolist()[0]],
                     node['z'].iat[node[node['No'] == tmp_element.at['0', 'nodeK']].index.tolist()[0]],
                     node['z'].iat[node[node['No'] == tmp_element.at['0', 'nodeL']].index.tolist()[0]]]
        avgHeight = np.mean(heightVec)
        tol = 0.05
        for floorLevel in np.arange(totalFloorLevels):
            if abs(avgHeight - floor['h'].iat[floorLevel]) < tol:
                tmp_element.at['0', 'floor'] = floorLevel
                break
        # Assign principal direction
        vecIJ = np.subtract(node['pos'].iat[node[node['No'] == tmp_element.at['0', 'nodeJ']].index.tolist()[0]],
                            node['pos'].iat[node[node['No'] == tmp_element.at['0', 'nodeI']].index.tolist()[0]])
        vecLK = np.subtract(node['pos'].iat[node[node['No'] == tmp_element.at['0', 'nodeK']].index.tolist()[0]],
                            node['pos'].iat[node[node['No'] == tmp_element.at['0', 'nodeL']].index.tolist()[0]])
        tmp_element.at['0', 'b'] = gamma = linalg.norm(vecIJ + vecLK) / 2
        tmp_element.at['0', 'xAxis'] = np.round((vecIJ + vecLK) / linalg.norm(vecIJ + vecLK), decimals=4)
        tmp_element_list.append(tmp_element.values.tolist()[0])

    element = pd.DataFrame(tmp_element_list, columns=['No', 'wall', 'nodeI', 'nodeJ', 'nodeE', 'nodeVec', 'xAxis', 'h', 'b',
                                                      't', 'type', 'area', 'floor', 'mat', 'J', 'propVec', 'offsetI',
                                                      'offsetJ', 'Wpl', 'nodeK', 'nodeL', 'properties'])
    f2wconstraint = pd.DataFrame(tmp_f2wconstraint_list, columns=['master', 'slave', 'dofs'])

    # Create OpenSees model for the materials
    material = impMaterial.copy(deep=True)
    totalMaterials = impMaterial['E'].count()
    muR = pd.DataFrame(columns=['muR'], index=np.arange(totalMaterials))
    material = material.join(muR)
    for item in np.arange(totalMaterials):
        if material['Gc'].iat[item] == material['Gc'].iat[item]:  # will return false if the value is nan
            material['muR'].iat[item] = material['mu'].iat[item] * 0.5

    # Create OpenSees model for nodal masses
    totalNodalMasses = impNodalMass['mass'].count()
    for item in np.arange(totalNodalMasses):
        kNode = impNodalMass.index.tolist()[item]
        kWall = node['wall'].iat[node[node['No'] == kNode].index.tolist()[0]]
        node['addedMass'].iat[node[node['No'] == kNode].index.tolist()[0]] = \
            impNodalMass['mass'].iat[item]
        node['addedMassEcc'].iat[node[node['No'] == kNode].index.tolist()[0]] = \
            np.multiply(wall.at[kWall, 'xAxis'], impNodalMass['ecc_x']) + \
            np.multiply(wall.at[kWall, 'yAxis'], impNodalMass['ecc_z'])

    # Create OpenSees model for restraint variables
    totalRestraints = impRestraint['x'].count()
    for item in np.arange(totalRestraints):
        kNode = impRestraint.index.tolist()[item]
        newFix = newFix + 1
        fixconstraintNumber = fixconstraintNumber + 1
        tmp_fixconstraint.at['0', 'node'] = kNode
        tmp_fixconstraint.at['0', 'dofs'] = [1, 2, 3, 4, 5, 6]  # restrain everything
        tmp_fixconstraint_list.append(tmp_fixconstraint.values.tolist()[0])
        fixconstraint.reset_index(inplace=True, drop=True)

        # Check if the node was doubled (for 3D nodes)
        if (double3DNodes['original'] == kNode).any():
            newNode = double3DNodes.at[double3DNodes[double3DNodes['original'] == kNode].index.tolist()[0], 'copy']
            newFix = newFix + 1
            fixconstraintNumber = fixconstraintNumber + 1
            tmp_fixconstraint.at['0', 'node'] = newNode
            tmp_fixconstraint.at['0', 'dofs'] = [1, 2, 3, 4, 5, 6]  # restrain everything
            tmp_fixconstraint_list.append(tmp_fixconstraint.values.tolist()[0])

    fixconstraint = pd.DataFrame(tmp_fixconstraint_list, columns=['node', 'dofs'])

    # Create OpenSees model for analysis variables
    analysis = impAnalysis.copy(deep=True)
    totalAnalyses = impAnalysis['type'].count()
    scaling = pd.DataFrame(columns=['scaleFactor', 'scaledGroundMotion'], index=np.arange(totalAnalyses))
    analysis = analysis.join(scaling)
    # Calculate true scale factor of the accelerogram
    for item in np.arange(totalAnalyses):
        if impAnalysis['type'].iat[item] == 'Dynamic':
            # Read accelerogram
            tfilePath = "C:/Model Processing/tremuri_model_processing/basel_models_Pavia/"
            tfileName = analysis['groundMotion'].iat[item]
            completeFileLocation = join(tfilePath, tfileName)
            inputFile = open(completeFileLocation, "r").read()
            # read the lines of the input file
            linesFile = inputFile.split()
            lines = [float(acc) for acc in linesFile]  # Convert the accelerations to float
            # process
            if int(analysis['PGA'].iat[item]) < 0:
                analysis['PGA'].iat[item] = abs(np.amax(lines))
                analysis['scaleFactor'].iat[item] = -1.0
                analysis['scaledGroundMotion'].iat[item] = np.multiply(lines, -1)
            else:
                analysis['scaleFactor'].iat[item] = (-1 * analysis['PGA'].iat[item]) / (abs(np.amax(lines)))
                analysis['scaledGroundMotion'].iat[item] = np.multiply(lines, analysis['scaleFactor'].iat[item])


    node = node.set_index('No')
    polygon = polygon.set_index('Node - Global')
    element = element.set_index('No')
    floor.to_excel(writer, sheet_name='floors')
    node.to_excel(writer, sheet_name='nodes')
    polygon.to_excel(writer, sheet_name='polygons')
    element.to_excel(writer, sheet_name='elements')
    double3DNodes.to_excel(writer, sheet_name='double nodes')
    material.to_excel(writer, sheet_name='material')
    analysis.to_excel(writer, sheet_name='analysis')

    restraint = impRestraint.copy(deep=True)

    writer.save()
    print("Convert Tremuri to OpenSees completed in --- %s seconds ---" % (time.time() - startTime))

    return element, node, wall, floor, polygon, material, analysis, restraint, fixconstraint, w2wconstraint, f2wconstraint

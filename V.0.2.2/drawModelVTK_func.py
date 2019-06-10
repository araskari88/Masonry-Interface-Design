import convertTremuriToOpensees_func
import numpy as np
import time
import vtk


class arrowMaker(vtk.vtkActor):
    def __init__(self, startPoint, endPoint, zAxis, clr2plt):
        super().__init__()

        colors = vtk.vtkNamedColors()
        USER_MATRIX = False
        # Create an arrow.
        arrowSource = vtk.vtkArrowSource()

        # Compute a basis
        normalizedX = [0 for i in range(3)]
        normalizedY = [0 for i in range(3)]
        normalizedZ = [0 for i in range(3)]

        # The X axis is a vector from start to end
        math = vtk.vtkMath()
        math.Subtract(endPoint, startPoint, normalizedX)
        length = math.Norm(normalizedX)
        print(length)
        math.Normalize(normalizedX)

        # The Z axis is an arbitrary vector cross X
        arbitrary = zAxis
        math.Cross(normalizedX, arbitrary, normalizedZ)
        math.Normalize(normalizedZ)

        # The Y axis is Z cross X
        math.Cross(normalizedZ, normalizedX, normalizedY)
        matrix = vtk.vtkMatrix4x4()

        # Create the direction cosine matrix
        matrix.Identity()
        for i in range(3):
            matrix.SetElement(i, 0, normalizedX[i])
            matrix.SetElement(i, 1, normalizedY[i])
            matrix.SetElement(i, 2, normalizedZ[i])

        # Apply the transforms
        transform = vtk.vtkTransform()
        transform.Translate(startPoint)
        transform.Concatenate(matrix)
        transform.Scale(length, length, length)

        # Transform the polydata
        transformPD = vtk.vtkTransformPolyDataFilter()
        transformPD.SetTransform(transform)
        transformPD.SetInputConnection(arrowSource.GetOutputPort())

        # Create a mapper and actor for the arrow
        mapper = vtk.vtkPolyDataMapper()

        if USER_MATRIX:
            mapper.SetInputConnection(arrowSource.GetOutputPort())
            self.SetUserMatrix(transform.GetMatrix())
        else:
            mapper.SetInputConnection(transformPD.GetOutputPort())

        self.SetMapper(mapper)
        self.GetProperty().SetColor(colors.GetColor3d(clr2plt))
        renderer.AddActor(self)




def addWallToPatch(f_node_I, f_node_J, f_v_or, f_L, f_t, f_off_I, f_off_J, f_style):
    f_L = f_L
    f_t = f_t
    if f_style == '1D' or f_style == '2D':
        f_X = np.zeros((1, 4))
        f_Y = np.zeros((1, 4))
        f_Z = np.zeros((1, 4))
    else:
        f_X = np.zeros((6, 4))
        f_Y = np.zeros((6, 4))
        f_Z = np.zeros((6, 4))
    f_H_wall = np.linalg.norm(f_node_J - f_node_I)
    f_x_loc = (f_node_J - f_node_I) / np.linalg.norm(f_node_J - f_node_I)

    # check if the orientation vector is right as it can't be parallel to the axis of the wall
    if np.linalg.norm(f_v_or - np.multiply((np.dot(f_v_or.transpose(), f_x_loc)), f_x_loc)) == 0:
        print("WARNING: Orientation vector is parallel to the axis. The orientation vector is assumed parallel to the "
              "Global Z (or Global Y if this doesn't work.")
        f_v_or = np.array([[0], [0], [1]])
        if np.linalg.norm(f_v_or - np.multiply((np.dot(f_v_or.transpose(), f_x_loc)), f_x_loc)) == 0:
            f_v_or = np.array([[0], [1], [0]])

    f_v_or_x = np.multiply((np.dot(f_v_or.transpose(), f_x_loc)), f_x_loc)
    f_v_or_z = f_v_or - f_v_or_x
    f_z_loc = f_v_or_z / np.linalg.norm(f_v_or_z)
    f_y_loc = np.cross(f_z_loc.transpose(), f_x_loc.transpose()).transpose()

    if f_style == "2D":
        f_t = 0
    elif f_style == "1D":
        f_t = 0
        f_L = f_L * 0.01

    # full-shape view 3D
    # Base
    f_verticesI_loc = [[f_off_I[0][0], f_off_I[0][0], f_off_I[0][0], f_off_I[0][0]],
                       [f_off_I[1][0] - f_L/2, f_off_I[1][0] - f_L/2, f_off_I[1][0] + f_L/2, f_off_I[1][0] + f_L/2],
                       [f_off_I[2][0] - f_t/2, f_off_I[2][0] + f_t/2, f_off_I[2][0] + f_t/2, f_off_I[2][0] - f_t/2]]
    f_verticesI = np.zeros((3, 4))
    for f_kCol in np.arange(4):
        for f_Krow in np.arange(3):
            f_verticesI[f_Krow][f_kCol] = f_verticesI_loc[0][f_kCol] * f_x_loc[f_Krow][0] + \
                                          f_verticesI_loc[1][f_kCol] * f_y_loc[f_Krow][0] + \
                                          f_verticesI_loc[2][f_kCol] * f_z_loc[f_Krow][0]
    if f_style != '1D' and f_style != '2D':
        # add base I
        for f_memberCounter in np.arange(4):
            f_X[0][f_memberCounter] = f_node_I[0][0] + f_verticesI[0][f_memberCounter]
            f_Y[0][f_memberCounter] = f_node_I[1][0] + f_verticesI[1][f_memberCounter]
            f_Z[0][f_memberCounter] = f_node_I[2][0] + f_verticesI[2][f_memberCounter]

    f_verticesJ_loc = [[f_H_wall + f_off_I[0][0], f_H_wall + f_off_I[0][0], f_H_wall + f_off_I[0][0], f_H_wall + f_off_I[0][0]],
                       [f_off_J[1][0] - f_L / 2, f_off_J[1][0] - f_L / 2, f_off_J[1][0] + f_L / 2, f_off_J[1][0] + f_L / 2],
                       [f_off_J[2][0] - f_t / 2, f_off_J[2][0] + f_t / 2, f_off_J[2][0] + f_t / 2, f_off_J[2][0] - f_t / 2]]
    f_verticesJ = np.zeros((3, 4))
    for f_kCol in np.arange(4):
        for f_Krow in np.arange(3):
            f_verticesJ[f_Krow][f_kCol] = f_verticesJ_loc[0][f_kCol] * f_x_loc[f_Krow][0] + \
                                          f_verticesJ_loc[1][f_kCol] * f_y_loc[f_Krow][0] + \
                                          f_verticesJ_loc[2][f_kCol] * f_z_loc[f_Krow][0]

    for f_memberCounter in np.arange(4):
        if f_style != '1D' and f_style != '2D':
            # add base J
            f_X[1][f_memberCounter] = f_node_I[0][0] + f_verticesJ[0][f_memberCounter]
            f_Y[1][f_memberCounter] = f_node_I[1][0] + f_verticesJ[1][f_memberCounter]
            f_Z[1][f_memberCounter] = f_node_I[2][0] + f_verticesJ[2][f_memberCounter]
            # add other edges
            f_corners = [0, 1]
            f_tmp_mat = [[f_verticesI[0][f_corners[0]], f_verticesI[0][f_corners[1]], f_verticesJ[0][f_corners[1]],
                          f_verticesJ[0][f_corners[0]]],
                         [f_verticesI[1][f_corners[0]], f_verticesI[1][f_corners[1]], f_verticesJ[1][f_corners[1]],
                          f_verticesJ[1][f_corners[0]]],
                         [f_verticesI[2][f_corners[0]], f_verticesI[2][f_corners[1]], f_verticesJ[2][f_corners[1]],
                          f_verticesJ[2][f_corners[0]]]]
            f_X[2][f_memberCounter] = f_node_I[0][0] + f_tmp_mat[0][f_memberCounter]
            f_Y[2][f_memberCounter] = f_node_I[1][0] + f_tmp_mat[1][f_memberCounter]
            f_Z[2][f_memberCounter] = f_node_I[2][0] + f_tmp_mat[2][f_memberCounter]
            f_corners = [1, 2]
            f_tmp_mat = [[f_verticesI[0][f_corners[0]], f_verticesI[0][f_corners[1]], f_verticesJ[0][f_corners[1]],
                          f_verticesJ[0][f_corners[0]]],
                         [f_verticesI[1][f_corners[0]], f_verticesI[1][f_corners[1]], f_verticesJ[1][f_corners[1]],
                          f_verticesJ[1][f_corners[0]]],
                         [f_verticesI[2][f_corners[0]], f_verticesI[2][f_corners[1]], f_verticesJ[2][f_corners[1]],
                          f_verticesJ[2][f_corners[0]]]]
            f_X[3][f_memberCounter] = f_node_I[0][0] + f_tmp_mat[0][f_memberCounter]
            f_Y[3][f_memberCounter] = f_node_I[1][0] + f_tmp_mat[1][f_memberCounter]
            f_Z[3][f_memberCounter] = f_node_I[2][0] + f_tmp_mat[2][f_memberCounter]
            f_corners = [2, 3]
            f_tmp_mat = [[f_verticesI[0][f_corners[0]], f_verticesI[0][f_corners[1]], f_verticesJ[0][f_corners[1]],
                          f_verticesJ[0][f_corners[0]]],
                         [f_verticesI[1][f_corners[0]], f_verticesI[1][f_corners[1]], f_verticesJ[1][f_corners[1]],
                          f_verticesJ[1][f_corners[0]]],
                         [f_verticesI[2][f_corners[0]], f_verticesI[2][f_corners[1]], f_verticesJ[2][f_corners[1]],
                          f_verticesJ[2][f_corners[0]]]]
            f_X[4][f_memberCounter] = f_node_I[0][0] + f_tmp_mat[0][f_memberCounter]
            f_Y[4][f_memberCounter] = f_node_I[1][0] + f_tmp_mat[1][f_memberCounter]
            f_Z[4][f_memberCounter] = f_node_I[2][0] + f_tmp_mat[2][f_memberCounter]
            f_corners = [3, 0]
            f_tmp_mat = [[f_verticesI[0][f_corners[0]], f_verticesI[0][f_corners[1]], f_verticesJ[0][f_corners[1]],
                          f_verticesJ[0][f_corners[0]]],
                         [f_verticesI[1][f_corners[0]], f_verticesI[1][f_corners[1]], f_verticesJ[1][f_corners[1]],
                          f_verticesJ[1][f_corners[0]]],
                         [f_verticesI[2][f_corners[0]], f_verticesI[2][f_corners[1]], f_verticesJ[2][f_corners[1]],
                          f_verticesJ[2][f_corners[0]]]]
            f_X[5][f_memberCounter] = f_node_I[0][0] + f_tmp_mat[0][f_memberCounter]
            f_Y[5][f_memberCounter] = f_node_I[1][0] + f_tmp_mat[1][f_memberCounter]
            f_Z[5][f_memberCounter] = f_node_I[2][0] + f_tmp_mat[2][f_memberCounter]
        else:
            f_corners = [3, 0]
            f_tmp_mat = [[f_verticesI[0][f_corners[0]], f_verticesI[0][f_corners[1]], f_verticesJ[0][f_corners[1]],
                          f_verticesJ[0][f_corners[0]]],
                         [f_verticesI[1][f_corners[0]], f_verticesI[1][f_corners[1]], f_verticesJ[1][f_corners[1]],
                          f_verticesJ[1][f_corners[0]]],
                         [f_verticesI[2][f_corners[0]], f_verticesI[2][f_corners[1]], f_verticesJ[2][f_corners[1]],
                          f_verticesJ[2][f_corners[0]]]]
            f_X[0][f_memberCounter] = f_node_I[0][0] + f_tmp_mat[0][f_memberCounter]
            f_Y[0][f_memberCounter] = f_node_I[1][0] + f_tmp_mat[1][f_memberCounter]
            f_Z[0][f_memberCounter] = f_node_I[2][0] + f_tmp_mat[2][f_memberCounter]
    f_X = f_X.transpose()
    f_Y = f_Y.transpose()
    f_Z = f_Z.transpose()
    return [f_X, f_Y, f_Z]


completeFileLocation3 = ""


def drMoVTKFunc():
    global impElement, impNode, impWall, impFloor, impPolygon, impMaterial, impAnalysis, renderer, maxX, maxY
    startTime = time.time()
    convertTremuriToOpensees_func.completeFileLocation2 = completeFileLocation3
    convertTremuriToOpensees_func.CONVtriOPSfunc()

    colors = vtk.vtkNamedColors()
    # These are the point ids corresponding to each face.
    faces = [[0, 1, 2, 3], [4, 5, 6, 7], [0, 1, 5, 4], [1, 2, 6, 5], [2, 3, 7, 6], [3, 0, 4, 7]]
    faceId = vtk.vtkIdList()
    faceId.InsertNextId(6)  # Six faces make up the cell.
    for face in faces:
        faceId.InsertNextId(len(face))  # The number of points in the face.
        [faceId.InsertNextId(i) for i in face]

    # Visualize
    renderer = vtk.vtkRenderer()
    renderWindow = vtk.vtkRenderWindow()
    renderWindow.SetWindowName('Polyhedron')
    renderWindow.AddRenderer(renderer)
    renderWindowInteractor = vtk.vtkRenderWindowInteractor()
    renderWindowInteractor.SetRenderWindow(renderWindow)

    # assign the required objects to variables
    impMaterial = convertTremuriToOpensees_func.material.copy(deep=True)
    impElement = convertTremuriToOpensees_func.element.copy(deep=True)
    impNode = convertTremuriToOpensees_func.node.copy(deep=True)
    impWall = convertTremuriToOpensees_func.wall.copy(deep=True)
    impFloor = convertTremuriToOpensees_func.floor.copy(deep=True)
    impPolygon = convertTremuriToOpensees_func.polygon.copy(deep=True)
    impAnalysis = convertTremuriToOpensees_func.analysis.copy(deep=True)

    maxX = -1 * np.inf
    maxY = -1 * np.inf
    totalElements = impElement['type'].count()
    floorToPlot = 0
    for item in np.arange(totalElements):
        if impElement['type'].iloc[item] == "FloorShell":
            if len(impElement['nodeVec'].iloc[item]) == 4:
                floorToPlot = floorToPlot + 1
                xx = [
                    impNode.at[impElement['nodeVec'].iloc[item][0], 'x'],
                    impNode.at[impElement['nodeVec'].iloc[item][1], 'x'],
                    impNode.at[impElement['nodeVec'].iloc[item][2], 'x'],
                    impNode.at[impElement['nodeVec'].iloc[item][3], 'x']]
                yy = [
                    impNode.at[impElement['nodeVec'].iloc[item][0], 'y'],
                    impNode.at[impElement['nodeVec'].iloc[item][1], 'y'],
                    impNode.at[impElement['nodeVec'].iloc[item][2], 'y'],
                    impNode.at[impElement['nodeVec'].iloc[item][3], 'y']]
                zz = [
                    impNode.at[impElement['nodeVec'].iloc[item][0], 'z'],
                    impNode.at[impElement['nodeVec'].iloc[item][1], 'z'],
                    impNode.at[impElement['nodeVec'].iloc[item][2], 'z'],
                    impNode.at[impElement['nodeVec'].iloc[item][3], 'z']]
                points = vtk.vtkPoints()
                points.InsertNextPoint(xx[0], yy[0], zz[0])
                points.InsertNextPoint(xx[1], yy[1], zz[1])
                points.InsertNextPoint(xx[2], yy[2], zz[2])
                points.InsertNextPoint(xx[3], yy[3], zz[3])
                maxX = max(maxX, max(xx))
                maxY = max(maxY, max(yy))

                # Create the polygon
                polygon = vtk.vtkPolygon()
                polygon.GetPointIds().SetNumberOfIds(4)  # make a quad
                polygon.GetPointIds().SetId(0, 0)
                polygon.GetPointIds().SetId(1, 1)
                polygon.GetPointIds().SetId(2, 2)
                polygon.GetPointIds().SetId(3, 3)

                # Add the polygon to a list of polygons
                polygons = vtk.vtkCellArray()
                polygons.InsertNextCell(polygon)

                # Create a PolyData
                polygonPolyData = vtk.vtkPolyData()
                polygonPolyData.SetPoints(points)
                polygonPolyData.SetPolys(polygons)

                # Create a mapper and actor
                mapper = vtk.vtkPolyDataMapper()
                mapper.SetInputData(polygonPolyData)

                actor = vtk.vtkActor()
                actor.SetMapper(mapper)
                actor.GetProperty().SetColor(colors.GetColor3d("Green"))
                actor.GetProperty().SetOpacity(0.6)
                renderer.AddActor(actor)

                center = [np.mean(xx), np.mean(yy), np.mean(zz)]
                baseLength = impElement['b'].iloc[item]
                arrowLength = 1/4 * baseLength
                arrowTip = 1/3 * arrowLength
                arrowWidth = 1/1.5 * arrowTip
                xAxis = impElement['xAxis'].iloc[item]
                zAxis = impFloor.at[int(impElement['floor'].iloc[item]), 'zAxis']
                yAxis = np.cross(zAxis, xAxis)
                xx = [center[0] - (arrowLength - arrowTip) * xAxis[0] - arrowWidth * yAxis[0],
                      center[0] - arrowLength * xAxis[0], center[0] + arrowLength * xAxis[0],
                      center[0] + (arrowLength - arrowTip) * xAxis[0] + arrowWidth * yAxis[0]]
                yy = [center[1] - (arrowLength - arrowTip) * xAxis[1] - arrowWidth * yAxis[1],
                      center[1] - arrowLength * xAxis[1], center[1] + arrowLength * xAxis[1],
                      center[1] + (arrowLength - arrowTip) * xAxis[1] + arrowWidth * yAxis[1]]
                zz = [center[2] - (arrowLength - arrowTip) * xAxis[2] - arrowWidth * yAxis[2],
                      center[2] - arrowLength * xAxis[2], center[2] + arrowLength * xAxis[2],
                      center[2] + (arrowLength - arrowTip) * xAxis[2] + arrowWidth * yAxis[2]]
                if floorToPlot == 1:
                    xDir4 = [xx]
                    yDir4 = [yy]
                    zDir4 = [zz]
                else:
                    xDir4.append(xx)
                    yDir4.append(yy)
                    zDir4.append(zz)



    xDir4 = np.array(xDir4).transpose()
    yDir4 = np.array(yDir4).transpose()
    zDir4 = np.array(zDir4).transpose()

    totalNodes = impNode['x'].count()
    nodeToPlot = 0
    wallPatch = 0
    for item in np.arange(totalNodes):
        nodeToPlot = nodeToPlot + 1
        tmpX_vec = impNode['x'].iloc[item]
        tmpY_vec = impNode['y'].iloc[item]
        tmpZ_vec = impNode['z'].iloc[item]
        if nodeToPlot == 1:
            X_vec = [tmpX_vec]
            Y_vec = [tmpY_vec]
            Z_vec = [tmpZ_vec]
        else:
            X_vec.append(tmpX_vec)
            Y_vec.append(tmpY_vec)
            Z_vec.append(tmpZ_vec)
        if impNode.index[item] in impPolygon.index:
            sub_polygon = impPolygon.groupby(impPolygon.index).get_group(
                impNode.index[item])
            test = impNode.index[item]
            sub_count = sub_polygon['xDim'].count()
            for sub_item in np.arange(sub_count):
                nWall = impNode['wall'].iloc[item]
                nodeI = sub_polygon['blCorner'].iloc[sub_item] + np.dot(impWall.at[nWall, 'xAxis'],
                                                                        sub_polygon['xDim'].iloc[sub_item] / 2)
                nodeI = np.array([nodeI]).transpose()  # transpose to convert the variable to a column vector
                nodeJ = sub_polygon['blCorner'].iloc[sub_item] + np.dot(impWall.at[nWall, 'xAxis'],
                                                                        sub_polygon['xDim'].iloc[sub_item] / 2) + \
                        np.dot(impWall.at[nWall, 'yAxis'], sub_polygon['yDim'].iloc[sub_item])
                nodeJ = np.array([nodeJ]).transpose()  # transpose to convert the variable to a column vector
                v_or = impWall.at[nWall, 'zAxis']
                v_or = np.array([v_or]).transpose()  # transpose to convert the variable to a column vector
                L = sub_polygon['xDim'].iloc[sub_item]
                t = sub_polygon['t'].iloc[sub_item]
                wallPatch = wallPatch + 1
                [xx, yy, zz] = addWallToPatch(nodeI, nodeJ, v_or, L, t, [[0], [0], [0]], [[0], [0], [0]], 'wireframe')
                points = vtk.vtkPoints()
                points.InsertNextPoint(xx[0][0], yy[0][0], zz[0][0])
                points.InsertNextPoint(xx[1][0], yy[1][0], zz[1][0])
                points.InsertNextPoint(xx[2][0], yy[2][0], zz[2][0])
                points.InsertNextPoint(xx[3][0], yy[3][0], zz[3][0])
                points.InsertNextPoint(xx[0][1], yy[0][1], zz[0][1])
                points.InsertNextPoint(xx[1][1], yy[1][1], zz[1][1])
                points.InsertNextPoint(xx[2][1], yy[2][1], zz[2][1])
                points.InsertNextPoint(xx[3][1], yy[3][1], zz[3][1])
                ugrid = vtk.vtkUnstructuredGrid()
                ugrid.SetPoints(points)
                ugrid.InsertNextCell(vtk.VTK_POLYHEDRON, faceId)
                # Create a mapper and actor
                mapper = vtk.vtkDataSetMapper()
                mapper.SetInputData(ugrid)
                actor = vtk.vtkActor()
                actor.SetMapper(mapper)
                actor.GetProperty().SetColor(colors.GetColor3d('Silver'))
                renderer.AddActor(actor)
                maxX = max(maxX, max(map(max, xx)))
                maxY = max(maxY, max(map(max, yy)))

    # Draw the elements
    elementWallNo = 0
    pier = 0
    spandrel = 0
    for item in np.arange(totalElements):
        if impElement['wall'].iloc[item] == impElement['wall'].iloc[item]:  # will return false if the value is nan
            elementWallNo = elementWallNo + 1
    for item in np.arange(totalElements):
        if impElement['type'].iloc[item] == "Macroelement3d":
            if elementWallNo != 0:
                nWall = impElement['wall'].iloc[item]
                v_or = impWall.at[int(nWall), 'zAxis']
                v_or = np.array([v_or]).transpose()  # transpose to convert the variable to a column vector

                nodeE = impNode.at[int(impElement['nodeE'].iloc[item]), 'pos']
                nodeE = np.array([nodeE]).transpose()  # transpose to convert the variable to a column vector
                tmp_val = np.dot(0.5 * impElement['h'].iloc[item], impElement['xAxis'].iloc[item])
                tmp_val = np.array([tmp_val]).transpose()  # transpose to convert the variable to a column vector
                nodeI = nodeE - tmp_val
                nodeJ = nodeE + tmp_val

                nodeE1 = nodeE
                nodeE2 = nodeE

                zAxisRotI = v_or
                zAxisRotJ = v_or
                shift = 0
                t = impElement['t'].iloc[item]
                [xx1, yy1, zz1] = addWallToPatch(nodeI, nodeE1, zAxisRotI, impElement['b'].iloc[item],
                                                 t, [[0], [0], [0]], [[0], [0.5 * shift], [0]], "wireframe")
                [xx2, yy2, zz2] = addWallToPatch(nodeE2, nodeJ, zAxisRotJ, impElement['b'].iloc[item],
                                                 t, [[0], [0.5 * shift], [0]], [[0], [0], [0]], "wireframe")
                if abs(np.dot([[0, 0, 1]], impElement['xAxis'].iloc[item]) > 0.9):
                    pier = pier + 1
                    if pier == 1:
                        cPiers = [[1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1]]
                    else:
                        cPiers.append([1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1])
                    points = vtk.vtkPoints()
                    points.InsertNextPoint(xx1[0][0], yy1[0][0], zz1[0][0])
                    points.InsertNextPoint(xx1[1][0], yy1[1][0], zz1[1][0])
                    points.InsertNextPoint(xx1[2][0], yy1[2][0], zz1[2][0])
                    points.InsertNextPoint(xx1[3][0], yy1[3][0], zz1[3][0])
                    points.InsertNextPoint(xx1[0][1], yy1[0][1], zz1[0][1])
                    points.InsertNextPoint(xx1[1][1], yy1[1][1], zz1[1][1])
                    points.InsertNextPoint(xx1[2][1], yy1[2][1], zz1[2][1])
                    points.InsertNextPoint(xx1[3][1], yy1[3][1], zz1[3][1])
                    ugrid = vtk.vtkUnstructuredGrid()
                    ugrid.SetPoints(points)
                    ugrid.InsertNextCell(vtk.VTK_POLYHEDRON, faceId)
                    # Create a mapper and actor
                    mapper = vtk.vtkDataSetMapper()
                    mapper.SetInputData(ugrid)
                    actor = vtk.vtkActor()
                    actor.SetMapper(mapper)
                    actor.GetProperty().SetColor(colors.GetColor3d('Red'))
                    renderer.AddActor(actor)
                    maxX = max(maxX, max(map(max, xx1)))
                    maxY = max(maxY, max(map(max, yy1)))

                    points = vtk.vtkPoints()
                    points.InsertNextPoint(xx2[0][0], yy2[0][0], zz2[0][0])
                    points.InsertNextPoint(xx2[1][0], yy2[1][0], zz2[1][0])
                    points.InsertNextPoint(xx2[2][0], yy2[2][0], zz2[2][0])
                    points.InsertNextPoint(xx2[3][0], yy2[3][0], zz2[3][0])
                    points.InsertNextPoint(xx2[0][1], yy2[0][1], zz2[0][1])
                    points.InsertNextPoint(xx2[1][1], yy2[1][1], zz2[1][1])
                    points.InsertNextPoint(xx2[2][1], yy2[2][1], zz2[2][1])
                    points.InsertNextPoint(xx2[3][1], yy2[3][1], zz2[3][1])
                    ugrid = vtk.vtkUnstructuredGrid()
                    ugrid.SetPoints(points)
                    ugrid.InsertNextCell(vtk.VTK_POLYHEDRON, faceId)
                    # Create a mapper and actor
                    mapper = vtk.vtkDataSetMapper()
                    mapper.SetInputData(ugrid)
                    actor = vtk.vtkActor()
                    actor.SetMapper(mapper)
                    actor.GetProperty().SetColor(colors.GetColor3d('Red'))
                    renderer.AddActor(actor)
                    maxX = max(maxX, max(map(max, xx2)))
                    maxY = max(maxY, max(map(max, yy2)))
                else:
                    spandrel = spandrel + 1
                    if spandrel == 1:
                        cSpandrels = [[1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1]]
                    else:
                        cSpandrels.append([1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1])
                    points = vtk.vtkPoints()
                    points.InsertNextPoint(xx1[0][0], yy1[0][0], zz1[0][0])
                    points.InsertNextPoint(xx1[1][0], yy1[1][0], zz1[1][0])
                    points.InsertNextPoint(xx1[2][0], yy1[2][0], zz1[2][0])
                    points.InsertNextPoint(xx1[3][0], yy1[3][0], zz1[3][0])
                    points.InsertNextPoint(xx1[0][1], yy1[0][1], zz1[0][1])
                    points.InsertNextPoint(xx1[1][1], yy1[1][1], zz1[1][1])
                    points.InsertNextPoint(xx1[2][1], yy1[2][1], zz1[2][1])
                    points.InsertNextPoint(xx1[3][1], yy1[3][1], zz1[3][1])
                    ugrid = vtk.vtkUnstructuredGrid()
                    ugrid.SetPoints(points)
                    ugrid.InsertNextCell(vtk.VTK_POLYHEDRON, faceId)
                    # Create a mapper and actor
                    mapper = vtk.vtkDataSetMapper()
                    mapper.SetInputData(ugrid)
                    actor = vtk.vtkActor()
                    actor.SetMapper(mapper)
                    actor.GetProperty().SetColor(colors.GetColor3d('Blue'))
                    renderer.AddActor(actor)
                    maxX = max(maxX, max(map(max, xx1)))
                    maxY = max(maxY, max(map(max, yy1)))

                    points = vtk.vtkPoints()
                    points.InsertNextPoint(xx2[0][0], yy2[0][0], zz2[0][0])
                    points.InsertNextPoint(xx2[1][0], yy2[1][0], zz2[1][0])
                    points.InsertNextPoint(xx2[2][0], yy2[2][0], zz2[2][0])
                    points.InsertNextPoint(xx2[3][0], yy2[3][0], zz2[3][0])
                    points.InsertNextPoint(xx2[0][1], yy2[0][1], zz2[0][1])
                    points.InsertNextPoint(xx2[1][1], yy2[1][1], zz2[1][1])
                    points.InsertNextPoint(xx2[2][1], yy2[2][1], zz2[2][1])
                    points.InsertNextPoint(xx2[3][1], yy2[3][1], zz2[3][1])
                    ugrid = vtk.vtkUnstructuredGrid()
                    ugrid.SetPoints(points)
                    ugrid.InsertNextCell(vtk.VTK_POLYHEDRON, faceId)
                    # Create a mapper and actor
                    mapper = vtk.vtkDataSetMapper()
                    mapper.SetInputData(ugrid)
                    actor = vtk.vtkActor()
                    actor.SetMapper(mapper)
                    actor.GetProperty().SetColor(colors.GetColor3d('Blue'))
                    renderer.AddActor(actor)
                    maxX = max(maxX, max(map(max, xx2)))
                    maxY = max(maxY, max(map(max, yy2)))

    # Draw rigid beams in undeformed configuration
    sizeBeams = 0.35
    for item in np.arange(totalElements):
        if impElement['type'].iloc[item] == "ElasticBeam" or impElement['type'].iloc[item] == "NonlinearBeam":
            if elementWallNo != 0:
                nWall = impElement['wall'].iloc[item]
                v_or = impWall.at[int(nWall), 'zAxis']
                v_or = np.array([v_or]).transpose()  # transpose to convert the variable to a column vector

                if np.isnan(impElement['offsetI'].iloc[item]).any():
                    nodeI = impNode.at[impElement['nodeI'].iloc[item], 'pos']
                else:
                    nodeI = impNode.at[impElement['nodeI'].iloc[item], 'pos'] + impElement['offsetI'].iloc[item]

                if np.isnan(impElement['offsetJ'].iloc[item]).any():
                    nodeJ = impNode.at[impElement['nodeJ'].iloc[item], 'pos']
                else:
                    nodeJ = impNode.at[impElement['nodeJ'].iloc[item], 'pos'] +\
                            impElement['offsetJ'].iloc[item]
                nodeI = np.array([nodeI]).transpose()
                nodeJ = np.array([nodeJ]).transpose()
                zAxisRotI = v_or
                zAxisRotJ = v_or
                t = sizeBeams
                [xx1, yy1, zz1] = addWallToPatch(nodeI, nodeJ, zAxisRotI, sizeBeams, t, [[0], [0], [0]], [[0], [0], [0]], "wireframe")
                points = vtk.vtkPoints()
                points.InsertNextPoint(xx1[0][0], yy1[0][0], zz1[0][0])
                points.InsertNextPoint(xx1[1][0], yy1[1][0], zz1[1][0])
                points.InsertNextPoint(xx1[2][0], yy1[2][0], zz1[2][0])
                points.InsertNextPoint(xx1[3][0], yy1[3][0], zz1[3][0])
                points.InsertNextPoint(xx1[0][1], yy1[0][1], zz1[0][1])
                points.InsertNextPoint(xx1[1][1], yy1[1][1], zz1[1][1])
                points.InsertNextPoint(xx1[2][1], yy1[2][1], zz1[2][1])
                points.InsertNextPoint(xx1[3][1], yy1[3][1], zz1[3][1])
                ugrid = vtk.vtkUnstructuredGrid()
                ugrid.SetPoints(points)
                ugrid.InsertNextCell(vtk.VTK_POLYHEDRON, faceId)
                # Create a mapper and actor
                mapper = vtk.vtkDataSetMapper()
                mapper.SetInputData(ugrid)
                actor = vtk.vtkActor()
                actor.SetMapper(mapper)
                actor.GetProperty().SetColor(colors.GetColor3d('Silver'))
                renderer.AddActor(actor)
                maxX = max(maxX, max(map(max, xx1)))
                maxY = max(maxY, max(map(max, yy1)))

    # Plot the floors
    nRows = np.size(xDir4, 0)
    nCols = np.size(xDir4, 1)

    startPoint = [maxX, 0, 0]
    endPoint = [maxX + 1, 0, 0]
    zAxis = [0, 0, 1]
    mkXaxis = arrowMaker(startPoint, endPoint, zAxis, 'Cyan')

    startPoint = [0, maxY, 0]
    endPoint = [0, maxY + 1, 0]
    mkXaxis = arrowMaker(startPoint, endPoint, zAxis, 'Cyan')



    tmp_nodeCount = 0
    for colItem in np.arange(nCols):
        for rowItem in np.arange(nRows):
            if rowItem == 0:
                tmp_nodeCoordinate = [[xDir4[rowItem, colItem], yDir4[rowItem, colItem], zDir4[rowItem, colItem]]]
            else:
                tmp_nodeCoordinate.append([xDir4[rowItem, colItem], yDir4[rowItem, colItem], zDir4[rowItem, colItem]])
        if colItem == 0:
            nodeCoordinate = [tmp_nodeCoordinate]
        else:
            nodeCoordinate.append(tmp_nodeCoordinate)

    print("Convert Tremuri to OpenSees completed in --- %s seconds ---" % (time.time() - startTime))

    renderer.SetBackground(colors.GetColor3d('White'))
    renderer.ResetCamera()
    renderer.GetActiveCamera().Roll(30)
    renderer.GetActiveCamera().Pitch(90)
    renderer.GetActiveCamera().Elevation(30)
    renderWindow.Render()
    # renderWindowInteractor.Initialize()

    return impElement, impNode, impWall, impFloor, impPolygon, impMaterial, impAnalysis, renderer

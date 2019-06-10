import math
import numpy as np
import time
import pandas as pd
import subprocess
import os
from os.path import join

cfilePath = os.getcwd()  # current working directory

# initialize the variables that are going to be written in TCL file
# modeling parameter dataframes
impNode = ''
impWall = ''
impElement = ''
impPolygon = ''
impMaterial = ''
impFixConstraint = ''
impW2wConstraint = ''
impF2wConstraint = ''
impAnalysis = ''
# project and run-time data
projectName = ''
TCLfilePath = os.getcwd() + "\\" + "tcl"
OUTPUTfilePath = os.getcwd() + "\\" + "output"
motionFilePath = "C:\Model Processing\tremuri_model_processing\basel_models_Pavia\input"
# variable definitions
freeVibrationTime = 0



def wrtOPSfunc():
    fileName = projectName
    batchFileName = fileName + ".bat"
    tclFileName = fileName + ".tcl"
    massDistribution = "Standard"
    macroelementType = "Tremuri"
    pushoverPatterns = "Standard"
    ignoreDrift = True
    pDelta = True
    flexureShells = False
    dropDrift = 0.004

    startTime = time.time()

    tmp_filesToRun = pd.DataFrame(columns=['fileName', 'outputFiles'], index=['0'])
    tmp_filesToRun_list = []

    if not os.path.exists(TCLfilePath):
        os.mkdir(TCLfilePath)
    fid = open(join(TCLfilePath, tclFileName), "w+")

    wallToWallConnection = '  1 2 3'
    floorToWallConnection = '  1 2 3 4 5'
    csi = -1  # damping ratio

    # initial stuff and materials
    fid.write("wipe\n\n")
    fid.write("setMaxOpenFiles 2048;	        		# Max number of recorders\n")
    fid.write("set Ubig 1.e10; 			   	 		# a really large number\n")
    fid.write("set Usmall [expr 1.0/$Ubig]; 			# a really small number\n")
    fid.write("set g    " + '{:9.2f}'.format(9.81) + "; \n")
    fid.write("set pi   " + '{:9.7f}'.format(math.pi) + ";\n\n")
    fid.write("# Create ModelBuilder (with three-dimensions (-ndm) and 6 DOF/node (-ndf))\n")
    fid.write("model basic -ndm 3 -ndf 6\n\n")

    # nodes
    fid.write("#NODES ------------------------------------------------------------ \n")
    fid.write("# Definition of the geometry\n# Create nodes\n#       tag     X         Y         Z  \n")
    node2dVec = [[0], [0], [0]]
    totalNodes = impNode['x'].count()
    for item in np.arange(totalNodes):
        fid.write("node " + '{:6d}'.format(impNode.index[item]) +
                  '{:10.3f}'.format(impNode['x'].iat[item]) +
                  '{:10.3f}'.format(impNode['y'].iat[item]) +
                  '{:10.3f}'.format(impNode['z'].iat[item]) + ' \n')
        if impNode['repartition'].iat[item] == impNode['repartition'].iat[item]:
            node2dVec = np.concatenate((node2dVec, np.concatenate(([[impNode.index[item]]], np.array([impNode['repartition'].iat[item]]).transpose()), axis=0)), axis=1)
    node2dVec = node2dVec.astype(int)
    fid.write("#END NODES ------------------------------------------------------------ \n")
    fid.write('puts "Nodes defined." \n\n\n')

    totalWalls = impWall['origin'].count()
    for item in np.arange(totalWalls):
        fid.write("geomTransf PDelta " + '{:6d}'.format(item + 1) +
                  '{:7.3f}'.format(impWall['zAxis'].iat[item][0]) +
                  '{:7.3f}'.format(impWall['zAxis'].iat[item][1]) +
                  '{:7.3f}'.format(impWall['zAxis'].iat[item][2]) + "\n")

    # macroelements
    fid.write("\n#MACROELEMENTS --------------------------------------------------------- \n")
    if macroelementType == "Tremuri":
        fid.write("#element Macroelement3d $eTag $nI $nJ $nE $aX $aY $aZ $oopX $oopY $oopZ -tremuri   $h $L $t $E $G $fc $mu $c $Gc $beta $driftF $driftS\n")
    else:
        fid.write("#element Macroelement3d $eTag $nI $nJ $nE $aX $aY $aZ $oopX $oopY $oopZ  -pier     $h $L $t $E $G $fc $mu $c $Gc $dropDrift $muR $driftF $driftS \n")

    totalElements = impElement['nodeI'].count()
    for item in np.arange(totalElements):
        if impElement['type'].iat[item] == "Macroelement3d":
            if pDelta:
                pDeltaString = " -pDelta "
            else:
                pDeltaString = ""

            kMat = int(impElement["mat"].iat[item])

            if massDistribution == "Standard" or massDistribution == "Consistent":
                densityString = " -density" + '{:9.1f}'.format(impMaterial.at[kMat, 'rho'])
            else:
                densityString = ""

            if massDistribution == "Consistent":
                massString = " -cmass"
            else:
                massString = ""

            if ignoreDrift:
                drift_F = -1
                drift_S = -1

            if macroelementType == "Tremuri":
                # tremuri implementation
                if abs(np.dot(impElement['xAxis'].iat[item], [[0], [0], [0]])) > 0.9:
                    elementType = "  -tremuri  "
                else:
                    elementType = "  -tremuri  "

                fid.write("element Macroelement3d    " + '{:6d}'.format(impElement.index[item]) +
                          '{:8d}'.format(impElement['nodeI'].iat[item]) +
                          '{:9d}'.format(impElement['nodeJ'].iat[item]) +
                          '{:9d}'.format(int(impElement['nodeE'].iat[item])) +
                          '{:9.3f}'.format(impElement['xAxis'].iat[item][0]) +
                          '{:7.3f}'.format(impElement['xAxis'].iat[item][1]) +
                          '{:7.3f}'.format(impElement['xAxis'].iat[item][2]) +
                          '{:9.3f}'.format(impWall.at[int(impElement['wall'].iat[item]), 'zAxis'][0]) +
                          '{:7.3f}'.format(impWall.at[int(impElement['wall'].iat[item]), 'zAxis'][1]) +
                          '{:7.3f}'.format(impWall.at[int(impElement['wall'].iat[item]), 'zAxis'][2]) + elementType +
                          '{:6.3f}'.format(impElement['h'].iat[item]) +
                          '{:7.3f}'.format(impElement['b'].iat[item]) +
                          '{:7.3f}'.format(impElement['t'].iat[item]) +
                          '{:10.3e}'.format(impMaterial.at[kMat, 'E']) +
                          '{:10.3e}'.format(impMaterial.at[kMat, 'G']) +
                          '{:10.3e}'.format(impMaterial.at[kMat, 'fc']) +
                          '{:7.3f}'.format(impMaterial.at[kMat, 'mu']) +
                          '{:10.3e}'.format(impMaterial.at[kMat, 'tau0']) +
                          '{:7.3f}'.format(impMaterial.at[kMat, 'Gc']) +
                          '{:7.3f}'.format(impMaterial.at[kMat, 'beta']) +
                          '{:9.5f}'.format(drift_F) + '{:9.5f}'.format(drift_S) + densityString + massString +
                          pDeltaString + "\n")
            else:
                # standard implementation
                if impElement['xAxis'].iat[item][2] < 0.1 * np.linalg.norm(impElement['xAxis'].iat[item]):
                    elementType = "  -spandrel "
                else:
                    elementType = "  -pier     "

                fid.write("element Macroelement3d    " + '{:6d}'.format(impElement.index[item]) +
                          '{:8d}'.format(impElement['nodeI'].iat[item]) +
                          '{:9d}'.format(impElement['nodeJ'].iat[item]) +
                          '{:9d}'.format(impElement['nodeE'].iat[item]) +
                          '{:9.3f}'.format(impElement['xAxis'].iat[item][0]) +
                          '{:7.3f}'.format(impElement['xAxis'].iat[item][1]) +
                          '{:7.3f}'.format(impElement['xAxis'].iat[item][2]) +
                          '{:9.3f}'.format(impWall.at[impElement['wall'].iat[item], 'zAxis'][0]) +
                          '{:7.3f}'.format(impWall.at[impElement['wall'].iat[item], 'zAxis'][1]) +
                          '{:7.3f}'.format(impWall.at[impElement['wall'].iat[item], 'zAxis'][2]) + elementType +
                          '{:6.3f}'.format(impElement['h'].iat[item]) +
                          '{:7.3f}'.format(impElement['b'].iat[item]) +
                          '{:7.3f}'.format(impElement['t'].iat[item]) +
                          '{:10.3e}'.format(impMaterial.at[kMat, 'E']) +
                          '{:10.3e}'.format(impMaterial.at[kMat, 'G']) +
                          '{:10.3e}'.format(impMaterial.at[kMat, 'fc']) +
                          '{:7.3f}'.format(impMaterial.at[kMat, 'mu']) +
                          '{:10.3e}'.format(impMaterial.at[kMat, 'tau0']) +
                          '{:7.3f}'.format(impMaterial.at[kMat, 'Gc']) +
                          '{:7.3f}'.format(dropDrift) +
                          '{:7.3f}'.format(impMaterial.at[kMat, 'muR']) +
                          '{:9.5f}'.format(drift_F) + '{:9.5f}'.format(drift_S) + densityString + massString +
                          pDeltaString + "\n")
        elif impElement['type'].iat[item] == "TriangularMacroelement":
            if pDelta:
                pDeltaString = " -pDelta "
            else:
                pDeltaString = ""

            kMat = impElement["mat"].iat[item]
            elementType = "  -gable  "

            if massDistribution == "Standard" or massDistribution == "Consistent":
                densityString = " -density" + '{:9.1f}'.format(impMaterial.at[kMat, 'rho'])
            else:
                densityString = ""

            if massDistribution == "Consistent":
                massString = " -cmass"
            else:
                massString = ""

            if ignoreDrift:
                drift_F = -1
                drift_S = -1

            if macroelementType == "Tremuri":
                # tremuri implementation
                fid.write("element Macroelement3d    " + '{:6d}'.format(impElement.index[item]) +
                          '{:8d}'.format(impElement['nodeI'].iat[item]) +
                          '{:9d}'.format(impElement['nodeJ'].iat[item]) +
                          '{:9d}'.format(impElement['nodeE'].iat[item]) +
                          '{:9.3f}'.format(impElement['xAxis'].iat[item][0]) +
                          '{:7.3f}'.format(impElement['xAxis'].iat[item][1]) +
                          '{:7.3f}'.format(impElement['xAxis'].iat[item][2]) +
                          '{:9.3f}'.format(impWall.at[impElement['wall'].iat[item], 'zAxis'][0]) +
                          '{:7.3f}'.format(impWall.at[impElement['wall'].iat[item], 'zAxis'][1]) +
                          '{:7.3f}'.format(impWall.at[impElement['wall'].iat[item], 'zAxis'][2]) +
                          elementType + '{:6.3f}'.format(impElement['h'].iat[item]) +
                          '{:7.3f}'.format(impElement['b'].iat[item]) +
                          '{:7.3f}'.format(impElement['t'].iat[item]) +
                          '{:10.3e}'.format(impMaterial.at[kMat, 'E']) +
                          '{:10.3e}'.format(impMaterial.at[kMat, 'G']) +
                          '{:10.3e}'.format(impMaterial.at[kMat, 'fc']) +
                          '{:7.3f}'.format(impMaterial.at[kMat, 'mu']) +
                          '{:10.3e}'.format(impMaterial.at[kMat, 'tau0']) +
                          '{:7.3f}'.format(impMaterial.at[kMat, 'Gc']) + '{:7.3f}'.format(1.0)
                          + '{:7.3f}'.format(impMaterial.at[kMat, 'beta']) +
                          '{:9.5f}'.format(drift_F) + '{:9.5f}'.format(drift_S) + densityString + massString +
                          pDeltaString + "\n")
            else:
                # standard implementation
                fid.write("element Macroelement3d    " + '{:6d}'.format(impElement.index[item]) +
                          '{:8d}'.format(impElement['nodeI'].iat[item]) +
                          '{:9d}'.format(impElement['nodeJ'].iat[item]) +
                          '{:9d}'.format(impElement['nodeE'].iat[item]) +
                          '{:9.3f}'.format(impElement['xAxis'].iat[item][0]) +
                          '{:7.3f}'.format(impElement['xAxis'].iat[item][1]) +
                          '{:7.3f}'.format(impElement['xAxis'].iat[item][2]) +
                          '{:9.3f}'.format(impWall.at[impElement['wall'].iat[item], 'zAxis'][0]) +
                          '{:7.3f}'.format(impWall.at[impElement['wall'].iat[item], 'zAxis'][1]) +
                          '{:7.3f}'.format(impWall.at[impElement['wall'].iat[item], 'zAxis'][2]) + elementType +
                          '{:6.3f}'.format(impElement['h'].iat[item]) +
                          '{:7.3f}'.format(impElement['b'].iat[item]) +
                          '{:7.3f}'.format(impElement['t'].iat[item]) +
                          '{:10.3e}'.format(impMaterial.at[kMat, 'E']) +
                          '{:10.3e}'.format(impMaterial.at[kMat, 'G']) +
                          '{:10.3e}'.format(impMaterial.at[kMat, 'fc']) +
                          '{:7.3f}'.format(impMaterial.at[kMat, 'mu']) +
                          '{:10.3e}'.format(impMaterial.at[kMat, 'tau0']) +
                          '{:7.3f}'.format(impMaterial.at[kMat, 'Gc']) + '{:7.3f}'.format(1.0)
                          + '{:7.3f}'.format(dropDrift) +
                          '{:7.3f}'.format(impMaterial.at[kMat, 'muR']) +
                          '{:9.5f}'.format(drift_F) + '{:9.5f}'.format(drift_S) + densityString + massString +
                          pDeltaString + "\n")
    fid.write("#END Macrolements------------------------------------------------------------ \n\n")

    # shells
    fid.write("\n#SHELLS  --------------------------------------------------------- \n\n")
    fid.write("#element ShellMITC4 $eleTag $iNode $jNode $kNode $lNode $secTag \n")
    for item in np.arange(totalElements):
        if impElement['type'].iat[item] == "FloorShell":
            if flexureShells:
                if not np.isnan(impElement['properties'].iat[item]).any():
                    ni = (impElement['properties'].iat[item][0] /
                          (2 * impElement['properties'].iat[item][3])) - 1
                    if ni > 0.5 or ni == np.inf or ni < 0:
                        print("WARINING: invalid Poisson's ratio calculated for shell. A value of ni=0.2 is assumed for element " + impElement.index[item])
                        ni = 0.2
                else:
                    print("WARINING: invalid Poisson's ratio calculated for shell. A value of ni=0.2 is assumed for element " + impElement.index[item])
                    ni = 0.2

                fid.write("section ElasticMembranePlateSection  " +
                          '{:6d}'.format(int(impElement.index[item])) +
                          '{:10.1f}'.format(
                              float(impElement['properties'].iat[item][0] * 10 ** (-6))) + "e+06" +
                          '{:10.1f}'.format(
                              float(impElement['properties'].iat[item][0] * 10 ** (-6))) + "e+06" +
                          '{:10.3f}'.format(ni) +
                          '{:10.3f}'.format(float(impElement['t'].iat[item])) + " \n")
            else:
                fid.write("section OrthotropicMembraneSection   " +
                          '{:d}'.format(int(impElement.index[item])) +
                          '{:12.1f}'.format(float(impElement['properties'].iat[item][0]) * 10 ** (-6)) + "e+06" +
                          '{:11.1f}'.format(float(impElement['properties'].iat[item][1]) * 10 ** (-6)) + "e+06" +
                          '{:11.3f}'.format(float(impElement['properties'].iat[item][2])) +
                          '{:11.1f}'.format(float(impElement['properties'].iat[item][3]) * 10 ** (-6)) + "e+06" +
                          '{:11.3f}'.format(float(impElement['t'].iat[item])) +
                          '{:11.1f}'.format(0.0) + "  \n")
            fid.write("element ShellMITC4    " +
                      '{:d}'.format(impElement.index[item]) +
                      '{:8d}'.format(impElement['nodeI'].iat[item]) +
                      '{:9d}'.format(impElement['nodeJ'].iat[item]) +
                      '{:9d}'.format(int(impElement['nodeK'].iat[item])) +
                      '{:8d}'.format(int(impElement['nodeL'].iat[item])) +
                      '{:8d}'.format(impElement.index[item]) + " \n")

    fid.write("#END Shells ------------------------------------------------------------ \n\n")

    # fixed nodes
    fid.write("#CONSTRAINTS --------------------------------------------------------- \n")
    totalFixConstraints = impFixConstraint['node'].count()
    for item in np.arange(totalFixConstraints):
        dofs = [int(dof) for dof in impFixConstraint['dofs'].iat[item]]
        fid.write("fix  " + '{:6d}'.format(int(impFixConstraint['node'].iat[item])) +
                  ''.join('{:3d}'.format(dof) for dof in dofs) + "\n")

    fid.write("#END Constraints------------------------------------------------------------ \n\n")

    # wall to wall - floor to wall connections
    fid.write("#WALL TO WALL CONNECTIONS --------------------------------------------------------- \n")
    totalW2wConstraints = impW2wConstraint['master'].count()
    for item in np.arange(totalW2wConstraints):
        constrainedNode = 0
        for kConstrained in np.arange(totalFixConstraints):
            if int(impFixConstraint['node'].iat[kConstrained]) == \
                    impW2wConstraint['master'].iat[item] \
                    or int(impFixConstraint['node'].iat[kConstrained]) == \
                    impW2wConstraint['slave'].iat[item]:
                constrainedNode = 1
                break

        # check if a non rigid link must be setup
        foundConnection = False
        index = 0
        # omitted this part

        if foundConnection and constrainedNode != 1:
            print('WARNING: no implementation yet provided for nonlinear wall to wall connection. Rigid connection between '
                  'nodes ' + '{:d}'.format(int(impW2wConstraint['master'].iat[item])) + ' and ' +
                  '{:d}'.format(int(impW2wConstraint['slave'].iat[item])) + '.')

        if constrainedNode != 1:
            fid.write("equalDOF " + '{:6d}'.format(int(impW2wConstraint['master'].iat[item])) +
                      '{:7d}'.format(int(impW2wConstraint['slave'].iat[item])) + wallToWallConnection + "\n")

    fid.write("\n\n#FLOOR TO WALL CONNECTIONS --------------------------------------------------------- \n")
    totalF2wConstraints = impF2wConstraint['master'].count()
    for item in np.arange(totalF2wConstraints):
        fid.write("equalDOF " + '{:6d}'.format(int(impF2wConstraint['master'].iat[item])) +
                  '{:7d}'.format(int(impF2wConstraint['slave'].iat[item])) + floorToWallConnection + "\n")

    fid.write("#END Connections ------------------------------------------------------ \n\n")

    # rigid beams
    fid.write("#RIGID LINKS ---------------------------------------------------------- \n")
    kEl = totalElements
    # rigid beam section is omitted
    fid.write("# ----------------\n")
    kTransf = totalWalls
    for item in np.arange(totalElements):
        if impElement['type'].iat[item] == "ElasticBeam":
            kWall = int(impElement['wall'].iat[item])
            kTransf = kTransf + 1
            fid.write("geomTransf Linear " + '{:6d}'.format(kTransf) +
                      ''.join('{:7.3f}'.format(component) for component in impWall.at[kWall, 'zAxis'])
                      + " -jntOffset" + "".join('{:7.3f}'.format(component) for component in impElement['offsetI'].iat[item]) +
                      "".join('{:7.3f}'.format(component) for component in impElement['offsetJ'].iat[item]) +
                      "  \n")
            kEl = kEl + 1

            if float(impMaterial.at[int(impElement['mat'].iat[item]), 'G']) == 0:
                impMaterial.at[int(impElement['mat'].iat[item]), 'G'] = \
                    0.3 * float(impMaterial.at[int(impElement['mat'].iat[item]), 'E'])

            fid.write("element elasticBeamColumn" + '{:7d}'.format(kEl) +
                      '{:7d}'.format(int(impElement['nodeI'].iat[item])) +
                      '{:7d}'.format(int(impElement['nodeJ'].iat[item])) +
                      '{:10.3e}'.format(float(impElement['area'].iat[item])) +
                      '{:10.3e}'.format(float(impMaterial.at[int(impElement['mat'].iat[item]), 'E'])) +
                      '{:10.3e}'.format(float(impMaterial.at[int(impElement['mat'].iat[item]), 'G'])) +
                      '{:10.3e}'.format(float(impElement['J'].iat[item])) +
                      '{:10.3e}'.format(float(impElement['J'].iat[item])) +
                      '{:10.3e}'.format(float(impElement['J'].iat[item])) + '{:8d}'.format(kTransf) + "\n")
    fid.write("#END Elastic beams---------------------------------------------------- \n\n")

    # nonlinear beams
    fid.write("#NONLINEAR BEAMS ---------------------------------------------------------- \n")
    for item in np.arange(totalElements):
        if impElement['type'].iat[item] == "NonlinearBeam":
            kWall = impElement['wall'].iat[item]
            kTransf = kTransf + 1
            fid.write("geomTransf Linear " + '{:6d}'.format(kTransf) +
                      ''.join('{:7.3f}'.format(component) for component in impWall.at[kWall, 'zAxis'])
                      + " -jntOffset" + "".join('{:7.3f}'.format(component) for component in impElement['offsetI'].iat[item]) +
                      "".join('{:7.3f}'.format(-1 * component) for component in impElement['offsetJ'].iat[item]) +
                      "  \n")
            kEl = kEl + 1
            fid.write("element elasticBeamColumn" + '{:7d}'.format(kEl) +
                      '{:7d}'.format(int(impElement['nodeI'].iat[item])) +
                      '{:7d}'.format(int(impElement['nodeJ'].iat[item])) +
                      '{:10.3e}'.format(float(impElement['area'].iat[item])) +
                      '{:10.3e}'.format(float(
                          impMaterial.at[impElement['mat'].iat[item], 'E'])) +
                      '{:10.3e}'.format(float(
                          impMaterial.at[impElement['mat'].iat[item], 'G'])) +
                      '{:10.3e}'.format(float(impElement['J'].iat[item])) +
                      '{:10.3e}'.format(float(impElement['J'].iat[item])) +
                      '{:10.3e}'.format(float(impElement['J'].iat[item])) + '{:8d}'.format(
                kTransf) + "\n")
    fid.write("#END Nonlinear beams---------------------------------------------------- \n\n")

    # additional masses
    # mass distribution. options 'Tremuri', 'Lumped', 'Consistent', 'Standard'
    totalPolygons = impPolygon['xDim'].count()
    addMass = pd.DataFrame(columns=['mass'], index=np.arange(totalNodes))
    addMassTremuri = pd.DataFrame(columns=['massTremuri'], index=np.arange(totalNodes))
    addloadX = pd.DataFrame(columns=['load_X'], index=np.arange(totalNodes))
    addloadY = pd.DataFrame(columns=['load_Y'], index=np.arange(totalNodes))
    addloadZ = pd.DataFrame(columns=['load_Z'], index=np.arange(totalNodes))

    for item in np.arange(totalNodes):
        addMass['mass'].iat[item] = [0, 0, 0, 0, 0, 0]
        addMassTremuri['massTremuri'].iat[item] = [0, 0, 0, 0, 0, 0]

        addloadX['load_X'].iat[item] = [[0, 0, 0, 0, 0, 0]]
        addloadY['load_Y'].iat[item] = [[0, 0, 0, 0, 0, 0]]
        addloadZ['load_Z'].iat[item] = [[0, 0, 0, 0, 0, 0]]

    for item in np.arange(totalPolygons):
        kWall = impNode.at[impPolygon.index[item], 'wall']
        xAxis = np.array(impWall.at[kWall, 'xAxis'])
        yAxis = np.array(impWall.at[kWall, 'yAxis'])
        zAxis = np.array(impWall.at[kWall, 'zAxis'])
        nodeLoc = impNode.index.get_loc(impPolygon.index[item])

        m = float(impPolygon['area'].iat[item]) * float(impPolygon['t'].iat[item]) * float(impPolygon['rho'].iat[item])
        baricenter = impPolygon['blCorner'].iat[item] + np.dot(np.dot(xAxis, impPolygon['xDim'].iat[item]), 0.5) + \
                     np.dot(np.dot(yAxis, impPolygon['yDim'].iat[item]), 0.5)
        r = np.matrix(baricenter - impNode.at[impPolygon.index[item], 'pos'])
        r = r.transpose()

        # true mass
        addMass['mass'].iat[nodeLoc] = addMass['mass'].iat[nodeLoc] + np.dot([1, 1, 1, r[1] ** 2 + r[2] ** 2, r[0] ** 2 +
                                                                              r[2] ** 2, r[0] ** 2 + r[1] ** 2], m)

        # forces for vertical analysis and pushover
        F = np.dot(m, [[1], [0], [0]])
        moment = (np.cross(r.transpose(), F.transpose())).transpose()
        addloadX['load_X'].iat[nodeLoc] = addloadX['load_X'].iat[nodeLoc] + np.concatenate(
            (F.transpose(), moment.transpose()), axis=1)

        F = np.dot(m, [[0], [1], [0]])
        moment = (np.cross(r.transpose(), F.transpose())).transpose()
        addloadY['load_Y'].iat[nodeLoc] = addloadY['load_Y'].iat[nodeLoc] + np.concatenate(
            (F.transpose(), moment.transpose()), axis=1)

        F = np.dot(m, [[0], [0], [1]])
        moment = (np.cross(r.transpose(), F.transpose())).transpose()
        addloadZ['load_Z'].iat[nodeLoc] = addloadZ['load_Z'].iat[nodeLoc] + np.concatenate(
            (F.transpose(), moment.transpose()), axis=1)

        # tremuri mass distribution
        xAxis = np.array(impWall.at[kWall, 'xAxis'])
        yAxis = np.array(impWall.at[kWall, 'yAxis'])
        zAxis = np.array(impWall.at[kWall, 'zAxis'])

        # node2dVec
        if not impPolygon.index[item] in node2dVec[0]:
            addMassTremuri['massTremuri'].iat[nodeLoc] = addMassTremuri['massTremuri'].iat[nodeLoc] + np.dot([1, 1, 1, 0, 0, 0], m)
        else:
            valIndex = list(node2dVec[0]).index(impPolygon.index[item])
            dist1 = np.linalg.norm(np.subtract(impNode.at[impPolygon.index[item], 'pos'], impNode.at[node2dVec[1][valIndex], 'pos']))
            dist2 = np.linalg.norm(np.subtract(impNode.at[impPolygon.index[item], 'pos'], impNode.at[node2dVec[2][valIndex], 'pos']))
            distTot = dist1 + dist2

            addMassTremuri['massTremuri'].iat[nodeLoc] = addMassTremuri['massTremuri'].iat[nodeLoc] + np.dot(np.concatenate(
                (abs(xAxis.transpose()) + abs(yAxis.transpose()), [0, 0, 0])), m)

            addMassTremuri['massTremuri'].iat[impNode.index.get_loc(node2dVec[1][valIndex])] = \
                addMassTremuri['massTremuri'].iat[impNode.index.get_loc(node2dVec[1][valIndex])] + np.dot(np.concatenate(
                    (abs(zAxis.transpose()), [0, 0, 0])), m * dist2 / distTot)
            addMassTremuri['massTremuri'].iat[impNode.index.get_loc(node2dVec[2][valIndex])] = \
                addMassTremuri['massTremuri'].iat[impNode.index.get_loc(node2dVec[2][valIndex])] + np.dot(np.concatenate(
                    (abs(zAxis.transpose()), [0, 0, 0])), m * dist1 / distTot)

        # add added mass if any
        if not np.isnan(impNode.at[impPolygon.index[item], 'addedMass']):
            m = impNode.at[impPolygon.index[item], 'addedMass']
            r = impNode.at[impPolygon.index[item], 'addedMassEcc']

            addMass['mass'].iat[nodeLoc] = addMass['mass'].iat[nodeLoc] + np.dot([1, 1, 1, r[1] ** 2 + r[2] ** 2, r[0] ** 2 +
                                                                              r[2] ** 2, r[0] ** 2 + r[1] ** 2], m)

            # forces for vertical analysis and pushover
            F = np.dot(m, [[1], [0], [0]])
            moment = (np.cross(r.transpose(), F.transpose())).transpose()
            addloadX['load_X'].iat[nodeLoc] = addloadX['load_X'].iat[nodeLoc] + np.concatenate(
                (F.transpose(), moment.transpose()), axis=1)

            F = np.dot(m, [[0], [1], [0]])
            moment = (np.cross(r.transpose(), F.transpose())).transpose()
            addloadY['load_Y'].iat[nodeLoc] = addloadY['load_Y'].iat[nodeLoc] + np.concatenate(
                (F.transpose(), moment.transpose()), axis=1)

            F = np.dot(m, [[0], [0], [1]])
            moment = (np.cross(r.transpose(), F.transpose())).transpose()
            addloadZ['load_Z'].iat[nodeLoc] = addloadZ['load_Z'].iat[nodeLoc] + np.concatenate(
                (F.transpose(), moment.transpose()), axis=1)

            # tremuri mass distribution
            xAxis = np.array(impWall.at[kWall, 'xAxis'])
            yAxis = np.array(impWall.at[kWall, 'yAxis'])
            zAxis = np.array(impWall.at[kWall, 'zAxis'])

            if not impPolygon.index[item] in node2dVec[0]:
                addMassTremuri['massTremuri'].iat[nodeLoc] = addMassTremuri['massTremuri'].iat[nodeLoc] + \
                                                             np.dot([1, 1, 1, r[1] ** 2 + r[2] ** 2, r[0] ** 2 + r[2] ** 2,
                                                                     r[0] ** 2 + r[1] ** 2], m)
            else:
                valIndex = list(node2dVec[0]).index(impPolygon.index[item])
                dist1 = np.linalg.norm(
                    np.subtract(impNode.at[impPolygon.index[item], 'pos'], impNode.at[node2dVec[1][valIndex], 'pos']))
                dist2 = np.linalg.norm(
                    np.subtract(impNode.at[impPolygon.index[item], 'pos'], impNode.at[node2dVec[2][valIndex], 'pos']))
                distTot = dist1 + dist2

                addMassTremuri['massTremuri'].iat[nodeLoc] = addMassTremuri['massTremuri'].iat[nodeLoc] + \
                                                             np.dot(np.concatenate((abs(xAxis.transpose()) +
                                                                                    abs(yAxis.transpose()), [0, 0, 0])), m)

                addMassTremuri['massTremuri'].iat[impNode.index.get_loc(node2dVec[1][valIndex])] = \
                    addMassTremuri['massTremuri'].iat[impNode.index.get_loc(node2dVec[1][valIndex])] + np.dot(np.concatenate(
                        (abs(zAxis.transpose()), [0, 0, 0])), m * dist2 / distTot)
                addMassTremuri['massTremuri'].iat[impNode.index.get_loc(node2dVec[2][valIndex])] = \
                    addMassTremuri['massTremuri'].iat[impNode.index.get_loc(node2dVec[2][valIndex])] + np.dot(np.concatenate(
                        (abs(zAxis.transpose()), [0, 0, 0])), m * dist1 / distTot)

    # add element masses to Tremuri mass and pushover loads
    for item in np.arange(totalElements):
        if impElement['type'].iat[item] == "Macroelement3d":
            elementMass = impElement['b'].iat[item] * impElement['t'].iat[item] * impElement['h'].iat[item] * impMaterial.at[int(impElement['mat'].iat[item]), 'rho']

            elementWall = int(impElement['wall'].iat[item])
            xAxis = np.array(impWall.at[elementWall, 'xAxis'])
            yAxis = np.array(impWall.at[elementWall, 'yAxis'])
            zAxis = np.array(impWall.at[elementWall, 'zAxis'])

            if massDistribution == "Lumped" or massDistribution == "Tremuri" or massDistribution == "Standard":
                totWeight = np.dot([[1], [0], [0]], elementMass)
                offsetI = np.matrix(impNode.at[int(impElement['nodeE'].iat[item]), 'pos'] - \
                          impElement['h'].iat[item] * 0.5 * impElement['xAxis'].iat[item] - \
                          impNode.at[impElement['nodeI'].iat[item], 'pos']).transpose()
                offsetJ = np.matrix(impNode.at[int(impElement['nodeE'].iat[item]), 'pos'] + \
                          impElement['h'].iat[item] * 0.5 * impElement['xAxis'].iat[item] - \
                          impNode.at[impElement['nodeJ'].iat[item], 'pos']).transpose()

                momentI = np.cross(offsetI.transpose(), np.dot(totWeight.transpose(), 0.5)).transpose()
                momentJ = np.cross(offsetJ.transpose(), np.dot(totWeight.transpose(), 0.5)).transpose()

                addloadX['load_X'].iat[impNode.index.get_loc(impElement['nodeI'].iat[item])] = \
                    addloadX['load_X'].iat[impNode.index.get_loc(impElement['nodeI'].iat[item])] + \
                    np.concatenate((0.5 * totWeight.transpose(), momentI.transpose()), axis=1)

                addloadX['load_X'].iat[impNode.index.get_loc(impElement['nodeJ'].iat[item])] = \
                    addloadX['load_X'].iat[impNode.index.get_loc(impElement['nodeJ'].iat[item])] + \
                    np.concatenate((0.5 * totWeight.transpose(), momentJ.transpose()), axis=1)

                totWeight = np.dot([[0], [1], [0]], elementMass)
                momentI = np.cross(offsetI.transpose(), np.dot(totWeight.transpose(), 0.5)).transpose()
                momentJ = np.cross(offsetJ.transpose(), np.dot(totWeight.transpose(), 0.5)).transpose()

                addloadY['load_Y'].iat[impNode.index.get_loc(impElement['nodeI'].iat[item])] = \
                    addloadY['load_Y'].iat[impNode.index.get_loc(impElement['nodeI'].iat[item])] + \
                    np.concatenate((0.5 * totWeight.transpose(), momentI.transpose()), axis=1)
                addloadY['load_Y'].iat[impNode.index.get_loc(impElement['nodeJ'].iat[item])] = \
                    addloadY['load_Y'].iat[impNode.index.get_loc(impElement['nodeJ'].iat[item])] + \
                    np.concatenate((0.5 * totWeight.transpose(), momentJ.transpose()), axis=1)

                if massDistribution != "Standard":
                    totWeight = np.dot([[0], [0], [1]], elementMass)
                    momentI = np.cross(offsetI.transpose(), np.dot(totWeight.transpose(), 0.5)).transpose()
                    momentJ = np.cross(offsetJ.transpose(), np.dot(totWeight.transpose(), 0.5)).transpose()

                    addloadZ['load_Z'].iat[impNode.index.get_loc(impElement['nodeI'].iat[item])] = \
                        addloadZ['load_Z'].iat[impNode.index.get_loc(impElement['nodeI'].iat[item])] + \
                        np.concatenate((0.5 * totWeight.transpose(), momentI.transpose()), axis=1)
                    addloadZ['load_Z'].iat[impNode.index.get_loc(impElement['nodeJ'].iat[item])] = \
                        addloadZ['load_Z'].iat[impNode.index.get_loc(impElement['nodeJ'].iat[item])] + \
                        np.concatenate((0.5 * totWeight.transpose(), momentJ.transpose()), axis=1)

                if massDistribution == "Lumped":
                    addMass['mass'].iat[impNode.index.get_loc(impElement['nodeI'].iat[item])] = \
                        addMass['mass'].iat[impNode.index.get_loc(impElement['nodeI'].iat[item])] + \
                        np.dot([1, 1, 1, 0, 0, 0], elementMass * 0.5)
                    addMass['mass'].iat[impNode.index.get_loc(impElement['nodeJ'].iat[item])] = \
                        addMass['mass'].iat[impNode.index.get_loc(impElement['nodeJ'].iat[item])] + \
                        np.dot([1, 1, 1, 0, 0, 0], elementMass * 0.5)

            if not impElement['nodeI'].iat[item] in node2dVec[0]:
                addMassTremuri['massTremuri'].iat[impNode.index.get_loc(impElement['nodeI'].iat[item])] = \
                    addMassTremuri['massTremuri'].iat[impNode.index.get_loc(impElement['nodeI'].iat[item])] + \
                    np.dot([1, 1, 1, 0, 0, 0], elementMass * 0.5)
            else:
                valIndex = list(node2dVec[0]).index(impElement['nodeI'].iat[item])
                dist1 = np.linalg.norm(
                    np.subtract(impNode.at[impElement['nodeI'].iat[item], 'pos'], impNode.at[node2dVec[1][valIndex], 'pos']))
                dist2 = np.linalg.norm(
                    np.subtract(impNode.at[impElement['nodeI'].iat[item], 'pos'], impNode.at[node2dVec[2][valIndex], 'pos']))
                distTot = dist1 + dist2

                addMassTremuri['massTremuri'].iat[impNode.index.get_loc(impElement['nodeI'].iat[item])] = \
                    addMassTremuri['massTremuri'].iat[impNode.index.get_loc(impElement['nodeI'].iat[item])] + \
                    np.dot(np.concatenate((abs(xAxis.transpose()) + abs(yAxis.transpose()), [0, 0, 0])), elementMass * 0.5)

                addMassTremuri['massTremuri'].iat[impNode.index.get_loc(node2dVec[1][valIndex])] = \
                    addMassTremuri['massTremuri'].iat[impNode.index.get_loc(node2dVec[1][valIndex])] + \
                    np.dot(np.concatenate((abs(zAxis.transpose()), [0, 0, 0])), (elementMass * 0.5) * (dist2 / distTot))
                addMassTremuri['massTremuri'].iat[impNode.index.get_loc(node2dVec[2][valIndex])] = \
                    addMassTremuri['massTremuri'].iat[impNode.index.get_loc(node2dVec[2][valIndex])] + \
                    np.dot(np.concatenate((abs(zAxis.transpose()), [0, 0, 0])), (elementMass * 0.5) * (dist1 / distTot))

            if not impElement['nodeJ'].iat[item] in node2dVec[0]:
                addMassTremuri['massTremuri'].iat[impNode.index.get_loc(impElement['nodeJ'].iat[item])] = \
                    addMassTremuri['massTremuri'].iat[impNode.index.get_loc(impElement['nodeJ'].iat[item])] + \
                    np.dot([1, 1, 1, 0, 0, 0], elementMass * 0.5)
            else:
                valIndex = list(node2dVec[0]).index(impElement['nodeJ'].iat[item])
                dist1 = np.linalg.norm(
                    np.subtract(impNode.at[impElement['nodeJ'].iat[item], 'pos'], impNode.at[node2dVec[1][valIndex], 'pos']))
                dist2 = np.linalg.norm(
                    np.subtract(impNode.at[impElement['nodeJ'].iat[item], 'pos'], impNode.at[node2dVec[2][valIndex], 'pos']))
                distTot = dist1 + dist2

                addMassTremuri['massTremuri'].iat[impNode.index.get_loc(impElement['nodeJ'].iat[item])] = \
                    addMassTremuri['massTremuri'].iat[impNode.index.get_loc(impElement['nodeJ'].iat[item])] + \
                    np.dot(np.concatenate((abs(xAxis.transpose()) + abs(yAxis.transpose()), [0, 0, 0])), elementMass * 0.5)

                addMassTremuri['massTremuri'].iat[impNode.index.get_loc(node2dVec[1][valIndex])] = \
                    addMassTremuri['massTremuri'].iat[impNode.index.get_loc(node2dVec[1][valIndex])] + \
                    np.dot(np.concatenate((abs(zAxis.transpose()), [0, 0, 0])), (elementMass * 0.5) * (dist2 / distTot))
                addMassTremuri['massTremuri'].iat[impNode.index.get_loc(node2dVec[2][valIndex])] = \
                    addMassTremuri['massTremuri'].iat[impNode.index.get_loc(node2dVec[2][valIndex])] + \
                    np.dot(np.concatenate((abs(zAxis.transpose()), [0, 0, 0])), (elementMass * 0.5) * (dist1 / distTot))

    for item in np.arange(totalElements):
        if impElement['type'].iat[item] == "TriangularMacroelement":
            elementMass = 0.5 * impElement['b'].iat[item] * impElement['t'].iat[item] * impElement['h'].iat[item] * impMaterial.at[impElement['mat'].iat[item], 'rho']

            elementWall = impElement['wall'].iat[item]
            xAxis = np.array(impWall.at[elementWall, 'xAxis'])
            yAxis = np.array(impWall.at[elementWall, 'yAxis'])
            zAxis = np.array(impWall.at[elementWall, 'zAxis'])

            if massDistribution == "Lumped" or massDistribution == "Tremuri" or massDistribution == "Standard":
                totWeight = np.dot([[1], [0], [0]], elementMass)
                offsetI = impNode.at[impElement['nodeE'].iat[item], 'pos'] - \
                          impElement['h'].iat[item] * 0.5 * impElement['xAxis'].iat[item] - \
                          impNode.at[impElement['nodeI'].iat[item], 'pos']
                offsetJ = impNode.at[impElement['nodeE'].iat[item], 'pos'] + \
                          impElement['h'].iat[item] * 0.5 * impElement['xAxis'].iat[item] - \
                          impNode.at[impElement['nodeJ'].iat[item], 'pos']
                momentI = np.cross(offsetI, totWeight * 0.5)
                momentJ = np.cross(offsetJ, totWeight * 0.5)

                addloadX.at[impElement['nodeI'].iat[item], 'load_X'] = \
                    addloadX.at[impElement['nodeI'].iat[item], 'load_X'] + \
                    np.concatenate((0.5 * totWeight.transpose(), momentI.transpose()))
                addloadX.at[impElement['nodeJ'].iat[item], 'load_X'] = \
                    addloadX.at[impElement['nodeJ'].iat[item], 'load_X'] + \
                    np.concatenate((0.5 * totWeight.transpose(), momentJ.transpose()))

                totWeight = np.dot([[0], [1], [0]], elementMass)
                momentI = np.cross(offsetI, totWeight * 0.5)
                momentJ = np.cross(offsetJ, totWeight * 0.5)

                addloadY.at[impElement['nodeI'].iat[item], 'load_Y'] = \
                    addloadY.at[impElement['nodeI'].iat[item], 'load_Y'] + \
                    np.concatenate((0.5 * totWeight.transpose(), momentI.transpose()))
                addloadY.at[impElement['nodeJ'].iat[item], 'load_Y'] = \
                    addloadY.at[impElement['nodeJ'].iat[item], 'load_Y'] + \
                    np.concatenate((0.5 * totWeight.transpose(), momentJ.transpose()))

                if massDistribution != "Standard":
                    totWeight = np.dot([[0], [0], [1]], elementMass)
                    momentI = np.cross(offsetI, totWeight * 0.5)
                    momentJ = np.cross(offsetJ, totWeight * 0.5)

                    addloadZ.at[impElement['nodeI'].iat[item], 'load_Z'] = \
                        addloadZ.at[impElement['nodeI'].iat[item], 'load_Z'] + \
                        np.concatenate((0.0 * totWeight.transpose(), momentI.transpose()))
                    addloadZ.at[impElement['nodeJ'].iat[item], 'load_Z'] = \
                        addloadZ.at[impElement['nodeJ'].iat[item], 'load_Z'] + \
                        np.concatenate((1.0 * totWeight.transpose(), momentJ.transpose()))

                if massDistribution == "Lumped":
                    addMass.at[impElement['nodeI'].iat[item], 'mass'] = \
                        addMass.at[impElement['nodeI'].iat[item], 'mass'] + \
                        np.concatenate(([1, 1, 1, 0, 0, 0], elementMass * 0.5))
                    addMass.at[impElement['nodeJ'].iat[item], 'mass'] = \
                        addMass.at[impElement['nodeJ'].iat[item], 'mass'] + \
                        np.concatenate(([1, 1, 1, 0, 0, 0], elementMass * 0.5))

            if not impElement['nodeI'].iat[item] in node2dVec[0]:
                addMassTremuri['massTremuri'].iat[impNode.index.get_loc(impElement['nodeI'].iat[item])] = \
                    addMassTremuri['massTremuri'].iat[impNode.index.get_loc(impElement['nodeI'].iat[item])] + \
                    np.dot([1, 1, 1, 0, 0, 0], elementMass * 0.5)
            else:
                valIndex = list(node2dVec[0]).index(impElement['nodeI'].iat[item])
                dist1 = np.linalg.norm(
                    np.subtract(impNode.at[impElement['nodeI'].iat[item], 'pos'], impNode.at[node2dVec[1][valIndex], 'pos']))
                dist2 = np.linalg.norm(
                    np.subtract(impNode.at[impElement['nodeI'].iat[item], 'pos'], impNode.at[node2dVec[2][valIndex], 'pos']))
                distTot = dist1 + dist2

                addMassTremuri['massTremuri'].iat[impNode.index.get_loc(impElement['nodeI'].iat[item])] = \
                    addMassTremuri['massTremuri'].iat[impNode.index.get_loc(impElement['nodeI'].iat[item])] + \
                    np.dot(np.concatenate((abs(xAxis.transpose()) + abs(yAxis.transpose()), [0, 0, 0])), elementMass * 0.5)

                addMassTremuri['massTremuri'].iat[impNode.index.get_loc(node2dVec[1][valIndex])] = \
                    addMassTremuri['massTremuri'].iat[impNode.index.get_loc(node2dVec[1][valIndex])] + \
                    np.dot(np.concatenate((abs(zAxis.transpose()), [0, 0, 0])), (elementMass * 0.5) * (dist2 / distTot))
                addMassTremuri['massTremuri'].iat[impNode.index.get_loc(node2dVec[2][valIndex])] = \
                    addMassTremuri['massTremuri'].iat[impNode.index.get_loc(node2dVec[2][valIndex])] + \
                    np.dot(np.concatenate((abs(zAxis.transpose()), [0, 0, 0])), (elementMass * 0.5) * (dist1 / distTot))

            if not impElement['nodeJ'].iat[item] in node2dVec[0]:
                addMassTremuri['massTremuri'].iat[impNode.index.get_loc(impElement['nodeJ'].iat[item])] = \
                    addMassTremuri['massTremuri'].iat[impNode.index.get_loc(impElement['nodeJ'].iat[item])] + \
                    np.dot([1, 1, 1, 0, 0, 0], elementMass * 0.5)
            else:
                valIndex = list(node2dVec[0]).index(impElement['nodeJ'].iat[item])
                dist1 = np.linalg.norm(
                    np.subtract(impNode.at[impElement['nodeJ'].iat[item], 'pos'], impNode.at[node2dVec[1][valIndex], 'pos']))
                dist2 = np.linalg.norm(
                    np.subtract(impNode.at[impElement['nodeJ'].iat[item], 'pos'], impNode.at[node2dVec[2][valIndex], 'pos']))
                distTot = dist1 + dist2

                addMassTremuri['massTremuri'].iat[impNode.index.get_loc(impElement['nodeJ'].iat[item])] = \
                    addMassTremuri['massTremuri'].iat[impNode.index.get_loc(impElement['nodeJ'].iat[item])] + \
                    np.dot(np.concatenate((abs(xAxis.transpose()) + abs(yAxis.transpose()), [0, 0, 0])), elementMass * 0.5)

                addMassTremuri['massTremuri'].iat[impNode.index.get_loc(node2dVec[1][valIndex])] = \
                    addMassTremuri['massTremuri'].iat[impNode.index.get_loc(node2dVec[1][valIndex])] + \
                    np.dot(np.concatenate((abs(zAxis.transpose()), [0, 0, 0])), (elementMass * 0.5) * (dist2 / distTot))
                addMassTremuri['massTremuri'].iat[impNode.index.get_loc(node2dVec[2][valIndex])] = \
                    addMassTremuri['massTremuri'].iat[impNode.index.get_loc(node2dVec[2][valIndex])] + \
                    np.dot(np.concatenate((abs(zAxis.transpose()), [0, 0, 0])), (elementMass * 0.5) * (dist1 / distTot))

    # compute total model mass (and eccentricity?)
    totMass = [0, 0, 0]
    barycenter = np.matrix([0, 0, 0]).transpose()
    for item in np.arange(totalNodes):
        totMass = totMass + addMassTremuri['massTremuri'].iat[item][0:3]
        barycenter = barycenter + [[np.dot(impNode['x'].iat[item], addMassTremuri['massTremuri'].iat[item][2])],
                                   [np.dot(impNode['y'].iat[item], addMassTremuri['massTremuri'].iat[item][2])],
                                   [np.dot(impNode['z'].iat[item], addMassTremuri['massTremuri'].iat[item][2])]]

    barycenter = np.divide(barycenter, totMass)

    print('Total Mass, x: ' + '{:.1f}'.format(totMass[0]))
    print('Total Mass, y: ' + '{:.1f}'.format(totMass[1]))
    print('Total Mass, z: ' + '{:.1f}'.format(totMass[2]))

    print('Centroid x: ' + '{:.3f}'.format(np.array(barycenter[0])[0][0]))
    print('Centroid y: ' + '{:.3f}'.format(np.array(barycenter[1])[0][0]))
    print('Centroid z: ' + '{:.3f}'.format(np.array(barycenter[2])[0][0]))

    # write masses
    fid.write("#NODAL MASSES ------------------------------------------------------------ \n")
    fid.write("#       tag         X         Y         Z        RX        RY        RZ \n")
    for item in np.arange(totalNodes):
        if massDistribution == "Tremuri":
            if np.linalg.norm(addMassTremuri['massTremuri'].iat[item]) > 0:
                fid.write("mass " + '{:6d}'.format(impNode.index[item]) +
                          '{:10.1f}'.format(addMassTremuri['massTremuri'].iat[item][0]) +
                          '{:10.1f}'.format(addMassTremuri['massTremuri'].iat[item][1]) +
                          '{:10.1f}'.format(addMassTremuri['massTremuri'].iat[item][2]) +
                          '{:10.1f}'.format(addMassTremuri['massTremuri'].iat[item][3]) +
                          '{:10.1f}'.format(addMassTremuri['massTremuri'].iat[item][4]) +
                          '{:10.1f}'.format(addMassTremuri['massTremuri'].iat[item][5]) + " \n")
        else:
            if np.linalg.norm(addMass['mass'].iat[item]) > 0:
                fid.write("mass " + '{:6d}'.format(impNode.index[item]) +
                          '{:10.1f}'.format(addMass['mass'].iat[item][0]) +
                          '{:10.1f}'.format(addMass['mass'].iat[item][1]) +
                          '{:10.1f}'.format(addMass['mass'].iat[item][2]) +
                          '{:10.1f}'.format(addMass['mass'].iat[item][3]) +
                          '{:10.1f}'.format(addMass['mass'].iat[item][4]) +
                          '{:10.1f}'.format(addMass['mass'].iat[item][5]) + " \n")
    fid.write("#END MASSES ------------------------------------------------------------ \n")

    # close model file
    fid.write('puts "Model defined." \n\n\n')
    fid.close()
    tmp_filesToRun.at['0', 'fileName'] = join(TCLfilePath, tclFileName)
    tmp_filesToRun.at['0', 'outputFiles'] = np.nan
    tmp_filesToRun_list.append(tmp_filesToRun.values.tolist()[0])

    # Analysis files
    nFiles = 1
    totalAnalyses = impAnalysis['type'].count()
    maxMacroelement = impElement.groupby(['type']).get_group('Macroelement3d')['type'].count()  # count the number of macroelements
    for item in np.arange(totalAnalyses):
        nFiles = nFiles + 1
        outFileName = projectName + "_" + str(item + 1) + "_" + impAnalysis['type'].iat[item] + ".tcl"
        fout = open(join(TCLfilePath, outFileName), "w+")
        if impAnalysis['type'].iat[item] == "Modal":
            # modal analysis
            fout.write("# -------------------------------------------- \n")
            fout.write("# Modal Analysis ----------------------------- \n")
            fout.write("# -------------------------------------------- \n\n")
            fout.write("set numModes " + '{:d}'.format(impAnalysis['nModes'].iat[item]) + "; \n\n")

            fout.write("system BandGeneral \n")
            fout.write("numberer RCM \n")
            fout.write("constraints Transformation \n\n")
            fout.write("# set recorders for modal analysis \n")

            for kMode in np.arange(impAnalysis['nModes'].iat[item]):
                fout.write('recorder Node -file "' + OUTPUTfilePath + projectName + '_mode ' + str(kMode + 1) + '.out' + '" -nodeRange ' + '{:d}'.format(min(impNode.index)) + ' ' + '{:d}'.format(max(impNode.index)) + ' -dof 1 2 3 4 5 6 "eigen ' + '{:d}'.format(kMode + 1))

            fout.write("\n\n")

            fout.write("# eigenvalues analysis \n")
            fout.write("set lambda [eigen  $numModes]; \n\n")

            fout.write("set omega {} \n")
            fout.write("set f {} \n")
            fout.write("set T {} \n\n")

            fout.write("foreach lam $lambda { \n")
            fout.write("  lappend omega [expr sqrt($lam)] \n")
            fout.write("  lappend f [expr sqrt($lam)/(2.*$pi)] \n")
            fout.write("  lappend T [expr (2.*$pi)/sqrt($lam)] \n")
            fout.write("} \n")

            fout.write("# write output \n")
            fout.write('set period "' + OUTPUTfilePath + projectName + '"_periods.out \n')
            fout.write('set Periods [open $period "w"] \n')
            fout.write("set ind 0; \n")
            fout.write("foreach tt $T {  \n")
            fout.write("   set toPlot    [lindex $f  $ind]		 \n")
            fout.write('   puts $Periods " $tt $toPlot" \n')
            fout.write("   set ind [expr $ind+1];	 \n")
            fout.write("	 puts [expr $tt]  \n")
            fout.write("}  \n")
            fout.write("close $Periods  \n\n")

            fout.write("record \n\n")

            fout.write('puts "Eigenvalues analysis completed." \n')
            fout.write("remove recorders; \n\n")

            fout.close()
            tmp_filesToRun.at['0', 'fileName'] = join(TCLfilePath, outFileName)
            tmp_filesToRun.at['0', 'outputFiles'] = []
            for kMode in np.arange(impAnalysis['nModes'].iat[item]):
                tmp_filesToRun.at['0', 'outputFiles'].append(OUTPUTfilePath + projectName + '_mode ' + str(kMode + 1) + '.out')
            tmp_filesToRun.at['0', 'outputFiles'].append(OUTPUTfilePath + projectName + "_periods.out")
            tmp_filesToRun_list.append(tmp_filesToRun.values.tolist()[0])
        elif impAnalysis['type'].iat[item] == "selfWeight":
            # vertical load analysis
            accVec = [[impAnalysis['accVec1'].iat[item]], [impAnalysis['accVec2'].iat[item]], [impAnalysis['accVec3'].iat[item]]]

            fout.write("# -------------------------------------------- \n")
            fout.write("# Self Weight analysis------------------------ \n")
            fout.write("# -------------------------------------------- \n\n")

            fout.write("# set recorders \n")
            fout.write('recorder Node -file "' + OUTPUTfilePath + 'analysis' + str(item + 1) + '_' + impAnalysis['type'].iat[item] + '_allDispl.out' + '"  -time -nodeRange ' + '{:d}'.format(min(impNode.index)) + ' ' + '{:d}'.format(max(impNode.index)) + ' -dof 1 2 3 4 5 6 disp\n')
            fout.write('recorder Node -file "' + OUTPUTfilePath + 'analysis' + str(item + 1) + '_' + impAnalysis['type'].iat[item] + '_allForce.out' + '"  -time -nodeRange ' + '{:d}'.format(min(impNode.index)) + ' ' + '{:d}'.format(max(impNode.index)) + ' -dof 1 2 3 4 5 6 reaction \n\n')

            fout.write('recorder Element -file "' + OUTPUTfilePath + 'analysis' + str(item + 1) + '_' + impAnalysis['type'].iat[item] + '_allElementForce.out' + '"  -time -eleRange 1 ' + '{:d}'.format(maxMacroelement) + ' localForce \n')
            fout.write('recorder Element -file "' + OUTPUTfilePath + 'analysis' + str(item + 1) + '_' + impAnalysis['type'].iat[item] + '_allElementDrift.out' + '"  -time -eleRange 1 ' + '{:d}'.format(maxMacroelement) + ' drift \n')
            fout.write('recorder Element -file "' + OUTPUTfilePath + 'analysis' + str(item + 1) + '_' + impAnalysis['type'].iat[item] + '_allElementShearDamage.out' + '"  -time -eleRange 1 ' + '{:d}'.format(maxMacroelement) + ' shear state \n\n')

            fout.write("# Define constant axial load\n")
            fout.write("#NODAL LOADS------------------------------------------------------------ \n")
            fout.write('pattern Plain ' + '{:d}'.format(item + 1) + ' "Linear" {\n')

            totalLoad = [0, 0, 0, 0, 0, 0]

            for nodeItem in np.arange(totalNodes):
                if np.linalg.norm(addloadZ['load_Z'].iat[nodeItem]) > 0:
                    nodeLoad = np.dot(accVec[0][0], addloadX['load_X'].iat[nodeItem]) + np.dot(accVec[1][0], addloadY['load_Y'].iat[nodeItem]) + np.dot(accVec[2][0], addloadZ['load_Z'].iat[nodeItem])
                    totalLoad = totalLoad + nodeLoad

                    fout.write("    load " + '{:6d}'.format(impNode.index[nodeItem]) + '{:10.3f}'.format(1e-3 * nodeLoad[0][0]) + 'e3' + '{:10.3f}'.format(1e-3 * nodeLoad[0][1]) + 'e3' + '{:10.3f}'.format(1e-3 * nodeLoad[0][2]) + 'e3' + '{:10.3f}'.format(1e-3 * nodeLoad[0][3]) + 'e3' + '{:10.3f}'.format(1e-3 * nodeLoad[0][4]) + 'e3' + '{:10.3f}'.format(1e-3 * nodeLoad[0][5]) + 'e3 \n')

            for elementItem in np.arange(totalElements):
                if impElement['type'].iat[elementItem] == "Macroelement3d":
                    if massDistribution == "Standard" or massDistribution == "Consistent":
                        fout.write("    eleLoad -ele " + '{:d}'.format(elementItem + 1) + " -type -selfWeight" + '{:7.3f}'.format(accVec[0][0]) + '{:7.3f}'.format(accVec[1][0]) + '{:7.3f}'.format(accVec[2][0]) + ' \n')

            fout.write("}\n")
            fout.write("#END LOADS ------------------------------------------------------------ \n\n")

            fout.write("#TOTAL NODAL LOADS (excluding element loads) : " + '{:.3f}'.format(1e-3 * totalLoad[0][0]) + 'e+3  ' + '{:.3f}'.format(1e-3 * totalLoad[0][1]) + 'e+3  ' + '{:2.3f}'.format(1e-3 * totalLoad[0][2]) + 'e+3  ' + '{:2.3f}'.format(1e-3 * totalLoad[0][3]) + 'e+3  ' + '{:2.3f}'.format(1e-3 * totalLoad[0][4]) + 'e+3  ' + '{:2.3f}'.format(1e-3 * totalLoad[0][5]) + 'e+3  ' + ' \n\n')

            fout.write("# Define analysis parameters\n")
            fout.write("wipeAnalysis\n")
            fout.write("system BandGeneral;  \n")
            fout.write("numberer RCM \n")
            fout.write("constraints Transformation \n\n")

            fout.write("integrator LoadControl 1 " + '{:d}'.format(impAnalysis['nSteps'].iat[item]) + ' \n')
            fout.write("test NormUnbalance " + '{:3.2e}'.format(impAnalysis['tol'].iat[item]) + ' ' + '{:d}'.format(impAnalysis['maxStep'].iat[item]) + " 1\n\n")
            fout.write("algorithm Newton\n")
            fout.write("analysis Static\n")

            fout.write("analyze 1 \n\n")

            fout.write("#set self weight as constant load and reset the time to 0\n")
            fout.write("loadConst -time 0.0 \n\n")

            fout.write('puts "Self Weight analysis completed." \n')
            fout.write("remove recorders; \n\n")

            fout.close()
            tmp_filesToRun.at['0', 'fileName'] = join(TCLfilePath, outFileName)
            tmp_filesToRun.at['0', 'outputFiles'] = []
            tmp_filesToRun.at['0', 'outputFiles'].append(OUTPUTfilePath + 'analysis' + str(item) + "_" + impAnalysis['type'].iat[item] + "_allDispl.out")
            tmp_filesToRun.at['0', 'outputFiles'].append(OUTPUTfilePath + 'analysis' + str(item) + "_" + impAnalysis['type'].iat[item] + "_allForce.out")
            tmp_filesToRun_list.append(tmp_filesToRun.values.tolist()[0])
        elif impAnalysis['type'].iat[item] == "PushoverRectangular":
            # rectangular pushover analysis
            direction = impAnalysis['DOF'].iat[item]
            fout.write("# -------------------------------------------- \n")
            fout.write("# Pushover, rectangular force pattern -------- \n")
            fout.write("# -------------------------------------------- \n\n")

            fout.write("# set recorders \n")
            fout.write('recorder Node -file ' + OUTPUTfilePath + '"analysis' + str(item + 1) + '_' + impAnalysis['type'].iat[item] + '_allDispl.out' + '"  -time -nodeRange ' + '{:d}'.format(min(impNode.index)) + ' ' + '{:d}'.format(max(impNode.index)) + ' -dof 1 2 3 4 5 6 disp\n')
            fout.write('recorder Node -file ' + OUTPUTfilePath + '"analysis' + str(item + 1) + '_' + impAnalysis['type'].iat[item] + '_allForce.out' + '"  -time -nodeRange ' + '{:d}'.format(min(impNode.index)) + ' ' + '{:d}'.format(max(impNode.index)) + ' -dof 1 2 3 4 5 6 reaction \n\n')

            fout.write('recorder Element -file ' + OUTPUTfilePath + '"analysis' + str(item + 1) + '_' + impAnalysis['type'].iat[item] + '_allElementForce.out' + '"  -time -eleRange 1 ' + '{:d}'.format(maxMacroelement) + ' localForce \n')
            fout.write('recorder Element -file ' + OUTPUTfilePath + '"analysis' + str(item + 1) + '_' + impAnalysis['type'].iat[item] + '_allElementDrift.out' + '"  -time -eleRange 1 ' + '{:d}'.format(maxMacroelement) + ' drift \n')
            fout.write('recorder Element -file ' + OUTPUTfilePath + '"analysis' + str(item + 1) + '_' + impAnalysis['type'].iat[item] + '_allElementShearDamage.out' + '"  -time -eleRange 1 ' + '{:d}'.format(maxMacroelement) + ' shear state \n\n')

            fout.write("# Define lateral force pattern \n")
            fout.write("#NODAL LOADS------------------------------------------------------------ \n")
            fout.write('pattern Plain ' + '{:d}'.format(item + 1) + ' "Linear" {\n')

            for nodeItem in np.arange(totalNodes):
                if pushoverPattern == "Tremuri":
                    if not impNode.index[nodeItem] in impFixConstraint['node']:
                        if direction == "ux":
                            if addMassTremuri['massTremuri'].iat[nodeItem][0] > 0.1:
                                fout.write("    load " + '{:6d}'.format(impNode.index[nodeItem]) + ' ' + '{:9.3f}'.format(9.81 * 1e-3 * addMassTremuri['massTremuri'].iat[nodeItem][0] * 1) + 'e3 ' + '{:9.3f}'.format(9.81 * 1e-3 * addMassTremuri['massTremuri'].iat[nodeItem][0] * 0) + 'e3 ' + '{:9.3f}'.format(9.81 * 1e-3 * addMassTremuri['massTremuri'].iat[nodeItem][0] * 0) + 'e3 ' + '{:9.3f}'.format(9.81 * 1e-3 * addMassTremuri['massTremuri'].iat[nodeItem][0] * 0) + 'e3 ' + '{:9.3f}'.format(9.81 * 1e-3 * addMassTremuri['massTremuri'].iat[nodeItem][0] * 0) + 'e3 ' + '{:9.3f}'.format(9.81 * 1e-3 * addMassTremuri['massTremuri'].iat[nodeItem][0] * 0) + 'e3 \n')
                        else:
                            if addMassTremuri['massTremuri'].iat[nodeItem][0] > 0.1:
                                fout.write("    load " + '{:6d}'.format(impNode.index[nodeItem]) + ' ' + '{:9.3f}'.format(9.81 * 1e-3 * addMassTremuri['massTremuri'].iat[nodeItem][1] * 0) + 'e3 ' + '{:9.3f}'.format(9.81 * 1e-3 * addMassTremuri['massTremuri'].iat[nodeItem][1] * 1) + 'e3 ' + '{:9.3f}'.format(9.81 * 1e-3 * addMassTremuri['massTremuri'].iat[nodeItem][1] * 0) + 'e3 ' + '{:9.3f}'.format(9.81 * 1e-3 * addMassTremuri['massTremuri'].iat[nodeItem][1] * 0) + 'e3 ' + '{:9.3f}'.format(9.81 * 1e-3 * addMassTremuri['massTremuri'].iat[nodeItem][1] * 0) + 'e3 ' + '{:9.3f}'.format(9.81 * 1e-3 * addMassTremuri['massTremuri'].iat[nodeItem][1] * 0) + 'e3 \n')
                else:
                    if not impNode.index[nodeItem] in impFixConstraint['node']:
                        if direction == "ux":
                            if np.linalg.norm(addloadX['load_X'].iat[nodeItem]) > 0:
                                fout.write("    load " + '{:6d}'.format(impNode.index[nodeItem]) + ' ' + '{:9.3f}'.format(9.81 * 1e-3 * addloadX['load_X'].iat[nodeItem][0]) + 'e3 ' + '{:9.3f}'.format(9.81 * 1e-3 * addloadX['load_X'].iat[nodeItem][1]) + 'e3 ' + '{:9.3f}'.format(9.81 * 1e-3 * addloadX['load_X'].iat[nodeItem][2]) + 'e3 ' + '{:9.3f}'.format(9.81 * 1e-3 * addloadX['load_X'].iat[nodeItem][3]) + 'e3 ' + '{:9.3f}'.format(9.81 * 1e-3 * addloadX['load_X'].iat[nodeItem][4]) + 'e3 ' + '{:9.3f}'.format(9.81 * 1e-3 * addloadX['load_X'].iat[nodeItem][5]) + 'e3 \n')
                        else:
                            if np.linalg.norm(addloadY['load_Y'].iat[nodeItem]) > 0:
                                fout.write("    load " + '{:6d}'.format(impNode.index[nodeItem]) + ' ' + '{:9.3f}'.format(9.81 * 1e-3 * addloadY['load_Y'].iat[nodeItem][0]) + 'e3 ' + '{:9.3f}'.format(9.81 * 1e-3 * addloadY['load_Y'].iat[nodeItem][1]) + 'e3 ' + '{:9.3f}'.format(9.81 * 1e-3 * addloadY['load_Y'].iat[nodeItem][2]) + 'e3 ' + '{:9.3f}'.format(9.81 * 1e-3 * addloadY['load_Y'].iat[nodeItem][3]) + 'e3 ' + '{:9.3f}'.format(9.81 * 1e-3 * addloadY['load_Y'].iat[nodeItem][4]) + 'e3 ' + '{:9.3f}'.format(9.81 * 1e-3 * addloadY['load_Y'].iat[nodeItem][5]) + 'e3 \n')

            for elementItem in np.arange(totalElements):
                if impElement['type'].iat[elementItem] == "Macroelement3d":
                    if massDistribution == "Consistent":
                        if direction == "ux":
                            fout.write("    eleLoad -ele " + '{:d}'.format(elementItem + 1) + " -type -selfWeight" + '{:7.3f}'.format(9.81) + '{:7.3f}'.format(0) + '{:7.3f}'.format(0) + ' \n')
                        else:
                            fout.write("    eleLoad -ele " + '{:d}'.format(elementItem + 1) + " -type -selfWeight" + '{:7.3f}'.format(0) + '{:7.3f}'.format(9.81) + '{:7.3f}'.format(0) + ' \n')

            fout.write("}\n")
            fout.write("#END LOADS ------------------------------------------------------------ \n\n")
            fout.write("#Note: The sum of horizontal forces is equal to the weight of the building.\n")
            fout.write("#The time variable of the analysis is therefore directly the base shear ratio H/W \n\n\n")

            fout.write("# Define analysis parameters\n")
            fout.write("set controlled_node   " + '{:d}'.format(impAnalysis['controlNode'].iat[item] + '\n'))

            if impAnalysis['DOF'].iat[item] == "ux":
                fout.write("set controlled_dof    1\n\n")
            else:
                fout.write("set controlled_dof    2\n\n")

            fout.write("set incr " + '{:f}'.format(impAnalysis['maxDisp'].iat[item] / impAnalysis['nSteps'].iat[item]) + '\n')
            fout.write("set maxDispl  " + '{:f}'.format(impAnalysis['maxDisp'].iat[item]) + "\n\n")
            fout.write("set substepIfNotConverged  1.\n\n")

            fout.write("set currentDisp [nodeDisp $controlled_node $controlled_dof]\n\n")
            fout.write("set nSteps [expr int(abs(($maxDispl-$currentDisp)/$incr))]\n\n")

            fout.write("constraints Plain\n")
            fout.write("numberer RCM \n")
            fout.write("system BandGeneral; \n")
            fout.write("analysis Static\n\n")

            fout.write("record;\n\n")

            fout.write("#wipeAnalysis\n")
            fout.write("while {$nSteps>=1} {\n")
            fout.write("    set nSteps [expr int(abs(($maxDispl-$currentDisp)/$incr))]\n")
            fout.write("    if ($nSteps<1) {\n")
            fout.write("       break;\n")
            fout.write("    }\n")
            fout.write("    test NormUnbalance " + '{:2.2e}'.format(impAnalysis['tol'].iat[item] * totMass[0] * 9.81) + " " + '{:d}'.format(35) + " " + '{:d}'.format(2) + "\n")
            fout.write("    algorithm Newton \n")
            fout.write("    integrator    DisplacementControl     $controlled_node      $controlled_dof     $incr\n")
            fout.write("    set ok [analyze $nSteps]\n\n")

            fout.write("    if ($ok!=0) {\n")
            fout.write("        test NormUnbalance " + '{:2.2e}'.format(impAnalysis['tol'].iat[item] * totMass[0] * 9.81) + '{:d}'.format(impAnalysis["maxStep"].iat[item]) + '{:d}'.format(5) + "\n")
            fout.write("        algorithm Newton -initial\n")
            fout.write("        integrator    DisplacementControl     $controlled_node      $controlled_dof     [expr $incr/$substepIfNotConverged] \n")
            fout.write("        set ok [analyze [expr int($substepIfNotConverged)]]\n")
            fout.write("    }\n")
            fout.write("    set currentDisp [nodeDisp $controlled_node $controlled_dof]\n")
            fout.write('    puts [format "Continues from displacement %%.2f mm" [expr $currentDisp*1000.]]; \n\n')

            fout.write("}\n\n")

            fout.write("remove loadPattern 3\n\n")

            fout.write('puts "Rectangular pushover direction ux completed." \n\n')
            fout.write("remove recorders; \n\n")

            fout.close()
            tmp_filesToRun.at['0', 'fileName'] = join(TCLfilePath, outFileName)
            tmp_filesToRun.at['0', 'outputFiles'] = []
            tmp_filesToRun.at['0', 'outputFiles'].append(OUTPUTfilePath + 'analysis' + str(item) + "_" + impAnalysis['type'].iat[item] + "_allDispl.out")
            tmp_filesToRun.at['0', 'outputFiles'].append(OUTPUTfilePath + 'analysis' + str(item) + "_" + impAnalysis['type'].iat[item] + "_allForce.out")
            tmp_filesToRun_list.append(tmp_filesToRun.values.tolist()[0])
        elif impAnalysis['type'].iat[item] == "Dynamic":
            # dynamic analysis
            Rayleigh = [float(impAnalysis['rayleigh1'].iat[item]), float(impAnalysis['rayleigh2'].iat[item])]
            direction = impAnalysis['DOF'].iat[item]
            fout.write("# -------------------------------------------------------------------------------------------- \n")
            fout.write("# Dynamic analysis, direction " + direction + " \n")
            GMplace = impAnalysis['groundMotion'].iat[item].find("/")
            GMlen = len(impAnalysis['groundMotion'].iat[item])
            GMfile = impAnalysis['groundMotion'].iat[item][GMplace + 1:GMlen]
            groundMotionFullPath = join(motionFilePath, GMfile)
            fout.write("# Ground motion: " + groundMotionFullPath + "  \n")
            fout.write("# Duration: " + '{:.2f}'.format(len(impAnalysis['scaledGroundMotion'].iat[item]) * impAnalysis['dt'].iat[item]) + " s\n")
            fout.write("# Scale factor: " + '{:.4f}'.format(impAnalysis['scaleFactor'].iat[item]) + "\n")
            fout.write("# PGA: " + '{:.3f}'.format(impAnalysis['PGA'].iat[item] / 9.81) + " g  \n")
            fout.write("# -------------------------------------------------------------------------------------------- \n\n")

            fout.write("# set recorders \n")
            fout.write('recorder Node -file "' + OUTPUTfilePath + 'analysis' + str(item + 1) + '_' + impAnalysis['type'].iat[item] + '_allDispl.out"' + '  -time -nodeRange ' + '{:d}'.format(min(impNode.index)) + ' ' + '{:d}'.format(max(impNode.index)) + ' -dof 1 2 3 4 5 6 disp\n')
            fout.write('recorder Node -file "' + OUTPUTfilePath + 'analysis' + str(item + 1) + '_' + impAnalysis['type'].iat[item] + '_allForce.out"' + '  -time -nodeRange ' + '{:d}'.format(min(impNode.index)) + ' ' + '{:d}'.format(max(impNode.index)) + ' -dof 1 2 3 4 5 6 reaction\n\n')

            fout.write('recorder Element -file "' + OUTPUTfilePath + 'analysis' + str(item + 1) + '_' + impAnalysis['type'].iat[item] + '_allElementForce.out' + '"  -time -eleRange 1 ' + '{:d}'.format(maxMacroelement) + ' localForce \n')
            fout.write('recorder Element -file "' + OUTPUTfilePath + 'analysis' + str(item + 1) + '_' + impAnalysis['type'].iat[item] + '_allElementDrift.out' + '"  -time -eleRange 1 ' + '{:d}'.format(maxMacroelement) + ' drift \n')
            fout.write('recorder Element -file "' + OUTPUTfilePath + 'analysis' + str(item + 1) + '_' + impAnalysis['type'].iat[item] + '_allElementShearDamage.out' + '"  -time -eleRange 1 ' + '{:d}'.format(maxMacroelement) + ' shear state \n\n')
            fout.write("# Define dynamic excitation\n")
            fout.write("# ----------------------------------------------\n")
            fout.write("set dt_GM  " + '{:f}'.format(impAnalysis['dt'].iat[item]) + ";\n")
            fout.write("set currentTime -" + '{:f}'.format(impAnalysis['dt'].iat[item]) + "\n")
            fout.write("set currentTime 0.0;\n")
            fout.write("loadConst -time $currentTime\n\n")

            fout.write('set groundMotionPath "' + groundMotionFullPath + '"; \n')
            if impAnalysis['DOF'].iat[item] == "ux":
                fout.write("set direction    1 \n\n")
            else:
                fout.write("set direction    2 \n\n")
            fout.write("timeSeries Path " + '{:d}'.format(item + 1) + "  -dt $dt_GM  -filePath $groundMotionPath  -factor " + '{:f}'.format(impAnalysis['scaleFactor'].iat[item]) + '\n')
            fout.write("#                           $patternTag $dir -accel $tsTag <-vel0 $vel0> <-fact $cFactor>\n")
            fout.write("pattern UniformExcitation   " + '{:d}'.format(item + 1) + "    $direction   -accel " + '{:d}'.format(item + 1) + " \n\n\n")

            fout.write("# Define damping model\n")
            fout.write("# ----------------------------------------------\n")
            fout.write("set betaKinitial    1.0;\n")
            fout.write("set betaKcurrent    0.0;\n")
            fout.write("set betaKcommitted  0.0;\n\n")
            if csi < 0:
                fout.write("# User defined. Alpha (mass proportional) " + '{:f}'.format(Rayleigh[0]) + ", beta (initial stiffness proprotional) " + '{:f}'.format(Rayleigh[1]) + "\n")
                fout.write("rayleigh     " + '{:f}'.format(Rayleigh[0]) + "      [expr $betaKcurrent* " + '{:f}'.format(Rayleigh[1]) + "]     [expr $betaKinitial* " + '{:f}'.format(Rayleigh[1]) + "]    [expr $betaKcommitted* " + '{:f}'.format(Rayleigh[1]) + "];\n\n\n")
            else:
                fout.write("# Rayleigh damping, " + '{:f}'.format(csi * 100) + " on the first two frequencies\n")
                fout.write("set csi  " + '{:f}'.format(csi) + "\n")
                fout.write("set pi  " + '{:f}'.format(math.pi) + "\n")
                fout.write("set f1 [expr [lindex $f 0] ];\n")
                fout.write("set f2 [expr [lindex $f 1] ];\n\n")

                fout.write("set beta   [expr 2.0*$csi / (2.*$pi*$f1 + 2.*$pi*$f2)] ;\n")
                fout.write("set alpha  [expr $beta*(2.*$pi*$f1)*(2.*$pi*$f2)] ;\n\n")

                fout.write('puts [format "Rayleigh damping coeffcients, alpha %%f, beta %%f" $alpha $beta]; \n\n')
                fout.write("rayleigh     $alpha    [expr $betaKinitial*$beta]     [expr $betaKcurrent*$beta]    [expr $betaKcommitted*$beta];\n\n\n")

            fout.write("# Create the analysis\n")
            fout.write("# ----------------------------------------------\n")
            fout.write("#wipeAnalysis\n")
            fout.write("constraints Transformation\n")
            fout.write("numberer RCM \n")
            fout.write("system SparseGEN; \n")
            fout.write("integrator Newmark 0.5 0.25 \n")
            fout.write("analysis Transient\n\n")

            fout.write("set maxTime  " + '{:f}'.format(impAnalysis['nSteps'].iat[item] * impAnalysis['dt'].iat[item]) + "\n")
            fout.write("set subd " + '{:f}'.format(impAnalysis['subd'].iat[item]) + ";\n")
            fout.write("set incr " + '{:f}'.format(impAnalysis['dt'].iat[item] / impAnalysis['subd'].iat[item]) + ";\n")
            fout.write("set substepIfNotConverged  1.\n\n")

            fout.write("while {$currentTime<$maxTime} {\n")
            fout.write("    set nSteps [expr int(abs($maxTime-$currentTime)/$incr)]\n")
            fout.write("    if ($nSteps<1) {\n")
            fout.write("       break;\n")
            fout.write("    }\n")
            fout.write("    test NormUnbalance " + '{:2.2e}'.format(impAnalysis['tol'].iat[item] * totMass[0] * 9.81) + " " + '{:d}'.format(35) + " " + '{:d}'.format(2) + "\n")
            fout.write("    algorithm Newton \n\n")

            fout.write("    set ok  [analyze $nSteps  $incr]\n\n")

            fout.write("    if ($ok!=0) {\n")
            fout.write("        test NormUnbalance " + '{:2.2e}'.format(impAnalysis['tol'].iat[item] * totMass[0] * 9.81) + " " + '{:d}'.format(impAnalysis['maxStep'].iat[item]) + " " + '{:d}'.format(5) + "\n")
            fout.write("        algorithm Newton -initial\n")
            fout.write("        set ok  [analyze [expr int($substepIfNotConverged)]  [expr $incr/$substepIfNotConverged]]\n\n")
            fout.write("    }\n")
            fout.write("    set currentTime [getTime]\n")
            fout.write('    puts [format "Continues from time %.3f s" $currentTime]; \n\n')

            fout.write("}\n\n")

            fout.write("after 5000\n\n")

            fout.write("remove loadPattern " + '{:d}'.format(item + 1) + "\n\n")

            if freeVibrationTime > 0:
                fout.write('puts "Adding ' + '{:.3f}'.format(freeVibrationTime) + ' s of free vibrations..."\n\n')
                fout.write("pattern UniformExcitation   " + '{:d}'.format(item + 1) + "    $direction   -accel " + '{:d}'.format(item + 1) + " -fact 0.0 \n")

                fout.write("set maxTime  " + '{:f}'.format(impAnalysis['nSteps'].iat[item] * impAnalysis['dt'].iat[item] + freeVibrationTime) + "\n")
                fout.write("system SparseGEN; \n")

                fout.write("while {$currentTime<$maxTime} {\n")
                fout.write("    set nSteps [expr int(abs($maxTime-$currentTime)/$incr)]\n")
                fout.write("    if ($nSteps<1) {\n")
                fout.write("       break;\n")
                fout.write("    }\n")
                fout.write("    test NormUnbalance " + '{:2.2e}'.format(impAnalysis['tol'].iat[item] * totMass[0] * 9.81) + '{:d}'.format(35) + '{:d}'.format(2))
                fout.write("    algorithm Newton \n\n")

                fout.write("    set ok  [analyze $nSteps  $incr]\n\n")

                fout.write("    if ($ok!=0) {\n")
                fout.write("        test NormUnbalance " + '{:2.2e}'.format(impAnalysis['tol'].iat[item] * totMass[0] * 9.81) + " " + '{:d}'.format(impAnalysis['maxStep'].iat[item]) + '{:d}'.format(5) + "\n")
                fout.write("        algorithm Newton -initial\n")
                fout.write("        set ok  [analyze [expr int($substepIfNotConverged)]  [expr $incr/$substepIfNotConverged]]\n\n")

                fout.write("    }\n")
                fout.write("    set currentTime [getTime]\n")
                fout.write('    puts [format "Continues from time %%.3f s" $currentTime]; \n\n')

                fout.write("}\n\n")

                fout.write("after 5000\n\n")

            fout.write('puts "Dynamic analysis completed. (' + impAnalysis['groundMotion'].iat[item] + ', scale factor ' + '{:f}'.format(impAnalysis['scaleFactor'].iat[item]) + ', PGA ' + '{:f}'.format(impAnalysis['PGA'].iat[item]) + ', direction ' + direction + '" \n\n')
            fout.write("remove recorders; \n\n")

            fout.write("after 5000\n\n")

            fout.close()
            tmp_filesToRun.at['0', 'fileName'] = join(TCLfilePath, outFileName)
            tmp_filesToRun.at['0', 'outputFiles'] = []
            tmp_filesToRun.at['0', 'outputFiles'].append(OUTPUTfilePath + 'analysis' + str(item) + "_" + impAnalysis['type'].iat[item] + "_allDispl.out")
            tmp_filesToRun.at['0', 'outputFiles'].append(OUTPUTfilePath + 'analysis' + str(item) + "_" + impAnalysis['type'].iat[item] + "_allForce.out")
            tmp_filesToRun_list.append(tmp_filesToRun.values.tolist()[0])

    # write batch to run
    filesToRun = pd.DataFrame(tmp_filesToRun_list, columns=['fileName', 'outputFiles'])
    outFileName = projectName + "_batch.tcl"
    fid = open(join(TCLfilePath, outFileName), "w+")
    for kFile in np.arange(nFiles):
        if kFile == 0:
            fid.write("#load Model \n")
        else:
            fid.write("#execute analysis: " + impAnalysis['type'].iat[kFile - 1] + " \n")
        fid.write("source " + filesToRun['fileName'].iat[kFile] + ";\n\n")

    fid.write('puts "---------------------------------------------------------------" \n')
    fid.write('puts "All analyses completed-----------------------------------------" \n')
    fid.write('puts "---------------------------------------------------------------" \n')

    fid.write("wipe \n")
    fid.write("exit \n")

    fid.close()

    print("--- %s seconds ---" % (time.time() - startTime))

    # write the opensees batch file
    fopBAT = open(batchFileName, "w+")
    fopBAT.write("echo off\n")
    fopBAT.write("cls\n")
    fopBAT.write("echo Starting OpenSees..\n")
    fopBAT.write("echo off\n")
    outFileName = projectName + "_batch.tcl"
    fopBAT.write('"C:/Program Files/Tcl/bin/openSees.exe" ' + '"' + join(TCLfilePath, outFileName) + '"\n')
    # fopBAT.write("pause\n")
    fopBAT.close()

    # run opensees
    totalPath = cfilePath + "\\" + tclFileName
    #subprocess.call([batchFileName])
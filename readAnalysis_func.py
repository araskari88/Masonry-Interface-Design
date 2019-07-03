import numpy as np
import pandas as pd
import time

completeFileLocation4 = ''
analysis = ''
analysisType = ''
nodeList = ''
display_dt = ""
ultimate_time = ""
dt = ""

def read_anlz_func():
    global node_disps
    start_time = time.time()  # just to track the time passed for going through each module
    open_file = open(completeFileLocation4, "r")  # Open the Tremuri file
    input_file = open_file.read()  # Read the Tremuri file

    # read the lines of the input file
    lines = input_file.splitlines()  # split the lines of the input file
    open_file.close()  # close the input file after reading its data

    num_dt = len(lines)

    if analysisType == 'selfWeight':
        node_disps = pd.DataFrame(columns=['Node', 'Disp'], index=[i for i in np.arange(len(nodeList))])
    elif analysisType == 'Dynamic':
        node_disps = pd.DataFrame(columns=['Time', 'Node', 'Disp'], index=[i for i in np.arange(len(nodeList) * len(lines))])

    if analysisType == 'selfWeight':
        params = lines[0].split()
        for node_number in np.arange(len(nodeList)):
            node_disps['Node'].iat[node_number] = nodeList[node_number]
            node_disps['Disp'].iat[node_number] = [float(params[1 + node_number * 6]), float(params[2 + node_number * 6]),
                                                   float(params[3 + node_number * 6]), float(params[4 + node_number * 6]),
                                                   float(params[5 + node_number * 6]), float(params[6 + node_number * 6])]
    elif analysisType == 'Dynamic':
        lineCounter = 0
        for line in lines:
            params = line.split()
            for node_number in np.arange(len(nodeList)):
                node_disps['Time'].iat[lineCounter * len(nodeList) + node_number] = float(params[0])
                node_disps['Node'].iat[lineCounter * len(nodeList) + node_number] = nodeList[node_number]
                node_disps['Disp'].iat[lineCounter * len(nodeList) + node_number] = [float(params[1 + node_number * 6]),
                                                                                     float(params[2 + node_number * 6]),
                                                                                     float(params[3 + node_number * 6]),
                                                                                     float(params[4 + node_number * 6]),
                                                                                     float(params[5 + node_number * 6]),
                                                                                     float(params[6 + node_number * 6])]
            lineCounter += 1

    node_disps = pd.DataFrame(node_disps, columns=['Time', 'Node', 'Disp'])
    print("done")
    print(num_dt)
    print("Tremuri_Input completed in --- %s seconds ---" % (time.time() - start_time))

    return node_disps, num_dt

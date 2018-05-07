#!/usr/bin/env python

# ASuMa, Mar 2018
# Read data from files, calculate and plot Parson's coefficient
# See main() documentation below for usage details

import platform
import getopt, sys
import matplotlib.pyplot as plt
import numpy as np

def version():
    """
        Prints Python version used
    """
    print("Code writen for Python3.6.4. You're using python version:")
    print(platform.python_version())

def Load_File(filename):
    """
        Loads a data file
    """
    with open(filename) as file:
        data = file.readlines()
    return data

def Increase_Dictionary(dictio, data, index):
    """
        Add the fmi value in correct word-pair data to the given dictionary
    """
    for line in data:
        split = line.split()
        name = split[0] + " " + split[1]
        fmi = float(split[2])
        dictio.setdefault(name, [np.Inf, np.Inf, np.Inf])[index] = fmi
    return dictio

def Plot_Scatter(dictio, savefile):
    """
        Calculates Pearson's coefficients and plots data in dictio
        in 2 scatter plots, into savefile.png
    """
    def eliminate_Inf(data_struc):
        """
            Eliminates datapoints where at least one coord is Inf
        """
        clean_struct = [[],[]]
        count_eliminated = 0
        for x, y in zip(data_struc[0], data_struc[1]):
            if x == np.Inf or y == np.Inf:
                count_eliminated += 1
                continue
            clean_struct[0].append(x)
            clean_struct[1].append(y)
        return clean_struct, count_eliminated

    LG_dist_data = [[],[]]
    LG_no_dist_data = [[],[]]
    pairs_missing_LG = 0
    for k, value in dictio.items():
        if value[0] == np.Inf:
            pairs_missing_LG += 1
            #print("Pair missing in LG file: {}".format(k))
            continue
        LG_dist_data[0].append(value[0])
        LG_dist_data[1].append(value[1])
        LG_no_dist_data[0].append(value[0])
        LG_no_dist_data[1].append(value[2])

    print("Pairs missing in LG file: {}".format(pairs_missing_LG))
    LG_dist_data, dist_missing = eliminate_Inf(LG_dist_data)
    print("Pairs missing in dist file: {}".format(dist_missing))
    LG_no_dist_data, no_dist_missing = eliminate_Inf(LG_no_dist_data)
    print("Pairs missing in no-dist file: {}".format(no_dist_missing))

    # calculate Pearson's coefficient for each pair
    pearR_dist = np.corrcoef(LG_dist_data[0], LG_dist_data[1])[1,0]
    pearR_no_dist = np.corrcoef(LG_no_dist_data[0], LG_no_dist_data[1])[1,0]

    # scatter plots
    fig, (ax1, ax2) = plt.subplots(1, 2)
    fig.suptitle("FMI scatter-data")
    ax1.scatter(LG_dist_data[0], LG_dist_data[1], c = 'b', marker = '.', label = "R = %.4f"%(pearR_dist))
    ax1.set_title('LG vs Distance')
    ax1.set(xlabel = 'LG data', ylabel = 'window data')
    ax1.legend()
    ax1.axis('scaled')
    ax2.scatter(LG_no_dist_data[0], LG_no_dist_data[1], c = 'r', marker = '.', label = "R = %.4f"%(pearR_no_dist))
    ax2.set(xlabel = 'LG data')
    ax2.set_title('LG vs No-Distance')
    ax2.legend()
    ax2.axis('scaled')
    plt.savefig(savefile + ".png")

def main(argv):
    """
        Scatter-plots data in files and calculates Pearson's correlation
        coefficient between them.

        Usage: ./PearsonsCoeff.py -l <LG file> -d <distance file> 
               -n <no-distance file> -p <plotfile>

        LG file             file with LG any fmi
        distance file       file with window distance fmi
        no-distance file    file with window no-distance fmi
        plotfile            Name of ouputfile
    """

    version()

    LG_file = ''
    dist_file = ''
    no_dist_file = ''
    plot_file = ''

    try:
        opts, args = getopt.getopt(argv, "hl:d:n:p:", ["LGfile=", "distFile=",
         "noDistFile=", "plotfile="])
    except getopt.GetoptError:
        print("Usage: ./PearsonsCoeff.py -l <LG file> -d <distance file> -n <no-distance file> -p <plotfile>")
        sys.exit(2)
    for opt, arg in opts:
        if opt == '-h':
            print("Usage: ./PearsonsCoeff.py -l <LG file> -d <distance file> -n <no-distance file> -p <plotfile>")
            sys.exit()
        elif opt in ("-l", "--LGfile"):
            LG_file = arg
        elif opt in ("-d", "--distFile"):
            dist_file = arg
        elif opt in ("-n", "--noDistFile"):
            no_dist_file = arg
        elif opt in ("-p", "--plotfile"):
            plot_file = arg

    LG_data = Load_File(LG_file)
    dist_data = Load_File(dist_file)
    no_dist_data = Load_File(no_dist_file)
    word_pair_dict = {}
    word_pair_dict = Increase_Dictionary(word_pair_dict, LG_data, 0)
    word_pair_dict = Increase_Dictionary(word_pair_dict, dist_data, 1)
    word_pair_dict = Increase_Dictionary(word_pair_dict, no_dist_data, 2)
    Plot_Scatter(word_pair_dict, plot_file)

if __name__ == '__main__':
    main(sys.argv[1:])
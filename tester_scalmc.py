import subprocess, os, sys
import time
import argparse
trials = [10, 20, 30, 40]
probs_6 = [0.9937774332, 0.984357068639, 0.976468369026, 0, 0, 0]
probs_12 = [0, 0, 0, 0, 0, 0]
probs_arr = [probs_6, probs_12]
circuits = [6, 12]
# for epsilon in [.001, .1, .25, .5, 1]:
for epsilon in [.1]:
    for index in range(len(circuits)):
        probs = probs_arr[index]
        circ = circuits[index]
        test_name = 'phi' + str(circ) + '_epsilon_' + str(epsilon) + 'SCALMC.txt'
        with open(test_name, 'w') as f:
            for i in range(len(trials)):
                aiger_path = "tests/phi" + str(circ) + "_" + str(trials[i]) + "/phi" + str(circ) + "_" + str(trials[i]) + ".aig"
                if i >= len(probs):
                    command = "python2.7 prob_approximator.py " + aiger_path + " " + "tests/raw_files/source_" + str(circ) + ".aag -e " + str(epsilon)
                    command += " --ignore_partition"
                    info = os.popen(command).readlines()
                else:
                    command = "python2.7 prob_approximator.py " + aiger_path + " " + "tests/raw_files/source_" + str(circ) + ".aag -e " + str(epsilon) + " -ap " + str(probs[i])
                    command += " --ignore_partition"
                    info = os.popen(command).readlines()             
                for line in info:
                    print(line)
                    if "Actual Probability: " in line and i >= len(probs):
                        probs += [float(line.split(':')[1].strip(' \n'))]
                    f.write(line)
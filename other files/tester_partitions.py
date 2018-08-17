import subprocess, os, sys
import time
import argparse
trials = [10, 40]
probs_6 = [.9961, .8789]
probs_12 = [.3809, .1396]
probs_arr = [probs_6, probs_12]
circuits = [6, 12]
# for epsilon in [.001, .1, .25, .5, 1]:
for epsilon in [.001]:
    for index in range(len(circuits)):
        probs = probs_arr[index]
        circ = circuits[index]
        for convergence_limit in [.1, .001, .0005]:
            # for threshold in [5, 10, 16, 32]:
            for threshold in [8, 16, 32]:
                # for method in ["3n/4", "n/2"]:
                # for method in ["n-5", "nlogn", "3n/4","n/2"]:
                for method in ["n-5", "nlogn"]:
                    if convergence_limit == .1 and threshold > 16:
                        continue
                    if (method == "n-5" or method == "nlogn") or (threshold <= 10 and convergence_limit >= .01):
                        method_str = method
                        if method == "3n/4":
                            method_str = "0-75n"
                        elif method == "n/2":
                            method_str = "0-50n"
                        print(method_str)
                        test_name = "phi" + str(circ) + "_method_" + str(method_str) + "_conv_" + str(convergence_limit) + "_thresh_" + str(threshold) + ".txt"
                        with open(test_name, "w") as f:
                            for i in range(len(trials)):
                                aiger_path = "tests/phi" + str(circ) + "_" + str(trials[i]) + "/phi" + str(circ) + "_" + str(trials[i]) + ".aig"
                                command = "python2.7 prob_approximator.py " + aiger_path + " " + "tests/raw_files/source_" + str(circ) + ".aag -e " + str(epsilon) + " -ap " + str(0.0)
                                command += " --method " + str(method)
                                command += " --threshold " + str(threshold)
                                command += " --convergence_limit " + str(convergence_limit)
                                command += " --ignore_original"
                                info = os.popen(command).readlines()                
                                for line in info:
                                    print(line)
                                    if "Actual Probability: " in line and i >= len(probs):
                                        probs += [float(line.split(':')[1].strip(' \n'))]
                                    f.write(line)
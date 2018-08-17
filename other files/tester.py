import subprocess, os, sys
import time
import argparse
trials = [10, 40]
probs_6 = [0.9937774332, 0.984357068639, 0.976468369026, 0, 0, 0]
probs_12 = [0, 0, 0, 0, 0, 0]
probs_arr = [probs_6, probs_12]
circuits = [6, 12]
# for epsilon in [.001, .1, .25, .5, 1]:
for epsilon in [.001, 1]:
    for index in range(len(circuits)):
        probs = probs_arr[index]
        circ = circuits[index]
        if epsilon == 0.001:
            for convergence_limit in [.001, .0005]:
                for threshold in [16, 32, 64]:
                    # for method in ["n-5", "nlogn"]:
                    # for method in ["n-5", "nlogn", "3n/4","n/2"]:
                    for method in ["n-5","nlogn"]:
                        method_str = method
                        if method == "3n/4":
                            method_str = "0-75n"
                        elif method == "n/2":
                            method_str = "0-50n"
                        test_name = "phi" + str(circ) + "_epsilon_" + str(epsilon) + "_method_" + str(method_str) + "_conv_" + str(convergence_limit) + "_thresh_" + str(threshold) + ".txt"
                        with open(test_name, "w") as f:
                            for i in range(len(trials)):
                                aiger_path = "tests/phi" + str(circ) + "_" + str(trials[i]) + "/phi" + str(circ) + "_" + str(trials[i]) + ".aig"
                                command = "python2.7 PSMC_code/prob_approximator_cnf_direct.py " + aiger_path + " " + "tests/raw_files/source_" + str(circ) + ".aag -e " + str(epsilon) + " -ap " + str(0.0)
                                command += " --method " + str(method)
                                command += " --threshold " + str(threshold)
                                command += " --convergence_limit " + str(convergence_limit)
                                command += " --ignore_original"
                                info = os.popen(command).readlines()            	
                                for line in info:
                                    print(line)
                                    f.write(line)
        else:
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
                        f.write(line)
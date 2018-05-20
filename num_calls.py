import subprocess, os, sys
import time
import argparse
trials = [10, 40]
probs_6 = [.9961, .8789]
probs_12 = [.3809, .1396]
probs_arr = [probs_6, probs_12]
circuits = [6, 12]
conv_data = {610: [], 640: [], 1210: [], 1240: []}
threshold_data = {610: [], 640: [], 1210: [], 1240: []}
# for epsilon in [.001, .1, .25, .5, 1]:
for epsilon in [.001]:
    for index in range(len(circuits)):
        probs = probs_arr[index]
        circ = circuits[index]
        for convergence_limit in [.1, .001, .0005, .0001]:
            threshold = 32
            # for threshold in [5, 10, 16, 32]:
            # for method in ["n-5", "nlogn", "3n/4","n/2"]:
            for method in ["nlogn"]:
                if (method == "n-5" or method == "nlogn"):
                    method_str = method
                    # if method == "3n/4":
                    #     method_str = "0-75n"
                    # elif method == "n/2":
                    #     method_str = "0-50n"
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
                                if "Number of partitions sampled: " in line:
                                    print(str(circ * 100 + trials[i]) + "--" + line)
                                    conv_data[circ * 100 + trials[i]] += [int(line.split(':')[1].strip(' \n'))]

for epsilon in [.001]:
    for index in range(len(circuits)):
        probs = probs_arr[index]
        circ = circuits[index]
        for threshold in [8, 16, 32, 64]:
            convergence_limit = 0.001
            # for threshold in [5, 10, 16, 32]:
            # for method in ["n-5", "nlogn", "3n/4","n/2"]:
            for method in ["nlogn"]:
                if (method == "n-5" or method == "nlogn"):
                    method_str = method
                    # if method == "3n/4":
                    #     method_str = "0-75n"
                    # elif method == "n/2":
                    #     method_str = "0-50n"
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
                                if "Number of partitions sampled: " in line:
                                    print(str(circ * 100 + trials[i]) + "--" + line)
                                    threshold_data[circ * 100 + trials[i]] += [int(line.split(':')[1].strip(' \n'))]

for info in [(610, "phi6_10"), (640, "phi6_40"), (1210, "phi12_10"), (1240, "phi12_40")]:
    name = info[1]
    i = 0
    convergence_limits = [.1, .001, .0005, .0001]
    threshold = [8, 16, 32, 64]
    for data in [conv_data, threshold_data]:
        if i == 0:
            i += 1
            with open(name + "_convergence_limit", "w") as f:
                f.write("CIRCUIT: " + name + "\n")
                f.write("PARTITIONING METHOD: n - log(n) \n")
                f.write("Threshold = 32\n")
                for j in range(len(data[info[0]])):
                    nums = data[info[0]]
                    f.write("convergence_limit: " + str(convergence_limits[j]) + " -- Number of Calls to ScalMC: " + str(nums[j]) + "\n")
        else:
            with open(name + "_threshold", "w") as f:
                f.write("CIRCUIT: " + name + "\n")
                f.write("PARTITIONING METHOD: n - log(n) \n")
                f.write("Convergence Limit = 0.001\n")
                for j in range(len(data[info[0]])):
                    nums = data[info[0]]
                    f.write("threshold: " + str(threshold[j]) + " -- Number of Calls to ScalMC: "+ str(nums[j]) + "\n")




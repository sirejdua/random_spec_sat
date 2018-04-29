import subprocess, os, sys
import time
import argparse
trials = [10, 13, 20, 30, 40]
probs_6 = [0.9937774332, 0.984357068639, 0.976468369026]
probs_12 = []
probs_arr = [probs_6, probs_12]
circuits = [6, 12]
for index in range(len(circuits)):
    probs = probs_arr[index]
    circ = circuits[index]
    for epsilon in [0.001, 0.1, 0.25, 0.5, 1]:
        if epsilon == 0.001:
            for convergence_limit in [.1, .01, .001, .0005]:
                for threshold in [5, 10, 16, 32]:
                    for method in ["n-5", "3n/4","n/2", ]:
                        if method == "n-5" or (threshold <= 10 and convergence_limit >= .01):
                            test_name = 'phi' + str(circ) + '_epsilon_' + str(epsilon) + '_method_' + str(method) + '_conv_' + str(convergence_limit) + '_thresh_' + str(threshold) + '.txt'
                            with open(test_name, 'w') as f:
                                for i in range(len(trials)):
                                    aiger_path = 'tests/phi' + str(circ) + '_' + str(trials[i]) + '/phi' + str(circ) + '_' + str(trials[i]) + '.aig'
                                    if epsilon == 0.001:
                                        info = os.popen('python2.7 prob_approximator_small_partitions.py ' + aiger_path + ' ' + 'tests/raw_files/source_' + str(circ) + '.aag -e ' + str(epsilon) + ' -ap ' + str(probs[i]) + ' --ignore_original').readlines()            	
                                        for line in info:
                                            print(line)
                                            if "Actual Probability: " in line and i >= len(probs):
                                                probs += [float(line.split(':')[1].strip(' \n'))]
                                            f.write(line)
        else:
            test_name = 'phi' + str(circ) + '_epsilon_' + str(epsilon) + 'SCALMC.txt'
            with open(test_name, 'w') as f:
                for i in range(len(trials)):
                    aiger_path = 'tests/phi' + str(circ) + '_' + str(trials[i]) + '/phi' + str(circ) + '_' + str(trials[i]) + '.aig'
                    if i >= len(probs):
                        info = os.popen('python2.7 prob_approximator_small_partitions.py ' + aiger_path + ' ' + 'tests/raw_files/source_' + str(circ) + '.aag -e ' + str(epsilon) + ' --ignore_partition').readlines()
                    else:
                        info = os.popen('python2.7 prob_approximator_small_partitions.py ' + aiger_path + ' ' + 'tests/raw_files/source_' + str(circ) + '.aag -e ' + str(epsilon) + ' -ap ' + str(probs[i]) + ' --ignore_partition').readlines()             
                    for line in info:
                        print(line)
                        if "Actual Probability: " in line and i >= len(probs):
                            probs += [float(line.split(':')[1].strip(' \n'))]
                        f.write(line)
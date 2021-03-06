import subprocess, os, sys
import time
import argparse
circuits = ["phi7_6", "phi7_8", "phi7_10", "phi12_6", "phi12_8", "phi12_10"]
with open("290_results.txt", "w") as f:
    for k in range(1, 8):
        for index in range(len(circuits)):
            command = "python2.7 PSMC_weighted.py ../290_tests/" + str(circuits[index])+ "/" + str(circuits[index]) + ".cnf -ep 0.0001 -dp 0.0001 -eo 0.0001 -do 0.0001 --threshold 64 --convergence_limit 0.00001 -k " + str(k) + " --ignore_original"
            info = os.popen(command).readlines()      
            line_counter = 0
            print("Multiplicative Weights: Circuit: " + circuits[index])
            print("k: " + str(k))
            f.write("Multiplicative Weights: circuit: " + circuits[index] + ", k = " + str(k) + "\n")
            for line in info:
                if line_counter is 1:
                    print("written")
                    f.write(line)
                print(line)
                line_counter += 1
            f.write("\n")
            command = "python2.7 PSMC.py ../290_tests/" + str(circuits[index])+ "/" + str(circuits[index]) + ".cnf -ep 0.0001 -dp 0.0001 -eo 0.0001 -do 0.0001 --threshold 64 --convergence_limit 0.00001 -k " + str(k) + " --ignore_original"
            info = os.popen(command).readlines()      
            line_counter = 0
            print("Follow The Leader: Circuit: " + circuits[index])
            print("k: " + str(k))
            f.write("Follow The Leader: circuit: " + circuits[index] + ", k = " + str(k) + "\n")
            for line in info:
                if line_counter is 1:
                    f.write(line)
                    print("written")
                print(line)
                line_counter += 1
            f.write("\n")
            command = "python2.7 PSMC_clause_heuristic.py ../290_tests/" + str(circuits[index])+ "/" + str(circuits[index]) + ".cnf -ep 0.0001 -dp 0.0001 -eo 0.0001 -do 0.0001 --threshold 64 --convergence_limit 0.00001 -k " + str(k) + " --ignore_original"
            info = os.popen(command).readlines()      
            line_counter = 0
            print("Clause Heuristic: Circuit: " + circuits[index])
            print("k: " + str(k))
            f.write("Clause Heuristic: circuit: " + circuits[index] + ", k = " + str(k) + "\n")
            for line in info:
                if line_counter is 1:
                    print("written")
                    f.write(line)
                print(line)
                line_counter += 1
            f.write("\n")
            command = "python2.7 PSMC_DFS.py ../290_tests/" + str(circuits[index])+ "/" + str(circuits[index]) + ".cnf -ep 0.0001 -dp 0.0001 -eo 0.0001 -do 0.0001 --threshold 64 --convergence_limit 0.00001 -k " + str(k) + " --ignore_original"
            info = os.popen(command).readlines()      
            line_counter = 0
            print("DFS Partitioning: Circuit: " + circuits[index])
            print("k: " + str(k))
            f.write("DFS Partitioning: circuit: " + circuits[index] + ", k = " + str(k) + "\n")
            for line in info:
                if line_counter is 1:
                    print("written")
                    f.write(line)
                print(line)
                line_counter += 1
            f.write("\n\n")
        f.write("\n\n\n")


    for index in range(len(circuits)):
        command = "python2.7 PSMC.py ../290_tests/" + str(circuits[index])+ "/" + str(circuits[index]) + ".cnf -ep 0.0001 -dp 0.00001 -eo 0.0001 -do 0.0001 --threshold 64 --convergence_limit 0.00001 -k " + str(k) + " --ignore_partition"
        info = os.popen(command).readlines()
        f.write("ScalMC Exact Counting: circuit: " + str(circuits[index]) + "\n")
        line_counter = 0
        for line in info:
            if line_counter is 0:
                f.write(line)
                print("written")
            print(line)
            line_counter += 1
        f.write("\n")
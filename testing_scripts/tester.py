import subprocess, os, sys
import time
import argparse
# for epsilon in [.001, .1, .25, .5, 1]:
circuits = ["10sk_1_46", "17sk_3_45", "19sk_3_48", "20sk_1_51", "29sk_3_45", "27sk_3_32", "30sk_5_76", "32sk_4_38", "51sk_4_38", "54sk_12_97", "107sk_3_90"]
# circuits += ["paritysk_11_11", "ProcessBeansk_8_64", "s298_3_2", "s526_3_2", "s641_15_7", "s838_15_7", "s1238a_3_2", "s1238a_15_7", "s1423a_3_2"] 
circuits += ["s298_3_2", "s526_3_2", "s641_15_7", "s838_15_7", "s1238a_3_2", "s1238a_15_7", "s1423a_3_2"] 
circuits += ["blasted_case_0_b12_1", "blasted_case_1_b12_even2", "blasted_case_2_b12_1", "blasted_case_2_b14_3", "blasted_case_3_b14_1", "blasted_case6", "blasted_case17"]
circuits += ["blasted_case34", "blasted_squaring3", "blasted_squaring51"]
circuits += ["phi6_40", "phi12_10", "phi12_40"]
# with open("results.txt", "w") as f:
#     for index in range(len(circuits)):
#     # for method in ["n-5", "nlogn"]:
#     # for method in ["n-5", "nlogn", "3n/4","n/2"]:
#         for epsilon_original in range(2):
#             if i is 0:
#                 command = "python2.7 ../PSMC_code/prob_approximator_cnf_direct.py " + "../unigen_benchmarks/" + str(circuits[index])+ "/" + str(circuits[index]) + ".cnf -eo 1.2 -ep 1.2 -ad .12 -pd .35 --method nlogn --threshold 8 --convergence_limit 0.001"
#             else:
#                 command = "python2.7 ../PSMC_code/prob_approximator_cnf_direct.py " + "../unigen_benchmarks/" + str(circuits[index])+ "/" + str(circuits[index]) + ".cnf -eo 1 -ep 0.1 -ad .01 -pd .1 --method nlogn --threshold 8 --convergence_limit 0.001"                
#             # # command += " --ignore_original"
#             f.write("Circuit: " + circuits[index] + "\n")
#             print("Circuit: " + circuits[index])
#             info = os.popen(command).readlines()      
#             line_counter = 0          
#             for line in info:
#                 if line_counter is 0:
#                     f.write(line + "\n")
#                 else:
#                     print(line)
#                 line_counter += 1
#             f.write("\n")
config_index = 0
config_lst = [("0.1", "1.2", "2", "0.5", "2"), ("0.1", "0.4", "1.2", "0.35", "2"), ("0.001", "0.5", "1.2", "0.25", "4"), ("0.001", "0.25", "1.2", "0.12", "4"), ("0.001", "0.5", "1.2", "0.12", "8"), ("0.0005", "0.1", "0.25", "0.12", "8")]
for convergence_limit, epsilon_partition, epsilon_partition_upper_limit, delta_partition, threshold_lower_limit in config_lst:
    config_index += 1
    config_info = "config info: "
    config_info += " --epsilon_partition " + epsilon_partition
    config_info += " --delta_partition " + delta_partition
    config_info += " --method nlogn "
    config_info += " --threshold 8"
    config_info += " --threshold_lower_limit " + threshold_lower_limit
    config_info += " --epsilon_partition_upper_limit " + epsilon_partition_upper_limit 
    config_info += " --convergence_limit " + convergence_limit
    print(config_info + "\n")
    with open("results_" + str(config_index) + ".csv", "w") as f:
        f.write(config_info + "\n")
        f.write("circuit, time, probability\n")
        for index in range(len(circuits)):
            command = "python2.7 ../PSMC_code/PSMC.py " + "../test_benchmarks/" + str(circuits[index])+ "/" + str(circuits[index]) + ".cnf"
            command += " --epsilon_partition " + epsilon_partition
            command += " --delta_partition " + delta_partition
            command += " --method nlogn "
            command += " --threshold 8"
            command += " --threshold_lower_limit " + threshold_lower_limit
            command += " --epsilon_partition_upper_limit " + epsilon_partition_upper_limit 
            command += " --convergence_limit " + convergence_limit
            command += " --ignore_original"
            info = os.popen(command).readlines()      
            line_counter = 0
            print("Circuit: " + circuits[index])
            for line in info:
                if line_counter is 0:
                    f.write(line)
                print(line)
                line_counter += 1
for epsilon_original, delta_original in [(2, 0.4), (1.2, .12), (0.1, 0.1)]:
    config_index += 1
    with open("results_" + str(config_index) + ".csv", "w") as f:
        f.write("epsilon_original " + str(epsilon_original) + ", delta_original " + str(delta_original) + "\n")
        f.write("circuit, time, probability\n")
        for index in range(len(circuits)):
            command = "python2.7 ../PSMC_code/prob_approximator_cnf_direct.py " + "../test_benchmarks/" + str(circuits[index])+ "/" + str(circuits[index]) + ".cnf -eo " + str(epsilon_original) + " -do " + str(delta_original) + " --method nlogn --ignore_partition"
            info = os.popen(command).readlines()      
            line_counter = 0
            print("Circuit: " + circuits[index])
            for line in info:
                if line_counter is 0:
                    f.write(line)
                print(line)
                line_counter += 1


import subprocess, os, sys
import time
import argparse
# for epsilon in [.001, .1, .25, .5, 1]:
circuits = ["10sk_1_46", "17sk_3_45", "19sk_3_48", "20sk_1_51", "29sk_3_45", "27sk_3_32", "30sk_5_76", "32sk_4_38", "51sk_4_38", "54sk_12_97", "107sk_3_90"]
# circuits += ["paritysk_11_11", "ProcessBeansk_8_64", "s298_3_2", "s526_3_2", "s641_15_7", "s838_15_7", "s1238a_3_2", "s1238a_15_7", "s1423a_3_2"] 
circuits += ["s298_3_2", "s526_3_2", "s641_15_7", "s838_15_7", "s1238a_3_2", "s1238a_15_7", "s1423a_3_2"] 
circuits += ["blasted_case_0_b12_1", "blasted_case_1_b12_even2", "blasted_case_2_b12_1", "blasted_case_2_b14_3", "blasted_case_3_b14_1", "blasted_case6", "blasted_case17"]
circuits += ["blasted_case34", "blasted_squaring3", "blasted_squaring51", "blasted_TR_b12_2_linear", "blasted_TR_b14_2_linear", "blasted_TR_b14_even3_linear"]
with open("results.txt", "w") as f:
    for index in range(len(circuits)):
    # for method in ["n-5", "nlogn"]:
    # for method in ["n-5", "nlogn", "3n/4","n/2"]:
        for i in range(2):
            if i is 0:
                command = "python2.7 ../PSMC_code/prob_approximator_cnf_direct.py " + "../unigen_benchmarks/" + str(circuits[index])+ "/" + str(circuits[index]) + ".cnf -eo 1.5 -ad .12 -pd .35 --method nlogn --threshold 8 --convergence_limit 0.001"
            else:
                command = "python2.7 ../PSMC_code/prob_approximator_cnf_direct.py " + "../unigen_benchmarks/" + str(circuits[index])+ "/" + str(circuits[index]) + ".cnf -eo 1 -ad .01 -pd .1 --method nlogn --threshold 8 --convergence_limit 0.001"                
            # command += " --ignore_original"
            f.write("Circuit: " + circuits[index] + "\n")
            print("Circuit: " + circuits[index])
            info = os.popen(command).readlines()                
            for line in info:
                print(line)
                f.write(line)
            f.write("\n")

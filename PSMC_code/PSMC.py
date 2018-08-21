import subprocess, os, sys
import time
import argparse
from partition_random_sample import *
import math
##########################################################
### PSMC on a CNF file without Aiger circuit unrolling ###
##########################################################

###################
##argument parser##
###################

parser = argparse.ArgumentParser()
parser.add_argument("filename", help = "cnf file path")
parser.add_argument("-k", "--num_partition_variables", help = "number of partitioning variables", type = int, default = -1)
parser.add_argument("-eo", "--epsilon_original", help = "epsilon bound on original", type = float, default = 2)
parser.add_argument("-ep", "--epsilon_partition", help = "epsilon value for partition at start", type = float, default = 2)
parser.add_argument("-do", "--delta_original", help = "the delta for the original", type = float, default = .1)
parser.add_argument("-dp", "--delta_partition", help = "the delta for the partitions", type = float, default = .99)
parser.add_argument("-ap", "--actual_probability", help = "don't calculate the exact probability; just use this number", type = float, default = -1)
parser.add_argument("-epul", "--epsilon_partition_upper_limit", help = "upper limit on epsilon used on any larger cell sizes", type = float, default = 5)
parser.add_argument("-tl", "--threshold_lower_limit", help = "the lower bound on the threshold to be used", type = float, default = 8)
parser.add_argument("--method", action='store', choices=["3n/4","n/2", "n-5", "nlogn"], default = "nlogn", help='partitioning technique')
parser.add_argument("--threshold", help='number of iterations to convergence', type = float, default = 4)
parser.add_argument("--convergence_limit", help='the bound to which the density must converge to', type = float, default = 0.001)
parser.add_argument("--ignore_original", help = "run scalmc on the original model", action = "store_true")
parser.add_argument("--ignore_partition", help = "run scalmc on the original model", action = "store_true")
args = parser.parse_args()
run_on_partition = not args.ignore_partition
run_on_original = not args.ignore_original
k = int(args.num_partition_variables)
num_clauses = 0
original_count = 0
original_time = 0
n = 0
filename = args.filename

##################################################################
# Get the number of clauses and the number of counting variables #
##################################################################

sub_value = 0
with open(filename, 'r') as f:
    found = False
    file_lines = f.readlines()
    for i in range(len(file_lines)):
        x = file_lines[i]
        if "c ind" in x:
            n += len(x.split(' ')) - 3
        elif "p cnf " in x:
            num_clauses = int(x.split(' ')[-1])
            if n is 0:
                sub_value = int(x.split(' ')[-2])
if n is 0:
    n = sub_value
# print("File: " + filename.split('/')[-1].split('.cnf')[0])
# print("n = " + str(n))

#############################################
# set the parameters appropriately          # 
# pivotAC and epsilon for PSMC and original #
#############################################

epsilon_main = float(args.epsilon_original)
pivotAC_main = int(math.ceil(9.84 * (1 + (epsilon_main / (1.0 + epsilon_main))) * (1 + (1.0/epsilon_main)) * (1 + (1.0/epsilon_main))))
epsilon_partition = float(args.epsilon_partition)
pivotAC_partition = int(math.ceil(9.84 * (1 + (epsilon_partition / (1.0 + epsilon_partition))) * (1 + (1.0/epsilon_partition)) * (1 + (1.0/epsilon_partition))))

delta_partition = float(args.delta_partition)
delta_original = float(args.delta_original)

epsilon_partition_upper_limit = float(args.epsilon_partition_upper_limit)

######################
# SCALMC ON ORIGINAL #
######################

if run_on_original:
    ##count number of original solutions
    start = time.time()
    info = os.popen("./../../maxcount/scalmc --pivotAC " + str(pivotAC_main) + " --delta " + str(delta_original) + " " + filename).readlines()[-1]
    # info = os.popen("./../../maxcount/scalmc --pivotAC " + str(pivotAC_main) + " --delta .05 " + filename).readlines()[-1]
    # info = os.popen("./../../maxcount/scalmc " + filename).readlines()[-1]
    num_sols = info.split(': ')[1].split(' x ')
    base, exp = int(num_sols[1].split('^')[0]), int(num_sols[1].split('^')[1].strip("\n"))
    original_count += int(num_sols[0]) * base**exp
    end = time.time()
    original_time = end - start
    j = 0

    # convert answer to scientific notation.
    while original_count % (2**(j+1)) == 0:
        j += 1
    original_count_str = str(original_count/(2**j)) + " x 2^" + str(j)
    # print("Original Probability: " + str(float(original_count)/(2**n)))
    # print("epsilon for original = " + str(epsilon_main))
    # print("Time for original: " + str(original_time))
    # print("Original Count: " + original_count_str)

########################
# SCALMC ON PARTITIONS #
########################
if run_on_partition:
    # if k (the number of partitioning variables) was never specified, calculate it according to the parameters of the cnf file
    if k == -1:
        if args.method == "3n/4":
            k = int(.75*n)
        elif args.method == "n/2":
            k = int(0.5*n)
        elif args.method == "nlogn":
            k = int(n - math.log(n, 2))
        else: 
            k = n-5
    # print("Partitioning Technique: " + str(args.method))
    # print("k = " + str(k))

    # PSMC decreases the threshold for the steps needed to convergence as we expand the cell size. what should be the lower limit?
    threshold_lower_limit = int(args.threshold_lower_limit)
    # What should be the limit of convergence?
    convergence_limit = float(args.convergence_limit)
    # How many iterations where the density does not change by more than the convergence limit until we determine convergence?
    threshold = int(args.threshold)
    # How many free variables
    free_vars = n - k
    #partition the file, time it
    start = time.time()
    variable_order = get_top_vars(k, 1000, filename)
    partition_vars = variable_order[:k]
    end = time.time()
    #count number of partitioned solutions
    file_gen_time = end - start

    #how many iterations have i gone through in which the density has not deviated more than convergence_limit (the max allowed)?
    
    density_counter = 0

    #how to calculate the average density: density_sum/partitions_sampled (partitions_sampled is for CURRENT VALUE OF K)
    
    density_sum = 0.0
    total_files = 0
    partitions_sampled = 0    
    density = 0

    # time the algorithm
    partition_time = 0
    start = time.time()
    converged = False

    # which partitions have i tested?
    partitions = set()

    
    empty_counter = 0 # how many empty partitions have i sampled?
    delta = 0.1
    level = 1 # the number of values k has taken on.
    i = 0
    min_k = int(math.log(n, 2))
    #find p
    # p = 0
    # lim = n
    # while lim > 0:
    #     lim = lim - (2**p) * math.log(n, 2)
    #     p += 1
    # p -= 1
    final_start_time = time.time()
    while not converged:

        # What is k (# of partitioning variables) currently at?  It is the max of (min_k, decremented_k)
        # because the idea is to reduce k by decreasing by 2 * math.log(n, 2) until it reaches the minimum possible size
        # once you reach the minimum possible size, stop decreasing k.

        decremented_k = int(n - (2**(level-1))*math.log(n, 2))
        min_k = int(math.log(n, 2))
        # if we have sampled a sufficient # of empty partitions....
        # n/(2**(level - 1)) : each time we increase k, we decrease the amount of empty partitions before a reset by a factor of 2
        # until we cannot decrease it anymore (the floor is max(2, math.log(n, 2))).
        if empty_counter > max(n/(2**(level - 1)), math.log(n, 2), 2) and min_k < decremented_k:
            # then reduce k by dividing by 2, tweak epsilon by multiplying by 2, and adjust pivot_AC accordingly.
            # also reset the density measures: partitions_sampled, density, density_counter, density_sum.

            epsilon_partition = min(epsilon_partition * 2, epsilon_partition_upper_limit)
            pivotAC_partition = int(math.ceil(9.84 * (1 + (epsilon_partition / (1.0 + epsilon_partition))) * (1 + (1.0/epsilon_partition)) * (1 + (1.0/epsilon_partition))))
            empty_counter = 0
            level += 1
            partitions = set()
            density_counter = 0
            density_sum = 0.0
            partitions_sampled = 0
            density = 0
            i = 0
            # p = max (p-1, 0)
            decremented_k = int(n - (2**(level-1))*math.log(n, 2))
            min_k = int(math.log(n, 2))
            if args.method == "nlogn":
                # k = 10
                k = max(min_k, decremented_k)
            else:
                k = max(k-10, 0)
            # print("k: " + str(k))
            partition_vars = variable_order[:k]
            final_start_time = time.time()

        old_density = density
        assignment_str = ""
        generator = time.time()

        # generate a partition assignment that has not been sampled yet.
        while assignment_str in partitions or assignment_str == "":
            assignment_str = random_string_generator(k)
            if len(partitions) == 2**k:
                converged = True
                break
        end_gen = time.time()
        partitions.add(assignment_str)
        # write the partition to file
        write_partition(partition_vars, filename, i, bin_string = assignment_str)
        info = os.popen("./../../maxcount/scalmc --pivotAC " + str(pivotAC_partition) + " --delta " + str(delta_partition) + " " + filename.split('.cnf')[0] + "-window-" + str(i) + ".cnf").readlines()[-1]
        # info = os.popen("./../../maxcount/scalmc --pivotAC " + str(pivotAC_partition) + " --delta " + str(delta) + " " + filename.split('.cnf')[0] + "-window-" + str(i) + ".cnf").readlines()[-1]
        # info = os.popen("./../../maxcount/scalmc " + filename.split('.cnf')[0] + "-window-" + str(i) + ".cnf").readlines()[-1]
        partitions_sampled += 1
        try:
            # if this partition is satisfiable...
            num_sols = info.split(': ')[1].split(' x ')
            base, exp = int(num_sols[1].split('^')[0]), int(num_sols[1].split('^')[1].strip("\n"))
            density_sum += float(int(num_sols[0]) * (base**exp))/(2**(n-k))
            density = density_sum/partitions_sampled
            empty_counter = 0

            #if the density does not change by more than convergence_limit
            if abs(density - old_density) <= convergence_limit:
                density_counter += 1
                if density_counter >= max(int(threshold/(2**(level-1))), threshold_lower_limit):
                    # GO TO THE ELSE CASE IF AND ONLY IF our density is 1 but we have sampled unSAT assignments when generating partitioning variables...
                    if (not allOne and density != 1) or (allOne and density == 1):
                        converged = True
                    else:
                        free_vars = int(free_vars * 2)
                        k = n - free_vars
                        density_counter = 0
                        threshold = int(threshold / 2)
                        if k <= 0 or threshold <= 1:
                            converged = True
                        density = 0
                        density_sum = 0
                        partition_vars = variable_order[:k]
                        partitions = set()
            else:
                density_counter = 0
        except: 
            # if the partition is unSAT
            empty_counter += 1
            density = density_sum/partitions_sampled
            if abs(density - old_density) > convergence_limit:
                density_counter = 0
        # print(density)
        total_files += 1
        i += 1
    end = time.time()
    partition_time = end - start
    partition_count = density * 2**n
    i = 0
    # while int(partition_count) % (2**(i+1)) == 0:
    #     i += 1

    partition_count_str = str(int(partition_count)/(2**i)) + " x 2^" + str(i)
if not args.ignore_partition:
    partition_time_str = '{:.{p}g}'.format(partition_time + file_gen_time, p=4)
    partition_accuracy_str = '{:.{p}g}'.format(density, p=4)
if not args.ignore_original:
    original_time_str = '{:.{p}g}'.format(original_time, p=4)
    original_accuracy_str = '{:.{p}g}'.format(float(original_count)/(2**n), p=4)

result_info = filename.split('/')[-1].split('.cnf')[0]
if not args.ignore_partition:
    result_info += ", " + partition_time_str
if not args.ignore_original:
    result_info += ", " + original_time_str 
if not args.ignore_partition:
    result_info += ", " + partition_accuracy_str 
if not args.ignore_original:
     result_info += ", " + original_accuracy_str
    
print(result_info)
print("************************************************")
if not args.ignore_partition:
    print("Time for partitioned with partitioning overhead : " + '{:.{p}g}'.format(partition_time + file_gen_time, p=4))
    print("Time taken for final k value: " + str(end - final_start_time))
if not args.ignore_original:
    print("Time for original: " + '{:.{p}g}'.format(original_time, p=4))
if not args.ignore_partition:
    print("Partitioned Probability: " + '{:.{p}g}'.format(density, p=4))
if not args.ignore_original:
    print("Original Probability: " + '{:.{p}g}'.format(float(original_count)/(2**n), p=4))
    if not args.ignore_partition:
        print("Percent Error: " + str(100*abs((density - float(original_count)/(2**n))/(float(original_count)/(2**n)))))
print("************************************************")

    # partition_count_str = str(int(partition_count)/(2**i)) + " x 2^" + str(i)
    # print("************************************************")
    # print("Convergence Limit: " + str(convergence_limit))
    # print("Iterations to Convergence - Threshold: " + str(args.threshold))
    # print("Partitioned Probability: " + str(density))
    # print("Time for partitioned with partitioning overhead : {}".format(partition_time + file_gen_time))
    # print("Time for partitioned without partitioning overhead: {}".format(partition_time))
    # print("Time taken for final k value: " + str(end - final_start_time))
    # if not args.ignore_original and not args.ignore_partition:
    #     print("Original Probability: " + str(float(original_count)/(2**n)))
    #     print("Time for original: " + str(original_time))
    #     print("Percent Error: " + str(100*abs((density - float(original_count)/(2**n))/(float(original_count)/(2**n)))))
    # print("Number of partitions sampled: {}".format(total_files))
    # print("Final # of partitioning variables (k): " + str(k))
    # print("Number of partitions sampled with k = " + str(k) + ": " + str(partitions_sampled))
    # print("************************************************")
    # print("Partitioned Count: " + partition_count_str)

# if args.actual_probability == -1:
#     prob = os.popen("aigcount " + aiger_file + "out.aag").readlines()[0][:-2]
# else:
#     prob = args.actual_probability
# print("Actual Probability: " + str(float(prob)))

# if aiger:
#     os.system("./../aiger-1.9.9/aigand " + aiger_file + ".aig " + aiger_file + ".aig")
#     os.system("./../aiger-1.9.9/aigtoaig " + aiger_file + ".aig " + aiger_file + ".aag")
#     os.system("aigcompose " + aiger_file + ".aag " + "tests/raw_files/source.aag " + aiger_file + ".aag")
#     prob = os.system("aigcount " + aiger_file + ".aag").readlines()
#     print("Actual Probability: " + str(prob))

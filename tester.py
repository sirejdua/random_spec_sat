import subprocess, os, sys
import time
import argparse
from partition_random_sample import *

#################
### argparser ###
#################
parser = argparse.ArgumentParser()
parser.add_argument("aiger_file", help = "path to aiger circuit unrolling")
parser.add_argument("-k", "--num_partition_variables", help = "number of partitioning variables", type = int, default = 4)
parser.add_argument("-e", "--epsilon", help = "epsilon bound on answer with 98% probability", type = float, default = 2)
args = parser.parse_args()
aiger_file = args.aiger_file.split('.a')[0]
epsilon = float(args.epsilon)
pivotAC = int(math.ceil(9.84 * (1 + (epsilon / (1.0 + epsilon))) * (1 + (1.0/epsilon)) * (1 + (1.0/epsilon))))
k = int(args.num_partition_variables)
num_files = 2**k

original_count = 0
n = 0
#count the number of solutions in the aiger file, generate cnf from aiger file
os.system("./../aiger-1.9.9/aigand " + aiger_file + ".aig " + aiger_file + "and.aig")
os.system("./../aiger-1.9.9/aigtoaig " + aiger_file + "and.aig " + aiger_file + ".aag")
os.system("aigcompose " + "tests/raw_files/source.aag " + aiger_file + ".aag " + aiger_file + "out.aag")
os.system("python3 aigtocnf_ind.py " + aiger_file + "out.aag " + aiger_file + ".cnf ")
filename = aiger_file + ".cnf"
print(filename)
partition_formula(get_top_vars(k, 100000, filename), filename)

with open(filename, 'r') as f:
    x = f.readline()
    if "c ind" in x:
        n = len(x.split(' ')) - 3

##count number of original solutions
start = time.time()
#MONTE CARLO ON ORIGINAL
(sampleMant, sampleExp, sampleExact) = countSampleWithMonteCarlo(15000, counting_vars, clauses[:])
original_count += sampleMant * 2**sampleExp
# info = os.popen("./../maxcount/scalmc --pivotAC " + str(pivotAC) + " --delta 0.02 " + filename).readlines()[-1]
# num_sols = info.split(': ')[1].split(' x ')
# base, exp = int(num_sols[1].split('^')[0]), int(num_sols[1].split('^')[1].strip("\n"))
# original_count += int(num_sols[0]) * base**exp
end = time.time()
print("Time for original: " + str(end - start))

#count number of partitioned solutions
partition_count = 0
i = 0
start = time.time()
for i in range(num_files):
    #MONTE CARLO ON PARTITIONS
    (sampleMant, sampleExp, sampleExact) = countSampleWithMonteCarlo(15000, counting_vars, clauses[:] + partition_clauses[i])
    partition_count += sampleMant * 2**sampleExp
    # print(2, '%.3f x 2^%d' % (sampleMant, sampleExp))
    # start = time.time()
    # info = os.popen("./../maxcount/scalmc --pivotAC " + str(pivotAC) + " --delta 0.02 " + filename.split('.cnf')[0] + "-window-" + str(i) + ".cnf").readlines()[-1]
    # try:
    #     num_sols = info.split(': ')[1].split(' x ')
    #     base, exp = int(num_sols[1].split('^')[0]), int(num_sols[1].split('^')[1].strip("\n"))
    #     partition_count += int(num_sols[0]) * base**exp
    # except:
    #     continue
    # #print("Time for partitioned: " + str(end - start))
    # end = time.time()
    # print("Time for partitioned : {}".format(end - start))
    # i += end-start
end = time.time()
print("Time for partitioned: " + str(end - start))
i /= num_files

i = 0
while partition_count % (2**(i+1)) == 0:
    i += 1

j = 0
while original_count % (2**(j+1)) == 0:
    j += 1

original_count_str = str(original_count/(2**j)) + " x 2^" + str(j)
partition_count_str = str(partition_count/(2**i)) + " x 2^" + str(i)

print("Number of partitions: " + str(num_files))
print("Partitioned Count: " + partition_count_str)
print("Original Count: " + original_count_str)
print("Partitioned Probability: " + str(float(partition_count)/(2**n)))
print("Original Probability: " + str(float(original_count)/(2**n)))
prob = os.popen("aigcount " + aiger_file + "out.aag").readlines()[0][:-2]
print("Actual Probability: " + str(float(prob)))

# if aiger:
#     os.system("./../aiger-1.9.9/aigand " + aiger_file + ".aig " + aiger_file + ".aig")
#     os.system("./../aiger-1.9.9/aigtoaig " + aiger_file + ".aig " + aiger_file + ".aag")
#     os.system("aigcompose " + aiger_file + ".aag " + "tests/raw_files/source.aag " + aiger_file + ".aag")
#     prob = os.system("aigcount " + aiger_file + ".aag").readlines()
#     print("Actual Probability: " + str(prob))

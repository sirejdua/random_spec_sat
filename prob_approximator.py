import subprocess, os, sys
import time
import argparse
from partition_random_sample import *
#################
### argparser ###
#################
parser = argparse.ArgumentParser()
parser.add_argument("aiger_file", help = "path to aiger circuit unrolling")
parser.add_argument("aiger_source", help = "path to aiger source")
parser.add_argument("-k", "--num_partition_variables", help = "number of partitioning variables", type = int, default = -1)
parser.add_argument("-e", "--epsilon", help = "epsilon bound on answer with 98% probability", type = float, default = 2)
parser.add_argument("-ap", "--actual_probability", help = "don't calculate the exact probability; just use this number", type = float, default = -1)
args = parser.parse_args()
aiger_file = args.aiger_file.split('.a')[0].split('.cnf')[0]
k = int(args.num_partition_variables)
num_clauses = 0
original_count = 0
n = 0
#count the number of solutions in the aiger file, generate cnf from aiger file
os.system("./../aiger-1.9.9/aigand " + aiger_file + ".aig " + aiger_file + "and.aig")
os.system("./../aiger-1.9.9/aigtoaig " + aiger_file + "and.aig " + aiger_file + ".aag")
os.system("aigcompose " + args.aiger_source + " " + aiger_file + ".aag " + aiger_file + "out.aag")
os.system("python3 aigtocnf_ind.py " + aiger_file + "out.aag " + aiger_file + ".cnf ")
filename = aiger_file + ".cnf"

with open(filename, 'r') as f:
    found = False
    while not found:
        x = f.readline()
        if "c ind" in x:
            n += len(x.split(' ')) - 3
        elif "p cnf " in x:
            num_clauses = int(x.split(' ')[-1])
            found = True
            if n is 0:
                n = int(x.split(' ')[-2])

#if k was never specified, calculate it according to the parameters of the cnf file
if k == -1:
    k = max(1, int(n*0.75))

#set the parameters appropriately
epsilon_main = float(args.epsilon)
epsilon_partition = .001
pivotAC_main = int(math.ceil(9.84 * (1 + (epsilon_main / (1.0 + epsilon_main))) * (1 + (1.0/epsilon_main)) * (1 + (1.0/epsilon_main))))
pivotAC_partition = int(math.ceil(9.84 * (1 + (epsilon_partition / (1.0 + epsilon_partition))) * (1 + (1.0/epsilon_partition)) * (1 + (1.0/epsilon_partition))))

#partition the file, time it
start = time.time()
partition_vars = get_top_vars(k, 25000, filename)
end = time.time()
file_gen_time = end - start
##count number of original solutions
start = time.time()
#SCALMC ON ORIGINAL
info = os.popen("./../maxcount/scalmc --pivotAC " + str(pivotAC_main) + " --delta 0.02 " + filename).readlines()[-1]
num_sols = info.split(': ')[1].split(' x ')
base, exp = int(num_sols[1].split('^')[0]), int(num_sols[1].split('^')[1].strip("\n"))
original_count += int(num_sols[0]) * base**exp
end = time.time()
original_time = end - start


#count number of partitioned solutions
# partition_count = 0
density_counter = 0
density_sum = 0.0
density = 0
partition_time = 0
num_files = 2**k
start = time.time()
file_list = np.array(range(num_files))
np.random.shuffle(file_list)
file_counter = 0
for i in file_list:
    #SCALMC ON PARTITIONS
    unsat_partition = False
    old_density = density
    write_partition(partition_vars, filename, i)
    info = os.popen("./../maxcount/scalmc --pivotAC " + str(pivotAC_partition) + " --delta 0.02 " + filename.split('.cnf')[0] + "-window-" + str(i) + ".cnf").readlines()[-1]
    try:
        num_sols = info.split(': ')[1].split(' x ')
        base, exp = int(num_sols[1].split('^')[0]), int(num_sols[1].split('^')[1].strip("\n"))
        density_sum += float(int(num_sols[0]) * (base**exp))/(2**(n-k))
    except: 
        unsat_partition = True
    file_counter += 1
    density = density_sum/file_counter
    if abs(density - old_density) <= .0005:
        density_counter += 1
        if density_counter >= 3*k:
            break
    else:
        density_counter = 0
end = time.time()
partition_time = end - start

partition_count = density * 2**n
i = 0
while int(partition_count) % (2**(i+1)) == 0:
    i += 1

j = 0
while original_count % (2**(j+1)) == 0:
    j += 1

original_count_str = str(original_count/(2**j)) + " x 2^" + str(j)
partition_count_str = str(int(partition_count)/(2**i)) + " x 2^" + str(i)

print("File: " + filename.split('/')[-1].split('.')[0])
print("k = " + str(k))
# print("Partitioned Count: " + partition_count_str)
# print("Original Count: " + original_count_str)
print("Original Probability: " + str(float(original_count)/(2**n)))
print("epsilon for original = " + str(epsilon_main))
print("Time for original: " + str(original_time))
print("Partitioned Probability: " + str(float(partition_count)/(2**n)))
print("epsilon for partitioned = " + str(epsilon_partition))
print("Time for partitioned with partitioning overhead : {}".format(partition_time + file_gen_time))
print("Time for partitioned without partitioning overhead: {}".format(partition_time))
if args.actual_probability == -1:
    prob = os.popen("aigcount " + aiger_file + "out.aag").readlines()[0][:-2]
else:
    prob = args.actual_probability
print("Actual Probability: " + str(float(prob)))

# if aiger:
#     os.system("./../aiger-1.9.9/aigand " + aiger_file + ".aig " + aiger_file + ".aig")
#     os.system("./../aiger-1.9.9/aigtoaig " + aiger_file + ".aig " + aiger_file + ".aag")
#     os.system("aigcompose " + aiger_file + ".aag " + "tests/raw_files/source.aag " + aiger_file + ".aag")
#     prob = os.system("aigcount " + aiger_file + ".aag").readlines()
#     print("Actual Probability: " + str(prob))

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
aiger_file = args.aiger_file.split('.a')[0].split('.cnf')[0]
k = int(args.num_partition_variables)
epsilon_main = float(args.epsilon)
epsilon_partition = epsilon_main/(k*k)
pivotAC_main = int(math.ceil(9.84 * (1 + (epsilon_main / (1.0 + epsilon_main))) * (1 + (1.0/epsilon_main)) * (1 + (1.0/epsilon_main))))
pivotAC_partition = int(math.ceil(9.84 * (1 + (epsilon_partition / (1.0 + epsilon_partition))) * (1 + (1.0/epsilon_partition)) * (1 + (1.0/epsilon_partition))))
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
    while True:
        x = f.readline()
        if "c ind" in x:
            n += len(x.split(' ')) - 3
            print(n)
        else:
            break
if n is 0:
    n = len(counting_vars.keys())
    print(n)

##count number of original solutions
start = time.time()
#MONTE CARLO ON ORIGINAL
# (sampleMant, sampleExp, sampleExact) = countSampleWithMonteCarlo(15000, counting_vars, clauses[:])
# original_count += sampleMant * 2**sampleExp
#SCALMC ON ORIGINAL
info = os.popen("./../maxcount/scalmc --pivotAC " + str(pivotAC_main) + " --delta 0.02 " + filename).readlines()[-1]
print(info)
num_sols = info.split(': ')[1].split(' x ')
base, exp = int(num_sols[1].split('^')[0]), int(num_sols[1].split('^')[1].strip("\n"))
original_count += int(num_sols[0]) * base**exp

end = time.time()
print("Time for original: " + str(end - start))

#count number of partitioned solutions
partition_count = 0
i = 0
density = 0.0
density_counter = 0
time_total = 0
start = time.time()
file_list = np.array(range(num_files))
np.random.shuffle(file_list)
file_counter = 0
for i in file_list:
    print("file window: " + str(i))
    #MONTE CARLO ON PARTITIONS
    # (sampleMant, sampleExp, sampleExact) = countSampleWithMonteCarlo(500, counting_vars, clauses[:] + partition_clauses[i])
    # partition_count += sampleMant * 2**sampleExp
    # print(2, '%.3f x 2^%d' % (sampleMant, sampleExp))
    #SCALMC ON PARTITIONS
    start = time.time()
    info = os.popen("./../maxcount/scalmc --pivotAC " + str(pivotAC_partition) + " --delta 0.001 " + filename.split('.cnf')[0] + "-window-" + str(i) + ".cnf").readlines()[-1]
    try:
        num_sols = info.split(': ')[1].split(' x ')
        base, exp = int(num_sols[1].split('^')[0]), int(num_sols[1].split('^')[1].strip("\n"))
        # partition_count += int(num_sols[0]) * base**exp
        partition_count = int(num_sols[0]) * base**exp
        print(int(num_sols[0]) * base**exp)
        old_density = density
        file_counter += 1
        end = time.time()
        time_total += end - start
        density = (density + float(partition_count)/(2**(n-k)))/file_counter
        if density - old_density <= .0000001:
            density_counter += 1
            print(density_counter)
            if density_counter >= 5:
                break
        else:
            density_counter = 0
    except: 
        continue
    #print("Time for partitioned: " + str(end - start))
    # i += end-start
# end = time.time()
# print("Time for partitioned: " + str(end - start))
i /= num_files

i = 0
while partition_count % (2**(i+1)) == 0:
    i += 1

j = 0
while original_count % (2**(j+1)) == 0:
    j += 1

partition_count = density * 2**n
original_count_str = str(original_count/(2**j)) + " x 2^" + str(j)
partition_count_str = str(partition_count/(2**i)) + " x 2^" + str(i)

print("Number of partitions: " + str(num_files))
print("Partitioned Count: " + partition_count_str)
print("Original Count: " + original_count_str)
print("Partitioned Probability: " + str(float(partition_count)/(2**n)))
print("Original Probability: " + str(float(original_count)/(2**n)))
print("Time for partitioned : {}".format(time_total))
prob = os.popen("aigcount " + aiger_file + "out.aag").readlines()[0][:-2]
print("Actual Probability: " + str(float(prob)))

# if aiger:
#     os.system("./../aiger-1.9.9/aigand " + aiger_file + ".aig " + aiger_file + ".aig")
#     os.system("./../aiger-1.9.9/aigtoaig " + aiger_file + ".aig " + aiger_file + ".aag")
#     os.system("aigcompose " + aiger_file + ".aag " + "tests/raw_files/source.aag " + aiger_file + ".aag")
#     prob = os.system("aigcount " + aiger_file + ".aag").readlines()
#     print("Actual Probability: " + str(prob))

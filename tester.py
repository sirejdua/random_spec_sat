import subprocess, os, sys

filename = sys.argv[1]
num_files = int(sys.argv[2])
original_count = 0

##count number of original solutions
info = os.popen("./../maxcount/scalmc " + filename).readlines()[-1]
num_sols = info.split(': ')[1].split(' x ')
base, exp = int(num_sols[0]), int(num_sols[1].split('^')[1].strip("\n"))
original_count += int(num_sols[0]) * base**exp

#count number of partitioned solutions
partition_count = 0
for i in range(num_files):
    info = os.popen("./../maxcount/scalmc " + filename.split('.')[0] + "-window-" + str(i) + ".cnf").readlines()[-1]
    num_sols = info.split(': ')[1].split(' x ')
    print(i)
    base, exp = int(num_sols[0]), int(num_sols[1].split('^')[1].strip("\n"))
    partition_count += int(num_sols[0]) * base**exp

print("Partitioned Count: " + str(partition_count))
print("Original Count: " + str(original_count))

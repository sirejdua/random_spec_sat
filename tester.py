import subprocess, os, sys
import time

filename = sys.argv[1]
num_files = int(sys.argv[2])
original_count = 0

##count number of original solutions
start = time.time()
info = os.popen("./../maxcount/scalmc " + filename).readlines()[-1]
num_sols = info.split(': ')[1].split(' x ')
base, exp = int(num_sols[1].split('^')[0]), int(num_sols[1].split('^')[1].strip("\n"))
original_count += int(num_sols[0]) * base**exp
end = time.time()
print("Time for original: " + str(end - start))

#count number of partitioned solutions
partition_count = 0
start = time.time()
for i in range(num_files):
    info = os.popen("./../maxcount/scalmc " + filename.split('.')[0] + "-window-" + str(i) + ".cnf").readlines()[-1]
    try:
        num_sols = info.split(': ')[1].split(' x ')
        base, exp = int(num_sols[1].split('^')[0]), int(num_sols[1].split('^')[1].strip("\n"))
        partition_count += int(num_sols[0]) * base**exp
    except:
        continue
end = time.time()
#print("Time for partitioned: " + str(end - start))
print("Time for partitioned: {}".format(end - start))

i = 0
while partition_count % (2**(i+1)) == 0:
    i += 1

j = 0
while original_count % (2**(j+1)) == 0:
    j += 1

original_count_str = str(original_count/(2**j)) + " x 2^" + str(j)
partition_count_str = str(partition_count/(2**i)) + " x 2^" + str(i)

print("Partitioned Count: " + partition_count_str)
print("Original Count: " + original_count_str)

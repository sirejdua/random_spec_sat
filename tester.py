import subprocess, os, sys
import time

filename = sys.argv[1]
num_files = int(sys.argv[2])
aiger = True
try:
    aiger_file = sys.argv[3].split('.a')[0]
except:
    print("no aiger file found")
    aiger = False
original_count = 0
k = 0
with open(filename, 'r') as f:
    x = f.readline()
    if "c ind" in x:
        k = len(x.split(' ')) - 3

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
i = 0
for i in range(num_files):
    start = time.time()
    
    info = os.popen("./../maxcount/scalmc " + filename.split('.')[0] + "-window-" + str(i) + ".cnf").readlines()[-1]
    try:
        num_sols = info.split(': ')[1].split(' x ')
        base, exp = int(num_sols[1].split('^')[0]), int(num_sols[1].split('^')[1].strip("\n"))
        partition_count += int(num_sols[0]) * base**exp
    except:
        continue
    #print("Time for partitioned: " + str(end - start))
    end = time.time()
    print("Time for partitioned : {}".format(end - start))
    i += end-start
i /= num_files

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
print(k)
print("Partitioned Probability: " + str(partition_count/(2**k)))
print("Original Probability: " + str(original_count/(2**k)))
# #convert aiger file to .aag
# os.popen("./../aiger-1.9.9/aigtoaig " + aiger_file + ".aig " + aiger_file + ".aag")
# os.popen("./../aiger-1.9.9/aigand " + aiger_file + ".aag " + aiger_file + ".aig")
# os.popen("./../aiger-1.9.9/aigtoaig " + aiger_file + ".aig " + aiger_file + ".aag")
# os.popen("aigcount " + aiger_file + ".aag")

if aiger:
    os.system("./../aiger-1.9.9/aigtoaig " + aiger_file + ".aig " + aiger_file + ".aag")
    print("aigtoaig")
    os.system("./../aiger-1.9.9/aigand " + aiger_file + ".aag " + aiger_file + ".aig")
    print("aigand")
    os.system("./../aiger-1.9.9/aigtoaig " + aiger_file + ".aig " + aiger_file + ".aag")
    print("aigtoaig")
    os.system("aigcompose " + aiger_file + ".aag " + "tests/raw_files/source.aag " + aiger_file + ".aig")
    print("aigcompose")
    os.system("./../aiger-1.9.9/aigtoaig " + aiger_file + ".aig " + aiger_file + ".aag")
    print("aigtoaig")
    os.system("./../aiger-1.9.9/aigand " + aiger_file + ".aag " + aiger_file + ".aig")
    print("aigand")
    os.system("./../aiger-1.9.9/aigtoaig " + aiger_file + ".aig " + aiger_file + ".aag")
    print("aigtoaig")

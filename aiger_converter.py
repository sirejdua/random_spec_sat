import os, sys, subprocess
aiger_file = sys.argv[1].split('.a')[0]
os.system("./../aiger-1.9.9/aigtoaig " + aiger_file + ".aig " + aiger_file + ".aag")
print("hii")
os.system("./../aiger-1.9.9/aigand " + aiger_file + ".aag " + aiger_file + ".aig")
print("hii")
os.system("./../aiger-1.9.9/aigtoaig " + aiger_file + ".aig " + aiger_file + ".aag")
print("hii")
print(aiger_file)
os.system("aigcount " + aiger_file + ".aag")
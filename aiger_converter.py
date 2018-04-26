import os, sys, subprocess
aiger_file = sys.argv[1].split('.a')[0]
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
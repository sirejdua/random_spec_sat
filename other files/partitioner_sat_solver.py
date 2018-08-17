from cnf_creator import *
import sys
import os
import math
import random
import time
import itertools
import argparse
import subprocess
import numpy as np

####################################
##### PARTITIONER ##################
####################################
num_clauses_initial = 0
output = ""
def get_top_vars(k, c, filename):
    global num_clauses_initial
    #finds top k partitioning variables of formula after c iterations of the solver running
    var_counts = np.zeros(k)
    counting_vars = set()
    #get the number of variables and create the appropriate array
    f = open(filename, 'r')
    found = False
    while not found:
        line = f.readline()
        if line[0] == 'c':
            line = line.split(' ')
            ind_vars = line[2:-1]
            for i in range(len(ind_vars)):
                counting_vars.add(int(ind_vars[i]))
        elif line[0] == 'p':
            line = line.split(' ')
            var_counts = np.zeros(int(line[2]))
            found = True
    f.close()

    #now begin the process of maintaining counts
    counter = 0
    all_found = False
    while not all_found and counter < c:
        #kind of hackish but meh
        os.system('minisat ' + filename + ' ' + filename.split('.')[0]  + '-sol.cnf')
        with open(filename.split('.')[0]  + '-sol.cnf', 'r') as sol_file:
            status = sol_file.readline()
            if 'UNSAT' not in status:
                #if there exists a solution....
                assignments = sol_file.readline().split(' ')[:-1]
                new_assignments = []
                ##construct constraint
                for i in range(len(assignments)):
                    if assignments[i][0] == '-':
                        new_assignments += [assignments[i][1:]]
                    else:
                        if int(assignments[i]) in counting_vars:
                            var_counts[int(assignments[i])] += 1
                        new_assignments += ['-' + assignments[i]]
                assignment = ""
                for a in new_assignments:
                    assignment = assignment + a + ' '
                assignment += '0\n'
                #add constraint to original file
                with open(filename, 'r') as file:
                    data = file.readlines()
                num_data = data[1].split(' ')
                num_data[-1] = str(int(num_data[-1]) + 1) 
                constraints_and_clauses = num_data[0] + ' ' + num_data[1] + ' ' + num_data[2] + ' ' + num_data[3] + '\n'
                data[1] = constraints_and_clauses
                ###write modified info back to the file banning this last solution and adjusting the number of clauses
                with open(filename, 'w') as file:
                    file.writelines(data)
                    if counter == 0:
                        num_clauses_initial = len(data) - 3
                    file.write(assignment)
                counter += 1
            else:
                all_found = True
    #get k top vars
    for i in range(len(var_counts)):
        if i in counting_vars:
            if var_counts[i] < counter - var_counts[i]:
                var_counts[i] = counter - var_counts[i]
        # else:
            # var_values[i] = 1
    var_counts = np.argsort(-var_counts)
    # var_values = np.array([var_values[i] for i in var_counts[:k]])
    return var_counts[:k]

def partition_formula(var_counts, filename):
    n = len(var_counts)
    for index in range(2**n):
        #get binary string corresponding to index
        b = bin(index)[2:]
        l = len(b)
        b = str(0) * (n - l) + b
        ##construct constraint
        assignment = ""
        for i in range(len(b)):
            if b[i] == '1':
                assignment += str(var_counts[i]) + ' 0\n'
            else:
                assignment += '-' + str(var_counts[i]) + ' 0\n'
        #add constraint to original file
        with open(filename.split('.')[0] + ".cnf", 'r') as file:
            data = file.readlines()
        num_data = data[1].split(' ')
        num_data[-1] = str(int(num_data[-1]) + 1) 
        constraints_and_clauses = num_data[0] + ' ' + num_data[1] + ' ' + num_data[2] + ' ' + num_data[3] + '\n'
        data[1] = constraints_and_clauses
        ###write modified info back to the file banning this last solution and adjusting the number of clauses
        name = filename.split('.')[0] + '-window-' + str(index) + '.cnf'
        f = open(name, 'w')
        f.writelines(data)
        f.write(assignment)
        f.close()

#################################
##### END PARTITIONER ###########
#################################
if __name__ == "__main__":
    output = str(sys.argv[1]).split('.')[0]
    with open(output + ".cnf", 'r') as f:
        data = f.readlines()
        with open(output + "copy.cnf", 'w') as filecopy:
            filecopy.writelines(data)
    partition_formula(get_top_vars(4, 10, output + 'copy.cnf'), output + '.cnf')



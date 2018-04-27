from cnf_creator import *
import sys
import os
import math
import random
import pycryptosat
import time
import itertools
import argparse
import subprocess
import numpy as np

###################################
##### RANDOM SAMPLER ##############
###################################

randbool = lambda: random.random() < 0.5

def solverForSample(clauses):
    # set up solver with clauses from original formula
    solver = pycryptosat.Solver()
    for clause in clauses:
        solver.add_clause(clause)
    return solver

def sample_solutions(numMCSamples, counting_vars, clauses): 
    solver = solverForSample(clauses)
    # take samples
    positiveSamples = 0
    for i in range(numMCSamples):
        # generate random assignment to the counting variables
        assumptions = []
        for var in counting_vars.keys():
            if randbool():
                assumptions.append(var)
            else:
                assumptions.append(-var)
        # check if assignment is consistent
        sat, model = solver.solve(assumptions)
        if sat:
            positiveSamples += 1
            for var_assignment in assumptions: 
                if var_assignment > 0:
                    counting_vars[var_assignment] += 1
    return positiveSamples

#############################
##### PARTITIONER ###########
#############################
num_clauses_initial = 0
output = ""
def get_top_vars(k, numMCSamples, filename):
    global num_clauses_initial
    #finds top k partitioning variables of formula after c random samples drawn from the counting variables
    var_counts = np.zeros(k)
    counting_vars = dict()
    #get the number of variables and create the appropriate array
    clauses = []
    counter = 0
    with open(filename, 'r') as f:
        for f_line in f:
            line = f_line.split(' ')
            if line[0] == 'c' and counter == 0:
                ind_vars = line[2:-1]
                counter += 1
                for i in range(len(ind_vars)):
                    counting_vars[int(ind_vars[i])] = 0
            elif line[0] == 'p':
                var_counts = np.zeros(int(line[2]))
            elif line[0] == 'c' and counter != 0:
                continue
            else:
                clauses.append([int(i) for i in line[:-1]])
                counter += 1
    counter = sample_solutions(numMCSamples, counting_vars, clauses)
    for i in counting_vars.keys():
        var_counts[i] = counting_vars[i]
    #get k top vars
    for i in range(len(var_counts)):
        if i in counting_vars:
            if var_counts[i] < counter - var_counts[i]:
                var_counts[i] = counter - var_counts[i]
    var_counts = np.argsort(-var_counts)
    return var_counts[:k]

def partition_formula(var_counts, filename):
    n = len(var_counts)
    for index in range(2**n):
        window_assignments = var_counts.copy()
        #get binary string corresponding to index
        b = bin(index)[2:]
        l = len(b)
        b = str(0) * (n - l) + b
        ##construct constraint
        assignment = ""
        for i in range(len(b)):
            if b[i] == '1':
                continue
            else:
                window_assignments[i] = -var_counts[i]
        #add constraint to original file
        with open(filename, 'r') as file:
            data = file.readlines()

        num_data = []
        new_data = []
        num_clauses = 0
        var_set = set()
        different_vars = False
        for i in range(len(data)):
            if "->" in data[i]:
                continue
            else:
                if "c ind" in data[i]:
                    str_ind = "c ind "
                    for independent_variable in data[i].strip("c ind ").split(' ')[:-1]:
                        if independent_variable not in var_counts:
                            str_ind += str(independent_variable) + " "
                    str_ind += "0\n"
                    new_data += [str_ind]
                elif "p cnf" in data[i]:
                    num_data = data[i].split(' ')
                    num_data[-1] = str(int(num_data[-1]) + n) 
                    constraints_and_clauses = num_data[0] + ' ' + num_data[1] + ' ' + num_data[2] + ' ' + num_data[3] + '\n'
                    data[i] = constraints_and_clauses
                    new_data += [data[i]]
                elif "c" in data[i]:
                    continue
                else:
                    clause = data[i].split(' ')
                    clause = [int(x) for x in clause[:-1]]
                    new_clause = ""
                    add_clause = True
                    different_vars = False
                    for variable in clause:
                        #is the variable assignment consistent with a window assignment? then the clause is already SAT
                        if variable in window_assignments:
                            add_clause = False
                            break
                        #what if all the variables in this are inconsistent with the window assignment? Then the formula is UNSAT
                        elif abs(variable) not in var_counts:
                            different_vars = True
                            new_clause += str(variable) + " "
                            if abs(variable) not in var_set:
                                var_set.add(variable)
                    if add_clause and not different_vars:
                        break
                    if add_clause:
                        num_clauses += 1
                        new_data += [new_clause + "0\n"]
        if different_vars:
            for i in range(len(new_data)):
                if "p cnf" in new_data[i]:
                    num_data = new_data[i].split(' ')
                    constraints_and_clauses = num_data[0] + ' ' + num_data[1] + ' ' + str(len(var_set)) + ' ' + str(num_clauses) + '\n'
                    data[i] = constraints_and_clauses
                    new_data += [data[i]]
            ###write modified info back to the file
            name = filename.split('.cnf')[0] + '-window-' + str(index) + '.cnf'
            with open(name, 'w') as f:
                f.writelines(new_data)
            f.close()

#################################
##### END PARTITIONER ###########
#################################
if __name__ == "__main__":
    output = str(sys.argv[1])
    try:
        k = int(sys.argv[2])
    except:
        k = 4
    # with open(output + ".cnf", 'r') as f:
    #     data = f.readlines()
    #     with open(output + "copy.cnf", 'w') as filecopy:
    #         filecopy.writelines(data)
    partition_formula(get_top_vars(k, 50000, output), output)



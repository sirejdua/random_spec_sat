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
count = 0
var_weights = np.zeros(5) #indicates the likelihood of drawing a 1
def update_weights(assignment_arr, probs, sat=False):
    probs = probs + (1 - probs) * 1/(3*(4 * assignment_arr - 2))
    return probs

def reset_count():
    global count
    count = 0

def random_string_generator(k, probs):
    global count
    assignment_str = ""
    # if count is 0:
    #     update_weights(k, "")
    for i in range(k):
        if random.random() < probs[i]:
            assignment_str += "0"
        else:
            assignment_str += "1"
    return assignment_str

def solverForSample(clauses):
    # set up solver with clauses from original formula
    solver = pycryptosat.Solver()
    for clause in clauses:
        solver.add_clause(clause)
    return solver

def sample_solutions(numSamples, counting_vars, clauses): 
    solver = solverForSample(clauses)
    # take samples
    positiveSamples = 0
    for i in range(numSamples):
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

def countSampleWithMonteCarlo(numMCSamples, counting_vars, clauses):
    solver = solverForSample(clauses)

    # if formula is UNSAT, don't bother sampling
    sat, model = solver.solve()
    if not sat:
        return (0, 0, True)

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

    sampleMant = float(positiveSamples) / numMCSamples
    sampleExp = len(counting_vars.keys())
    while sampleMant > 0 and sampleMant < 1:
        sampleMant *= 2
        sampleExp -= 1
    return (sampleMant, sampleExp, False)

#############################
##### PARTITIONER ###########
#############################

num_clauses_initial = 0
output = ""
counting_vars = dict()
clauses = []
allOne = 0
def get_top_vars(k, numSamples, filename):
    global num_clauses_initial
    #finds top k partitioning variables of formula after c random samples drawn from the counting variables
    var_counts = np.zeros(k)
    global counting_vars
    #get the number of variables and create the appropriate array
    global clauses
    #get the number of positive samples
    global allOne
    counter = 0
    with open(filename, 'r') as f:
        for f_line in f:
            line = f_line.split(' ')
            if "c ind" in f_line:
                ind_vars = line[2:-1]
                counter += 1
                for i in range(len(ind_vars)):
                    counting_vars[int(ind_vars[i])] = 0
            elif line[0] == 'p':
                num_vars_total = int(line[2])
                var_counts = np.zeros(num_vars_total + 1)
                #if no ind vars are specified
            elif line[0] == 'c' and counter != 0:
                continue
            else:
                clauses.append([int(i) for i in line[:-1]])
                counter += 1
    if len(counting_vars.keys()) == 0:
        for i in range(1, len(var_counts)):
            counting_vars[i] = 0
    counter = sample_solutions(numSamples, counting_vars, clauses)
    allOne = (counter == numSamples)
    if counter == 0:
        for i in counting_vars.keys():
            var_counts[i] = 1
    else: 
        for i in counting_vars.keys():
            var_counts[i] = counting_vars[i]
    #get k top vars
    for i in range(len(var_counts)):
        if i in counting_vars:
            if var_counts[i] < counter - var_counts[i]:
                var_counts[i] = counter - var_counts[i]
    var_counts = np.argsort(-var_counts)
    return var_counts

def partition_formula(var_counts, filename): 
    n = len(var_counts)
    for index in range(2**n):
        #get binary string corresponding to index
        write_partition(var_counts, filename, index)

def write_partition(var_counts, filename, index, bin_string = None):
    #var counts: an array with index i representing the ith variable to partition on.
    n = len(var_counts)
    b = bin(index)[2:]
    l = len(b)
    b = str(0) * (n - l) + b
    if bin_string is not None:
        b = bin_string
    ##construct constraint
    assignment = ""
    for i in range(len(b)):
        if b[i] == '1':
            assignment += str(var_counts[i]) + ' 0\n'
        else:
            assignment += '-' + str(var_counts[i]) + ' 0\n'
    #add constraint to original file
    with open(filename, 'r') as file:
        data = file.readlines()
    num_data = []
    for i in range(len(data)):
        if "p cnf" in data[i]:
            num_data = data[i].split(' ')
            num_data[-1] = str(int(num_data[-1]) + n) 
            constraints_and_clauses = num_data[0] + ' ' + num_data[1] + ' ' + num_data[2] + ' ' + num_data[3] + '\n'
            data[i] = constraints_and_clauses
            break
    ###write modified info back to the file
    name = filename.split('.cnf')[0] + '-window-' + str(index) + '.cnf'
    with open(name, 'w') as f:
        f.writelines(data)
        f.write(assignment)
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



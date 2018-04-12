import sys, os, subprocess
from shutil import copyfile
import numpy as np
#try opening up the given file, exit if not possible
convert = True
count = False
output = ""
num_clauses_initial = 0

def convert_to_cnf():
    global output 
    try:
        f = open(str(sys.argv[1]), 'r')
    except:
        print("No file named " + str(sys.argv[1]))
        sys.exit()

    #assemble the variable and clauses list
    clauses = []
    variables = dict()
    counter = 1
    for line in f:
        line = line.strip(' ,')
        #add clauses to list
        line = line.strip("Or").strip("()\n")
        clauses += [line]
        #add variables to set
        line_vars = line.split(', ')
        for var in line_vars:
            var = var.strip("Not()\n,")
            if var not in variables:
                variables[var] = counter
                counter += 1
    f.close()
    print(len(clauses))
    #after obtaining the variable and clause sets...construct the file
    if len(sys.argv) >= 3:
        output = str(sys.argv[2]).split('.')[0]
    else:
        output = str(sys.argv[1]).split('.')[0] 
    with open(output + ".cnf", 'w') as f:
        f.write('c ' + str(sys.argv[1]) + "\n")
        f.write('c\n')
        f.write('p cnf ' + str(len(variables.keys())) + ' ' + str(len(clauses)) + "\n")
        for clause in clauses:
            clause_vars = clause.split(', ')
            line = ""
            for var in clause_vars:
                if var[0] == "N":
                    line += "-"
                var = var.strip("Not()\n,")
                #get the number corresponding to the actual variable
                var = variables[var]
                line = line + str(var) + ' '
            line += "0"
            f.write(line + "\n")
    with open(output + ".cnf", 'r') as f:
        data = f.readlines()
        with open(output + "copy.cnf", 'w') as filecopy:
            filecopy.writelines(data)

################## 
# MODEL COUNTING #
##################
def count_model():
    counter = 0
    all_found = False
    while not all_found:
        #kind of hackish but meh
        os.system('minisat modelcpy.cnf model-sol.cnf')
        with open('model-sol.cnf', 'r') as sol_file:
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
                        new_assignments += ['-' + assignments[i]]
                assignment = ""
                for k in new_assignments:
                    assignment = assignment + k + ' '
                assignment += '0\n'
                #add constraint to original file
                with open('modelcpy.cnf', 'r') as file:
                    data = file.readlines()
                num_data = data[2].split(' ')
                num_data[-1] = str(int(num_data[-1]) + 1) 
                constraints_and_clauses = num_data[0] + ' ' + num_data[1] + ' ' + num_data[2] + ' ' + num_data[3] + '\n'
                data[2] = constraints_and_clauses
                ###write modified info back to the file banning this last solution and adjusting the number of clauses
                with open('modelcpy.cnf', 'w') as file:
                    file.writelines(data)
                    file.write(assignment)
                counter += 1
            else:
                all_found = True
    return counter

###################
#    PARTITION    #
###################
def get_top_vars(k, c, filename):
    global num_clauses_initial
    #finds top k partitioning variables of formula after c iterations of the solver running
    var_counts = np.zeros(k)
    #get the number of variables and create the appropriate array
    f = open(filename, 'r')
    found = False
    while not found:
        line = f.readline()
        if line[0] == 'p':
            line = line.split(' ')
            print("hey")
            var_counts = np.zeros(int(line[2]))
            found = True
            # var_values = np.zeros(int(line[2]))
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
                        var_counts[int(assignments[i])] += 1
                        new_assignments += ['-' + assignments[i]]
                assignment = ""
                for a in new_assignments:
                    assignment = assignment + a + ' '
                assignment += '0\n'
                #add constraint to original file
                with open(filename, 'r') as file:
                    data = file.readlines()
                num_data = data[2].split(' ')
                num_data[-1] = str(int(num_data[-1]) + 1) 
                constraints_and_clauses = num_data[0] + ' ' + num_data[1] + ' ' + num_data[2] + ' ' + num_data[3] + '\n'
                data[2] = constraints_and_clauses
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
        if var_counts[i] < counter - var_counts[i]:
            var_counts[i] = counter - var_counts[i]
        # else:
            # var_values[i] = 1
    var_counts = np.argsort(var_counts)
    print(var_counts)
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
        with open(filename.split('.')[0] + "copy.cnf", 'r') as file:
            data = file.readlines()
        num_data = data[2].split(' ')
        num_data[-1] = str(int(num_data[-1]) + 1) 
        constraints_and_clauses = num_data[0] + ' ' + num_data[1] + ' ' + num_data[2] + ' ' + num_data[3] + '\n'
        data[2] = constraints_and_clauses
        ###write modified info back to the file banning this last solution and adjusting the number of clauses
        name = filename.split('.')[0] + '-window-' + str(index) + '.cnf'
        f = open(name, 'w')
        f.writelines(data)
        f.write(assignment)
        f.close()
################################
if count == True:
    count_model()
    print(counter)
if convert == True:
    convert_to_cnf()
    print(output)
else:
    output = str(sys.argv[1]).split('.')[0]
partition_formula(get_top_vars(4, 10, output + '.cnf'), output + '.cnf')
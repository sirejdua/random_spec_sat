import sys
import math
from dd import cudd as _bdd

def parse_cnf(filename):
    #takes as input a cnf file
    #returns a list containing clauses, and a set containing each of the variables.
    #                           each of these clauses is represented as a list
    #                           ex: [1, -2, 3] <==> (1 \/ (!2) \/ 3)
    fi = open(filename, "r")
    lines = fi.readlines()
    fi.close()

    clauses = []
    current_clause = []
    problem_defined = False
    problem_definition_line = -1
    num_variables = -1
    num_clauses = -1
    variables = set()

    for i, line in zip(range(len(lines)), lines):
        tokens = line.split()
        if len(tokens) > 0:
            if tokens[0] == 'p':
                assert not problem_defined, "Error: problem defined on lines {} and {}".format(problem_definition_line, i)
                assert len(tokens) == 4, "Problem definition on line {} should be \np, [problem type], [number of variables], [number of clauses]"
                assert tokens[1].lower() == 'cnf'
                num_variables, num_clauses = tokens[2], tokens[3]
                assert int(num_variables) > 0 and int(num_clauses) > 0, "Not enough variables or clauses in problem defintion."
                problem_defined = True
                problem_definition_line = i                    
            elif tokens[0] == 'c':
                pass
            else:
                for token in tokens:
                    if token == '0':
                        clauses.append(current_clause)
                        current_clause = []
                    else:
                        token_var = abs(int(token))
                        variables.add("v" + str(token_var))
                        current_clause.append(token)
    assert len(current_clause) == 0, "Last clause not terminated"
    return clauses, variables

def construct_bdd(clauses, variables):
    #takes as input a list of clauses, and a set containing the variable names.
    #returns an equisatisfiable BDD from the dd package.
    bdd = _bdd.BDD()
    bdd.declare(*list(variables))
    #print(bdd)
    clauses_str = []
    for clause in clauses:
        disjunction = []
        for token in clause:
            if token[0] == '-':
                disjunction.append(token.replace('-', '~ v'))

            else:
                disjunction.append('v' + token)
        clauses_str.append('(' + ' \/ '.join(disjunction) + ')') 
        #print(clauses_str)
        #print(variables)
        #sys.exit(1)
    cnf_str = ' /\ '.join(clauses_str)
    #print(cnf_str)
    top_node = bdd.add_expr(cnf_str)
    return bdd, top_node

def model_count_bdd(bdd, node, variables):
    models = list(bdd.pick_iter(node, list(variables)))
    return len(models)

def main(filename):
    clauses, variables = parse_cnf(filename)
    bdd, top_node = construct_bdd(clauses, variables)
    print(model_count_bdd(bdd, top_node, variables))


if __name__ == '__main__':
    assert len(sys.argv) == 2, "Example usage:\n python cnf_converter.py model.cnf"
    main(sys.argv[1])

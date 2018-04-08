import z3
import itertools

# ----------------------------------------
# Part (b): Unique solutions to Sum-Sudoku
# ----------------------------------------

def var(name):
    "Create a variable of the appropriate type here."
    return z3.Int(name)

def var_bv(name):
    "Create a variable of the appropriate type here."
    return z3.BitVec(name, 3)

def val(v):
    """Create an SMT literal of the appropriate type that corresponds to the
    Python integer 'v' here."""
    # If you are using integers to represent the grid variables, you can just
    # return v, but if you are using bit-vectors, you will need to use
    # z3.BitVecVal(v, <width>) to construct a bit-vector literal.
    return z3.BitVecVal(v, 4)

def create_grid(k, initial_x, initial_y):
    S = z3.Solver()
    #k-step unrolling of a 4x4 gridworld deterministic MDP
    s_x = [var('s_{' + str(i) + 'x}') for i in range(k)]
    s_y = [var('s_{' + str(i) + 'y}') for i in range(k)]
    act_x = [var('a_{' + str(i) + 'x}') for i in range(k-1)]
    act_y = [var('a_{' + str(i) + 'y}') for i in range(k-1)]
    #add constraint that forall i, -1 <= a_{xi} <= 1 and the same for the y's
    # S.add(z3.And([act_x[i] <= 1 for i in range(k)]))
    # S.add(z3.And([act_x[i] >= -1 for i in range(k)]))
    # S.add(z3.And([act_y[i] <= 1 for i in range(k)]))
    # S.add(z3.And([act_y[i] >= -1 for i in range(k)]))
    # ##
    # ##add constraint that -2 <= s_{xi} <= 1 and the same for the y
    # S.add(z3.And([s_x[i] <= 1 for i in range(k)]))
    # S.add(z3.And([s_x[i] >= -2 for i in range(k)]))
    # S.add(z3.And([s_y[i] <= 1 for i in range(k)]))
    # S.add(z3.And([s_y[i] >= -2 for i in range(k)]))

    # #add constraint that s_ix = s_{i-1}x + a_{i-1}x
    # S.add(z3.And([s_x[i+1] == s_x[i] + a_x[i] for i in range(k-1)]))
    # S.add(z3.And([s_y[i+1] == s_y[i] + a_y[i] for i in range(k-1)]))

    # S.add(z3.And([s_x[0] == initial_x]))
    # S.add(z3.And([s_y[0] == initial_y]))

    c_0 = z3.And([act_x[i] <= 1 for i in range(k-1)])
    c_1 = z3.And([act_x[i] >= -1 for i in range(k-1)])
    c_2 = z3.And([act_y[i] <= 1 for i in range(k-1)])
    c_3 = z3.And([act_y[i] >= -1 for i in range(k-1)])
    ##
    ##add constraint that -2 <= s_{xi} <= 1 and the same for the y
    c_4 = z3.And([s_x[i] <= 1 for i in range(k)])
    c_5 = z3.And([s_x[i] >= -2 for i in range(k)])
    c_6 = z3.And([s_y[i] <= 1 for i in range(k)])
    c_7 = z3.And([s_y[i] >= -2 for i in range(k)])

    #add constraint that s_ix = s_{i-1}x + a_{i-1}x
    c_8 = z3.And([s_x[i+1] == s_x[i] + act_x[i] for i in range(k-1)])
    c_9 = z3.And([s_y[i+1] == s_y[i] + act_y[i] for i in range(k-1)])

    c_10 = z3.And([s_x[0] == initial_x])
    c_11 = z3.And([s_y[0] == initial_y])

    g = z3.Goal()
    g.add(c_1, c_2, c_3, c_4, c_5, c_6, c_7, c_8, c_9, c_10, c_11)

    z3.describe_tactics()
    t = z3.Tactic('tseitin-cnf')
    print(t(g))

def test():
    x = z3.BitVec('x', 5)
    y = z3.BitVec('y', 5)

    c1 = z3.And(x >= 1, x <= 10)
    c2 = z3.And(y >= 1, y <= 10)
    c3 = z3.Distinct(x,y)

    g = z3.Goal()
    g.add(c1, c2 ,c3)
    # bool_exp = g.AsBoolExpr()

    # t = z3.Tactic('tseitin-cnf')
    # subgoal = t(g.as_expr())
    # z3.print_cnf(subgoal)
    
    # z3.describe_tactics()
    t = z3.Then('simplify', 'bit-blast', 'tseitin-cnf')
    subgoal = t(g)
    assert len(subgoal) == 1
    # Traverse each clause of the first subgoal
    f = open('test.txt', 'w')
    f.write(str(subgoal[0])[1:-1])
    f.close()

def create_grid_bv(k, initial_x, initial_y):
    S = z3.Solver()
    #k-step unrolling of a 4x4 gridworld deterministic MDP
    s_x = [var_bv('s_{' + str(i) + 'x}') for i in range(k)]
    s_y = [var_bv('s_{' + str(i) + 'y}') for i in range(k)]
    act_x = [var_bv('a_{' + str(i) + 'x}') for i in range(k-1)]
    act_y = [var_bv('a_{' + str(i) + 'y}') for i in range(k-1)]

    c_0 = z3.And([act_x[i] <= 1 for i in range(k-1)])
    c_1 = z3.And([act_x[i] >= -1 for i in range(k-1)])
    c_2 = z3.And([act_y[i] <= 1 for i in range(k-1)])
    c_3 = z3.And([act_y[i] >= -1 for i in range(k-1)])
    ##
    ##add constraint that -2 <= s_{xi} <= 1 and the same for the y
    c_4 = z3.And([s_x[i] <= 1 for i in range(k)])
    c_5 = z3.And([s_x[i] >= -2 for i in range(k)])
    c_6 = z3.And([s_y[i] <= 1 for i in range(k)])
    c_7 = z3.And([s_y[i] >= -2 for i in range(k)])

    #add constraint that s_ix = s_{i-1}x + a_{i-1}x
    c_8 = z3.And([s_x[i+1] == s_x[i] + act_x[i] for i in range(k-1)])
    c_9 = z3.And([s_y[i+1] == s_y[i] + act_y[i] for i in range(k-1)])

    c_10 = z3.And([s_x[0] == initial_x])
    c_11 = z3.And([s_y[0] == initial_y])
    g = z3.Goal()
    # S.add([c_0, c_1, c_2, c_3, c_4, c_5, c_6, c_7, c_8, c_9, c_10, c_11])
    g.add([c_1, c_2, c_3, c_4, c_5, c_6, c_7, c_8, c_9, c_10, c_11])
    t = z3.Then('simplify', 'bit-blast', 'tseitin-cnf')
    subgoal = t(g)
    assert len(subgoal) == 1
    # Traverse each clause of the first subgoal
    f = open('model.txt', 'w')
    for c in subgoal[0]:
        f.write(str(c) + "\n")
    f.close()
    return S.to_smt2()

if __name__ == '__main__':
    # test()
    create_grid_bv(3, 0, 0)
    # x = create_grid_bv(3, 0, 0)
    # f = open('model.smt2', 'w')
    # f.write(x)
    # f.close()

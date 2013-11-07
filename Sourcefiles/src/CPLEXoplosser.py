#!/usr/bin/python
# ---------------------------------------------------------------------------
# File: CPLEXoplosser.py
# Version 2.1
# ---------------------------------------------------------------------------
#
# CPLEXoplosser.py - Reading and optimizing a MIP problem
#
# This module is called from the main program, with the file to be solved
# specified as the argument.
#
#    CPLEXoplosser(filename)
# 
# The output is a XML-file with the solution to the MIP-problem.

import cplex
from cplex.exceptions import CplexSolverError

def CPLEXoplosser(filename):
    
    c = cplex.Cplex(filename)
#     c.parameters.tuning.timelimit.set(600.0)
    # Probeer die probleem wat in die toevoerleer gegee is oplos
    try:
        c.solve()
    except CplexSolverError:
        print "Exception raised during solve"
        return
    
    status = c.solution.get_status()
    print c.solution.status[status]
    if status == c.solution.status.unbounded:
        print "Model is unbounded, please ensure all events are bound to at least one other event"
        return
    if status == c.solution.status.infeasible:
        print "Model is infeasible, the model is set too tightly, please relax some constraints"
        return
    if status == c.solution.status.infeasible_or_unbounded:
        print "Model is infeasible or unbounded"
        return
    #c.write("UIT.lp")
    s_type   = c.solution.get_solution_type()
    
    print "Solution status = " , status, ":",
    # the following line prints the status as a string
    print c.solution.status[status]
    
    if s_type == c.solution.type.none:
        print "No solution available"
        return
    print "Objective value = " , c.solution.get_objective_value()
    c.solution.write("solution.sol")
    print '\n\n Solution written to solution.sol'
    print 

# if __name__ == "__main__":
#     if len(sys.argv) != 2:
#         print "Usage: mipex2.py filename"
#         print "  filename   Name of a file, with .mps, .lp, or .sav"
#         print "             extension, and a possible, additional .gz"
#         print "             extension"
#         sys.exit(-1)
#     i97lp(sys.argv[1])
# else:
#     prompt = """Enter the path to a file with .mps, .lp, or .sav
# extension, and a possible, additional .gz extension:
# The path must be entered as a string; e.g. "my_model.mps"\n """
#     fname = input(prompt)
#     i97lp(fname)

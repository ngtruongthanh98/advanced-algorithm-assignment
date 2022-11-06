# https://mlabonne.github.io/blog/linearoptimization/
# Compare solver: https://medium0.com/@chongjingting/4-ways-to-solve-linear-programming-in-python-b4af36b7894d
# Scipy (optimize.linprog) vs PuLP (pulp.LpProblem) vs CVXPY (cp.Problem) vs Gurobi - Gurobipy (Model) vs Pyomo (ConcreteModel) 
# vs PySCIPOpt (Model) vs Google OR-Tools (pywraplp.Solver) vs Gekko (GEKKO) vs Pyomo (ConcreteModel)  vs NAG (naginterfaces.library.opt)
# vs MIPLIB (mip)
# vs CVXOPT (cvxopt.solvers.lp)  vs SCIP Optimization Suite (scip.Model)
# https://www.supplychaindataanalytics.com/using-solvers-for-optimization-in-python/
# https://www.gurobi.com/resources/open-source-linear-and-mixed-integer-programming-software-and-solvers/
# vs COIN-OR vs ilp (old)




# Google OR-Tools: https://github.com/google/or-tools
# https://developers.google.com/optimization/introduction/python
# https://developers.google.com/optimization/
# https://google.github.io/or-tools/python/ortools/linear_solver/pywraplp.html
# !python -m pip install --upgrade --user -q ortools

# Import OR-Tools' wrapper for linear solvers
from ortools.linear_solver import pywraplp

# Create a linear solver using the GLOP backend
solver = pywraplp.Solver('Maximize army power', pywraplp.Solver.GLOP_LINEAR_PROGRAMMING)


# Create the variables we want to optimize
swordsmen = solver.IntVar(0, solver.infinity(), 'swordsmen')
bowmen = solver.IntVar(0, solver.infinity(), 'bowmen')
horsemen = solver.IntVar(0, solver.infinity(), 'horsemen')

# Add constraints for each resource
solver.Add(swordsmen*60 + bowmen*80 + horsemen*140 <= 1200) # Food
solver.Add(swordsmen*20 + bowmen*10 <= 800)                 # Wood
solver.Add(bowmen*40 + horsemen*100 <= 600)                 # Gold

# Maximize the objective function
solver.Maximize(swordsmen*70 + bowmen*95 + horsemen*230)

status = solver.Solve()

# If an optimal solution has been found, print results
if status == pywraplp.Solver.OPTIMAL:
  print('================= Solution =================')
  print(f'Solved in {solver.wall_time():.2f} milliseconds in {solver.iterations()} iterations')
  print()
  print(f'Optimal power = {solver.Objective().Value()} 💪power')
  print('Army:')
  print(f' - 🗡️Swordsmen = {swordsmen.solution_value()}')
  print(f' - 🏹Bowmen = {bowmen.solution_value()}')
  print(f' - 🐎Horsemen = {horsemen.solution_value()}')
else:
  print('The solver could not find an optimal solution.')


# Berth length (S)
#
#
#
#
#
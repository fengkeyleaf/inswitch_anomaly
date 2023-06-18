# -*- coding: utf-8 -*-

import numpy as np
from scipy.optimize import minimize

"""
file:
description:
language: python3 3.11.3
author: @Xiaoyu Tongyang, fengkeyleaf@gmail.com
        Personal website: https://fengkeyleaf.com
"""

__version__ = "1.0"

# Define the objective function
def objective_function(y):
    return -y

# Define the constraint function
def constraint(x):
    return x - np.max(x)

# Set initial guess for y
initial_y = 0.0

# Set the bounds for y
bounds = [(None, None)]  # no bounds on y

# Define the optimization problem
problem = {
    'fun': objective_function,
    'x0': initial_y,
    'bounds': bounds,
    'constraints': {'type': 'ineq', 'fun': constraint}
}

# Solve the optimization problem
result = minimize(**problem)

# Retrieve the optimal value of y
optimal_y = result.x

print("Optimal y:", optimal_y)
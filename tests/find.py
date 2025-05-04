import os
import itertools
import numpy as np

def total_variation_distance(vector1, vector2):
    # Check if both vectors have the same length
    if len(vector1) != len(vector2):
        raise ValueError("Both vectors must have the same length")
    
    # Convert the vectors to numpy arrays for easier calculations
    vector1 = np.array(vector1)
    vector2 = np.array(vector2)
    
    # Normalize the vectors
    vector1 = vector1 / np.sum(vector1)
    vector2 = vector2 / np.sum(vector2)
    
    # Calculate the element-wise absolute difference
    absolute_diff = np.abs(vector1 - vector2)
    
    # Sum the absolute differences and divide by 2
    total_var_distance = 0.5 * np.sum(absolute_diff)
    
    return total_var_distance

def read_cnf_and_weights(file_path):
    cnf_clauses = []
    weights = {}
    with open(file_path, 'r') as f:
        for line in f:
            tokens = line.strip().split()
            if tokens[0] == 'p':
                continue
            elif tokens[0] == 'w':
                var, weight = int(tokens[1]), float(tokens[2])
                weights[var] = weight
            else:
                clause = [int(x) for x in tokens[:-1]]  # Exclude the last '0'
                cnf_clauses.append(clause)
    return cnf_clauses, weights

def is_satisfying_assignment(clauses, assignment):
    for clause in clauses:
        if not any(assignment[abs(lit) - 1] == (lit > 0) for lit in clause):
            return False
    return True

def calculate_assignment_weight(weights, assignment):
    total_weight = 1.0  # Start with 1 for multiplication
    for var, val in enumerate(assignment, start=1):  # Enumerating from 1 to align with CNF variable numbering
        if val:  # if the variable is set to True
            total_weight *= weights.get(var, 1)  # Multiply by the weight of the variable
        else:  # if the variable is set to False
            total_weight *= (1 - weights.get(var, 0))  # Multiply by (1 - weight) of the variable
    return total_weight

def main(folder_path):
    files = [f for f in os.listdir(folder_path) if f.endswith('.cnf')]
    num_vars = 20
    for j in range(100):  # Assuming 10 pairs of files
        file1 = f"{num_vars}_{j}_0.cnf"
        file2 = f"{num_vars}_{j}_1.cnf"

        if file1 in files and file2 in files:

            clauses1, weights1 = read_cnf_and_weights(os.path.join(folder_path, file1))
            clauses2, weights2 = read_cnf_and_weights(os.path.join(folder_path, file2))

            pdf1 = []
            pdf2 = []

            for assignment in itertools.product([False, True], repeat=num_vars):
                if is_satisfying_assignment(clauses1, assignment):
                    pdf1.append(calculate_assignment_weight(weights1, assignment))
                else:
                    pdf1.append(0.0)


                if is_satisfying_assignment(clauses2, assignment):
                    pdf2.append(calculate_assignment_weight(weights2, assignment))
                else:
                    pdf2.append(0.0)

        print(f"{j},{total_variation_distance(pdf1,pdf2)}")

if __name__ == "__main__":
    main('.')  # Replace this with your actual folder path


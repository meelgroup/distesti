import random
import copy
random.seed(12)

def generate_random_3cnf(num_vars, num_clauses):
    cnf_formula = []
    for _ in range(num_clauses):
        clause = []
        for _ in range(3):
            var = random.randint(1, num_vars)  # Choose a random variable from 1 to num_vars
            literal = var if random.random() < 0.5 else -var  # Negate the variable with 50% probability
            clause.append(literal)
        cnf_formula.append(clause)
    return cnf_formula

def cnf_to_dimacs(cnf_formula, num_vars):
    dimacs_list = []
    dimacs_list.append(f"p cnf {num_vars} {len(cnf_formula)}")
    for clause in cnf_formula:
        dimacs_list.append(" ".join(map(str, clause)) + " 0")
    return "\n".join(dimacs_list)

def append_weights(num_vars):
    weight_lines = []
    for i in range(num_vars):
        numerator = random.randint(1, 3)  # Random numerator between 0 and 3
        weight = float(numerator / 4)  # Convert the rational number to a float
        weight_lines.append(f"w {i+1} {weight}")
    return "\n"+"\n".join(weight_lines)

def perturb(cnf_formula, num_vars, num_clauses):
    r = int(random.random()*num_clauses)
    for v in range(3):
        rep = random.randint(1,num_vars)
        rep = rep if random.random()  < 0.5 else -rep
        cnf_formula[r][v] = rep

    return cnf_formula
     
if __name__ == "__main__":
    num_vars = 20
    num_clauses = 25
    
    for j in range(100):
        random_3cnf = generate_random_3cnf(num_vars, num_clauses)
        perturbed = copy.deepcopy(random_3cnf)  # Create a deep copy of random_3cnf
        perturb(perturbed, num_vars, num_clauses)  # Modify the deep copy

        dimacs = cnf_to_dimacs(random_3cnf, num_vars)
        perturbed_dimacs = cnf_to_dimacs(perturbed, num_vars)

        weights = append_weights(num_vars)
        
        with open(f"{num_vars}_{j}_0.cnf", "w") as f:
            f.write(dimacs + weights)
        with open(f"{num_vars}_{j}_1.cnf", "w") as f:
            f.write(perturbed_dimacs + weights)  

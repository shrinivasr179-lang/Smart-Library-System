
import networkx as nx
import matplotlib.pyplot as plt
from itertools import product


# 1. CARTESIAN PRODUCT

def cartesian_product(A, B):
    return list(product(A, B))


# 2. RELATIONS

def create_relation(pairs):
    return set(pairs)


def check_reflexive(A, R):
    return all((a, a) in R for a in A)


def check_symmetric(R):
    return all((b, a) in R for a, b in R)


def check_transitive(R):
    for a, b in R:
        for c, d in R:
            if b == c and (a, d) not in R:
                return False
    return True


# 3. ONE-TO-ONE FUNCTION

def is_one_to_one(function):
    values = list(function.values())
    return len(values) == len(set(values))


# 4. ONTO FUNCTION

def is_onto(function, codomain):
    return set(function.values()) == set(codomain)


# 5. INVERSE FUNCTION

def inverse_function(function):
    if not is_one_to_one(function):
        raise ValueError("Inverse is not a function: mapping is not one-to-one")

    return {v: k for k, v in function.items()}


# 6. ZERO-ONE MATRIX

def zero_one_matrix(A, R):
    matrix = []

    for a in A:
        row = []

        for b in A:
            row.append(1 if (a, b) in R else 0)

        matrix.append(row)

    return matrix


# 7. EQUIVALENCE RELATION

def is_equivalence_relation(A, R):
    return (
        check_reflexive(A, R)
        and check_symmetric(R)
        and check_transitive(R)
    )


# 8. HASSE DIAGRAM

def create_hasse_diagram():

    elements = [1, 2, 4, 8]

    G = nx.DiGraph()
    G.add_nodes_from(elements)

    # Divisibility relation
    for a in elements:
        for b in elements:
            if a < b and b % a == 0:
                # Add only cover relations
                if not any(
                    a < c < b and c % a == 0 and b % c == 0
                    for c in elements
                ):
                    G.add_edge(a, b)

    return G


def display_hasse_diagram():

    G = create_hasse_diagram()

    position = {
        1: (0, 0),
        2: (0, 1),
        4: (0, 2),
        8: (0, 3)
    }

    nx.draw(
        G,
        position,
        with_labels=True,
        node_size=1800,
        node_color="lightblue",
        arrows=False,
        font_size=14
    )

    plt.title("Hasse Diagram - Divisibility Relation")
    plt.savefig("hasse_diagram.png")
    plt.show()


# MAIN PROGRAM

if __name__ == "__main__":

    print("\nINTELLIGENT LIBRARY")
    print("RELATIONS AND FUNCTIONS MODULE")

    A = [1, 2, 3]
    B = ["Python", "Java"]

    # Cartesian Product
    print("\n1. CARTESIAN PRODUCT")
    print(cartesian_product(A, B))

    # Relation
    R = {(1, 1), (2, 2), (3, 3)}

    print("\n2. RELATION PROPERTIES")
    print("Reflexive:", check_reflexive(A, R))
    print("Symmetric:", check_symmetric(R))
    print("Transitive:", check_transitive(R))

    # Function
    function = {1: 2, 2: 4, 3: 6}

    print("\n3. ONE-TO-ONE FUNCTION")
    print(is_one_to_one(function))

    print("\n4. ONTO FUNCTION")
    print(is_onto(function, [2, 4, 6]))

    # Inverse
    print("\n5. INVERSE FUNCTION")
    print(inverse_function(function))

    # Zero-One Matrix
    print("\n6. ZERO-ONE MATRIX")

    matrix = zero_one_matrix(A, R)

    for row in matrix:
        print(row)

    # Equivalence
    print("\n7. EQUIVALENCE RELATION")
    print(is_equivalence_relation(A, R))

    # Hasse Diagram
    print("\n8. HASSE DIAGRAM")
    display_hasse_diagram()

    print("\nRELATIONS AND FUNCTIONS MODULE COMPLETED!")

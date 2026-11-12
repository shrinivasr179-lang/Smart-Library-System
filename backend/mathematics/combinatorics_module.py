
import math


# 1. FUNDAMENTAL COUNTING PRINCIPLE

def sum_rule(a, b):
    return a + b


def product_rule(a, b):
    return a * b


# 2. PERMUTATIONS

def permutation(n, r):
    if n < 0 or r < 0 or r > n:
        raise ValueError("Invalid n and r")
    return math.factorial(n) // math.factorial(n - r)


# 3. COMBINATIONS

def combination(n, r):
    if n < 0 or r < 0 or r > n:
        raise ValueError("Invalid n and r")
    return math.comb(n, r)


# 4. COMBINATIONS WITH REPETITION

def combination_repetition(n, r):
    if n <= 0 or r < 0:
        raise ValueError("Invalid n and r")

    return math.comb(n + r - 1, r)


# 5. BINOMIAL THEOREM

def binomial_coefficient(n, r):
    return math.comb(n, r)


def binomial_expansion(n):
    terms = []

    for r in range(n + 1):
        coefficient = math.comb(n, r)
        terms.append(coefficient)

    return terms


# 6. MATHEMATICAL INDUCTION EXAMPLE
# Sum of first n natural numbers = n(n+1)/2

def natural_sum(n):
    return n * (n + 1) // 2


def verify_induction(n):
    actual_sum = sum(range(1, n + 1))
    formula_sum = natural_sum(n)

    return actual_sum == formula_sum


# 7. WELL ORDERING PRINCIPLE EXAMPLE
# Find the smallest positive number satisfying a condition.

def smallest_number_divisible_by(n, divisor):
    if n < 1 or divisor < 1:
        raise ValueError("Inputs must be positive")

    while n % divisor != 0:
        n += 1

    return n


# MAIN PROGRAM

if __name__ == "__main__":

    print("\nINTELLIGENT LIBRARY")
    print("COUNTING AND COMBINATORICS MODULE")

    print("\n1. FUNDAMENTAL COUNTING PRINCIPLE")

    print("Sum Rule (5 + 3):", sum_rule(5, 3))
    print("Product Rule (5 x 3):", product_rule(5, 3))

    print("\n2. PERMUTATIONS")

    print("P(5, 2):", permutation(5, 2))

    print("\n3. COMBINATIONS")

    print("C(5, 2):", combination(5, 2))

    print("\n4. COMBINATIONS WITH REPETITION")

    print("Repetition C(5, 2):",
          combination_repetition(5, 2))

    print("\n5. BINOMIAL THEOREM")

    print("(x + y)^4 coefficients:",
          binomial_expansion(4))

    print("\n6. MATHEMATICAL INDUCTION")

    print("Sum of first 10 numbers:",
          natural_sum(10))

    print("Induction verification:",
          verify_induction(10))

    print("\n7. WELL ORDERING PRINCIPLE")

    print("Smallest number >= 10 divisible by 4:",
          smallest_number_divisible_by(10, 4))

    print("\nCOMBINATORICS MODULE COMPLETED!")

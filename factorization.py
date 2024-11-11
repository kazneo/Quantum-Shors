import numpy as np

def factorization(N):
    while True:
        # Step 1: Check if N is even
        if N % 2 == 0:
            return (2, N // 2)
        
        # Step 2: Check if N is prime
        if is_prime(N):
            return None  # N is prime, no factors found
        
        # Step 3: Assume N is not a prime power
        a = np.random.randint(2, N)
        
        # Step 4: Find GCD and check if it's non-trivial
        g = gcd(a, N)
        if g != 1 and g != N:
            return (g, N // g)  # Non-trivial factor found
        
        # Step 5: Check if a and N are coprime
        if g == 1:
            # Step 6: Find order r (using a placeholder function)
            r = order_finding(a, N)
            if r is None or r % 2 != 0:
                continue  # If r is odd or not found, repeat
            
            # Step 7: Compute g = gcd(N, a^(r/2) + 1)
            a_r_half = pow(a, r // 2, N)  # Compute a^(r/2) mod N
            g = gcd(N, a_r_half + 1)
            if g != 1 and g != N:
                return (g, N // g)  # Non-trivial factor found

def is_prime(n):
    if n <= 1:
        return False
    for i in range(2, int(n**0.5) + 1):
        if n % i == 0:
            return False
    return True

# Function to find greatest common divisor
def gcd(a, b):
    while b:
        a, b = b, a % b
    return a

def order_finding(a, N):
    # Placeholder for quantum order finding
    # In practice, this should be replaced with a quantum algorithm
    for r in range(1, N):
        if pow(a, r, N) == 1:
            return r
    return None

if __name__ == "__main__":
    N = 213  # Example number to factor
    print (N)
    factors = factorization(N)
    print(f"Factors of {N}: {factors}")
from qiskit import QuantumCircuit
from qiskit.quantum_info import SparsePauliOp
from qiskit.transpiler.preset_passmanagers import generate_preset_pass_manager
from qiskit_ibm_runtime import EstimatorV2 as Estimator
from qiskit_ibm_runtime import QiskitRuntimeService
from qiskit_ibm_runtime import SamplerV2 as Sampler
from qiskit.circuit.library import GroverOperator, MCMT, ZGate
from qiskit.visualization import plot_distribution

from qiskit.circuit.library import QFT

import math
import numpy as np
import random

#N = 33
N = 1001 
#N = 1203 # kind of an upper bound. For some reason the classical initialization is too slow here. 
num_qubits = math.ceil(math.log2(N)) # <-- number of qubits, on the order of log_2 of the target number 
num_qubits_0 = 2 * num_qubits # <-- twice as many ancillary qubits 
pi = math.pi

print("num_qubits:", num_qubits)

# Function dump 
def c_amodN(a, power, n_qubits): 
    # Applies circuits for modulo exponentiation 
        U = QuantumCircuit(num_qubits)
        for iteration in range(power): 
            if(a % 2 != 0):
                for q in range(n_qubits//2):
                    U.x(q) 
        U = U.to_gate() 
        c_U = U.control(1) 
        
        return c_U 


def controlled_U(circuit, num_qubit, a): 
    #Applies a controlled U to a circuit
    for q in range(num_qubits_0): 
        cir = c_amodN(a, 2**q, num_qubit) 
        circuit.append(cir, [q] + [i + num_qubits_0 for i in range(num_qubits)])
    return circuit 


def psi(circuit, num_qubit, a): 
    # Not really used, but an alternate way to make a transition state 
    circuit.x(-1)
    circuit.barrier()
    circuit = controlled_U(circuit, num_qubit, a)
    return circuit


def modexp(a, k, base): 
    # An alternate way to compute a modulo exponentiation 
    num = a**k 
    while(num >= base): #problem arises here, need a faster way to dial in an upper bound. 
        num -= base 
    return num 


def qft_rotations(circuit, n):
    # A helper for the Quantum Fourier Transform circuit 
    if n == 0:
        return circuit
    n -= 1
    circuit.h(n)
    for qubit in range(n):
        circuit.cp(pi/2**(n-qubit), qubit, n)
    qft_rotations(circuit, n)

def swap_registers(circuit, n):
    # Another helper for the QFT 
    for qubit in range(n//2):
        circuit.swap(qubit, n-qubit-1)
    return circuit

def qft(circuit, n): 
    # Applies the Quantum Fourier Transform 
    qft_rotations(circuit, n)
    swap_registers(circuit, n)
    return circuit

def inverse_qft(circuit, n):
    # Inverts the QFT 
    qft_circ = qft(QuantumCircuit(n), n)
    invqft_circ = qft_circ.inverse()
    circuit.append(invqft_circ, circuit.qubits[:n])
    return circuit.decompose() 

def gcd(c, b): 
    # Euclid's Algorithm for finding the greatest common divisor of two numbers 
        if c == 0:
            return b
        return gcd(b % a, a)


# Start of the classical section of Shor's Algorithm 
if(N % 2 == 0): 
    print("Trivial factors found:") 
    print(int(N/2), 2)
    exit() 

# Determine if prime power at some point 
# Do that here. 
keepGoing = 1

while(keepGoing == 1):

    a = random.randint(1,N-1) # pick a random integer 
    print("a =", a)

    
    myGcd = gcd(a, N) 
    if(myGcd != 1 and N/myGcd//1 == N/myGcd):
        print("Trivial factors found:")
        print(myGcd, int(N/myGcd)) 
        exit() 
        
    print("past gcd")

    # Create a new circuit with two qubits
    qc = QuantumCircuit(num_qubits + num_qubits_0)

    # Hadamards on the 0 qubits 
    for i in range(num_qubits_0):
        qc.h(i)

    # X gates to prepare the 1 qubits 
    for i in range(num_qubits):
        qc.x(num_qubits_0 + i)

    # Apply Controlled-U_f gates on the 1 qubits 
    for q in range(num_qubits_0): 
        cir = c_amodN(a, 2**q, num_qubits) 
        qc.append(cir, [q] + [i + num_qubits_0 for i in range(num_qubits)])

    print("past first half of circuit")

    # Apply the inverse QFT to the 0 qubits and measure 
    inverse_qft(qc,num_qubits_0)
    qc.measure_all()

    qc.draw("mpl", filename = 'shorCircuit.png')

    scaleNum = 2 # for debugging purposes 

    print("full circuit processed")
    
    # my actual API key 
    service = QiskitRuntimeService(channel="ibm_quantum", token={token})
    backend = service.backend("ibm_rensselaer")

    target = backend.target
    pm = generate_preset_pass_manager(target=target, optimization_level=3)

    circuit_isa = pm.run(qc)
    circuit_isa.draw(output="mpl", idle_wires=False, style="iqp")

    sampler = Sampler(backend=backend)
    sampler.options.default_shots = 10_000
    result = sampler.run([circuit_isa]).result()
    dist = result[0].data.meas.get_counts()

    scaleNum = num_qubits

    print(dist)
    

    """
    dist = {
    '000000': 596, 
    '010010': 986, 
    '011011': 752, 
    '010011': 1931,
    '001001': 668, 
    '000010': 733, 
    '010000': 440, 
    '001000': 173, 
    '011000': 264, 
    '001011': 1689,
    '011001': 553, 
    '001110': 37, 
    '000101': 11, 
    '011010': 192, 
    '001010': 676, 
    '000001': 94, 
    '010001': 268, 
    '000011': 171, 
    '000100': 14, 
    '011110': 16, 
    '001111': 35, 
    '001100': 32, 
    '011111': 9, 
    '010111': 52, 
    '001101': 34, 
    '010101': 34, 
    '010100': 30, 
    '000111': 24, 
    '100010': 4, 
    '010110': 26, 
    '000110': 13, 
    '011101': 11, 
    '111011': 5, 
    '101011': 6, 
    '110011': 3, 
    '011100': 6, 
    '101010': 2, 
    '101001': 3, 
    '110010': 3, 
    '110001': 1, 
    '111001': 1, 
    '110000': 1, 
    '100000': 1}
    """
    #print(dist) 

    # Interpret the distribution of results for 10000 shots 
    maxVal = 0
    maxKey = ""
    for key in dist: 
        if(dist[key] > maxVal): 
            maxVal = dist[key]
            maxKey = key 

    print(maxVal)
    print(maxKey)

    maxKey = maxKey[scaleNum:]
    maxKey = maxKey[::-1]
    print(maxKey)

    # Back to the classical part of the algorithm 
    r = int(maxKey,2)
    r = int(2**num_qubits_0 / r)

    print(r)

    #plot_distribution(dist)

    # Repeat from the very beginning if the number you got was odd. 
    if(r % 2 == 1): 
        print("r:", r)
        print("r odd, restarting") 
        continue 
    else: 
        print("r:", r)
        keepGoing = 0

    g = gcd(N, a**(r/2)+1)
    
    # Hope that your simulation survived all the errors from the quantum computer and determine a result 
    print("Factors:", g, N/g)
    
    break


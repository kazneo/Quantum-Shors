# -*- coding: utf-8 -*-
"""
Created on Tue Oct  8 12:48:39 2024

@author: Seth
"""

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

num_qubits = 2
num_qubits_0 = 2 * num_qubits
N = 7
a = random.randint(1,N)
print(a)

# Create a new circuit with two qubits
qc = QuantumCircuit(num_qubits + num_qubits_0)

for i in range(num_qubits_0):
    qc.h(i)
 
# Add a Hadamard gate to qubit 0
#qc.h(0)
 
# Perform a controlled-X gate on qubit 1, controlled by qubit 0
#qc.cx(0, 1)
 
# Return a drawing of the circuit using MatPlotLib
pi = math.pi
# State prep 
#qc.x(0)
#qc = qc + QFT(num_qubits=4, approximation_degree=0, do_swaps=True, inverse=False, insert_barriers=True, name='qft')


def c_amodN(a, power, n_qubits): 
    """
    Controlled multiplication by a mod N 
    a -- rand num btwn 1 and N 
    power -- 2^a??? 
    """
    U = QuantumCircuit(num_qubits)
    for iteration in range(power): 
        if(a % 2 != 0):
            for q in range(n_qubits//2):
                U.x(q) 
    U = U.to_gate() 
    c_U = U.control(1) 
    
    return c_U 

"""
def controlled_U(circuit, num_qubit, a): 
    #Applies a controlled U to a circuit
    for q in range(num_qubit): 
        cir = c_amodN(a, 2**q, num_qubit) 
        circuit.append(cir, [q] + [i+num_qubit for i in range(num_qubit//2)])
        #circuit.append(cir)
    return circuit 
"""

def controlled_U(circuit, num_qubit, a): 
    #Applies a controlled U to a circuit
    for q in range(num_qubits_0): 
        cir = c_amodN(a, 2**q, num_qubit) 
        circuit.append(cir, [q] + [i + num_qubits_0 for i in range(num_qubits)])
        #circuit.append(cir)
    return circuit 

"""
def controlled_U(circuit, num_qubit, a): 
    for q in range(num_qubit): 
        cir = c_amodN(a, 2**q, num_qubit)
        for i in range(num_qubit//2): 
            val = i + num_qubit 
            if(val >= num_qubit):
                val = num_qubit - 1
            circuit.append(cir, [q] + [val])
        #circuit.append(cir)
    return circuit 
"""

def psi(circuit, num_qubit, a): 
    circuit.x(-1)
    circuit.barrier()
    circuit = controlled_U(circuit, num_qubit, a)
    return circuit


def modexp(a, k, base): 
    num = a**k 
    while(num >= base): #problem arises here, need a faster way to dial in an upper bound. 
        num -= base 
    return num 

#for i in range(8):
    #print(modexp(2, i, 21))

"""
myMatrix = [] 

def makeRow(a, N, row, num_qubits):
    # We can transpose this later 
    myRow = []
    modResult = modexp(a, row, N) 
    for i in range(modResult): 
        myRow.append(0)
    myRow.append(1)
    for i in range(modResult+1, 2**num_qubits): 
        myRow.append(0) 
    return myRow
        
#print(makeRow(0,3,[], 0, 3))

for i in range(2**num_qubits): 
    print("started")
    myMatrix.append(makeRow(a, N, i, num_qubits))
    print("done")
    print(i)
    
print(myMatrix) 

def transpose(matrix): 
    mat2 = []
    
    for i in range(len(matrix)): 
        emptyRow = [] 
        for k in range(len(matrix)):
            emptyRow.append(0) 
        mat2.append(emptyRow) 
        
    for i in range(len(matrix)): 
        for k in range(len(matrix)): 
            mat2[i][k] = matrix[k][i] 
    return mat2 

myMatrix = transpose(myMatrix) 
print(myMatrix)
"""    
#qc.unitary(myMatrix, [0,1,2,3])


def qft_rotations(circuit, n):
    if n == 0:
        return circuit
    n -= 1
    circuit.h(n)
    for qubit in range(n):
        circuit.cp(pi/2**(n-qubit), qubit, n)
    qft_rotations(circuit, n)

def swap_registers(circuit, n):
    for qubit in range(n//2):
        circuit.swap(qubit, n-qubit-1)
    return circuit

def qft(circuit, n):
    qft_rotations(circuit, n)
    swap_registers(circuit, n)
    return circuit

def inverse_qft(circuit, n):
    qft_circ = qft(QuantumCircuit(n), n)
    invqft_circ = qft_circ.inverse()
    circuit.append(invqft_circ, circuit.qubits[:n])
    return circuit.decompose() 




for q in range(num_qubits_0): 
    cir = c_amodN(a, 2**q, num_qubits) 
    print(cir)
    qc.append(cir, [q] + [i + num_qubits_0 for i in range(num_qubits)])
        #circuit.append(cir)



#qc = controlled_U(qc, num_qubits, a)
inverse_qft(qc,4)


qc.measure_all()

qc.draw("mpl", filename = 'shorCircuit.png')


#qc.draw("mpl")

"""
service = QiskitRuntimeService(channel="ibm_quantum", token=[])
backend = service.backend("ibm_rensselaer")

target = backend.target
pm = generate_preset_pass_manager(target=target, optimization_level=3)
#pm = generate_preset_pass_manager(optimization_level=1)


circuit_isa = pm.run(qc)
circuit_isa.draw(output="mpl", idle_wires=False, style="iqp")
"""
"""
from qiskit.primitives import StatevectorEstimator
estimator = StatevectorEstimator()


from qiskit.primitives import StatevectorSampler
pm = generate_preset_pass_manager(optimization_level=1)

isa_circuit = pm.run(qc)

sampler = StatevectorSampler()
job = sampler.run([isa_circuit])
dist = job.result()[0].data.meas.get_counts()  
"""

"""
sampler = Sampler(backend=backend)
sampler.options.default_shots = 10_000
result = sampler.run([circuit_isa]).result()
dist = result[0].data.meas.get_counts()
"""
"""
observable = SparsePauliOp(["II", "XX", "YY", "ZZ"], coeffs=[1, 1, -1, 1])
isa_circuit = pm.run(qc)
isa_observable = observable.apply_layout(isa_circuit.layout)
job = estimator.run([(isa_circuit, isa_observable)])
result = job.result()
dist = result[0].data.meas.get_counts()
"""

#print(dist)

#plot_distribution(dist)

"""
# Convert to an ISA circuit and layout-mapped observables.
pm = generate_preset_pass_manager(backend=backend, optimization_level=1)
isa_circuit = pm.run(qc)
 
isa_circuit.draw('mpl', idle_wires=False)

estimator = Estimator(mode=backend)
estimator.options.resilience_level = 1
estimator.options.default_shots = 10000
 
mapped_observables = [
    observable.apply_layout(isa_circuit.layout) for observable in observables
]
 
# One pub, with one circuit to run against five different observables.
job = estimator.run([(isa_circuit, mapped_observables)])
 
# Use the job ID to retrieve your job data later
print(f">>> Job ID: {job.job_id()}")

job_result = job.result()
 
# This is the result from our single pub, which had six observables,
# so contains information on all six.
pub_result = job.result()[0]
"""
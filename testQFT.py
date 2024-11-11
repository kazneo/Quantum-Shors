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


 
# Create a new circuit with two qubits
qc = QuantumCircuit(4)
 
# Add a Hadamard gate to qubit 0
#qc.h(0)
 
# Perform a controlled-X gate on qubit 1, controlled by qubit 0
#qc.cx(0, 1)
 
# Return a drawing of the circuit using MatPlotLib
pi = math.pi
# State prep 
#qc.x(0)
#qc = qc + QFT(num_qubits=4, approximation_degree=0, do_swaps=True, inverse=False, insert_barriers=True, name='qft')

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

inverse_qft(qc,4)


#qc.measure_all()

qc.draw("mpl", filename = 'qftCircuit.png')


#qc.draw("mpl")

"""
service = QiskitRuntimeService(channel="ibm_quantum", token={Token})
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
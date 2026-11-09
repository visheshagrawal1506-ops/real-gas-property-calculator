import numpy as np
import math

from eos import calculate_pvt
from gas_data import (
    get_gas_properties,
    REFERENCE_TEMPERATURE,
    REFERENCE_PRESSURE,
    S_REFERENCE
)

R_BAR = 0.08314462618       # L.bar/(mol.K)
R_J = 8.314462618           # J/(mol.K)

def calculate_daT_dT(gas, T, a, kappa):

    properties = get_gas_properties(gas)

    Tc = properties["Tc"]

    g = 1 + kappa * (1 - math.sqrt(T / Tc))

    dalpha_dT = -kappa * g / math.sqrt(T * Tc)

    daT_dT = a * dalpha_dT

    return daT_dT

def calculate_ideal_entropy(gas, T, P):

    properties = get_gas_properties(gas)

    Cp = properties["Cp_ig"]

    S_ideal = (
        S_REFERENCE
        + Cp * math.log(T / REFERENCE_TEMPERATURE)
        - R_J * math.log(P / REFERENCE_PRESSURE)
    )

    return S_ideal

def calculate_entropy_departure(gas, T, P, pvt_results, phase="vapor"):

    parameters = pvt_results["parameters"]

    a = parameters["a"]
    b = parameters["b"]
    alpha = parameters["alpha"]
    kappa = parameters["kappa"]
    B = parameters["B"]

    aT = a * alpha

    daT_dT = calculate_daT_dT(gas, T, a, kappa)

    if phase == "vapor":
        Z = pvt_results["Z_vapor"]

    elif phase == "liquid":
        Z = pvt_results["Z_liquid"]

    else:
        raise ValueError("Phase must be 'vapor' or 'liquid'.")

    numerator = Z + (1 + math.sqrt(2)) * B
    denominator = Z + (1 - math.sqrt(2)) * B

    if Z - B <= 0 or numerator <= 0 or denominator <= 0:
        raise ValueError("Invalid values for entropy calculation.")

    log_term = math.log(numerator / denominator)

    S_departure = R_J * (
        math.log(Z - B)
        + (daT_dT / (2 * math.sqrt(2) * b * R_BAR))
        * log_term
    )

    return S_departure


def calculate_entropy(gas, T, P, pvt_results, phase="vapor"):

    S_ideal = calculate_ideal_entropy(gas, T, P)

    S_departure = calculate_entropy_departure(
        gas, T, P, pvt_results, phase
    )

    S_total = S_ideal + S_departure

    return {
        "S_ideal": S_ideal,
        "S_departure": S_departure,
        "S_total": S_total
    }

if __name__ == "__main__":

    gas = "methane"

    T = 300.0
    P = 50.0

    gas_properties = get_gas_properties(gas)

    pvt_results = calculate_pvt(gas_properties, T, P)

    results = calculate_entropy(
        gas, T, P, pvt_results, phase="vapor"
    )

    print("\n================================")
    print("ENTROPY CALCULATION")
    print("================================")

    print(f"\nGas: {get_gas_properties(gas)['name']}")
    print(f"Temperature: {T} K")
    print(f"Pressure: {P} bar")

    print("\nIDEAL GAS ENTROPY")
    print(f"S ideal = {results['S_ideal']:.4f} J/(mol.K)")

    print("\nENTROPY DEPARTURE")
    print(f"S departure = {results['S_departure']:.4f} J/(mol.K)")

    print("\nTOTAL REAL GAS ENTROPY")
    print(f"S total = {results['S_total']:.4f} J/(mol.K)")

    print("\n================================")

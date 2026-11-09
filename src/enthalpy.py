import math
import numpy as np

from eos import calculate_pvt
from gas_data import (
    get_gas_properties,
    REFERENCE_TEMPERATURE,
    H_REFERENCE
)

R = 0.08314462618

CONVERSION_FACTOR = 100.0

def calculate_daT_dT(gas, T, a, kappa):

    properties = get_gas_properties(gas)

    Tc = properties["Tc"]

    g = 1 + kappa * (1 - math.sqrt(T / Tc))

    dalpha_dT = -kappa * g / math.sqrt(T * Tc)

    daT_dT = a * dalpha_dT

    return daT_dT

def calculate_ideal_enthalpy(gas, T):

    properties = get_gas_properties(gas)

    Cp = properties["Cp_ig"]

    T_ref = REFERENCE_TEMPERATURE

    H_ref = H_REFERENCE

    # Constant heat capacity approximation

    H_ideal = H_ref + Cp * (T - T_ref)

    return H_ideal

def calculate_enthalpy_departure(
    gas, T, pvt_results, phase="vapor"
):

    parameters = pvt_results["parameters"]

    a = parameters["a"]
    b = parameters["b"]
    alpha = parameters["alpha"]
    kappa = parameters["kappa"]
    B = parameters["B"]

    if phase == "vapor":
        Z = pvt_results["Z_vapor"]

    elif phase == "liquid":
        Z = pvt_results["Z_liquid"]

    else:
        raise ValueError(
            "Phase must be 'vapor' or 'liquid'."
        )

    aT = a * alpha

    daT_dT = calculate_daT_dT(
        gas, T, a, kappa
    )
    numerator = Z + (1 + np.sqrt(2)) * B

    denominator = Z + (1 - np.sqrt(2)) * B

    if numerator <= 0 or denominator <= 0:
        raise ValueError(
            "Invalid logarithm argument in enthalpy calculation."
        )

    log_term = np.log(numerator / denominator)

    H_departure_Lbar = (
        R * T * (Z - 1)
        +
        (
            T * daT_dT - aT
        ) / (2 * np.sqrt(2) * b) * log_term
    )

    H_departure = (
        H_departure_Lbar * CONVERSION_FACTOR
    )

    return H_departure

def calculate_enthalpy(
    gas, T, pvt_results, phase="vapor"
):

    H_ideal = calculate_ideal_enthalpy(
        gas, T
    )

    H_departure = calculate_enthalpy_departure(
        gas, T, pvt_results, phase
    )

    H_total = H_ideal + H_departure

    return {
        "H_ideal": H_ideal,
        "H_departure": H_departure,
        "H_total": H_total
    }
if __name__ == "__main__":

    gas = get_gas_properties("methane")

    T = 300.0
    P = 50.0

    pvt_results = calculate_pvt(
        gas, T, P
    )

    results = calculate_enthalpy(
        gas, T, pvt_results
    )

    print("\n================================")
    print("ENTHALPY CALCULATION")
    print("================================")

    print("\nGas:", gas["name"])

    print("Temperature:", T, "K")
    print("Pressure:", P, "bar")

    print("\nIDEAL GAS ENTHALPY")

    print(
        f"H ideal = {results['H_ideal']:.4f} J/mol"
    )

    print("\nENTHALPY DEPARTURE")

    print(
        f"H departure = {results['H_departure']:.4f} J/mol"
    )

    print("\nTOTAL REAL GAS ENTHALPY")

    print(
        f"H total = {results['H_total']:.4f} J/mol"
    )

    print("\n================================")

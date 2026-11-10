import math
import numpy as np
from eos import calculate_pvt
from gas_data import (
    get_gas_properties,
    REFERENCE_TEMPERATURE,
    REFERENCE_PRESSURE,
    S_REFERENCE
)
R_BAR = 0.08314462618     
R_J = 8.314462618         


def get_gas_data(gas):
    if isinstance(gas, dict):
        return gas
    return get_gas_properties(gas)


def calculate_ideal_entropy(gas, T, P):
    if T <= 0 or P <= 0:
        raise ValueError(
            "Temperature and pressure must be positive."
        )
    properties = get_gas_data(gas)
    Cp = properties["Cp_ig"]
    S_ideal = (
        S_REFERENCE
        + Cp * math.log(T / REFERENCE_TEMPERATURE)
        - R_J * math.log(P / REFERENCE_PRESSURE)
    )
    return S_ideal


def get_selected_phase(pvt_results, phase):
    phase = str(phase).strip().lower()
    if phase in ("vapor", "vapour"):
        return "vapor"
    if phase == "liquid":
        return "liquid"
    if phase in (
        "auto",
        "auto (stable phase)",
        "stable",
        "single phase"
    ):
        stable_phase = pvt_results["stable_phase"].lower()
        if stable_phase == "liquid":
            return "liquid"
        return "vapor"
    raise ValueError(
        "Phase must be vapor, liquid or Auto (Stable Phase)."
    )


def calculate_entropy_departure(
    gas, T, P, pvt_results, phase="vapor", eos_model="PR"
):

    parameters = pvt_results["parameters"]
    b = parameters["b"]
    da_dT = parameters["da_dT"]
    B = parameters["B"]
    delta1 = parameters["delta1"]
    delta2 = parameters["delta2"]
    selected_phase = get_selected_phase(
        pvt_results, phase
    )
    if selected_phase == "vapor":
        Z = pvt_results["Z_vapor"]
    else:
        Z = pvt_results["Z_liquid"]

    if Z - B <= 0:
        raise ValueError(
            "Invalid value of Z - B in entropy calculation."
        )
    S_first = R_J * math.log(Z - B)
    if abs(delta1 - delta2) < 1e-12:
        return S_first
    numerator = Z + delta1 * B
    denominator = Z + delta2 * B
    if numerator <= 0 or denominator <= 0:
        raise ValueError(
            "Invalid logarithm argument in entropy calculation."
        )
    log_term = math.log(numerator / denominator)
    S_attraction = (
        R_J
        * da_dT
        / (b * (delta1 - delta2) * R_BAR)
        * log_term
    )
    S_departure = S_first + S_attraction
    return S_departure


def calculate_entropy(
    gas, T, P, pvt_results, phase="vapor", eos_model="PR"
):

    if T <= 0 or P <= 0:
        raise ValueError(
            "Temperature and pressure must be positive."
        )

    S_ideal = calculate_ideal_entropy(
        gas, T, P
    )

    S_departure = calculate_entropy_departure(
        gas,
        T,
        P,
        pvt_results,
        phase,
        eos_model
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
    eos_models = ["PR", "SRK", "RK", "VDW"]
    for model in eos_models:
        pvt_results = calculate_pvt(
            gas_properties, T, P, model
        )
        results = calculate_entropy(
            gas,
            T,
            P,
            pvt_results,
            phase="vapor",
            eos_model=model
        )
        print("\n================================")
        print(model, "ENTROPY CALCULATION")
        print("================================")
        print(f"\nGas: {gas_properties['name']}")
        print(f"Temperature: {T} K")
        print(f"Pressure: {P} bar")
        print("\nIDEAL GAS ENTROPY")
        print(
            f"S ideal = {results['S_ideal']:.4f} J/(mol.K)"
        )
        print("\nENTROPY DEPARTURE")
        print(
            f"S departure = {results['S_departure']:.4f} J/(mol.K)"
        )
        print("\nTOTAL REAL GAS ENTROPY")

        print(
            f"S total = {results['S_total']:.4f} J/(mol.K)"
        )
        print("\n================================")

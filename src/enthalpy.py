import math
import numpy as np

from eos import calculate_pvt
from gas_data import (
    get_gas_properties,
    REFERENCE_TEMPERATURE,
    H_REFERENCE
)

R = 0.08314462618
R_J = 8.314462618
CONVERSION_FACTOR = 100.0
def get_gas_data(gas):
    if isinstance(gas, dict):
        return gas
    return get_gas_properties(gas)


def calculate_ideal_enthalpy(gas, T):
    properties = get_gas_data(gas)
    Cp = properties["Cp_ig"]
    T_ref = REFERENCE_TEMPERATURE
    H_ref = H_REFERENCE
    H_ideal = H_ref + Cp * (T - T_ref)
    return H_ideal


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


def calculate_enthalpy_departure(
    gas, T, pvt_results, phase="vapor", eos_model="PR"
):
    parameters = pvt_results["parameters"]
    a = parameters["a"]
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
    H_first = R_J * T * (Z - 1)
    if abs(delta1 - delta2) < 1e-12:
        V = pvt_results["V_vapor"] if selected_phase == "vapor" else pvt_results["V_liquid"]
        H_attraction = -CONVERSION_FACTOR * a / V
        H_departure = H_first + H_attraction
        return H_departure
    numerator = Z + delta1 * B
    denominator = Z + delta2 * B
    if numerator <= 0 or denominator <= 0:
        raise ValueError(
            "Invalid logarithm argument in enthalpy calculation."
        )
    log_term = np.log(numerator / denominator)
    H_attraction = (
        CONVERSION_FACTOR
        * (T * da_dT - a)
        / (b * (delta1 - delta2))
        * log_term
    )
    H_departure = H_first + H_attraction
    return H_departure


def calculate_enthalpy(
    gas, T, pvt_results, phase="vapor", eos_model="PR"
):
    if T <= 0:
        raise ValueError("Temperature must be positive.")
    H_ideal = calculate_ideal_enthalpy(
        gas, T
    )
    H_departure = calculate_enthalpy_departure(
        gas,
        T,
        pvt_results,
        phase,
        eos_model
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
    eos_models = ["PR", "SRK", "RK", "VDW"]
    for model in eos_models:
        pvt_results = calculate_pvt(
            gas, T, P, model
        )
        results = calculate_enthalpy(
            gas,
            T,
            pvt_results,
            phase="vapor",
            eos_model=model
        )
        print("\n================================")
        print(model, "ENTHALPY CALCULATION")
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

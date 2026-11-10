import math

from eos import calculate_pvt, calculate_ln_phi
from gas_data import get_gas_properties


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


def calculate_fugacity_coefficient(
    pvt_results, phase="vapor", eos_model="PR"
):

    parameters = pvt_results["parameters"]

    A = parameters["A"]
    B = parameters["B"]

    selected_phase = get_selected_phase(
        pvt_results, phase
    )

    if selected_phase == "vapor":
        Z = pvt_results["Z_vapor"]
    else:
        Z = pvt_results["Z_liquid"]

    if B <= 0 or Z - B <= 0:
        raise ValueError(
            "Invalid values for fugacity calculation."
        )

    # Use the generalized fugacity equation from eos.py
    ln_phi = calculate_ln_phi(
        Z, A, B, parameters
    )

    phi = math.exp(ln_phi)

    return {
        "ln_phi": ln_phi,
        "phi": phi,
        "Z": Z,
        "phase": selected_phase
    }


def calculate_fugacity(
    gas, T, P, pvt_results, phase="vapor", eos_model="PR"
):

    if T <= 0 or P <= 0:
        raise ValueError(
            "Temperature and pressure must be positive."
        )

    coefficient_results = calculate_fugacity_coefficient(
        pvt_results,
        phase,
        eos_model
    )

    phi = coefficient_results["phi"]

    # Pure-component fugacity
    fugacity = phi * P

    return {
        "ln_phi": coefficient_results["ln_phi"],
        "phi": phi,
        "fugacity": fugacity,
        "Z": coefficient_results["Z"],
        "phase": coefficient_results["phase"]
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

        results = calculate_fugacity(
            gas,
            T,
            P,
            pvt_results,
            phase="vapor",
            eos_model=model
        )

        print("\n================================")
        print(model, "FUGACITY CALCULATION")
        print("================================")

        print(f"\nGas: {gas_properties['name']}")
        print(f"Temperature: {T} K")
        print(f"Pressure: {P} bar")

        print("\nFUGACITY COEFFICIENT")

        print(
            f"ln(phi) = {results['ln_phi']:.6f}"
        )

        print(
            f"phi = {results['phi']:.6f}"
        )

        print("\nPURE COMPONENT FUGACITY")

        print(
            f"Fugacity = {results['fugacity']:.6f} bar"
        )

        print("\n================================")

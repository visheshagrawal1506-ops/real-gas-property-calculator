
import math

from eos import calculate_pvt
from gas_data import get_gas_properties

def calculate_fugacity_coefficient(pvt_results, phase="vapor"):

    parameters = pvt_results["parameters"]

    A = parameters["A"]
    B = parameters["B"]

    if phase == "vapor":
        Z = pvt_results["Z_vapor"]

    elif phase == "liquid":
        Z = pvt_results["Z_liquid"]

    else:
        raise ValueError("Phase must be 'vapor' or 'liquid'.")

    if B <= 0 or Z - B <= 0:
        raise ValueError("Invalid values for fugacity calculation.")

    numerator = Z + (1 + math.sqrt(2)) * B
    denominator = Z + (1 - math.sqrt(2)) * B

    if numerator <= 0 or denominator <= 0:
        raise ValueError("Invalid logarithm argument.")

    log_term = math.log(numerator / denominator)

    ln_phi = (
        Z - 1
        - math.log(Z - B)
        - (A / (2 * math.sqrt(2) * B)) * log_term
    )

    phi = math.exp(ln_phi)

    return {
        "ln_phi": ln_phi,
        "phi": phi
    }

def calculate_fugacity(gas, T, P, pvt_results, phase="vapor"):

    coefficient_results = calculate_fugacity_coefficient(
        pvt_results, phase
    )

    phi = coefficient_results["phi"]

    fugacity = phi * P

    return {
        "ln_phi": coefficient_results["ln_phi"],
        "phi": phi,
        "fugacity": fugacity
    }


if __name__ == "__main__":

    gas = "methane"

    T = 300.0
    P = 50.0

    gas_properties = get_gas_properties(gas)

    pvt_results = calculate_pvt(gas_properties, T, P)

    results = calculate_fugacity(
        gas, T, P, pvt_results, phase="vapor"
    )

    print("\n================================")
    print("FUGACITY CALCULATION")
    print("================================")

    print(f"\nGas: {gas_properties['name']}")
    print(f"Temperature: {T} K")
    print(f"Pressure: {P} bar")

    print("\nFUGACITY COEFFICIENT")
    print(f"ln(phi) = {results['ln_phi']:.6f}")
    print(f"phi = {results['phi']:.6f}")

    print("\nPURE COMPONENT FUGACITY")
    print(f"Fugacity = {results['fugacity']:.6f} bar")

    print("\n================================")

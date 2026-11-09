import numpy as np
R = 0.08314462618
def calculate_eos_parameters(gas, T, P):

    if T <= 0 or P <= 0:
        raise ValueError(
            "Temperature and pressure must be positive."
        )

    Tc = gas["Tc"]
    Pc = gas["Pc"]
    omega = gas["omega"]

    a = 0.45724 * (R**2 * Tc**2) / Pc
    b = 0.07780 * (R * Tc) / Pc
    kappa = (
        0.37464
        + 1.54226 * omega
        - 0.26992 * omega**2
    )

    Tr = T / Tc
    alpha = (
        1 + kappa * (1 - np.sqrt(Tr))
    )**2

    A = (a * alpha * P) / (R**2 * T**2)
    B = (b * P) / (R * T)
    return {
        "a": a,
        "b": b,
        "kappa": kappa,
        "Tr": Tr,
        "alpha": alpha,
        "A": A,
        "B": B
    }

def calculate_compressibility_roots(A, B):

    coefficients = [
        1,
        -(1 - B),
        A - 3 * B**2 - 2 * B,
        -(A * B - B**2 - B**3)
    ]

    roots = np.roots(coefficients)
    real_roots = sorted([
        root.real
        for root in roots
        if abs(root.imag) < 1e-8
        and root.real > B
    ])

    if not real_roots:
        raise ValueError(
            "No physically admissible real roots found."
        )

    return real_roots

def calculate_molar_volume(Z, T, P):
    V = Z * R * T / P
    return V

def calculate_ln_phi(Z, A, B):
    sqrt_2 = np.sqrt(2)
    term1 = Z - 1
    term2 = -np.log(Z - B)
    numerator = Z + (1 + sqrt_2) * B
    denominator = Z + (1 - sqrt_2) * B
    term3 = -(
        A / (2 * sqrt_2 * B)
    ) * np.log(numerator / denominator)
    ln_phi = term1 + term2 + term3
    return ln_phi


def check_phase_stability(roots, A, B):

    if len(roots) == 1:

        return {
            "stable_phase": "single phase",
            "ln_phi_liquid": None,
            "ln_phi_vapor": None,
            "phi_liquid": None,
            "phi_vapor": None,
            "stability_message": (
                "Only one valid real root exists. "
                "A separate liquid-vapor stability "
                "comparison is not possible."
            )
        }


    Z_liquid = min(roots)
    Z_vapor = max(roots)

    ln_phi_liquid = calculate_ln_phi(
        Z_liquid, A, B
    )

    ln_phi_vapor = calculate_ln_phi(
        Z_vapor, A, B
    )

    phi_liquid = np.exp(ln_phi_liquid)
    phi_vapor = np.exp(ln_phi_vapor)
    tolerance = 1e-8

    if abs(ln_phi_liquid - ln_phi_vapor) < tolerance:

        stable_phase = "vapor-liquid equilibrium"

        message = (
            "The liquid-like and vapor-like roots have "
            "approximately equal fugacity coefficients. "
            "This indicates vapor-liquid equilibrium."
        )

    elif ln_phi_liquid < ln_phi_vapor:
        stable_phase = "liquid"
        message = (
            "The liquid-like root has the lower fugacity. "
            "The liquid-like phase is thermodynamically "
            "more stable."
        )

    else:

        stable_phase = "vapor"

        message = (
            "The vapor-like root has the lower fugacity. "
            "The vapor-like phase is thermodynamically "
            "more stable."
        )

    return {
        "stable_phase": stable_phase,
        "ln_phi_liquid": ln_phi_liquid,
        "ln_phi_vapor": ln_phi_vapor,
        "phi_liquid": phi_liquid,
        "phi_vapor": phi_vapor,
        "stability_message": message
    }

def calculate_pvt(gas, T, P):


    parameters = calculate_eos_parameters(
        gas, T, P
    )

    A = parameters["A"]
    B = parameters["B"]

    roots = calculate_compressibility_roots(
        A, B
    )

    Z_vapor = max(roots)
    Z_liquid = min(roots)

    V_vapor = calculate_molar_volume(
        Z_vapor, T, P
    )

    V_liquid = calculate_molar_volume(
        Z_liquid, T, P
    )


    stability_results = check_phase_stability(
        roots, A, B
    )

    results = {
        "parameters": parameters,
        "roots": roots,

        "Z_vapor": Z_vapor,
        "Z_liquid": Z_liquid,

        "V_vapor": V_vapor,
        "V_liquid": V_liquid,

        "stable_phase": stability_results["stable_phase"],

        "ln_phi_liquid": stability_results["ln_phi_liquid"],
        "ln_phi_vapor": stability_results["ln_phi_vapor"],

        "phi_liquid": stability_results["phi_liquid"],
        "phi_vapor": stability_results["phi_vapor"],

        "stability_message": stability_results["stability_message"]
    }

    return results

if __name__ == "__main__":

    from gas_data import get_gas_properties
    gas = get_gas_properties("propane")

    T = 250.0
    P = 10.0

    results = calculate_pvt(gas, T, P)
    parameters = results["parameters"]

    print("\n================================")
    print("PENG-ROBINSON EOS RESULTS")
    print("================================")

    print("\nGas:", gas["name"])

    print("Temperature:", T, "K")

    print("Pressure:", P, "bar")

    print("\nEOS PARAMETERS")

    print("a =", parameters["a"])

    print("b =", parameters["b"])

    print("kappa =", parameters["kappa"])

    print("alpha =", parameters["alpha"])

    print("\nDIMENSIONLESS PARAMETERS")

    print("A =", parameters["A"])

    print("B =", parameters["B"])

    print("\nCOMPRESSIBILITY ROOTS")

    print("Real roots:", results["roots"])

    print("Vapor-like Z:", results["Z_vapor"])

    print("Liquid-like Z:", results["Z_liquid"])

    print("\nMOLAR VOLUMES")

    print(
        "Vapor-like volume:",
        results["V_vapor"],
        "L/mol"
    )

    print(
        "Liquid-like volume:",
        results["V_liquid"],
        "L/mol"
    )

    print("\nFUGACITY COEFFICIENTS")

    print(
        "Liquid-like phi:",
        results["phi_liquid"]
    )

    print(
        "Vapor-like phi:",
        results["phi_vapor"]
    )

    print("\nPHASE STABILITY")

    print("Stable phase:", results["stable_phase"])

    print(results["stability_message"])

    print("\n================================")

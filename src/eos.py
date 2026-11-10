import numpy as np
R = 0.08314462618


def calculate_eos_parameters(gas, T, P, eos_model="PR"):
    if T <= 0 or P <= 0:
        raise ValueError("Temperature and pressure must be positive.")
    Tc = gas["Tc"]
    Pc = gas["Pc"]
    omega = gas["omega"]
    Tr = T / Tc
    if eos_model == "PR":
        a_c = 0.45724 * R**2 * Tc**2 / Pc
        b = 0.07780 * R * Tc / Pc
        kappa = (
            0.37464
            + 1.54226 * omega
            - 0.26992 * omega**2
        )
        alpha = (1 + kappa * (1 - np.sqrt(Tr)))**2
        a = a_c * alpha
        da_dT = (
            -a_c * kappa
            * (1 + kappa * (1 - np.sqrt(Tr)))
            / (Tc * np.sqrt(Tr))
        )
        delta1 = 1 + np.sqrt(2)
        delta2 = 1 - np.sqrt(2)
    elif eos_model == "SRK":
        a_c = 0.42747 * R**2 * Tc**2 / Pc
        b = 0.08664 * R * Tc / Pc
        kappa = (
            0.480
            + 1.574 * omega
            - 0.176 * omega**2
        )
        alpha = (1 + kappa * (1 - np.sqrt(Tr)))**2
        a = a_c * alpha
        da_dT = (
            -a_c * kappa
            * (1 + kappa * (1 - np.sqrt(Tr)))
            / (Tc * np.sqrt(Tr))
        )
        delta1 = 1.0
        delta2 = 0.0

    elif eos_model == "RK":
        a_c = 0.42748 * R**2 * Tc**2 / Pc
        b = 0.08664 * R * Tc / Pc
        a = a_c / np.sqrt(Tr)
        da_dT = -0.5 * a / T
        kappa = None
        alpha = 1 / np.sqrt(Tr)
        delta1 = 1.0
        delta2 = 0.0

    elif eos_model == "VDW":
        a_c = 27 * R**2 * Tc**2 / (64 * Pc)
        b = R * Tc / (8 * Pc)
        a = a_c
        da_dT = 0.0
        kappa = None
        alpha = 1.0
        delta1 = 0.0
        delta2 = 0.0

    else:
        raise ValueError(
            "Invalid EOS model. Choose PR, SRK, RK or VDW."
        )
    A = a * P / (R**2 * T**2)
    B = b * P / (R * T)

    return {
        "eos_model": eos_model,
        "a": a,
        "a_c": a_c,
        "b": b,
        "kappa": kappa,
        "Tr": Tr,
        "alpha": alpha,
        "da_dT": da_dT,
        "delta1": delta1,
        "delta2": delta2,
        "A": A,
        "B": B
    }


def calculate_compressibility_roots(A, B, parameters=None):
    if parameters is None:
        delta1 = 1 + np.sqrt(2)
        delta2 = 1 - np.sqrt(2)
    else:
        delta1 = parameters["delta1"]
        delta2 = parameters["delta2"]
    u = delta1 + delta2
    w = delta1 * delta2
    coefficients = [
        1,
        (u - 1) * B - 1,
        A - u * B - (u - w) * B**2,
        -(A * B + w * B**2 + w * B**3)
    ]
    roots = np.roots(coefficients)
    real_roots = sorted([
        root.real
        for root in roots
        if abs(root.imag) < 1e-8 and root.real > B
    ])

    if not real_roots:
        raise ValueError(
            "No physically admissible real roots found."
        )
    return real_roots


def calculate_molar_volume(Z, T, P):
    return Z * R * T / P


def calculate_ln_phi(Z, A, B, parameters=None):

    if parameters is None:
        delta1 = 1 + np.sqrt(2)
        delta2 = 1 - np.sqrt(2)
    else:
        delta1 = parameters["delta1"]
        delta2 = parameters["delta2"]

    term1 = Z - 1
    term2 = -np.log(Z - B)

    if abs(delta1 - delta2) < 1e-12:
        if abs(delta1) < 1e-12:
            term3 = -A / Z
        else:
            raise ValueError(
                "Invalid cubic EOS parameters."
            )
    else:
        numerator = Z + delta1 * B
        denominator = Z + delta2 * B
        term3 = -(
            A / (B * (delta1 - delta2))
        ) * np.log(numerator / denominator)
    return term1 + term2 + term3


def check_phase_stability(roots, A, B, parameters=None):
    if len(roots) == 1:
        Z = roots[0]
        ln_phi = calculate_ln_phi(
            Z, A, B, parameters
        )
        phi = np.exp(ln_phi)
        return {
            "stable_phase": "single phase",
            "ln_phi_liquid": ln_phi,
            "ln_phi_vapor": ln_phi,
            "phi_liquid": phi,
            "phi_vapor": phi,
            "stability_message": (
                "Only one physically admissible real root exists. "
                "The same root is used for both liquid-like and "
                "vapor-like calculations."
            )
        }

    Z_liquid = min(roots)
    Z_vapor = max(roots)
    ln_phi_liquid = calculate_ln_phi(
        Z_liquid, A, B, parameters
    )
    ln_phi_vapor = calculate_ln_phi(
        Z_vapor, A, B, parameters
    )
    phi_liquid = np.exp(ln_phi_liquid)
    phi_vapor = np.exp(ln_phi_vapor)
    tolerance = 1e-8

    if abs(ln_phi_liquid - ln_phi_vapor) < tolerance:
        stable_phase = "vapor-liquid equilibrium"
        message = (
            "The liquid-like and vapor-like roots have "
            "approximately equal fugacity coefficients. "
            "This indicates possible vapor-liquid equilibrium."
        )

    elif ln_phi_liquid < ln_phi_vapor:
        stable_phase = "liquid"
        message = (
            "The liquid-like root has the lower fugacity "
            "coefficient and is predicted to be more stable."
        )

    else:
        stable_phase = "vapor"
        message = (
            "The vapor-like root has the lower fugacity "
            "coefficient and is predicted to be more stable."
        )

    return {
        "stable_phase": stable_phase,
        "ln_phi_liquid": ln_phi_liquid,
        "ln_phi_vapor": ln_phi_vapor,
        "phi_liquid": phi_liquid,
        "phi_vapor": phi_vapor,
        "stability_message": message
    }


def calculate_pvt(gas, T, P, eos_model="PR"):
    parameters = calculate_eos_parameters(
        gas, T, P, eos_model
    )
    A = parameters["A"]
    B = parameters["B"]

    roots = calculate_compressibility_roots(
        A, B, parameters
    )

    Z_liquid = min(roots)
    Z_vapor = max(roots)
    V_liquid = calculate_molar_volume(
        Z_liquid, T, P
    )
    V_vapor = calculate_molar_volume(
        Z_vapor, T, P
    )
    stability_results = check_phase_stability(
        roots, A, B, parameters
    )

    return {
        "T": T,
        "P": P,
        "eos_model": eos_model,
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


if __name__ == "__main__":
    from gas_data import get_gas_properties
    gas = get_gas_properties("propane")
    T = 250.0
    P = 10.0
    eos_models = ["PR", "SRK", "RK", "VDW"]
    for model in eos_models:
        results = calculate_pvt(
            gas, T, P, model
        )
        parameters = results["parameters"]
        print("\n================================")
        print(model, "EOS RESULTS")
        print("================================")
        print("Gas:", gas["name"])
        print("Temperature:", T, "K")
        print("Pressure:", P, "bar")
        print("\nEOS PARAMETERS")
        print("a =", parameters["a"])
        print("b =", parameters["b"])
        print("alpha =", parameters["alpha"])
        print("da/dT =", parameters["da_dT"])
        print("\nDIMENSIONLESS PARAMETERS")
        print("A =", parameters["A"])
        print("B =", parameters["B"])
        print("\nCOMPRESSIBILITY ROOTS")
        print("Real roots:", results["roots"])
        print("Vapor-like Z:", results["Z_vapor"])
        print("Liquid-like Z:", results["Z_liquid"])
        print("\nMOLAR VOLUMES")
        print("Vapor-like volume:", results["V_vapor"], "L/mol")
        print("Liquid-like volume:", results["V_liquid"], "L/mol")
        print("\nFUGACITY COEFFICIENTS")
        print("Liquid-like phi:", results["phi_liquid"])
        print("Vapor-like phi:", results["phi_vapor"])
        print("\nPHASE STABILITY")
        print("Stable phase:", results["stable_phase"])
        print(results["stability_message"])

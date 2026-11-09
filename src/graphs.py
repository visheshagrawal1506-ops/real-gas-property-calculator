import numpy as np
import matplotlib.pyplot as plt
import os

from gas_data import get_gas_properties

R = 0.08314462618  # L.bar/(mol.K)

BASE_DIR = os.path.dirname(os.path.abspath(__file__))

PLOT_DIR = os.path.join(BASE_DIR, "plots")


def calculate_pressure(T, V, a, b, alpha):

    aT = a * alpha

    P = (
        (R * T) / (V - b)
        - aT / (V**2 + 2*b*V - b**2)
    )

    return P


def plot_pv_graph(gas_key):

    properties = get_gas_properties(gas_key)

    Tc = properties["Tc"]
    Pc = properties["Pc"]
    omega = properties["omega"]

    a = 0.45724 * (R**2 * Tc**2) / Pc

    b = 0.07780 * R * Tc / Pc

    kappa = (
        0.37464
        + 1.54226 * omega
        - 0.26992 * omega**2
    )

    temperatures = [
        0.85 * Tc,
        Tc,
        1.15 * Tc
    ]

    labels = [
        "Below critical temperature",
        "Critical temperature",
        "Above critical temperature"
    ]

    fig, ax = plt.subplots(figsize=(9, 6))

    for T, label in zip(temperatures, labels):

        Tr = T / Tc

        alpha = (
            1 + kappa * (1 - np.sqrt(Tr))
        )**2

        V_min = 1.02 * b

        V_max = 8 * R * T / Pc

        V = np.linspace(V_min, V_max, 600)

        P = calculate_pressure(T, V, a, b, alpha)

        ax.plot(V, P, label=label)

    # Graph formatting
        # Calculate and mark the critical point
    Vc = 0.3074 * R * Tc / Pc

    ax.scatter(
        Vc,
        Pc,
        color="red",
        marker="o",
        s=90,
        label="Critical Point",
        zorder=5
    )

    ax.annotate(
        f"Critical Point\n(Pc = {Pc:.2f} bar, Vc = {Vc:.4f} L/mol)",
        xy=(Vc, Pc),
        xytext=(15, 15),
        textcoords="offset points",
        fontsize=9,
        color="red",
        arrowprops=dict(arrowstyle="->", color="red")
    )

    ax.set_title(
        f"P-V Isotherms for {properties['name']} "
        "using Peng-Robinson EOS"
    )

    ax.set_xlabel("Molar Volume (L/mol)")

    ax.set_ylabel("Pressure (bar)")

    ax.set_ylim(0, 3 * Pc)

    ax.set_xlim(0, 4 * R * Tc / Pc)

    ax.grid(True)

    ax.legend()

    fig.tight_layout()

    # Create plots folder if it does not exist

    os.makedirs(PLOT_DIR, exist_ok=True)

    # Save graph

    filename = os.path.join(
        PLOT_DIR,
        f"{gas_key}_PV_graph.png"
    )

    fig.savefig(filename, dpi=300)

    plt.close(fig)

    print("\nGraph saved successfully at:", filename)

    return filename


if __name__ == "__main__":

    gas = "methane"

    plot_pv_graph(gas)
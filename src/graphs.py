import numpy as np
import matplotlib.pyplot as plt
import os
from gas_data import get_gas_properties
from eos import calculate_eos_parameters
R = 0.08314462618  
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
PLOT_DIR = os.path.join(BASE_DIR, "plots")
EOS_NAMES = {
    "PR": "Peng-Robinson",
    "SRK": "Soave-Redlich-Kwong",
    "RK": "Redlich-Kwong",
    "VDW": "Van der Waals"
}
EOS_MODELS = ["PR", "SRK", "RK", "VDW"]


def calculate_pressure(T, V, parameters):
    a = parameters["a"]
    b = parameters["b"]
    delta1 = parameters["delta1"]
    delta2 = parameters["delta2"]
    if np.any(np.asarray(V) <= b):
        raise ValueError(
            "Molar volume must be greater than b."
        )
    P = (
        R * T / (V - b)
        - a / (
            (V + delta1 * b)
            * (V + delta2 * b)
        )
    )
    return P


def get_critical_volume(properties, eos_model):
    Tc = properties["Tc"]
    Pc = properties["Pc"]
    if eos_model == "PR":
        Zc = 0.3074
    elif eos_model in ("SRK", "RK"):
        Zc = 1.0 / 3.0
    elif eos_model == "VDW":
        Zc = 3.0 / 8.0
    else:
        raise ValueError("Invalid EOS model.")
    Vc = Zc * R * Tc / Pc

    return Vc


def prepare_plot_folder():
    os.makedirs(PLOT_DIR, exist_ok=True)


def plot_pv_graph(gas_key, eos_model="PR"):
    properties = get_gas_properties(gas_key)
    if eos_model not in EOS_NAMES:
        raise ValueError(
            "Choose PR, SRK, RK or VDW."
        )
    Tc = properties["Tc"]
    Pc = properties["Pc"]
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
    try:
        for temperature, label in zip(temperatures, labels):
            parameters = calculate_eos_parameters(
                properties,
                temperature,
                1.0,
                eos_model
            )
            b = parameters["b"]
            V_min = 1.02 * b
            V_max = 8 * R * temperature / Pc
            V = np.linspace(
                V_min,
                V_max,
                800
            )
            pressure = calculate_pressure(
                temperature,
                V,
                parameters
            )
            ax.plot(
                V,
                pressure,
                label=label
            )
        Vc = get_critical_volume(
            properties,
            eos_model
        )
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
            f"Critical Point\n"
            f"(Pc = {Pc:.2f} bar, Vc = {Vc:.4f} L/mol)",
            xy=(Vc, Pc),
            xytext=(15, 15),
            textcoords="offset points",
            fontsize=9,
            color="red",
            arrowprops={
                "arrowstyle": "->",
                "color": "red"
            }
        )
        ax.set_title(
            f"P-V Isotherms for {properties['name']}\n"
            f"using {EOS_NAMES[eos_model]} EOS"
        )
        ax.set_xlabel("Molar Volume (L/mol)")
        ax.set_ylabel("Pressure (bar)")
        ax.set_ylim(0, 3 * Pc)
        ax.set_xlim(0, 4 * R * Tc / Pc)
        ax.grid(True)
        ax.legend()
        fig.tight_layout()
        prepare_plot_folder()
        filename = os.path.join(
            PLOT_DIR,
            f"{gas_key}_{eos_model}_PV_graph.png"
        )
        fig.savefig(
            filename,
            dpi=300
        )
        return filename
    finally:
        plt.close(fig)


def plot_pv_comparison_graph(gas_key, temperature):
    properties = get_gas_properties(gas_key)
    if not np.isfinite(temperature) or temperature <= 0:
        raise ValueError(
            "Temperature must be greater than zero."
        )
    Pc = properties["Pc"]
    parameter_sets = {
        model: calculate_eos_parameters(
            properties,
            temperature,
            1.0,
            model
        )
        for model in EOS_MODELS
    }
    largest_b = max(
        params["b"]
        for params in parameter_sets.values()
    )
    V_min = 1.02 * largest_b
    V_max = max(
        8 * R * temperature / Pc,
        12 * largest_b
    )
    volumes = np.linspace(
        V_min,
        V_max,
        1200
    )
    fig, ax = plt.subplots(figsize=(10, 6.5))
    try:
        for model in EOS_MODELS:

            pressure = np.asarray(
                calculate_pressure(
                    temperature,
                    volumes,
                    parameter_sets[model]
                ),
                dtype=float
            )
            pressure[~np.isfinite(pressure)] = np.nan
            pressure[pressure > 5 * Pc] = np.nan
            ax.plot(
                volumes,
                pressure,
                linewidth=2,
                label=EOS_NAMES[model]
            )
        ax.set_title(
            f"EOS Comparison: {properties['name']} "
            f"at {temperature:.2f} K"
        )
        ax.set_xlabel("Molar Volume (L/mol)")
        ax.set_ylabel("Pressure (bar)")
        ax.set_xlim(V_min, V_max)
        ax.set_ylim(0, 3 * Pc)
        ax.grid(True, alpha=0.35)
        ax.legend()
        fig.tight_layout()
        prepare_plot_folder()
        filename = os.path.join(
            PLOT_DIR,
            f"{gas_key}_EOS_comparison_{temperature:.2f}K.png"
        )

        fig.savefig(
            filename,
            dpi=300
        )
        return filename
    finally:
        plt.close(fig)
if __name__ == "__main__":
    gas = "methane"
    for model in EOS_MODELS:
        path = plot_pv_graph(
            gas,
            model
        )
        print(
            "Graph saved successfully at:",
            path
        )
    comparison_path = plot_pv_comparison_graph(
        gas,
        300.0
    )
    print(
        "Comparison graph saved at:",
        comparison_path
    )

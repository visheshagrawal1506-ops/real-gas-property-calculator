import streamlit as st
import os
import math
import csv
import io
import pandas as pd
from gas_data import get_gas_properties, get_available_gases
from eos import calculate_pvt
from enthalpy import calculate_enthalpy
from entropy import calculate_entropy
from fugacity import calculate_fugacity

from graphs import (
    plot_pv_graph,
    plot_pv_comparison_graph,
    EOS_NAMES,
    EOS_MODELS
)

st.set_page_config(
    page_title="Real Gas Property Calculator",
    page_icon="⚗️",
    layout="wide"
)

st.markdown("""
<style>
.block-container {
    padding-top: 2rem;
    padding-bottom: 2rem;
    max-width: 1400px;
}
[data-testid="stSidebar"] {
    border-right: 1px solid rgba(128, 128, 128, 0.2);
}
[data-testid="stMetric"] {
    background-color: rgba(128, 128, 128, 0.08);
    padding: 15px;
    border-radius: 10px;
}
.stButton > button,
.stDownloadButton > button {
    border-radius: 8px;
    font-weight: 600;
    min-height: 42px;
}
</style>
""", unsafe_allow_html=True)


for key in (
    "single_results",
    "comparison_results",
    "single_graph_path",
    "comparison_graph_path"
):
    if key not in st.session_state:
        st.session_state[key] = None


EOS_OPTIONS = {
    "Peng-Robinson": "PR",
    "Soave-Redlich-Kwong": "SRK",
    "Redlich-Kwong": "RK",
    "Van der Waals": "VDW"

}


def validate_inputs(temperature, pressure):
    if not math.isfinite(temperature) or not math.isfinite(pressure):
        raise ValueError(
            "Temperature and pressure must be finite."
        )
    if temperature <= 0:
        raise ValueError(
            "Temperature must be greater than zero."
        )
    if pressure <= 0:
        raise ValueError(
            "Pressure must be greater than zero."
        )


def resolve_phase(pvt, requested_phase):
    if requested_phase != "Auto (Stable Phase)":
        return requested_phase
    stable = str(
        pvt["stable_phase"]
    ).lower()
    if stable == "liquid":
        return "liquid"
    if stable in ("vapor", "single phase"):
        return "vapor"
    if stable == "vapor-liquid equilibrium":
        return "vapor"
    raise ValueError(
        "The software could not determine the stable phase."
    )


def calculate_model(
    gas_key,
    temperature,
    pressure,
    model,
    requested_phase
):

    gas_properties = get_gas_properties(gas_key)
    pvt = calculate_pvt(
        gas_properties,
        temperature,
        pressure,
        model
    )
    roots = pvt["roots"]
    if len(roots) == 0:
        raise ValueError(
            f"{EOS_NAMES[model]}: "
            "No valid real compressibility roots found."
        )
    pvt_values = [
        pvt["Z_vapor"],
        pvt["Z_liquid"],
        pvt["V_vapor"],
        pvt["V_liquid"]
    ] + [
        float(root) for root in roots
    ]
    if not all(
        math.isfinite(float(value))
        for value in pvt_values
    ):
        raise ValueError(
            f"{EOS_NAMES[model]}: Invalid PVT values."
        )

    if (
        pvt["V_vapor"] <= 0
        or pvt["V_liquid"] <= 0
    ):

        raise ValueError(
            f"{EOS_NAMES[model]}: "
            "Molar volume is not positive."
        )

    selected_phase = resolve_phase(
        pvt,
        requested_phase
    )

    enthalpy = calculate_enthalpy(
        gas_key,
        temperature,
        pvt,
        selected_phase,
        model
    )

    entropy = calculate_entropy(
        gas_key,
        temperature,
        pressure,
        pvt,
        selected_phase,
        model
    )

    fugacity = calculate_fugacity(
        gas_key,
        temperature,
        pressure,
        pvt,
        selected_phase,
        model
    )


    values = [
        enthalpy["H_ideal"],
        enthalpy["H_departure"],
        enthalpy["H_total"],
        entropy["S_ideal"],
        entropy["S_departure"],
        entropy["S_total"],

        fugacity["phi"],
        fugacity["fugacity"],
        fugacity["ln_phi"]

    ]
    if not all(
        math.isfinite(float(value))
        for value in values
    ):

        raise ValueError(
            f"{EOS_NAMES[model]}: "
            "Invalid thermodynamic property."
        )

    if (
        fugacity["phi"] <= 0
        or fugacity["fugacity"] <= 0
    ):

        raise ValueError(
            f"{EOS_NAMES[model]}: "
            "Fugacity values must be positive."
        )
    return {
        "gas_properties": gas_properties,
        "model": model,
        "pvt": pvt,
        "enthalpy": enthalpy,
        "entropy": entropy,
        "fugacity": fugacity,
        "selected_phase": selected_phase

    }

def make_comparison_dataframe(results):
    rows = []
    for model in EOS_MODELS:
        item = results[model]
        pvt = item["pvt"]
        selected_phase = item["selected_phase"]
        if selected_phase == "vapor":
            z = pvt["Z_vapor"]
            volume = pvt["V_vapor"]
        else:
            z = pvt["Z_liquid"]
            volume = pvt["V_liquid"]
        rows.append({
            "Equation of State": EOS_NAMES[model],
            "Selected Phase": selected_phase.capitalize(),
            "Real Roots": len(pvt["roots"]),
            "Compressibility Factor (Z)": z,
            "Molar Volume (L/mol)": volume,
            "Enthalpy (J/mol)": item["enthalpy"]["H_total"],
            "Entropy (J/mol.K)": item["entropy"]["S_total"],
            "Fugacity Coefficient": item["fugacity"]["phi"],
            "Fugacity (bar)": item["fugacity"]["fugacity"]

        })

    return pd.DataFrame(rows)

st.title("⚗️ Real Gas Property Calculator")
st.write(
    "A thermodynamic property calculator using "
    "four cubic equations of state."
)
st.caption(
    "Calculate PVT properties, enthalpy, entropy "
    "and fugacity for pure gases."
)
st.divider()

st.sidebar.title("Calculation Settings")
st.sidebar.write(
    "Enter the operating conditions below."
)

gas_options = get_available_gases()
gas = st.sidebar.selectbox(
    "Select Gas",
    gas_options,
    format_func=lambda key: get_gas_properties(key)["name"]
)

eos_name = st.sidebar.selectbox(
    "Select Equation of State",
    list(EOS_OPTIONS.keys())
)

eos_model = EOS_OPTIONS[eos_name]
T = st.sidebar.number_input(
    "Temperature (K)",
    min_value=1.0,
    value=300.0,
    step=10.0
)

P = st.sidebar.number_input(
    "Pressure (bar)",
    min_value=0.001,
    value=50.0,
    step=1.0
)

phase = st.sidebar.selectbox(
    "Select Phase",
    [
        "vapor",
        "liquid",
        "Auto (Stable Phase)"
    ]
)
st.sidebar.divider()

calculate_button = st.sidebar.button(
    "Calculate Properties",
    type="primary",
    use_container_width=True
)

compare_button = st.sidebar.button(
    "Compare All Four EOS",
    use_container_width=True
)

st.sidebar.caption(
    f"Selected Model: {eos_name}"
)


if calculate_button:
    try:
        validate_inputs(T, P)
        result = calculate_model(
            gas,
            T,
            P,
            eos_model,
            phase
        )
        st.session_state.single_results = {
            "gas": gas,
            "T": T,
            "P": P,
            "requested_phase": phase,
            "result": result
        }
        st.session_state.single_graph_path = None
        st.success(
            "Calculations completed successfully!"
        )
        
    except Exception as error:
        st.error(
            f"Calculation error: {error}"
        )
        st.exception(error)

if compare_button:
    try:
        validate_inputs(T, P)
        results = {}
        for model in EOS_MODELS:
            results[model] = calculate_model(
                gas,
                T,
                P,
                model,
                phase
            )
        st.session_state.comparison_results = {
            "gas": gas,
            "T": T,
            "P": P,
            "requested_phase": phase,
            "results": results,
            "table": make_comparison_dataframe(results)
        }
        st.session_state.comparison_graph_path = None
        st.success(
            "All four EOS models were calculated successfully!"
        )
        
    except Exception as error:
        st.error(
            f"Comparison error: {error}"
        )
        st.exception(error)

saved = st.session_state.single_results
if saved is not None:
    result = saved["result"]
    pvt = result["pvt"]
    h = result["enthalpy"]
    s = result["entropy"]
    f = result["fugacity"]
    roots = pvt["roots"]
    selected_phase = result["selected_phase"]
    gas_properties = result["gas_properties"]
    st.header("Single EOS Calculation")
    st.caption(
        f"{EOS_NAMES[result['model']]} | "
        f"{gas_properties['name']} | "
        f"{saved['T']:.2f} K | "
        f"{saved['P']:.3f} bar"
    )
    if len(roots) == 1:

        st.info(
            "Only one valid real compressibility root was found. "
            "The same root is used for both phase-wise displays."
        )
    else:
        st.info(
            f"{len(roots)} valid real compressibility roots were found. "
            "The smallest root is liquid-like and the largest "
            "root is vapor-like."
        )
    if saved["requested_phase"] == "Auto (Stable Phase)":

        st.info(
            f"Automatic phase selection: "
            f"{selected_phase.capitalize()}. "
            f"Stability result: {pvt['stable_phase']}."
        )


    csv_buffer = io.StringIO()
    writer = csv.writer(csv_buffer)
    writer.writerow([
        "Parameter",
        "Value"
    ])
    export_rows = [

        ["Gas", gas_properties["name"]],
        ["Equation of State", EOS_NAMES[result["model"]]],
        ["Temperature (K)", saved["T"]],
        ["Pressure (bar)", saved["P"]],
        ["Selected Phase", selected_phase.capitalize()],
        ["Predicted Stable Phase", pvt["stable_phase"]],
        ["Vapor Compressibility Factor", pvt["Z_vapor"]],
        ["Liquid Compressibility Factor", pvt["Z_liquid"]],
        ["Vapor Molar Volume (L/mol)", pvt["V_vapor"]],
        ["Liquid Molar Volume (L/mol)", pvt["V_liquid"]],
        [
            "Compressibility Roots",
            ", ".join(
                f"{float(x):.8f}"
                for x in roots
            )
        ],
        ["Ideal Gas Enthalpy (J/mol)", h["H_ideal"]],
        ["Enthalpy Departure (J/mol)", h["H_departure"]],
        ["Total Enthalpy (J/mol)", h["H_total"]],
        ["Ideal Gas Entropy (J/mol.K)", s["S_ideal"]],
        ["Entropy Departure (J/mol.K)", s["S_departure"]],
        ["Total Entropy (J/mol.K)", s["S_total"]],
        ["Fugacity Coefficient", f["phi"]],
        ["Fugacity (bar)", f["fugacity"]],
        ["Log Fugacity Coefficient", f["ln_phi"]]
    ]

    for row in export_rows:
        writer.writerow(row)

    st.download_button(
        "Download Results (CSV)",
        data=csv_buffer.getvalue(),
        file_name=f"{saved['gas']}_{result['model']}_results.csv",
        mime="text/csv",
        key="download_single_results"
    )

    tab1, tab2, tab3, tab4, tab5 = st.tabs([
        "PVT Properties",
        "Enthalpy",
        "Entropy",
        "Fugacity",
        "Phase Analysis"
    ])

    with tab1:
        st.subheader("PVT Properties")
        c1, c2, c3 = st.columns(3)
        c1.metric(
            "Gas",
            gas_properties["name"]
        )
        c2.metric(
            "Temperature",
            f"{saved['T']:.2f} K"
        )
        c3.metric(
            "Pressure",
            f"{saved['P']:.3f} bar"
        )
        st.write(
            f"**Selected Phase:** {selected_phase.capitalize()}"
        )

        if selected_phase == "vapor":
            z = pvt["Z_vapor"]
            v = pvt["V_vapor"]
        else:
            z = pvt["Z_liquid"]
            v = pvt["V_liquid"]
        c1, c2 = st.columns(2)
        c1.metric(
            "Selected Compressibility Factor",
            f"{z:.6f}"
        )
        c2.metric(
            "Selected Molar Volume",
            f"{v:.6f} L/mol"
        )

        st.subheader("Phase-wise PVT Properties")
        c1, c2 = st.columns(2)
        with c1:

            st.markdown("**Vapor-like Phase**")
            st.metric(
                "Compressibility Factor",
                f"{pvt['Z_vapor']:.6f}"
            )
            st.metric(
                "Molar Volume",
                f"{pvt['V_vapor']:.6f} L/mol"
            )

        with c2:
            st.markdown("**Liquid-like Phase**")
            st.metric(
                "Compressibility Factor",
                f"{pvt['Z_liquid']:.6f}"
            )
            st.metric(
                "Molar Volume",
                f"{pvt['V_liquid']:.6f} L/mol"
            )

        st.write("**Compressibility Roots**")
        st.write([
            round(float(root), 8)
            for root in roots
        ])

    with tab2:
        st.subheader("Enthalpy")
        c1, c2, c3 = st.columns(3)
        c1.metric(
            "Ideal Gas Enthalpy",
            f"{h['H_ideal']:.4f} J/mol"
        )
        c2.metric(
            "Enthalpy Departure",
            f"{h['H_departure']:.4f} J/mol"
        )

        c3.metric(
            "Total Enthalpy",
            f"{h['H_total']:.4f} J/mol"
        )


    with tab3:
        st.subheader("Entropy")
        c1, c2, c3 = st.columns(3)
        c1.metric(
            "Ideal Gas Entropy",
            f"{s['S_ideal']:.4f} J/(mol.K)"
        )
        c2.metric(
            "Entropy Departure",
            f"{s['S_departure']:.4f} J/(mol.K)"
        )
        c3.metric(
            "Total Entropy",
            f"{s['S_total']:.4f} J/(mol.K)"
        )

    with tab4:
        st.subheader("Pure Component Fugacity")
        c1, c2 = st.columns(2)
        c1.metric(
            "Fugacity Coefficient",
            f"{f['phi']:.6f}"
        )
        c2.metric(
            "Fugacity",
            f"{f['fugacity']:.6f} bar"
        )
        st.metric(
            "Log Fugacity Coefficient",
            f"{f['ln_phi']:.6f}"
        )

    with tab5:
        st.subheader("Phase Stability Analysis")
        st.write(
            f"**Predicted Stable Phase:** "
            f"{pvt['stable_phase'].capitalize()}"
        )
        st.info(
            pvt["stability_message"]
        )
        c1, c2 = st.columns(2)
        c1.metric(
            "Liquid-like Fugacity Coefficient",
            f"{pvt['phi_liquid']:.6f}"
        )
        c2.metric(
            "Vapor-like Fugacity Coefficient",
            f"{pvt['phi_vapor']:.6f}"
        )
        for index, root in enumerate(roots, start=1):
            st.write(
                f"Root {index}: {float(root):.8f}"
            )

st.divider()
st.header("EOS Comparison")
st.write(
    "Compare all four equations of state using the same gas, "
    "temperature, pressure and phase-selection setting."
)

comparison = st.session_state.comparison_results
if comparison is not None:
    st.caption(
        f"{get_gas_properties(comparison['gas'])['name']} | "
        f"{comparison['T']:.2f} K | "
        f"{comparison['P']:.3f} bar | "
        f"Requested phase: {comparison['requested_phase']}"
    )
    st.dataframe(
        comparison["table"].style.format({
            "Compressibility Factor (Z)": "{:.6f}",
            "Molar Volume (L/mol)": "{:.6f}",
            "Enthalpy (J/mol)": "{:.4f}",
            "Entropy (J/mol.K)": "{:.4f}",
            "Fugacity Coefficient": "{:.6f}",
            "Fugacity (bar)": "{:.6f}"
        }),
        use_container_width=True,
        hide_index=True
    )
    st.download_button(
        "Download EOS Comparison (CSV)",
        data=comparison["table"].to_csv(index=False),
        file_name=f"{comparison['gas']}_EOS_comparison.csv",
        mime="text/csv",
        key="download_comparison"
    )

    with st.expander(
        "View phase and root details for each EOS"
    ):
        for model in EOS_MODELS:
            item = comparison["results"][model]
            st.markdown(
                f"**{EOS_NAMES[model]}**"
            )
            st.write(
                f"Predicted stable phase: "
                f"{item['pvt']['stable_phase']}"
            )
            st.write(
                "Compressibility roots: "
                + ", ".join(
                    f"{float(root):.8f}"
                    for root in item["pvt"]["roots"]
                )
            )

st.divider()
st.header("P–V Isotherms")
st.write(
    f"Generate three temperature isotherms for "
    f"{get_gas_properties(gas)['name']} "
    f"using the {eos_name} Equation of State."
)

if st.button(
    "Generate P-V Graph",
    key="generate_single_graph"
):
    try:

        graph_path = plot_pv_graph(
            gas,
            eos_model
        )
        st.session_state.single_graph_path = {
            "path": graph_path,
            "gas": gas,
            "model": eos_model
        }

    except Exception as error:

        st.error(
            f"Graph generation error: {error}"
        )

single_graph = st.session_state.single_graph_path

if isinstance(single_graph, dict):
    graph_path = single_graph["path"]
    if os.path.exists(graph_path):
        graph_gas = get_gas_properties(
            single_graph["gas"]
        )
        graph_model = single_graph["model"]
        st.image(
            graph_path,
            caption=(
                f"P-V Isotherms for "
                f"{graph_gas['name']} "
                f"using {EOS_NAMES[graph_model]} EOS"
            ),
            use_container_width=True
        )
        st.success(
            "Graph generated successfully."
        )
    else:
        st.warning(
            "The graph file could not be found."
        )


st.divider()
st.header(
    "P–V Graph: Comparison of All Four EOS"
)
st.write(
    "Compare the pressure-volume curves of PR, SRK, RK "
    "and VDW at the same gas and temperature."
)

if st.button(
    "Generate Four-EOS Comparison Graph",
    key="generate_comparison_graph"
):
    try:
        graph_path = plot_pv_comparison_graph(
            gas,
            T
        )
        st.session_state.comparison_graph_path = {
            "path": graph_path,
            "gas": gas,
            "temperature": T
        }

    except Exception as error:
        st.error(
            f"Comparison graph error: {error}"
        )

comparison_graph = st.session_state.comparison_graph_path
if isinstance(comparison_graph, dict):
    graph_path = comparison_graph["path"]
    if os.path.exists(graph_path):
        graph_gas = get_gas_properties(
            comparison_graph["gas"]
        )
        graph_temperature = comparison_graph["temperature"]
        st.image(
            graph_path,
            caption=(
                f"Four-EOS P-V comparison for "
                f"{graph_gas['name']} "
                f"at {graph_temperature:.2f} K"
            ),
            use_container_width=True
        )

        st.success(
            "Four-EOS comparison graph generated successfully."
        )
    else:
        st.warning(
            "The comparison graph file could not be found."
        )


st.divider()
st.caption(
    "Real Gas Property Calculator | "
    "Peng-Robinson | SRK | RK | Van der Waals"
)

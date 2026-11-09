import streamlit as st
import os
import math
import csv
import io

from gas_data import get_gas_properties, get_available_gases
from eos import calculate_pvt
from enthalpy import calculate_enthalpy
from entropy import calculate_entropy
from fugacity import calculate_fugacity
from graphs import plot_pv_graph


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

.stButton > button {
    border-radius: 8px;
    font-weight: 600;
    min-height: 42px;
}

.stDownloadButton > button {
    border-radius: 8px;
    font-weight: 600;
}

</style>
""", unsafe_allow_html=True)

st.title("⚗️ Real Gas Property Calculator")

st.write(
    "A thermodynamic property calculator based on "
    "the Peng-Robinson Equation of State."
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
    ["vapor", "liquid", "Auto (Stable Phase)"]
)

st.sidebar.divider()

calculate_button = st.sidebar.button(
    "Calculate Properties",
    type="primary",
    use_container_width=True
)

st.sidebar.caption(
    "Model: Peng-Robinson EOS"
)

if calculate_button:

    try:

        if not math.isfinite(T) or not math.isfinite(P):

            st.error(
                "Temperature and pressure must be finite values."
            )

            st.stop()

        if T <= 0:

            st.error(
                "Temperature must be greater than zero."
            )

            st.stop()

        if P <= 0:

            st.error(
                "Pressure must be greater than zero."
            )

            st.stop()

        gas_properties = get_gas_properties(gas)

        if not gas_properties:

            st.error("Gas properties could not be found.")

            st.stop()

        pvt_results = calculate_pvt(
            gas_properties, T, P
        )

        roots = pvt_results["roots"]

        if len(roots) == 0:

            st.error(
                "No valid real compressibility roots were found. "
                "Try different temperature and pressure conditions."
            )

            st.stop()

        if not all(
            math.isfinite(float(root))
            for root in roots
        ):

            st.error(
                "Invalid compressibility roots were obtained."
            )

            st.stop()

        if (
            not math.isfinite(pvt_results["Z_vapor"])
            or not math.isfinite(pvt_results["Z_liquid"])
            or not math.isfinite(pvt_results["V_vapor"])
            or not math.isfinite(pvt_results["V_liquid"])
        ):

            st.error(
                "Invalid PVT properties were obtained. "
                "Please try different operating conditions."
            )

            st.stop()

        if (
            pvt_results["V_vapor"] <= 0
            or pvt_results["V_liquid"] <= 0
        ):

            st.error(
                "Calculated molar volume is not physically valid."
            )

            st.stop()

        if len(roots) == 1:

            st.info(
                "Only one valid real compressibility root was found. "
                "The same root is used for both phase calculations."
            )

        else:

            st.info(
                f"{len(roots)} valid real compressibility roots were found. "
                "The smallest root is liquid-like and the largest "
                "root is vapor-like."
            )


        selected_phase = phase

        if phase == "Auto (Stable Phase)":

            stable_phase = pvt_results["stable_phase"].lower()

            if stable_phase == "liquid":

                selected_phase = "liquid"

                st.info(
                    "Automatic phase selection: Liquid"
                )

            elif stable_phase == "vapor":

                selected_phase = "vapor"

                st.info(
                    "Automatic phase selection: Vapor"
                )

            elif stable_phase == "single phase":

                selected_phase = "vapor"

                st.info(
                    "Automatic phase selection: Single phase. "
                    "Only one valid real root exists."
                )

            elif stable_phase == "vapor-liquid equilibrium":

                selected_phase = "vapor"

                st.info(
                    "Automatic phase selection: Vapor-Liquid Equilibrium. "
                    "Both phases have approximately equal fugacity. "
                    "Vapor root is used for displaying properties."
                )

            else:

                st.error(
                    "The software could not determine the stable phase."
                )

                st.stop()

        enthalpy_results = calculate_enthalpy(
            gas, T, pvt_results, selected_phase
        )

        entropy_results = calculate_entropy(
            gas, T, P, pvt_results, selected_phase
        )

        fugacity_results = calculate_fugacity(
            gas, T, P, pvt_results, selected_phase
        )

        all_results = [
            enthalpy_results["H_ideal"],
            enthalpy_results["H_departure"],
            enthalpy_results["H_total"],
            entropy_results["S_ideal"],
            entropy_results["S_departure"],
            entropy_results["S_total"],
            fugacity_results["phi"],
            fugacity_results["fugacity"],
            fugacity_results["ln_phi"]
        ]

        if not all(
            math.isfinite(float(value))
            for value in all_results
        ):

            st.error(
                "One or more thermodynamic properties are invalid."
            )

            st.stop()

        if (
            fugacity_results["phi"] <= 0
            or fugacity_results["fugacity"] <= 0
        ):

            st.error(
                "Calculated fugacity or fugacity coefficient "
                "is not physically valid."
            )

            st.stop()

        csv_buffer = io.StringIO()
        csv_writer = csv.writer(csv_buffer)

        csv_writer.writerow(["Parameter", "Value"])

        export_data = [

            ["Gas", gas_properties["name"]],
            ["Temperature (K)", T],
            ["Pressure (bar)", P],
            ["Selected Phase", selected_phase.capitalize()],
            ["Predicted Stable Phase", pvt_results["stable_phase"]],

            ["Vapor Compressibility Factor", pvt_results["Z_vapor"]],
            ["Liquid Compressibility Factor", pvt_results["Z_liquid"]],

            ["Vapor Molar Volume (L/mol)", pvt_results["V_vapor"]],
            ["Liquid Molar Volume (L/mol)", pvt_results["V_liquid"]],

            [
                "Compressibility Roots",
                ", ".join(
                    f"{float(root):.8f}" for root in roots
                )
            ],

            ["Ideal Gas Enthalpy (J/mol)", enthalpy_results["H_ideal"]],
            ["Enthalpy Departure (J/mol)", enthalpy_results["H_departure"]],
            ["Total Enthalpy (J/mol)", enthalpy_results["H_total"]],

            ["Ideal Gas Entropy (J/mol.K)", entropy_results["S_ideal"]],
            ["Entropy Departure (J/mol.K)", entropy_results["S_departure"]],
            ["Total Entropy (J/mol.K)", entropy_results["S_total"]],

            ["Fugacity Coefficient", fugacity_results["phi"]],
            ["Fugacity (bar)", fugacity_results["fugacity"]],
            ["Log Fugacity Coefficient", fugacity_results["ln_phi"]],

            ["Liquid-like Fugacity Coefficient", pvt_results["phi_liquid"]],
            ["Vapor-like Fugacity Coefficient", pvt_results["phi_vapor"]]

        ]

        for row in export_data:
            csv_writer.writerow(row)

        st.success("Calculations completed successfully!")

        st.download_button(
            label="Download Results (CSV)",
            data=csv_buffer.getvalue(),
            file_name=f"{gas}_results.csv",
            mime="text/csv",
            key="download_results"
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

            col1, col2, col3 = st.columns(3)

            col1.metric(
                "Gas",
                gas_properties["name"]
            )

            col2.metric(
                "Temperature",
                f"{T:.2f} K"
            )

            col3.metric(
                "Pressure",
                f"{P:.3f} bar"
            )

            st.divider()

            if phase == "Auto (Stable Phase)":

                if pvt_results["stable_phase"].lower() == "single phase":

                    st.subheader(
                        "Selected Phase: Auto → Single Phase"
                    )

                elif pvt_results["stable_phase"].lower() == "vapor-liquid equilibrium":

                    st.subheader(
                        "Selected Phase: Auto → Vapor-Liquid Equilibrium"
                    )

                else:

                    st.subheader(
                        f"Selected Phase: Auto → {selected_phase.capitalize()}"
                    )

            else:

                st.subheader(
                    f"Selected Phase: {selected_phase.capitalize()}"
                )

            selected_Z = pvt_results[
                "Z_vapor" if selected_phase == "vapor" else "Z_liquid"
            ]

            selected_V = pvt_results[
                "V_vapor" if selected_phase == "vapor" else "V_liquid"
            ]

            col1, col2 = st.columns(2)

            col1.metric(
                "Selected Compressibility Factor",
                f"{selected_Z:.6f}"
            )

            col2.metric(
                "Selected Molar Volume",
                f"{selected_V:.6f} L/mol"
            )

            st.divider()

            st.subheader("Phase-wise PVT Properties")

            col1, col2 = st.columns(2)

            with col1:

                st.markdown("**Vapor-like Phase**")

                st.metric(
                    "Compressibility Factor",
                    f"{pvt_results['Z_vapor']:.6f}"
                )

                st.metric(
                    "Molar Volume",
                    f"{pvt_results['V_vapor']:.6f} L/mol"
                )

            with col2:

                st.markdown("**Liquid-like Phase**")

                st.metric(
                    "Compressibility Factor",
                    f"{pvt_results['Z_liquid']:.6f}"
                )

                st.metric(
                    "Molar Volume",
                    f"{pvt_results['V_liquid']:.6f} L/mol"
                )

            st.divider()

            st.markdown("**Compressibility Roots**")

            st.write([
                round(float(root), 8)
                for root in roots
            ])

        with tab2:

            st.subheader("Enthalpy")

            st.caption(
                "Enthalpy is calculated using ideal-gas "
                "and departure contributions."
            )

            col1, col2, col3 = st.columns(3)

            col1.metric(
                "Ideal Gas Enthalpy",
                f"{enthalpy_results['H_ideal']:.4f} J/mol"
            )

            col2.metric(
                "Enthalpy Departure",
                f"{enthalpy_results['H_departure']:.4f} J/mol"
            )

            col3.metric(
                "Total Enthalpy",
                f"{enthalpy_results['H_total']:.4f} J/mol"
            )

        with tab3:

            st.subheader("Entropy")

            st.caption(
                "Entropy is calculated using ideal-gas "
                "and departure contributions."
            )

            col1, col2, col3 = st.columns(3)

            col1.metric(
                "Ideal Gas Entropy",
                f"{entropy_results['S_ideal']:.4f} J/(mol.K)"
            )

            col2.metric(
                "Entropy Departure",
                f"{entropy_results['S_departure']:.4f} J/(mol.K)"
            )

            col3.metric(
                "Total Entropy",
                f"{entropy_results['S_total']:.4f} J/(mol.K)"
            )

        with tab4:

            st.subheader("Pure Component Fugacity")

            col1, col2 = st.columns(2)

            col1.metric(
                "Fugacity Coefficient",
                f"{fugacity_results['phi']:.6f}"
            )

            col2.metric(
                "Fugacity",
                f"{fugacity_results['fugacity']:.6f} bar"
            )

            st.divider()

            st.metric(
                "Log Fugacity Coefficient",
                f"{fugacity_results['ln_phi']:.6f}"
            )

        with tab5:

            st.subheader("Phase Stability Analysis")

            st.write(
                f"**Predicted Stable Phase:** "
                f"{pvt_results['stable_phase'].capitalize()}"
            )

            st.info(
                pvt_results["stability_message"]
            )

            st.divider()

            if pvt_results["phi_liquid"] is not None:

                col1, col2 = st.columns(2)

                col1.metric(
                    "Liquid-like Fugacity Coefficient",
                    f"{pvt_results['phi_liquid']:.6f}"
                )

                col2.metric(
                    "Vapor-like Fugacity Coefficient",
                    f"{pvt_results['phi_vapor']:.6f}"
                )

            st.divider()

            st.markdown("**Compressibility Roots**")

            for i, root in enumerate(roots, start=1):

                st.write(
                    f"Root {i}: {float(root):.8f}"
                )


    except Exception as error:

        st.error(
            f"Calculation error: {error}"
        )

        st.exception(error)

st.divider()

st.header("P–V Isotherms")

st.write(
    "Generate pressure-volume isotherms "
    "for the selected gas using the Peng-Robinson EOS."
)

if st.button(
    "Generate P-V Graph",
    use_container_width=False
):

    try:

        graph_path = plot_pv_graph(gas)

        if os.path.exists(graph_path):

            st.image(
                graph_path,
                caption=f"P-V Isotherms for {gas}",
                use_container_width=True
            )

            st.success(
                "Graph generated successfully!"
            )

        else:

            st.warning(
                "Graph file was not found."
            )

    except Exception as error:

        st.error(
            f"Graph generation error: {error}"
        )

st.divider()

st.caption(
    "Real Gas Property Calculator | "
    "Peng-Robinson Equation of State"
)
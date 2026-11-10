# Real Gas Property Calculator

A Python-based thermodynamic software for predicting the PVT behaviour and thermodynamic properties of pure real gases using four cubic equations of state.

The application is built using Python and Streamlit, with an interactive interface for performing calculations, comparing EOS models, generating graphs and exporting results.

## 1. Introduction

The Real Gas Property Calculator is designed to study the behaviour of real gases under different temperature and pressure conditions.

Unlike the ideal gas equation, real gas models account for the effect of intermolecular forces and the finite volume occupied by gas molecules. These effects become particularly important at high pressures and near the critical region.

The software uses four cubic equations of state (EOS) to calculate the properties of pure gases. It also includes calculations for enthalpy, entropy, fugacity and compressibility factor.

Users can select a gas, choose an equation of state, enter operating conditions and obtain the calculated results through an interactive Streamlit interface.

## 2. Objectives

The main objectives of this project are:

- To predict the PVT behaviour of real gases using cubic equations of state.
- To calculate the compressibility factor and molar volume.
- To calculate enthalpy and entropy using ideal-gas and departure contributions.
- To determine pure-component fugacity and fugacity coefficient.
- To identify liquid-like and vapour-like roots when multiple real roots are available.
- To provide an automatic phase-selection option based on fugacity comparison.
- To compare the predictions of different cubic equations of state.
- To generate pressure-volume graphs and export calculated results.

## 3. Equations of State Available

The software currently supports four cubic equations of state:

1. **Peng–Robinson (PR) EOS**
2. **Soave–Redlich–Kwong (SRK) EOS**
3. **Redlich–Kwong (RK) EOS**
4. **Van der Waals (VDW) EOS**

These models use critical properties and the acentric factor of each gas to calculate the required EOS parameters.

## 4. Gases Available

The software currently supports five pure gases:

1. Methane (CH₄)
2. Ethane (C₂H₆)
3. Propane (C₃H₈)
4. Carbon Dioxide (CO₂)
5. Nitrogen (N₂)

The gas data module stores the critical temperature, critical pressure, acentric factor, molecular weight and ideal-gas heat capacity for each component.

## 5. Main Features

### PVT Calculations
- Calculation of EOS parameters.
- Calculation of compressibility factor (Z).
- Calculation of molar volume.
- Calculation of pressure-volume behaviour at specified conditions.

### Phase and Root Analysis
- Identification of real roots of the cubic EOS.
- Selection of liquid-like and vapour-like roots when multiple valid roots are available.
- Automatic phase selection using a comparison of fugacity coefficients.
- Manual selection of vapour or liquid phase.

### Thermodynamic Properties
- Ideal-gas enthalpy calculation.
- Enthalpy departure calculation.
- Total enthalpy calculation.
- Ideal-gas entropy calculation.
- Entropy departure calculation.
- Total entropy calculation.

### Fugacity Calculations
- Calculation of pure-component fugacity coefficient.
- Calculation of pure-component fugacity.

### Graphical Analysis
- Generation of P–V isotherms for an individual EOS.
- Generation of comparison graphs for all four EOS models.
- Comparison of predicted pressure-volume behaviour at different conditions.

### Data Export
- Export of calculated results as CSV files.
- Export of EOS comparison results as CSV files.

## 6. Project Structure

The project is organised into separate Python modules, with each module handling a specific part of the calculations.

```text
real-gas-property-calculator/
│
├── README.md
├── requirements.txt
│
└── src/
    ├── main.py
    ├── gas_data.py
    ├── eos.py
    ├── enthalpy.py
    ├── entropy.py
    ├── fugacity.py
    └── graphs.py
```

### Description of Python Modules

| File | Purpose |
|---|---|
| `main.py` | Streamlit interface and integration of all calculations |
| `gas_data.py` | Stores pure-component properties |
| `eos.py` | EOS parameters, compressibility factor, roots, molar volume and fugacity coefficient |
| `enthalpy.py` | Ideal-gas and departure enthalpy calculations |
| `entropy.py` | Ideal-gas and departure entropy calculations |
| `fugacity.py` | Pure-component fugacity calculations |
| `graphs.py` | Pressure-volume graphs and EOS comparison plots |

## 7. Technologies and Libraries Used

- **Python** – Main programming language.
- **Streamlit** – Interactive web application interface.
- **NumPy** – Numerical calculations and polynomial root analysis.
- **Matplotlib** – Graph generation.
- **Pandas** – Tabular data handling and CSV export.

## 8. Installation and Execution

### Requirements

Python 3.10 or a compatible version is recommended.

### Step 1: Clone the repository

```bash
git clone https://github.com/visheshagrawal1506-ops/real-gas-property-calculator.git
```

### Step 2: Open the project directory

```bash
cd real-gas-property-calculator
```

### Step 3: Install the required libraries

```bash
pip install -r requirements.txt
```

### Step 4: Run the application

```bash
py -m streamlit run src/main.py
```

The application will open in your default web browser.

## 9. Assumptions and Limitations

- The current implementation deals with pure gases rather than gas mixtures.
- Ideal-gas heat capacity is treated as constant in the enthalpy and entropy calculations.
- Enthalpy and entropy are reported relative to the reference conditions defined in the software.
- Liquid-like and vapour-like roots are identified from the valid real roots of the cubic EOS.
- Automatic phase selection uses fugacity coefficient comparison as a simplified stability criterion. It is not a complete vapour-liquid equilibrium or flash calculation.
- Cubic equations of state are approximate models, and their predictions may differ from experimental values.

## 10. Future Scope

The project can be extended through:

- Addition of more pure-component gas data.
- Extension to gas mixtures using mixing rules.
- Vapour-liquid equilibrium and flash calculations.
- Temperature-dependent ideal-gas heat capacity.
- Comparison with experimental PVT data.
- Additional thermodynamic properties.
- Improved graphical and numerical analysis.

## 11. Conclusion

The Real Gas Property Calculator provides an interactive way to study the PVT behaviour and thermodynamic properties of pure real gases.

By implementing four cubic equations of state, the software allows users to compare different models and examine their predictions under varying operating conditions. The addition of enthalpy, entropy, fugacity, phase and graphical calculations makes it useful as a learning and computational tool for chemical engineering thermodynamics.

---

**Repository:** https://github.com/visheshagrawal1506-ops/real-gas-property-calculator

**Live Application:** https://real-gas-property-calculator.streamlit.app

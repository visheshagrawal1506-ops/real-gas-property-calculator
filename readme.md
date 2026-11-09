# Real Gas Property Calculator

## 1. Introduction

The Real Gas Property Calculator is a Python-based thermodynamic software developed using the Peng-Robinson Equation of State (PR EOS).

The main purpose of this software is to study the PVT behaviour of real gases and calculate their thermodynamic properties at different temperatures and pressures.

Unlike an ideal gas model, the Peng-Robinson equation considers the effect of intermolecular forces and the finite volume occupied by gas molecules.

The software provides an interactive interface where users can select a gas, enter the required conditions and obtain the calculated properties.

## 2. Objectives

The main objectives of this project are:

- To predict the PVT behaviour of real gases using the Peng-Robinson equation.
- To calculate the compressibility factor and molar volume.
- To determine enthalpy and entropy using ideal-gas and departure contributions.
- To calculate pure-component fugacity and fugacity coefficient.
- To identify liquid-like and vapor-like roots when multiple real roots are available.
- To generate pressure-volume graphs for different temperature conditions.

## 3. Gases Available

The software currently supports the following five pure gases:

1. Methane
2. Ethane
3. Propane
4. Carbon Dioxide
5. Nitrogen

The critical temperature, critical pressure, acentric factor, molecular weight and ideal-gas heat capacity values are stored in the gas data module.

## 4. Features

The main features of the software are:

- Calculation of Peng-Robinson EOS parameters.
- Calculation of compressibility factor (Z).
- Calculation of molar volume.
- Identification of liquid-like and vapor-like roots.
- Automatic phase selection using a simplified fugacity comparison.
- Calculation of ideal-gas enthalpy.
- Calculation of enthalpy departure.
- Calculation of total enthalpy.
- Calculation of ideal-gas entropy.
- Calculation of entropy departure.
- Calculation of total entropy.
- Calculation of pure-component fugacity coefficient.
- Calculation of pure-component fugacity.
- Generation of pressure-volume isotherms.

## 5. Project Structure

The project is divided into different Python modules. Each module performs a particular calculation.

```text
real_gas_software/
│
├── src/
│   ├── gas_data.py
│   ├── eos.py
│   ├── enthalpy.py
│   ├── entropy.py
│   ├── fugacity.py
│   ├── graphs.py
│   └── main.py
│
├── requirements.txt
└── README.md
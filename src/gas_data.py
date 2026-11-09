GAS_DATA = {

    "methane": {
        "name": "Methane",
        "formula": "CH4",
        "Tc": 190.564,
        "Pc": 45.99,
        "omega": 0.01142,
        "MW": 16.043,
        "Cp_ig": 35.69
    },

    "ethane": {
        "name": "Ethane",
        "formula": "C2H6",
        "Tc": 305.32,
        "Pc": 48.72,
        "omega": 0.0995,
        "MW": 30.070,
        "Cp_ig": 52.49
    },

    "propane": {
        "name": "Propane",
        "formula": "C3H8",
        "Tc": 369.83,
        "Pc": 42.48,
        "omega": 0.1523,
        "MW": 44.097,
        "Cp_ig": 73.60
    },

    "carbon_dioxide": {
        "name": "Carbon Dioxide",
        "formula": "CO2",
        "Tc": 304.13,
        "Pc": 73.77,
        "omega": 0.22394,
        "MW": 44.010,
        "Cp_ig": 37.13
    },

    "nitrogen": {
        "name": "Nitrogen",
        "formula": "N2",
        "Tc": 126.192,
        "Pc": 33.958,
        "omega": 0.0372,
        "MW": 28.014,
        "Cp_ig": 29.12
    }
}

REFERENCE_TEMPERATURE = 298.15  # K
REFERENCE_PRESSURE = 1.0       # bar

H_REFERENCE = 0.0  # J/mol
S_REFERENCE = 0.0  # J/mol/K


def get_gas_properties(gas_key):

    gas_key = gas_key.strip().lower()

    if gas_key not in GAS_DATA:
        raise ValueError(
            f"Gas '{gas_key}' is not available in the database."
        )

    return GAS_DATA[gas_key].copy()


def get_available_gases():

    return list(GAS_DATA.keys())


def display_gas_properties(gas_key):

    properties = get_gas_properties(gas_key)

    print("\n------ GAS PROPERTIES ------")

    print("Name:", properties["name"])
    print("Formula:", properties["formula"])

    print("Critical Temperature:",
          properties["Tc"], "K")

    print("Critical Pressure:",
          properties["Pc"], "bar")

    print("Acentric Factor:",
          properties["omega"])

    print("Molecular Weight:",
          properties["MW"], "g/mol")

    print("Ideal Gas Heat Capacity:",
          properties["Cp_ig"], "J/mol/K")

    print("----------------------------")


if __name__ == "__main__":

    print("AVAILABLE GASES:")

    for gas in get_available_gases():
        print("-", gas)

    display_gas_properties("methane")

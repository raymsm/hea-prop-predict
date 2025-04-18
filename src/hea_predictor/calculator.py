import pandas as pd
import numpy as np
import sys

# --- Constants ---
AVOGADRO_NUMBER = 6.02214076e23  # atoms/mol

def calculate_density_rom(composition, element_data):
    """
    Calculates the theoretical density using a rule-of-mixtures based on molar volume.
    Density = M_mix / Vm_mix
    Vm_mix = Sum(xi * Vm_i)
    Vm_i = Mi / rho_i

    Args:
        composition (dict): {element_symbol: atomic_fraction}.
        element_data (pd.DataFrame): DataFrame with element properties, indexed by symbol.

    Returns:
        float: Predicted density in g/cm³, or None if calculation fails.
    """
    total_molar_volume = 0.0
    total_molar_mass = 0.0
    missing_data_elements = []

    for element, fraction in composition.items():
        if element not in element_data.index:
            print(f"Error: Element '{element}' not found in property data.", file=sys.stderr)
            return None

        props = element_data.loc[element]
        atomic_mass = props['AtomicMass_amu']
        density = props['Density_g_cm3']

        if pd.isna(atomic_mass) or pd.isna(density):
            missing_data_elements.append(f"{element} (mass or density)")
            continue
        if density <= 0:
             print(f"Warning: Density for element {element} is non-positive ({density}). Skipping its contribution to density.", file=sys.stderr)
             continue # Avoid division by zero or nonsensical results

        molar_volume = atomic_mass / density  # cm³/mol
        total_molar_volume += fraction * molar_volume
        total_molar_mass += fraction * atomic_mass

    if missing_data_elements:
        print(f"Warning: Missing atomic mass or density data for: {', '.join(missing_data_elements)}. Density prediction might be inaccurate.", file=sys.stderr)

    if total_molar_volume <= 0:
        print(f"Error: Calculated total molar volume is non-positive ({total_molar_volume:.4f}). Cannot calculate density.", file=sys.stderr)
        return None
    if total_molar_mass <= 0:
         print(f"Error: Calculated total molar mass is non-positive ({total_molar_mass:.4f}). Cannot calculate density.", file=sys.stderr)
         return None


    predicted_density = total_molar_mass / total_molar_volume
    return predicted_density


def calculate_lattice_parameter_vegard(composition, element_data):
    """
    Calculates the theoretical lattice parameter 'a' using Vegard's Law.
    a_mix = Sum(xi * a_i)

    Args:
        composition (dict): {element_symbol: atomic_fraction}.
        element_data (pd.DataFrame): DataFrame with element properties, indexed by symbol.

    Returns:
        tuple: (predicted_lattice_param_A, list_of_structures, warning_issued)
               Returns (None, [], True) if calculation fails.
               warning_issued is True if structures differ or data is missing.
    """
    predicted_lattice_param = 0.0
    structures = set()
    contributing_elements = 0
    warning_issued = False
    missing_data_elements = []

    for element, fraction in composition.items():
        if element not in element_data.index:
            print(f"Error: Element '{element}' not found in property data.", file=sys.stderr)
            return None, [], True # Indicate failure

        props = element_data.loc[element]
        lattice_param = props['LatticeParameter_a_A']
        structure = props['CrystalStructure']

        if pd.isna(lattice_param) or lattice_param <= 0:
            missing_data_elements.append(f"{element} (lattice param)")
            continue # Skip elements with missing/invalid data

        predicted_lattice_param += fraction * lattice_param
        if pd.notna(structure):
            structures.add(str(structure).upper()) # Store unique structures found
        else:
            missing_data_elements.append(f"{element} (structure)")
        contributing_elements += 1


    if missing_data_elements:
         print(f"Warning: Missing or invalid lattice parameter/structure data for: {', '.join(missing_data_elements)}. Lattice parameter prediction might be inaccurate.", file=sys.stderr)
         warning_issued = True

    if contributing_elements == 0:
         print(f"Error: No elements with valid lattice parameter data found in composition.", file=sys.stderr)
         return None, [], True # Indicate failure

    if len(structures) > 1:
        print(f"Warning: Constituent elements have different crystal structures ({', '.join(sorted(list(structures)))}). Vegard's Law prediction assumes an 'average' but is physically less meaningful.", file=sys.stderr)
        warning_issued = True
    elif len(structures) == 0 and contributing_elements > 0:
        print(f"Warning: Crystal structures for contributing elements are undefined in the data. Vegard's Law applicability is unknown.", file=sys.stderr)
        warning_issued = True


    return predicted_lattice_param, sorted(list(structures)), warning_issued


def calculate_thermal_conductivity_rom(composition, element_data):
    """
    Calculates the thermal conductivity using a simple linear rule-of-mixtures.
    k_mix = Sum(xi * k_i)

    Args:
        composition (dict): {element_symbol: atomic_fraction}.
        element_data (pd.DataFrame): DataFrame with element properties, indexed by symbol.

    Returns:
        float: Predicted thermal conductivity in W/m·K, or None if calculation fails.
    """
    predicted_conductivity = 0.0
    contributing_elements = 0
    missing_data_elements = []

    for element, fraction in composition.items():
        if element not in element_data.index:
            print(f"Error: Element '{element}' not found in property data.", file=sys.stderr)
            return None # Indicate failure

        props = element_data.loc[element]
        conductivity = props['ThermalConductivity_W_mK']

        if pd.isna(conductivity):
             missing_data_elements.append(f"{element} (conductivity)")
             continue # Skip elements with missing data

        predicted_conductivity += fraction * conductivity
        contributing_elements += 1

    if missing_data_elements:
        print(f"Warning: Missing thermal conductivity data for: {', '.join(missing_data_elements)}. Prediction might be inaccurate.", file=sys.stderr)

    if contributing_elements == 0:
         print(f"Error: No elements with valid thermal conductivity data found in composition.", file=sys.stderr)
         return None # Indicate failure

    print("Warning: Thermal conductivity prediction uses a simple linear average (Sum xi*ki), which is a VERY rough estimate for alloys and ignores scattering effects.", file=sys.stderr)
    return predicted_conductivity
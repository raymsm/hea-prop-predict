import pandas as pd
import os
import sys

def load_element_data(filepath):
    """
    Loads elemental property data from a CSV file.

    Args:
        filepath (str): Path to the CSV data file.

    Returns:
        pandas.DataFrame: DataFrame containing element properties, indexed by 'Symbol'.
                          Returns None if the file cannot be loaded or is invalid.

    Raises:
        FileNotFoundError: If the filepath does not exist.
        ValueError: If required columns are missing in the CSV.
    """
    if not os.path.exists(filepath):
        raise FileNotFoundError(f"Error: Data file not found at '{filepath}'")

    try:
        df = pd.read_csv(filepath, comment='#') # Allow comments starting with #
        df['Symbol'] = df['Symbol'].str.strip()
        df.set_index('Symbol', inplace=True)

        # --- Basic Validation ---
        required_columns = [
            'AtomicMass_amu', 'Density_g_cm3',
            'CrystalStructure', 'LatticeParameter_a_A',
            'ThermalConductivity_W_mK'
        ]
        missing_cols = [col for col in required_columns if col not in df.columns]
        if missing_cols:
            raise ValueError(f"Error: Missing required columns in data file '{filepath}': {', '.join(missing_cols)}")

        # Convert numeric columns, handling potential errors
        numeric_cols = ['AtomicMass_amu', 'Density_g_cm3', 'LatticeParameter_a_A', 'ThermalConductivity_W_mK']
        for col in numeric_cols:
            df[col] = pd.to_numeric(df[col], errors='coerce') # Convert non-numeric to NaN

        return df

    except pd.errors.EmptyDataError:
        print(f"Error: Data file '{filepath}' is empty.", file=sys.stderr)
        return None
    except Exception as e:
        print(f"Error loading data from '{filepath}': {e}", file=sys.stderr)
        return None


def parse_composition(composition_str):
    """
    Parses the composition string (e.g., "Fe:0.6,Ni:0.4") into a dictionary.

    Args:
        composition_str (str): String representing the composition.

    Returns:
        dict: Dictionary of {element_symbol: atomic_fraction}.
              Returns None if parsing fails or fractions don't sum close to 1.0.
    """
    composition = {}
    total_fraction = 0.0
    try:
        parts = composition_str.split(',')
        if not parts or parts == ['']:
             raise ValueError("Composition string is empty.")

        for part in parts:
            element, fraction_str = part.strip().split(':')
            element = element.strip()
            fraction = float(fraction_str.strip())

            if not element:
                raise ValueError("Element symbol cannot be empty.")
            if fraction < 0 or fraction > 1:
                raise ValueError(f"Fraction for {element} ({fraction}) must be between 0 and 1.")
            if element in composition:
                raise ValueError(f"Duplicate element '{element}' found in composition.")

            composition[element] = fraction
            total_fraction += fraction

        # Check if fractions sum close to 1.0
        if not (0.999 < total_fraction < 1.001):
            print(f"Warning: Input fractions sum to {total_fraction:.4f}. They will be normalized.", file=sys.stderr)
            # Normalize fractions
            normalized_composition = {el: frac / total_fraction for el, frac in composition.items()}
            return normalized_composition
        else:
            return composition

    except ValueError as e:
        print(f"Error parsing composition string '{composition_str}': {e}", file=sys.stderr)
        return None
    except Exception as e:
        print(f"Unexpected error parsing composition string '{composition_str}': {e}", file=sys.stderr)
        return None
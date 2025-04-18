import argparse
import sys
import os
import pandas as pd
from . import data_loader
from . import calculator
from . import __version__

# Determine default data file path relative to this script file
DEFAULT_DATA_FILE = os.path.join(os.path.dirname(__file__), '..', '..', 'data', 'element_data.csv')
DEFAULT_DATA_FILE = os.path.abspath(DEFAULT_DATA_FILE) # Get absolute path

def main():
    parser = argparse.ArgumentParser(
        description=f"HEA Property Predictor (v{__version__}). Predicts basic properties of High Entropy Alloys "
                    "using Rule-of-Mixtures and Vegard's Law. "
                    "NOTE: Predictions are APPROXIMATIONS based on simplified models.",
        formatter_class=argparse.RawTextHelpFormatter # Preserve newlines in help
    )

    parser.add_argument(
        "composition",
        type=str,
        help="Composition of the material in atomic fractions. \n"
             "Format: 'Elem1:frac1,Elem2:frac2,...' (e.g., 'Fe:0.2,Co:0.2,Ni:0.2,Cr:0.2,Mn:0.2').\n"
             "Fractions should ideally sum to 1.0 (will be normalized otherwise)."
    )

    parser.add_argument(
        "-d", "--data",
        type=str,
        default=DEFAULT_DATA_FILE,
        help=f"Path to the element property data CSV file.\n(Default: {DEFAULT_DATA_FILE})"
    )

    parser.add_argument(
        "-o", "--output",
        type=str,
        default=None,
        help="Optional path to save the results to a text file."
    )

    parser.add_argument(
        "-v", "--version",
        action="version",
        version=f"%(prog)s {__version__}"
    )

    args = parser.parse_args()

    # --- 1. Load Data ---
    try:
        element_data = data_loader.load_element_data(args.data)
        if element_data is None:
            sys.exit(1) # Error message already printed by loader
    except FileNotFoundError:
         print(f"Error: Data file not found at '{args.data}'. Please check the path or use the -d option.", file=sys.stderr)
         sys.exit(1)
    except ValueError as e:
         print(f"Error reading data file '{args.data}': {e}", file=sys.stderr)
         sys.exit(1)
    except Exception as e:
         print(f"An unexpected error occurred while loading data: {e}", file=sys.stderr)
         sys.exit(1)


    # --- 2. Parse Composition ---
    composition_dict = data_loader.parse_composition(args.composition)
    if composition_dict is None:
        sys.exit(1) # Error message already printed by parser


    # --- 3. Validate Elements ---
    valid_elements = True
    for element in composition_dict.keys():
        if element not in element_data.index:
            print(f"Error: Element '{element}' from composition not found in the data file '{args.data}'.", file=sys.stderr)
            valid_elements = False
    if not valid_elements:
        print("Please check element symbols in your composition or update the data file.", file=sys.stderr)
        sys.exit(1)


    # --- 4. Perform Calculations ---
    print("\n--- Calculating Properties ---")
    predicted_density = calculator.calculate_density_rom(composition_dict, element_data)
    lattice_param_result = calculator.calculate_lattice_parameter_vegard(composition_dict, element_data)
    predicted_lattice_param, structures, _ = lattice_param_result # Unpack result
    predicted_conductivity = calculator.calculate_thermal_conductivity_rom(composition_dict, element_data)

    # --- 5. Display Results ---
    results = []
    results.append("--- HEA Property Prediction Results ---")
    results.append(f"Input Composition (Atomic Fractions): {composition_dict}")
    results.append("-" * 35)
    results.append("Predicted Properties (Approximate):")

    if predicted_density is not None:
        results.append(f"  Density (RoM):             {predicted_density:.3f} g/cm³")
    else:
        results.append("  Density (RoM):             Calculation Failed")

    if predicted_lattice_param is not None:
         structure_info = f" (Based on structures: {', '.join(structures)})" if structures else " (Structure info missing/mixed)"
         results.append(f"  Lattice Parameter (Vegard):  {predicted_lattice_param:.4f} Å {structure_info}")
    else:
         results.append( "  Lattice Parameter (Vegard):  Calculation Failed")

    if predicted_conductivity is not None:
        results.append(f"  Thermal Conductivity (RoM): {predicted_conductivity:.2f} W/m·K")
    else:
        results.append( "  Thermal Conductivity (RoM): Calculation Failed")

    results.append("-" * 35)
    results.append("IMPORTANT NOTES:")
    results.append(" - These predictions are based on simplified Rule-of-Mixtures/Vegard's Law.")
    results.append(" - Real HEA properties can deviate significantly due to phase formation,")
    results.append("   lattice distortion, electronic effects, and microstructure.")
    results.append(" - Vegard's Law is most applicable when constituents share the same crystal structure.")
    results.append(" - Thermal conductivity estimates are particularly rough approximations.")
    results.append(" - Accuracy depends heavily on the quality of the input elemental data.")
    results.append(" - Use these results for initial screening, not for final design.")

    output_string = "\n".join(results)
    print(f"\n{output_string}\n") # Print to console regardless

    # --- 6. Save Output (Optional) ---
    if args.output:
        try:
            with open(args.output, 'w') as f:
                f.write(output_string + "\n")
            print(f"Results saved to '{args.output}'")
        except IOError as e:
            print(f"Error: Could not write results to file '{args.output}': {e}", file=sys.stderr)


if __name__ == "__main__":
    main()
# HEA Property Predictor


A command-line tool to provide rapid, *approximate* estimates for basic properties (density, lattice parameter, thermal conductivity) of High Entropy Alloys (HEAs) based on their elemental composition. It utilizes simple Rule-of-Mixtures (RoM) and Vegard's Law models.

**Current Version:** 0.1.0

## :warning: Important Limitations :warning:

This tool is designed for **initial screening and hypothesis generation ONLY**. The underlying models (RoM, Vegard's Law) are highly simplified and have significant limitations:

1.  **Ideal Solution Assumption:** They assume an ideal solid solution forms, ignoring complex phase formation (e.g., intermetallics, phase separation), which is common in real HEAs.
2.  **Vegard's Law:** Strictly applies only when constituent elements share the *same crystal structure* and form a substitutional solid solution. The tool applies the formula regardless but issues warnings if structures differ or are unknown, as the physical meaning becomes less clear.
3.  **Lattice Distortion:** Ignores lattice distortion effects beyond simple averaging.
4.  **Thermal Conductivity:** The simple linear average for thermal conductivity is a **very rough estimate**. It neglects dominant electron and phonon scattering mechanisms crucial in alloys.
5.  **Data Dependency:** Predictions are entirely dependent on the accuracy and consistency of the elemental property data provided (`data/element_data.csv`). Use reliable data sources and be aware of variations (e.g., properties depend on temperature and phase).
6.  **Not for Design:** Do **NOT** use these results for final engineering design or quantitative analysis without experimental validation or more sophisticated modeling.

## Functionality

* Takes elemental composition (atomic fractions) as input.
* Loads elemental properties (atomic mass, density, crystal structure, lattice parameter 'a', thermal conductivity) from a CSV file.
* Calculates:
    * **Density:** Based on molar volume RoM.
    * **Lattice Parameter ('a'):** Based on Vegard's Law (linear average of constituent 'a' parameters).
    * **Thermal Conductivity:** Based on a linear RoM (simple average).
* Outputs predicted values to the console and optionally to a file.
* Includes warnings about model limitations and data inconsistencies.

## Installation

1.  **Clone the repository:**
    ```bash
    git clone [https://github.com/](https://github.com/)raymsm/hea-prop-predict.git
    cd hea-prop-predict
    ```
2.  **Create a virtual environment (recommended):**
    ```bash
    python -m venv venv
    source venv/bin/activate  # On Windows use `venv\Scripts\activate`
    ```
3.  **Install dependencies:**
    ```bash
    pip install -r requirements.txt
    ```

## Usage

Run the predictor from the command line using the `src/hea_predictor/cli.py` script.

**Basic Syntax:**

```bash
python src/hea_predictor/cli.py "<Composition_String>" [Options]
```
Arguments:
```bash
<Composition_String> (Required): The HEA composition in atomic fractions.
Format: "Elem1:frac1,Elem2:frac2,..."
Example: "Fe:0.2,Co:0.2,Ni:0.2,Cr:0.2,Mn:0.2"
Fractions should ideally sum to 1.0. If they don't, a warning will be issued, and they will be normalized internally for the calculation.
Options:

-d <path>, --data <path>: Path to the CSV file containing elemental property data.
Default: data/element_data.csv relative to the project root.
-o <path>, --output <path>: Path to save the output results to a text file.
Default: Print to console only.
-h, --help: Show the help message and exit.
-v, --version: Show the program's version number and exit.
```
Example:
```bash
# Predict properties for the Cantor alloy (equiatomic FeCoNiCrMn)
python src/hea_predictor/cli.py "Fe:0.2,Co:0.2,Ni:0.2,Cr:0.2,Mn:0.2"

# Use a custom data file and save output
python src/hea_predictor/cli.py "Al:0.1,Co:0.2,Cr:0.2,Fe:0.2,Ni:0.3" -d /path/to/my_custom_data.csv -o cantor_al_results.txt
```
Data File Format (element_data.csv)
The CSV data file requires the following columns:

Symbol: Element symbol (e.g., Fe, Co) - Used as the primary key.
Name: Element name (e.g., Iron) - Informational.
AtomicNumber: Atomic number - Informational.
AtomicMass_amu: Atomic mass in atomic mass units (amu).
Density_g_cm3: Density in g/cm³.
CrystalStructure: Common crystal structure at room temp (e.g., BCC, FCC, HCP). Crucial for Vegard's Law interpretation.
LatticeParameter_a_A: Lattice parameter 'a' in Angstroms (Å) corresponding to the listed structure. For non-cubic structures, using 'a' is a simplification.
ThermalConductivity_W_mK: Thermal conductivity in W/(m·K).
Notes:

Ensure data consistency (e.g., lattice parameter corresponds to the stated crystal structure).
Use # at the beginning of a line for comments in the CSV file.
Missing numeric values or non-positive values (for density, lattice parameter) will cause warnings or calculation failures for that property.
## Contributing
Contributions are welcome! Please feel free to submit pull requests or open issues for bugs, feature requests, or data updates.
Fork the repository.
Create a new branch (git checkout -b feature/your-feature-name).   
Make your changes.
Commit your changes (git commit -am 'Add some feature').
Push to the branch (git push origin feature/your-feature-name).
Create a new Pull Request.
## License
This project is licensed under the MIT License - see the **LICENSE** file for details.   

#!/usr/bin/env python3
"""
Quantum ESPRESSO Workshop Utilities
====================================

A comprehensive utility module for DFT calculations with Quantum ESPRESSO.

This module provides:
- Physical constants and unit conversions
- Shannon ionic radii database
- Input file generators
- Output file parsers
- Convergence analysis tools
- Stability checking functions

Author: DFT Workshop
License: Educational Use

Usage:
    from qe_workshop_utils import *

    # Unit conversions
    energy_ev = ry_to_ev(energy_ry)

    # Generate input files
    input_text = generate_scf_input(prefix='si', ecutwfc=40, ...)

    # Parse outputs
    results = parse_scf_output(output_text)
"""

import numpy as np
from pathlib import Path
import re
import json
from typing import Dict, List, Tuple, Optional, Union
from scipy.optimize import curve_fit

# ==============================================================================
# Physical Constants (CODATA 2018)
# ==============================================================================

BOHR_TO_ANGSTROM = 0.529177210903
ANGSTROM_TO_BOHR = 1.0 / BOHR_TO_ANGSTROM
RY_TO_EV = 13.605693122994
EV_TO_RY = 1.0 / RY_TO_EV
RY_BOHR3_TO_GPA = 14710.507848466
GPA_TO_RY_BOHR3 = 1.0 / RY_BOHR3_TO_GPA
HARTREE_TO_EV = 27.211386245988
KB_EV_K = 8.617333262e-5  # Boltzmann constant in eV/K
HBAR_EV_S = 6.582119569e-16  # Reduced Planck constant in eV·s

# ==============================================================================
# Unit Conversion Functions
# ==============================================================================

def bohr_to_angstrom(value: float) -> float:
    """Convert length from Bohr to Angstrom."""
    return value * BOHR_TO_ANGSTROM

def angstrom_to_bohr(value: float) -> float:
    """Convert length from Angstrom to Bohr."""
    return value * ANGSTROM_TO_BOHR

def ry_to_ev(value: float) -> float:
    """Convert energy from Rydberg to electron-volts."""
    return value * RY_TO_EV

def ev_to_ry(value: float) -> float:
    """Convert energy from electron-volts to Rydberg."""
    return value * EV_TO_RY

def ry_bohr3_to_gpa(value: float) -> float:
    """Convert pressure from Ry/Bohr³ to GPa."""
    return value * RY_BOHR3_TO_GPA

def kbar_to_gpa(value: float) -> float:
    """Convert pressure from kbar to GPa."""
    return value * 0.1

def volume_to_lattice_fcc(volume: float) -> float:
    """Convert FCC primitive cell volume to lattice parameter. V = a³/4"""
    return (4.0 * volume) ** (1.0 / 3.0)

def lattice_to_volume_fcc(a: float) -> float:
    """Convert FCC lattice parameter to primitive cell volume. V = a³/4"""
    return a ** 3 / 4.0

# ==============================================================================
# Shannon Ionic Radii Database (Angstrom)
# Format: {element: {oxidation: {coordination: radius}}}
# Reference: R.D. Shannon, Acta Cryst. A32, 751 (1976)
# ==============================================================================

SHANNON_RADII = {
    # Alkali metals
    'Li': {1: {4: 0.59, 6: 0.76, 8: 0.92}},
    'Na': {1: {4: 0.99, 6: 1.02, 8: 1.18, 12: 1.39}},
    'K':  {1: {6: 1.38, 8: 1.51, 12: 1.64}},
    'Rb': {1: {6: 1.52, 8: 1.61, 12: 1.72}},
    'Cs': {1: {6: 1.67, 8: 1.74, 12: 1.88}},
    # Alkaline earth metals
    'Be': {2: {4: 0.27, 6: 0.45}},
    'Mg': {2: {4: 0.57, 6: 0.72, 8: 0.89}},
    'Ca': {2: {6: 1.00, 8: 1.12, 12: 1.34}},
    'Sr': {2: {6: 1.18, 8: 1.26, 12: 1.44}},
    'Ba': {2: {6: 1.35, 8: 1.42, 12: 1.61}},
    # Transition metals
    'Ti': {2: {6: 0.86}, 3: {6: 0.67}, 4: {4: 0.42, 6: 0.605, 8: 0.74}},
    'V':  {2: {6: 0.79}, 3: {6: 0.64}, 4: {6: 0.58}, 5: {4: 0.355, 6: 0.54}},
    'Cr': {2: {6: 0.80}, 3: {6: 0.615}, 6: {4: 0.26, 6: 0.44}},
    'Mn': {2: {4: 0.66, 6: 0.83}, 3: {6: 0.645}, 4: {4: 0.39, 6: 0.53}, 7: {4: 0.25}},
    'Fe': {2: {4: 0.63, 6: 0.78}, 3: {4: 0.49, 6: 0.645}},
    'Co': {2: {4: 0.58, 6: 0.745}, 3: {6: 0.61}},
    'Ni': {2: {4: 0.55, 6: 0.69}, 3: {6: 0.56}},
    'Cu': {1: {2: 0.46, 4: 0.60, 6: 0.77}, 2: {4: 0.57, 6: 0.73}},
    'Zn': {2: {4: 0.60, 6: 0.74, 8: 0.90}},
    'Zr': {4: {4: 0.59, 6: 0.72, 8: 0.84}},
    # Main group
    'Al': {3: {4: 0.39, 6: 0.535}},
    'Ga': {3: {4: 0.47, 6: 0.62}},
    'In': {3: {6: 0.80, 8: 0.92}},
    'Si': {4: {4: 0.26, 6: 0.40}},
    'Ge': {4: {4: 0.39, 6: 0.53}},
    'Sn': {2: {6: 0.93}, 4: {4: 0.55, 6: 0.69}},
    'Pb': {2: {6: 1.19, 8: 1.29}, 4: {4: 0.65, 6: 0.775}},
    # Anions
    'O':  {-2: {2: 1.35, 3: 1.36, 4: 1.38, 6: 1.40, 8: 1.42}},
    'S':  {-2: {6: 1.84}},
    'Se': {-2: {6: 1.98}},
    'Te': {-2: {6: 2.21}},
    'F':  {-1: {2: 1.285, 4: 1.31, 6: 1.33}},
    'Cl': {-1: {6: 1.81}},
    'Br': {-1: {6: 1.96}},
    'I':  {-1: {6: 2.20}},
    'N':  {-3: {4: 1.46}},
    # Lanthanides (+3 state)
    'La': {3: {6: 1.032, 8: 1.16, 12: 1.36}},
    'Ce': {3: {6: 1.01}, 4: {6: 0.87}},
    'Gd': {3: {6: 0.938}},
    'Yb': {2: {6: 1.02}, 3: {6: 0.868}},
}

def get_shannon_radius(element: str, oxidation: int, coordination: int) -> Optional[float]:
    """
    Get Shannon ionic radius for an element.

    Parameters
    ----------
    element : str
        Element symbol (e.g., 'Fe', 'O')
    oxidation : int
        Oxidation state (e.g., 3 for Fe³⁺, -2 for O²⁻)
    coordination : int
        Coordination number (e.g., 6 for octahedral)

    Returns
    -------
    float or None
        Ionic radius in Angstrom, or None if not found
    """
    if element not in SHANNON_RADII:
        return None
    if oxidation not in SHANNON_RADII[element]:
        return None
    if coordination not in SHANNON_RADII[element][oxidation]:
        return None
    return SHANNON_RADII[element][oxidation][coordination]

# ==============================================================================
# Structure Validation Functions
# ==============================================================================

def check_charge_neutrality(composition: Dict[str, int],
                            oxidation_states: Dict[str, int]) -> Tuple[bool, float]:
    """
    Check if a compound is charge-neutral.

    Parameters
    ----------
    composition : dict
        Element counts, e.g., {'Sr': 1, 'Ti': 1, 'O': 3}
    oxidation_states : dict
        Oxidation states, e.g., {'Sr': 2, 'Ti': 4, 'O': -2}

    Returns
    -------
    is_neutral : bool
    total_charge : float
    """
    total_charge = 0.0
    for element, count in composition.items():
        if element not in oxidation_states:
            return False, float('nan')
        total_charge += count * oxidation_states[element]
    return abs(total_charge) < 1e-6, total_charge

# ==============================================================================
# Input File Generators
# ==============================================================================

def generate_scf_input(prefix: str, ecutwfc: float, ecutrho: float,
                       kpoints: Union[int, Tuple[int, int, int]],
                       pseudo_dir: str,
                       celldm1: float = None,
                       cell_parameters: List[List[float]] = None,
                       atomic_species: List[Tuple[str, float, str]] = None,
                       atomic_positions: List[Tuple[str, float, float, float]] = None,
                       nspin: int = 1,
                       starting_magnetization: List[float] = None,
                       hubbard_u: List[float] = None,
                       conv_thr: float = 1.0e-8) -> str:
    """
    Generate a complete SCF input file for Quantum ESPRESSO.

    Parameters
    ----------
    prefix : str
        Calculation prefix for output files
    ecutwfc : float
        Wavefunction cutoff in Ry
    ecutrho : float
        Charge density cutoff in Ry
    kpoints : int or tuple
        K-point grid (single int for cubic, or (kx, ky, kz) tuple)
    pseudo_dir : str
        Path to pseudopotential directory
    celldm1 : float, optional
        Lattice parameter in Bohr (for ibrav != 0)
    cell_parameters : list, optional
        3x3 list of cell vectors in Angstrom
    atomic_species : list, optional
        List of (symbol, mass, pp_file) tuples
    atomic_positions : list, optional
        List of (symbol, x, y, z) tuples in crystal coordinates
    nspin : int
        1 for non-spin-polarized, 2 for spin-polarized
    starting_magnetization : list, optional
        Initial magnetization for each species
    hubbard_u : list, optional
        Hubbard U values for each species
    conv_thr : float
        SCF convergence threshold in Ry

    Returns
    -------
    str : Complete input file content
    """
    kx, ky, kz = kpoints if isinstance(kpoints, tuple) else (kpoints, kpoints, kpoints)

    # Default atomic species and positions (Silicon)
    if atomic_species is None:
        atomic_species = [('Si', 28.0855, 'Si.upf')]
    if atomic_positions is None:
        atomic_positions = [('Si', 0.0, 0.0, 0.0), ('Si', 0.25, 0.25, 0.25)]

    nat = len(atomic_positions)
    ntyp = len(atomic_species)

    lines = []

    # CONTROL
    lines.append("&CONTROL")
    lines.append("    calculation = 'scf'")
    lines.append(f"    prefix = '{prefix}'")
    lines.append("    outdir = './tmp'")
    lines.append(f"    pseudo_dir = '{pseudo_dir}'")
    lines.append("    verbosity = 'high'")
    lines.append("    tprnfor = .true.")
    lines.append("    tstress = .true.")
    lines.append("/")
    lines.append("")

    # SYSTEM
    lines.append("&SYSTEM")
    lines.append("    ibrav = 0")
    lines.append(f"    nat = {nat}")
    lines.append(f"    ntyp = {ntyp}")
    lines.append(f"    ecutwfc = {ecutwfc}")
    lines.append(f"    ecutrho = {ecutrho}")
    lines.append("    occupations = 'smearing'")
    lines.append("    smearing = 'cold'")
    lines.append("    degauss = 0.01")

    if nspin == 2:
        lines.append(f"    nspin = {nspin}")
        if starting_magnetization:
            for i, mag in enumerate(starting_magnetization, 1):
                lines.append(f"    starting_magnetization({i}) = {mag}")

    if hubbard_u:
        lines.append("    lda_plus_u = .true.")
        for i, u in enumerate(hubbard_u, 1):
            lines.append(f"    Hubbard_U({i}) = {u}")

    lines.append("/")
    lines.append("")

    # ELECTRONS
    lines.append("&ELECTRONS")
    lines.append(f"    conv_thr = {conv_thr}")
    lines.append("    mixing_beta = 0.7")
    lines.append("/")
    lines.append("")

    # ATOMIC_SPECIES
    lines.append("ATOMIC_SPECIES")
    for symbol, mass, pp_file in atomic_species:
        lines.append(f"    {symbol}  {mass}  {pp_file}")
    lines.append("")

    # CELL_PARAMETERS
    if cell_parameters:
        lines.append("CELL_PARAMETERS {angstrom}")
        for vec in cell_parameters:
            lines.append(f"    {vec[0]:16.10f}  {vec[1]:16.10f}  {vec[2]:16.10f}")
        lines.append("")

    # ATOMIC_POSITIONS
    lines.append("ATOMIC_POSITIONS {crystal}")
    for item in atomic_positions:
        symbol, x, y, z = item[0], item[1], item[2], item[3]
        lines.append(f"    {symbol}  {x:12.8f}  {y:12.8f}  {z:12.8f}")
    lines.append("")

    # K_POINTS
    lines.append("K_POINTS {automatic}")
    lines.append(f"    {kx} {ky} {kz} 0 0 0")

    return '\n'.join(lines)

# ==============================================================================
# Output Parsers
# ==============================================================================

def parse_scf_output(output_text: str) -> Dict:
    """
    Parse key quantities from pw.x SCF output.

    Returns
    -------
    dict with keys:
        - converged: bool
        - total_energy_ry: float
        - total_energy_ev: float
        - n_iterations: int
        - total_force: float
        - pressure_kbar: float
        - volume_bohr3: float
        - fermi_energy: float (if available)
    """
    results = {
        'converged': 'convergence has been achieved' in output_text,
        'total_energy_ry': None,
        'total_energy_ev': None,
        'n_iterations': None,
        'total_force': None,
        'pressure_kbar': None,
        'volume_bohr3': None,
        'fermi_energy': None,
    }

    for line in output_text.split('\n'):
        # Total energy
        if '!' in line and 'total energy' in line:
            match = re.search(r'=\s+([\d.E+-]+)\s+Ry', line)
            if match:
                results['total_energy_ry'] = float(match.group(1))
                results['total_energy_ev'] = float(match.group(1)) * RY_TO_EV

        # Convergence iterations
        if 'convergence has been achieved in' in line:
            match = re.search(r'in\s+(\d+)', line)
            if match:
                results['n_iterations'] = int(match.group(1))

        # Volume
        if 'unit-cell volume' in line:
            match = re.search(r'=\s+([\d.]+)', line)
            if match:
                results['volume_bohr3'] = float(match.group(1))

        # Pressure
        if 'total   stress' in line and 'P=' in line:
            match = re.search(r'P=\s*([\d.E+-]+)', line)
            if match:
                results['pressure_kbar'] = float(match.group(1))

        # Total force
        if 'Total force' in line:
            match = re.search(r'Total force\s*=\s*([\d.]+)', line)
            if match:
                results['total_force'] = float(match.group(1))

        # Fermi energy
        if 'Fermi energy' in line:
            match = re.search(r'is\s+([\d.+-]+)', line)
            if match:
                results['fermi_energy'] = float(match.group(1))

        # Band edges (semiconductors)
        # Format: "highest occupied, lowest unoccupied level (ev):     6.2500    6.8500"
        if 'highest occupied, lowest unoccupied' in line:
            match = re.search(r'\(ev\):\s+([\d.]+)\s+([\d.]+)', line, re.IGNORECASE)
            if match:
                results['vbm'] = float(match.group(1))
                results['cbm'] = float(match.group(2))

    return results

def parse_bands_gnu(filename: str) -> Tuple[Optional[np.ndarray], Optional[np.ndarray]]:
    """
    Parse bands.dat.gnu file from QE bands.x.

    Returns
    -------
    k_distances : np.ndarray or None
    bands : np.ndarray or None (shape: nkpts × nbands)
    """
    data = []
    current_band = []

    with open(filename, 'r') as f:
        for line in f:
            line = line.strip()
            if not line:
                if current_band:
                    data.append(current_band)
                    current_band = []
            else:
                parts = line.split()
                if len(parts) >= 2:
                    current_band.append((float(parts[0]), float(parts[1])))

    if current_band:
        data.append(current_band)

    if not data:
        return None, None

    k_distances = np.array([p[0] for p in data[0]])
    bands = np.array([[p[1] for p in band] for band in data]).T

    return k_distances, bands

def parse_dos_output(filename: str) -> Tuple[np.ndarray, np.ndarray, Optional[np.ndarray], Optional[float]]:
    """
    Parse DOS output file from dos.x.

    Returns
    -------
    energy, dos, integrated_dos, fermi_energy
    """
    energy, dos, idos = [], [], []
    fermi = None

    with open(filename, 'r') as f:
        for line in f:
            if line.startswith('#'):
                match = re.search(r'EFermi\s*=\s*([\d.+-]+)', line)
                if match:
                    fermi = float(match.group(1))
                continue
            parts = line.split()
            if len(parts) >= 2:
                energy.append(float(parts[0]))
                dos.append(float(parts[1]))
                if len(parts) >= 3:
                    idos.append(float(parts[2]))

    return np.array(energy), np.array(dos), np.array(idos) if idos else None, fermi

# ==============================================================================
# Analysis Functions
# ==============================================================================

def birch_murnaghan(V: np.ndarray, E0: float, V0: float, B0: float, B0_prime: float) -> np.ndarray:
    """
    Third-order Birch-Murnaghan equation of state.

    E(V) = E0 + (9*V0*B0/16) * [(η-1)³*B0' + (η-1)²*(6-4η)]
    where η = (V0/V)^(2/3)
    """
    V = np.array(V)
    eta = (V0 / V) ** (2.0 / 3.0)
    E = E0 + (9.0 * V0 * B0 / 16.0) * (
        (eta - 1.0) ** 3 * B0_prime +
        (eta - 1.0) ** 2 * (6.0 - 4.0 * eta)
    )
    return E

def fit_birch_murnaghan(volumes: np.ndarray, energies: np.ndarray) -> Tuple[float, float, float, float]:
    """
    Fit Birch-Murnaghan EOS to E(V) data.

    Returns
    -------
    E0, V0, B0, B0_prime
    """
    # Initial guesses
    E0_init = energies.min()
    V0_init = volumes[np.argmin(energies)]
    B0_init = 0.0067  # ~100 GPa in Ry/Bohr³
    B0_prime_init = 4.0

    p0 = [E0_init, V0_init, B0_init, B0_prime_init]
    popt, _ = curve_fit(birch_murnaghan, volumes, energies, p0=p0)

    return tuple(popt)

def analyze_convergence(values: np.ndarray, threshold_mev: float = 1.0,
                        reference_idx: int = -1, n_atoms: int = 1) -> Tuple[np.ndarray, Optional[int]]:
    """
    Analyze convergence of energy values.

    Parameters
    ----------
    values : array
        Energy values in Ry
    threshold_mev : float
        Convergence threshold in meV/atom
    reference_idx : int
        Index of reference value (-1 for last)
    n_atoms : int
        Number of atoms for per-atom normalization

    Returns
    -------
    delta_e : array in meV/atom relative to reference
    converged_idx : first index where convergence is achieved
    """
    values = np.array(values)
    reference = values[reference_idx]

    # Convert Ry to meV/atom
    delta_e = (values - reference) * 13605.693 / n_atoms

    converged_idx = None
    for i, de in enumerate(delta_e):
        if abs(de) <= threshold_mev:
            converged_idx = i
            break

    return delta_e, converged_idx

# ==============================================================================
# Stability Checking
# ==============================================================================

def check_born_stability_cubic(C11: float, C12: float, C44: float) -> Tuple[bool, Dict[str, bool]]:
    """
    Check Born stability criteria for cubic crystals.

    Returns
    -------
    is_stable : bool
    criteria : dict of individual criteria
    """
    criteria = {
        'C11 > 0': C11 > 0,
        'C11 - C12 > 0': (C11 - C12) > 0,
        'C11 + 2*C12 > 0': (C11 + 2*C12) > 0,
        'C44 > 0': C44 > 0
    }
    return all(criteria.values()), criteria

def check_born_stability_hexagonal(C11: float, C12: float, C13: float,
                                   C33: float, C44: float) -> Tuple[bool, Dict[str, bool]]:
    """
    Check Born stability criteria for hexagonal crystals.
    """
    C66 = (C11 - C12) / 2
    criteria = {
        'C11 > |C12|': C11 > abs(C12),
        'C33*(C11+C12) > 2*C13²': C33 * (C11 + C12) > 2 * C13**2,
        'C44 > 0': C44 > 0,
        'C66 > 0': C66 > 0
    }
    return all(criteria.values()), criteria

def calculate_bulk_modulus_voigt(C11: float, C12: float) -> float:
    """Calculate Voigt bulk modulus for cubic crystal: B = (C11 + 2*C12) / 3"""
    return (C11 + 2 * C12) / 3

def calculate_shear_modulus_voigt(C11: float, C12: float, C44: float) -> float:
    """Calculate Voigt shear modulus for cubic crystal: G = (C11 - C12 + 3*C44) / 5"""
    return (C11 - C12 + 3 * C44) / 5

# ==============================================================================
# High-Symmetry K-Points
# ==============================================================================

HIGH_SYMMETRY_POINTS = {
    'FCC': {
        'G': (0.000, 0.000, 0.000),
        'X': (0.500, 0.000, 0.500),
        'W': (0.500, 0.250, 0.750),
        'K': (0.375, 0.375, 0.750),
        'L': (0.500, 0.500, 0.500),
        'U': (0.625, 0.250, 0.625),
    },
    'BCC': {
        'G': (0.000, 0.000, 0.000),
        'H': (0.500, -0.500, 0.500),
        'N': (0.000, 0.000, 0.500),
        'P': (0.250, 0.250, 0.250),
    },
    'HEX': {
        'G': (0.000, 0.000, 0.000),
        'M': (0.500, 0.000, 0.000),
        'K': (0.333, 0.333, 0.000),
        'A': (0.000, 0.000, 0.500),
        'L': (0.500, 0.000, 0.500),
        'H': (0.333, 0.333, 0.500),
    },
    'CUBIC': {
        'G': (0.000, 0.000, 0.000),
        'X': (0.500, 0.000, 0.000),
        'M': (0.500, 0.500, 0.000),
        'R': (0.500, 0.500, 0.500),
    }
}

def generate_kpath_card(crystal_system: str, path: List[Tuple[str, int]] = None) -> str:
    """
    Generate K_POINTS {crystal_b} card for band structure.

    Parameters
    ----------
    crystal_system : str
        'FCC', 'BCC', 'HEX', or 'CUBIC'
    path : list of (name, npoints) tuples, optional

    Returns
    -------
    str : K_POINTS card content
    """
    if crystal_system not in HIGH_SYMMETRY_POINTS:
        return None

    points = HIGH_SYMMETRY_POINTS[crystal_system]

    # Default paths
    default_paths = {
        'FCC': [('G', 20), ('X', 10), ('W', 10), ('K', 20), ('G', 20), ('L', 0)],
        'BCC': [('G', 20), ('H', 20), ('N', 20), ('G', 20), ('P', 0)],
        'HEX': [('G', 20), ('M', 20), ('K', 20), ('G', 20), ('A', 0)],
        'CUBIC': [('G', 20), ('X', 20), ('M', 20), ('G', 20), ('R', 0)],
    }

    if path is None:
        path = default_paths.get(crystal_system, default_paths['CUBIC'])

    lines = ["K_POINTS {crystal_b}"]
    lines.append(str(len(path)))

    for name, npts in path:
        coords = points[name]
        lines.append(f"  {coords[0]:.6f} {coords[1]:.6f} {coords[2]:.6f} {npts}  ! {name}")

    return '\n'.join(lines)

# ==============================================================================
# Module Info
# ==============================================================================

if __name__ == '__main__':
    print("QE Workshop Utilities Module")
    print("=" * 50)
    print("\nAvailable functions:")
    print("  - Unit conversions: bohr_to_angstrom, ry_to_ev, etc.")
    print("  - Structure: check_charge_neutrality, get_shannon_radius")
    print("  - Input: generate_scf_input")
    print("  - Output: parse_scf_output, parse_bands_gnu, parse_dos_output")
    print("  - Analysis: birch_murnaghan, fit_birch_murnaghan, analyze_convergence")
    print("  - Stability: check_born_stability_cubic, check_born_stability_hexagonal")
    print("  - K-paths: generate_kpath_card, HIGH_SYMMETRY_POINTS")
    print("\nExample:")
    print("  from qe_workshop_utils import *")
    print("  energy_ev = ry_to_ev(-15.85)")
    print(f"  >>> {ry_to_ev(-15.85):.4f} eV")

#!/usr/bin/env python3
"""
Workshop Setup Utility - Multi-Functional Support
==================================================

Provides automatic setup for QE workshop with support for:
- PBE (GGA) - Default, most common
- LDA - Local density approximation  
- PBEsol - GGA optimized for solids

Usage in notebooks:
    from workshop_setup import *
    
    # Download pseudopotentials for your elements
    setup_pseudopotentials(['Si', 'O'], functional='PBE')
    
    # Download ALL pseudopotentials at once (run once at workshop start)
    download_all_pseudopotentials()
    
    # Get recommended cutoffs
    ecutwfc, ecutrho = get_recommended_cutoffs(['Si', 'O'])
"""

import os
import sys
import subprocess
import urllib.request
import shutil
import re
from pathlib import Path
from typing import Dict, List, Tuple
from concurrent.futures import ThreadPoolExecutor, as_completed

import numpy as np
import matplotlib.pyplot as plt

plt.rcParams.update({'font.size': 12, 'axes.labelsize': 14, 'figure.figsize': (10, 6)})

# =============================================================================
# PATH CONFIGURATION
# =============================================================================
_THIS_FILE = Path(__file__).resolve()
WORKSHOP_ROOT = _THIS_FILE.parent.parent
NOTEBOOKS_DIR = WORKSHOP_ROOT / 'notebooks_enhanced'
PSEUDO_DIR = WORKSHOP_ROOT / 'pseudopotentials'
OUTPUT_DIR = WORKSHOP_ROOT / 'outputs'

PSEUDO_DIR.mkdir(parents=True, exist_ok=True)
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

# Subdirectories for each functional
(PSEUDO_DIR / 'PBE').mkdir(exist_ok=True)
(PSEUDO_DIR / 'LDA').mkdir(exist_ok=True)
(PSEUDO_DIR / 'PBEsol').mkdir(exist_ok=True)

# =============================================================================
# QE EXECUTABLE CONFIGURATION - Auto-detect QE 7.5 or system installation
# =============================================================================
def _is_docker():
    """Check if running inside Docker container."""
    return Path('/.dockerenv').exists() or os.environ.get('DOCKER_CONTAINER', False)

def _find_qe_executable():
    """
    Auto-detect QE installation path.
    Works for both Docker container and native installations.
    """
    search_paths = [
        # Docker container paths (checked first for Docker env)
        Path('/opt/qe/bin/pw.x'),
        Path('/usr/bin/pw.x'),
        # User compiled QE 7.x paths (for native installations)
        Path.home() / 'src' / 'qe-7.5' / 'bin' / 'pw.x',
        Path.home() / 'src' / 'qe-7.4' / 'bin' / 'pw.x',
        Path.home() / 'src' / 'qe-7.3' / 'bin' / 'pw.x',
        # Other common locations
        Path('/usr/local/bin/pw.x'),
        Path('/opt/quantum-espresso/bin/pw.x'),
    ]
    
    # If in Docker, prioritize Docker paths
    if _is_docker():
        docker_paths = [Path('/opt/qe/bin/pw.x'), Path('/usr/bin/pw.x')]
        for path in docker_paths:
            if path.exists():
                return str(path)
    
    # Check all paths
    for path in search_paths:
        if path.exists():
            return str(path)
    
    # Fall back to PATH
    pw_path = shutil.which('pw.x')
    if pw_path:
        return pw_path
    
    return 'pw.x'  # Default, hope it's in PATH

def _find_mpirun():
    """
    Auto-detect MPI runner.
    Works for both Docker container and native installations.
    """
    search_paths = [
        # Docker typically uses OpenMPI
        Path('/usr/bin/mpirun'),
        # Intel oneAPI (native installations)
        Path('/opt/intel/oneapi/mpi/latest/bin/mpirun'),
        Path.home() / 'intel' / 'oneapi' / 'mpi' / 'latest' / 'bin' / 'mpirun',
        # Other locations
        Path('/usr/local/bin/mpirun'),
    ]
    
    for path in search_paths:
        if path.exists():
            return str(path)
    
    return shutil.which('mpirun') or 'mpirun'

# =============================================================================
# MPI CONFIGURATION
# =============================================================================
NPROCS = int(os.environ.get('QE_NPROCS', (os.cpu_count()//2) or 1))
MPI_COMMAND = os.environ.get('QE_MPI_COMMAND', _find_mpirun())
PW_EXECUTABLE = os.environ.get('QE_PW_EXECUTABLE', _find_qe_executable())

# Other QE executables (auto-detect from same directory as pw.x)
_QE_BIN_DIR = Path(PW_EXECUTABLE).parent if Path(PW_EXECUTABLE).exists() else None
PP_EXECUTABLE = str(_QE_BIN_DIR / 'pp.x') if _QE_BIN_DIR else 'pp.x'
BANDS_EXECUTABLE = str(_QE_BIN_DIR / 'bands.x') if _QE_BIN_DIR else 'bands.x'
DOS_EXECUTABLE = str(_QE_BIN_DIR / 'dos.x') if _QE_BIN_DIR else 'dos.x'
PROJWFC_EXECUTABLE = str(_QE_BIN_DIR / 'projwfc.x') if _QE_BIN_DIR else 'projwfc.x'
PH_EXECUTABLE = str(_QE_BIN_DIR / 'ph.x') if _QE_BIN_DIR else 'ph.x'

# =============================================================================
# PHYSICAL CONSTANTS
# =============================================================================
BOHR_TO_ANGSTROM = 0.529177210903
ANGSTROM_TO_BOHR = 1.0 / BOHR_TO_ANGSTROM
RY_TO_EV = 13.605693122994
EV_TO_RY = 1.0 / RY_TO_EV
RY_TO_MEV = RY_TO_EV * 1000.0
KBAR_TO_GPA = 0.1

# =============================================================================
# PSEUDOPOTENTIAL DATABASE - Comprehensive for All Common Elements
# =============================================================================
# Format: {element: (ecutwfc_Ry, dual_factor, filename)}
# Source: SSSP v1.3 Efficiency (PBE), PSlibrary 1.0.0 (LDA, PBEsol)
# These are tested, reliable pseudopotentials from quantum-espresso.org

PSEUDO_DB = {
    'PBE': {
        # Period 1
        'H':  (60, 8, 'H.pbe-rrkjus_psl.1.0.0.UPF'),
        'He': (50, 4, 'He.pbe-kjpaw_psl.1.0.0.UPF'),
        # Period 2
        'Li': (40, 8, 'Li.pbe-sl-rrkjus_psl.1.0.0.UPF'),
        'Be': (50, 8, 'Be.pbe-n-rrkjus_psl.1.0.0.UPF'),
        'B':  (40, 8, 'B.pbe-n-rrkjus_psl.1.0.0.UPF'),
        'C':  (45, 8, 'C.pbe-n-kjpaw_psl.1.0.0.UPF'),
        'N':  (80, 8, 'N.pbe-n-kjpaw_psl.1.0.0.UPF'),
        'O':  (75, 8, 'O.pbe-n-kjpaw_psl.1.0.0.UPF'),
        'F':  (60, 8, 'F.pbe-n-kjpaw_psl.1.0.0.UPF'),
        'Ne': (80, 4, 'Ne.pbe-n-kjpaw_psl.1.0.0.UPF'),
        # Period 3
        'Na': (40, 8, 'Na.pbe-spn-kjpaw_psl.1.0.0.UPF'),
        'Mg': (35, 8, 'Mg.pbe-spnl-kjpaw_psl.1.0.0.UPF'),
        'Al': (30, 8, 'Al.pbe-nl-kjpaw_psl.1.0.0.UPF'),
        'Si': (40, 8, 'Si.pbe-n-rrkjus_psl.1.0.0.UPF'),
        'P':  (35, 8, 'P.pbe-nl-kjpaw_psl.1.0.0.UPF'),
        'S':  (40, 8, 'S.pbe-nl-kjpaw_psl.1.0.0.UPF'),
        'Cl': (45, 8, 'Cl.pbe-nl-kjpaw_psl.1.0.0.UPF'),
        'Ar': (60, 4, 'Ar.pbe-n-kjpaw_psl.1.0.0.UPF'),
        # Period 4
        'K':  (50, 8, 'K.pbe-spn-kjpaw_psl.1.0.0.UPF'),
        'Ca': (35, 8, 'Ca.pbe-spn-kjpaw_psl.1.0.0.UPF'),
        'Sc': (60, 8, 'Sc.pbe-spn-kjpaw_psl.1.0.0.UPF'),
        'Ti': (60, 8, 'Ti.pbe-spn-kjpaw_psl.1.0.0.UPF'),
        'V':  (55, 8, 'V.pbe-spnl-kjpaw_psl.1.0.0.UPF'),
        'Cr': (60, 12, 'Cr.pbe-spn-kjpaw_psl.1.0.0.UPF'),
        'Mn': (65, 12, 'Mn.pbe-spn-kjpaw_psl.0.3.1.UPF'),
        'Fe': (90, 12, 'Fe.pbe-spn-kjpaw_psl.1.0.0.UPF'),
        'Co': (55, 8, 'Co.pbe-spn-kjpaw_psl.0.3.1.UPF'),
        'Ni': (60, 8, 'Ni.pbe-n-kjpaw_psl.1.0.0.UPF'),
        'Cu': (55, 8, 'Cu.pbe-dn-kjpaw_psl.1.0.0.UPF'),
        'Zn': (50, 8, 'Zn.pbe-dnl-kjpaw_psl.1.0.0.UPF'),
        'Ga': (70, 8, 'Ga.pbe-dn-kjpaw_psl.1.0.0.UPF'),
        'Ge': (45, 8, 'Ge.pbe-dn-kjpaw_psl.1.0.0.UPF'),
        'As': (50, 8, 'As.pbe-n-kjpaw_psl.1.0.0.UPF'),
        'Se': (50, 8, 'Se.pbe-dn-kjpaw_psl.1.0.0.UPF'),
        'Br': (45, 8, 'Br.pbe-n-kjpaw_psl.1.0.0.UPF'),
        'Kr': (50, 4, 'Kr.pbe-dn-kjpaw_psl.1.0.0.UPF'),
        # Period 5
        'Rb': (40, 8, 'Rb.pbe-spn-kjpaw_psl.1.0.0.UPF'),
        'Sr': (40, 8, 'Sr.pbe-spn-kjpaw_psl.1.0.0.UPF'),
        'Y':  (45, 8, 'Y.pbe-spn-kjpaw_psl.1.0.0.UPF'),
        'Zr': (40, 8, 'Zr.pbe-spn-kjpaw_psl.1.0.0.UPF'),
        'Nb': (50, 8, 'Nb.pbe-spn-kjpaw_psl.1.0.0.UPF'),
        'Mo': (50, 8, 'Mo.pbe-spn-kjpaw_psl.1.0.0.UPF'),
        'Tc': (50, 8, 'Tc.pbe-spn-kjpaw_psl.0.3.1.UPF'),
        'Ru': (50, 8, 'Ru.pbe-spn-kjpaw_psl.1.0.0.UPF'),
        'Rh': (50, 8, 'Rh.pbe-spn-kjpaw_psl.1.0.0.UPF'),
        'Pd': (45, 8, 'Pd.pbe-spn-kjpaw_psl.1.0.0.UPF'),
        'Ag': (45, 8, 'Ag.pbe-n-kjpaw_psl.1.0.0.UPF'),
        'Cd': (50, 8, 'Cd.pbe-dnl-kjpaw_psl.1.0.0.UPF'),
        'In': (50, 8, 'In.pbe-dn-kjpaw_psl.1.0.0.UPF'),
        'Sn': (60, 8, 'Sn.pbe-dn-kjpaw_psl.1.0.0.UPF'),
        'Sb': (55, 8, 'Sb.pbe-n-kjpaw_psl.1.0.0.UPF'),
        'Te': (50, 8, 'Te.pbe-n-kjpaw_psl.1.0.0.UPF'),
        'I':  (45, 8, 'I.pbe-n-kjpaw_psl.1.0.0.UPF'),
        'Xe': (50, 4, 'Xe.pbe-dn-kjpaw_psl.1.0.0.UPF'),
        # Period 6
        'Cs': (40, 8, 'Cs.pbe-spn-kjpaw_psl.1.0.0.UPF'),
        'Ba': (35, 8, 'Ba.pbe-spn-kjpaw_psl.1.0.0.UPF'),
        'La': (55, 8, 'La.pbe-spfn-kjpaw_psl.1.0.0.UPF'),
        'Ce': (55, 8, 'Ce.pbe-spdn-kjpaw_psl.1.0.0.UPF'),
        'Hf': (50, 8, 'Hf.pbe-spn-kjpaw_psl.1.0.0.UPF'),
        'Ta': (50, 8, 'Ta.pbe-spn-kjpaw_psl.1.0.0.UPF'),
        'W':  (45, 8, 'W.pbe-spn-kjpaw_psl.1.0.0.UPF'),
        'Re': (50, 8, 'Re.pbe-spn-kjpaw_psl.1.0.0.UPF'),
        'Os': (50, 8, 'Os.pbe-spn-kjpaw_psl.1.0.0.UPF'),
        'Ir': (50, 8, 'Ir.pbe-n-kjpaw_psl.1.0.0.UPF'),
        'Pt': (50, 8, 'Pt.pbe-spfn-kjpaw_psl.1.0.0.UPF'),
        'Au': (50, 8, 'Au.pbe-spfn-kjpaw_psl.1.0.0.UPF'),
        'Hg': (50, 8, 'Hg.pbe-dnl-kjpaw_psl.1.0.0.UPF'),
        'Tl': (50, 8, 'Tl.pbe-dn-kjpaw_psl.1.0.0.UPF'),
        'Pb': (40, 8, 'Pb.pbe-dn-kjpaw_psl.1.0.0.UPF'),
        'Bi': (50, 8, 'Bi.pbe-dn-kjpaw_psl.1.0.0.UPF'),
    },
    'LDA': {
        # Period 1-2
        'H':  (60, 8, 'H.pz-rrkjus_psl.1.0.0.UPF'),
        'Li': (40, 8, 'Li.pz-sl-rrkjus_psl.1.0.0.UPF'),
        'Be': (50, 8, 'Be.pz-n-rrkjus_psl.1.0.0.UPF'),
        'B':  (40, 8, 'B.pz-n-rrkjus_psl.1.0.0.UPF'),
        'C':  (45, 8, 'C.pz-n-kjpaw_psl.1.0.0.UPF'),
        'N':  (80, 8, 'N.pz-n-kjpaw_psl.1.0.0.UPF'),
        'O':  (75, 8, 'O.pz-n-kjpaw_psl.1.0.0.UPF'),
        'F':  (60, 8, 'F.pz-n-kjpaw_psl.1.0.0.UPF'),
        # Period 3
        'Na': (40, 8, 'Na.pz-spn-kjpaw_psl.1.0.0.UPF'),
        'Mg': (35, 8, 'Mg.pz-spnl-kjpaw_psl.1.0.0.UPF'),
        'Al': (30, 8, 'Al.pz-nl-kjpaw_psl.1.0.0.UPF'),
        'Si': (40, 8, 'Si.pz-n-rrkjus_psl.1.0.0.UPF'),
        'P':  (35, 8, 'P.pz-nl-kjpaw_psl.1.0.0.UPF'),
        'S':  (40, 8, 'S.pz-nl-kjpaw_psl.1.0.0.UPF'),
        'Cl': (45, 8, 'Cl.pz-nl-kjpaw_psl.1.0.0.UPF'),
        # Period 4
        'K':  (50, 8, 'K.pz-spn-kjpaw_psl.1.0.0.UPF'),
        'Ca': (35, 8, 'Ca.pz-spn-kjpaw_psl.1.0.0.UPF'),
        'Ti': (60, 8, 'Ti.pz-spn-kjpaw_psl.1.0.0.UPF'),
        'V':  (55, 8, 'V.pz-spnl-kjpaw_psl.1.0.0.UPF'),
        'Cr': (60, 12, 'Cr.pz-spn-kjpaw_psl.1.0.0.UPF'),
        'Mn': (65, 12, 'Mn.pz-spn-kjpaw_psl.1.0.0.UPF'),
        'Fe': (90, 12, 'Fe.pz-spn-kjpaw_psl.1.0.0.UPF'),
        'Co': (55, 8, 'Co.pz-spn-kjpaw_psl.0.3.1.UPF'),
        'Ni': (60, 8, 'Ni.pz-spn-kjpaw_psl.0.3.1.UPF'),
        'Cu': (55, 8, 'Cu.pz-dn-kjpaw_psl.1.0.0.UPF'),
        'Zn': (50, 8, 'Zn.pz-dn-kjpaw_psl.1.0.0.UPF'),
        'Ga': (70, 8, 'Ga.pz-dn-kjpaw_psl.1.0.0.UPF'),
        'Ge': (45, 8, 'Ge.pz-dn-kjpaw_psl.1.0.0.UPF'),
        # Period 5
        'Sr': (40, 8, 'Sr.pz-spn-kjpaw_psl.1.0.0.UPF'),
        'Zr': (40, 8, 'Zr.pz-spn-kjpaw_psl.1.0.0.UPF'),
        'Ag': (45, 8, 'Ag.pz-spn-kjpaw_psl.1.0.0.UPF'),
        # Period 6
        'Ba': (35, 8, 'Ba.pz-spn-kjpaw_psl.1.0.0.UPF'),
        'Au': (50, 8, 'Au.pz-spfn-kjpaw_psl.1.0.0.UPF'),
        'Pb': (40, 8, 'Pb.pz-dn-kjpaw_psl.1.0.0.UPF'),
    },
    'PBEsol': {
        # Period 1-2
        'H':  (60, 8, 'H.pbesol-rrkjus_psl.1.0.0.UPF'),
        'Li': (40, 8, 'Li.pbesol-sl-rrkjus_psl.1.0.0.UPF'),
        'Be': (50, 8, 'Be.pbesol-n-rrkjus_psl.1.0.0.UPF'),
        'B':  (40, 8, 'B.pbesol-n-rrkjus_psl.1.0.0.UPF'),
        'C':  (45, 8, 'C.pbesol-n-kjpaw_psl.1.0.0.UPF'),
        'N':  (80, 8, 'N.pbesol-n-kjpaw_psl.1.0.0.UPF'),
        'O':  (75, 8, 'O.pbesol-n-kjpaw_psl.1.0.0.UPF'),
        'F':  (60, 8, 'F.pbesol-n-kjpaw_psl.1.0.0.UPF'),
        # Period 3
        'Na': (40, 8, 'Na.pbesol-spn-kjpaw_psl.1.0.0.UPF'),
        'Mg': (35, 8, 'Mg.pbesol-spnl-kjpaw_psl.1.0.0.UPF'),
        'Al': (30, 8, 'Al.pbesol-nl-kjpaw_psl.1.0.0.UPF'),
        'Si': (40, 8, 'Si.pbesol-n-rrkjus_psl.1.0.0.UPF'),
        'P':  (35, 8, 'P.pbesol-nl-kjpaw_psl.1.0.0.UPF'),
        'S':  (40, 8, 'S.pbesol-nl-kjpaw_psl.1.0.0.UPF'),
        'Cl': (45, 8, 'Cl.pbesol-nl-kjpaw_psl.1.0.0.UPF'),
        # Period 4
        'K':  (50, 8, 'K.pbesol-spn-kjpaw_psl.1.0.0.UPF'),
        'Ca': (35, 8, 'Ca.pbesol-spn-kjpaw_psl.1.0.0.UPF'),
        'Ti': (60, 8, 'Ti.pbesol-spn-kjpaw_psl.1.0.0.UPF'),
        'V':  (55, 8, 'V.pbesol-spnl-kjpaw_psl.1.0.0.UPF'),
        'Cr': (60, 12, 'Cr.pbesol-spn-kjpaw_psl.1.0.0.UPF'),
        'Mn': (65, 12, 'Mn.pbesol-spn-kjpaw_psl.1.0.0.UPF'),
        'Fe': (90, 12, 'Fe.pbesol-spn-kjpaw_psl.1.0.0.UPF'),
        'Co': (55, 8, 'Co.pbesol-spn-kjpaw_psl.0.3.1.UPF'),
        'Ni': (60, 8, 'Ni.pbesol-spn-kjpaw_psl.0.3.1.UPF'),
        'Cu': (55, 8, 'Cu.pbesol-dn-kjpaw_psl.1.0.0.UPF'),
        'Zn': (50, 8, 'Zn.pbesol-dn-kjpaw_psl.1.0.0.UPF'),
        'Ga': (70, 8, 'Ga.pbesol-dn-kjpaw_psl.1.0.0.UPF'),
        'Ge': (45, 8, 'Ge.pbesol-dn-kjpaw_psl.1.0.0.UPF'),
        # Period 5
        'Sr': (40, 8, 'Sr.pbesol-spn-kjpaw_psl.1.0.0.UPF'),
        'Y':  (45, 8, 'Y.pbesol-spn-kjpaw_psl.1.0.0.UPF'),
        'Zr': (40, 8, 'Zr.pbesol-spn-kjpaw_psl.1.0.0.UPF'),
        'Ag': (45, 8, 'Ag.pbesol-spn-kjpaw_psl.1.0.0.UPF'),
        'Sn': (60, 8, 'Sn.pbesol-dn-kjpaw_psl.1.0.0.UPF'),
        # Period 6
        'Ba': (35, 8, 'Ba.pbesol-spn-kjpaw_psl.1.0.0.UPF'),
        'La': (55, 8, 'La.pbesol-spfn-kjpaw_psl.1.0.0.UPF'),
        'Pt': (50, 8, 'Pt.pbesol-spfn-kjpaw_psl.1.0.0.UPF'),
        'Au': (50, 8, 'Au.pbesol-spfn-kjpaw_psl.1.0.0.UPF'),
        'Pb': (40, 8, 'Pb.pbesol-dn-kjpaw_psl.1.0.0.UPF'),
    },
}

# Backward compatibility
SSSP_EFFICIENCY = PSEUDO_DB['PBE']

# Download URLs
PP_URLS = {
    'PBE': "https://pseudopotentials.quantum-espresso.org/upf_files/",
    'LDA': "https://pseudopotentials.quantum-espresso.org/upf_files/",
    'PBEsol': "https://pseudopotentials.quantum-espresso.org/upf_files/",
}

# =============================================================================
# FUNCTIONAL SELECTION GUIDE
# =============================================================================
FUNCTIONAL_GUIDE = """
╔═══════════════════════════════════════════════════════════════════════════╗
║                    EXCHANGE-CORRELATION FUNCTIONAL GUIDE                  ║
╠═══════════════════════════════════════════════════════════════════════════╣
║                                                                           ║
║  FUNCTIONAL   │ USE FOR                        │ LATTICE ERROR │ NOTES   ║
║ ──────────────┼────────────────────────────────┼───────────────┼──────────║
║  LDA          │ Simple metals, trends          │ -1 to -3%     │ Fastest ║
║  PBE (GGA)    │ General purpose, molecules     │ +1 to +2%     │ DEFAULT ║
║  PBEsol       │ Solids, lattice constants      │ ~0%           │ Accurate║
║  PBE+U        │ Transition metal oxides        │ +1%           │ Add U   ║
║  HSE06        │ Band gaps (expensive)          │ ~0%           │ Hybrid  ║
║                                                                           ║
║  RECOMMENDATIONS:                                                         ║
║  • Start with PBE (most tested, good for most materials)                  ║
║  • Use PBEsol for accurate lattice constants in solids                    ║
║  • Use LDA for simple metals or when comparing to old literature          ║
║  • Add Hubbard U for d/f electron systems (see Notebook 06)               ║
║                                                                           ║
╚═══════════════════════════════════════════════════════════════════════════╝
"""

def print_functional_guide():
    """Print the functional selection guide."""
    print(FUNCTIONAL_GUIDE)


def print_workshop_banner():
    """Print workshop setup summary."""
    print("=" * 70)
    print("QUANTUM ESPRESSO WORKSHOP - SETUP")
    print("=" * 70)
    print("\nPaths:")
    print(f"  Workshop root:     {WORKSHOP_ROOT}")
    print(f"  Pseudopotentials:  {PSEUDO_DIR}")
    print(f"  Output directory:  {OUTPUT_DIR}")
    print("\nQE Executables:")
    print(f"  pw.x:    {PW_EXECUTABLE}")
    print(f"  MPI:     {MPI_COMMAND}")
    print(f"  NPROCS:  {NPROCS}")
    print("\nAvailable functionals: PBE, LDA, PBEsol")
    print(f"Elements in database: PBE({len(PSEUDO_DB['PBE'])}), LDA({len(PSEUDO_DB['LDA'])}), PBEsol({len(PSEUDO_DB['PBEsol'])})")
    print("=" * 70)


def verify_qe_installation():
    """Verify QE is properly installed and working."""
    print("=" * 60)
    print("VERIFYING QUANTUM ESPRESSO INSTALLATION")
    print("=" * 60)
    
    # Check pw.x exists
    pw_path = Path(PW_EXECUTABLE)
    if pw_path.exists():
        print(f"  ✓ pw.x found: {PW_EXECUTABLE}")
    elif shutil.which('pw.x'):
        print(f"  ✓ pw.x in PATH: {shutil.which('pw.x')}")
    else:
        print(f"  ✗ pw.x NOT FOUND!")
        print("    Please install QE or set QE_PW_EXECUTABLE environment variable")
        return False
    
    # Check MPI
    mpi_path = Path(MPI_COMMAND)
    if mpi_path.exists() or shutil.which(MPI_COMMAND):
        print(f"  ✓ MPI found: {MPI_COMMAND}")
    else:
        print(f"  ⚠ MPI not found, will run serial")
    
    # # Try to get version
    result = subprocess.run([PW_EXECUTABLE, '--version'], 
                       capture_output=True, text=True, input="", timeout=10)
    if result.returncode == 0 or 'PWSCF' in result.stdout:
        version_line = [l for l in result.stdout.split('\n') if 'PWSCF' in l or 'v.' in l]
        if version_line:
            print(f"  ✓ Version: {version_line[0].strip()}")
    
    print("=" * 60)
    return True

# =============================================================================
# PSEUDOPOTENTIAL DOWNLOAD FUNCTIONS
# =============================================================================

def download_pseudopotential(element: str, functional: str = 'PBE', 
                             force: bool = False) -> Path:
    """
    Download pseudopotential for an element.
    
    Parameters
    ----------
    element : str
        Element symbol (e.g., 'Si', 'Fe')
    functional : str
        'PBE', 'LDA', or 'PBEsol'
    force : bool
        Re-download even if file exists
    
    Returns
    -------
    Path to downloaded file
    """
    if functional not in PSEUDO_DB:
        raise ValueError(f"Functional '{functional}' not supported. Use: PBE, LDA, PBEsol")
    
    if element not in PSEUDO_DB[functional]:
        raise ValueError(f"Element '{element}' not in {functional} database")
    
    _, _, filename = PSEUDO_DB[functional][element]
    pp_dir = PSEUDO_DIR / functional
    filepath = pp_dir / filename
    
    if filepath.exists() and not force:
        return filepath
    
    url = PP_URLS[functional] + filename
    print(f"  Downloading {element} ({functional}): {filename}...", end=" ", flush=True)
    
    urllib.request.urlretrieve(url, filepath)
    print("✓")
    
    return filepath


def setup_pseudopotentials(elements: List[str], functional: str = 'PBE',
                          verbose: bool = True) -> Dict[str, Path]:
    """
    Download all required pseudopotentials.
    
    Parameters
    ----------
    elements : list
        List of element symbols
    functional : str
        'PBE', 'LDA', or 'PBEsol'
    verbose : bool
        Print status messages
    
    Returns
    -------
    dict : {element: filepath}
    """
    if verbose:
        print("=" * 60)
        print(f"PSEUDOPOTENTIAL SETUP - {functional}")
        print("=" * 60)
    
    result = {}
    missing = []
    
    for elem in elements:
        if elem not in PSEUDO_DB.get(functional, {}):
            print(f"  ⚠ Warning: {elem} not in {functional} database")
            continue
        
        _, _, filename = PSEUDO_DB[functional][elem]
        filepath = PSEUDO_DIR / functional / filename
        
        if filepath.exists():
            if verbose:
                print(f"  ✓ {elem}: {filename}")
            result[elem] = filepath
        else:
            missing.append(elem)
    
    if missing:
        if verbose:
            print(f"\n  Downloading {len(missing)} missing pseudopotentials...")
        for elem in missing:
            result[elem] = download_pseudopotential(elem, functional)
    
    if verbose:
        print("=" * 60)
        print(f"Pseudopotentials ready in: {PSEUDO_DIR / functional}")
        print("=" * 60)
    
    return result


def get_recommended_cutoffs(elements: List[str], functional: str = 'PBE') -> Tuple[float, float]:
    """
    Get recommended ecutwfc and ecutrho.
    
    Returns maximum from SSSP database for the element set.
    """
    max_ecutwfc = 0
    max_dual = 4
    
    db = PSEUDO_DB.get(functional, PSEUDO_DB['PBE'])
    
    for elem in elements:
        if elem in db:
            ecutwfc, dual, _ = db[elem]
            max_ecutwfc = max(max_ecutwfc, ecutwfc)
            max_dual = max(max_dual, dual)
        else:
            print(f"⚠ {elem} not in database, using 60 Ry default")
            max_ecutwfc = max(max_ecutwfc, 60)
    
    return max_ecutwfc, max_ecutwfc * max_dual


def get_pseudopotential_filename(element: str, functional: str = 'PBE') -> str:
    """Get pseudopotential filename for an element."""
    if element in PSEUDO_DB.get(functional, {}):
        return PSEUDO_DB[functional][element][2]
    raise ValueError(f"Element '{element}' not in {functional} database")


def get_pseudo_dir(functional: str = 'PBE') -> Path:
    """Get the pseudopotential directory for a functional."""
    return PSEUDO_DIR / functional


def download_all_pseudopotentials(functionals: List[str] = None, 
                                   max_workers: int = 4,
                                   verbose: bool = True) -> Dict[str, Dict[str, Path]]:
    """
    Download ALL pseudopotentials for workshop use.
    
    Run this ONCE at the start of the workshop to ensure all PPs are available.
    Uses parallel downloads for speed.
    
    Parameters
    ----------
    functionals : list
        List of functionals to download. Default: ['PBE', 'LDA', 'PBEsol']
    max_workers : int
        Number of parallel downloads
    verbose : bool
        Print progress
    
    Returns
    -------
    dict : {functional: {element: filepath}}
    
    Example
    -------
    >>> download_all_pseudopotentials()  # Downloads everything
    >>> download_all_pseudopotentials(['PBE'])  # Only PBE
    """
    if functionals is None:
        functionals = ['PBE', 'LDA', 'PBEsol']
    
    results = {}
    total_downloaded = 0
    total_existing = 0
    failed = []
    
    print("=" * 70)
    print("DOWNLOADING ALL PSEUDOPOTENTIALS FOR WORKSHOP")
    print("=" * 70)
    print(f"Functionals: {', '.join(functionals)}")
    print(f"Target directory: {PSEUDO_DIR}")
    print("=" * 70)
    
    for functional in functionals:
        if functional not in PSEUDO_DB:
            print(f"⚠ Unknown functional: {functional}")
            continue
        
        db = PSEUDO_DB[functional]
        pp_dir = PSEUDO_DIR / functional
        pp_dir.mkdir(exist_ok=True)
        
        results[functional] = {}
        to_download = []
        
        print(f"\n{functional} ({len(db)} elements):")
        
        # Check what's already there
        for elem, (_, _, filename) in db.items():
            filepath = pp_dir / filename
            if filepath.exists():
                results[functional][elem] = filepath
                total_existing += 1
            else:
                to_download.append((elem, filename))
        
        if not to_download:
            print(f"  ✓ All {len(db)} pseudopotentials already present")
            continue
        
        print(f"  Existing: {len(db) - len(to_download)}, To download: {len(to_download)}")
        
        # Download missing ones in parallel
        def download_one(item):
            elem, filename = item
            url = PP_URLS[functional] + filename
            filepath = pp_dir / filename
            urllib.request.urlretrieve(url, filepath)
            return elem, filepath
        
        with ThreadPoolExecutor(max_workers=max_workers) as executor:
            futures = {executor.submit(download_one, item): item for item in to_download}
            for future in as_completed(futures):
                elem, filename = futures[future]
                try:
                    elem, filepath = future.result()
                    results[functional][elem] = filepath
                    total_downloaded += 1
                    if verbose:
                        print(f"    ✓ {elem}: {filename}")
                except Exception as e:
                    failed.append((functional, elem, str(e)))
                    print(f"    ✗ {elem}: {e}")
    
    # Summary
    print("\n" + "=" * 70)
    print("DOWNLOAD SUMMARY")
    print("=" * 70)
    print(f"  Already present:  {total_existing}")
    print(f"  Downloaded:       {total_downloaded}")
    if failed:
        print(f"  Failed:           {len(failed)}")
        for func, elem, err in failed:
            print(f"    - {func}/{elem}: {err}")
    print("=" * 70)
    
    return results


def list_available_elements(functional: str = 'PBE') -> List[str]:
    """List all elements available for a functional."""
    return sorted(PSEUDO_DB.get(functional, {}).keys())


def get_pp_info(element: str, functional: str = 'PBE') -> dict:
    """Get pseudopotential info for an element."""
    if element not in PSEUDO_DB.get(functional, {}):
        return None
    ecutwfc, dual, filename = PSEUDO_DB[functional][element]
    filepath = PSEUDO_DIR / functional / filename
    return {
        'element': element,
        'functional': functional,
        'filename': filename,
        'ecutwfc': ecutwfc,
        'ecutrho': ecutwfc * dual,
        'dual': dual,
        'filepath': filepath,
        'exists': filepath.exists()
    }


# =============================================================================
# QE EXECUTION
# =============================================================================

def run_qe(input_file: Path, executable: str = None,
           nprocs: int = None, use_mpi: bool = True,
           timeout: int = 600) -> Tuple[str, float, bool]:
    """
    Run a Quantum ESPRESSO calculation.
    
    Parameters
    ----------
    input_file : Path
        Path to QE input file (.in)
    executable : str
        QE executable (default: auto-detected pw.x)
    nprocs : int
        Number of MPI processes (default: NPROCS from env or 4)
    use_mpi : bool
        Whether to use MPI (default: True)
    timeout : int
        Timeout in seconds (default: 600)
    
    Returns
    -------
    tuple : (output_text, elapsed_seconds, converged)
    """
    import time
    
    # Use auto-detected executable if not specified
    if executable is None:
        executable = PW_EXECUTABLE
    elif executable == 'pw.x':
        executable = PW_EXECUTABLE
    elif executable == 'pp.x':
        executable = PP_EXECUTABLE
    elif executable == 'bands.x':
        executable = BANDS_EXECUTABLE
    elif executable == 'dos.x':
        executable = DOS_EXECUTABLE
    elif executable == 'projwfc.x':
        executable = PROJWFC_EXECUTABLE
    elif executable == 'ph.x':
        executable = PH_EXECUTABLE
    
    nprocs = nprocs or NPROCS
    input_file = Path(input_file)
    output_file = input_file.with_suffix('.out')
    work_dir = input_file.parent
    
    if use_mpi and nprocs > 1:
        cmd = [MPI_COMMAND, '-np', str(nprocs), executable, '-in', input_file.name]
    else:
        cmd = [executable, '-in', input_file.name]
    
    print(f"Running: {' '.join(cmd)}")
    
    start = time.time()
    result = subprocess.run(cmd, capture_output=True, text=True,
                           cwd=work_dir, timeout=timeout)
    elapsed = time.time() - start
    
    output = result.stdout
    if result.stderr:
        output += "\n=== STDERR ===\n" + result.stderr
    
    with open(output_file, 'w') as f:
        f.write(output)
    
    converged = 'convergence has been achieved' in output.lower()
    
    if converged:
        print(f"  ✓ Converged in {elapsed:.1f}s")
    elif result.returncode != 0:
        print(f"  ✗ FAILED (exit code {result.returncode})")
    else:
        print(f"  ⚠ Completed in {elapsed:.1f}s (check convergence)")
    
    return output, elapsed, converged


def parse_qe_output(output: str) -> dict:
    """
    Parse QE output to extract key results.
    
    Returns dict with: total_energy, fermi_energy, n_iterations, forces, stress, etc.
    """
    import re
    
    results = {
        'converged': 'convergence has been achieved' in output.lower(),
        'total_energy_ry': None,
        'total_energy_ev': None,
        'fermi_energy_ev': None,
        'n_scf_iterations': None,
        'total_force_ry_bohr': None,
        'pressure_kbar': None,
        'cpu_time': None,
        'wall_time': None,
    }
    
    # Total energy
    match = re.search(r'!\s+total energy\s+=\s+([-\d.]+)\s+Ry', output)
    if match:
        results['total_energy_ry'] = float(match.group(1))
        results['total_energy_ev'] = results['total_energy_ry'] * RY_TO_EV
    
    # Fermi energy
    match = re.search(r'the Fermi energy is\s+([-\d.]+)\s+ev', output, re.IGNORECASE)
    if match:
        results['fermi_energy_ev'] = float(match.group(1))
    
    # Number of iterations
    match = re.search(r'convergence has been achieved in\s+(\d+)\s+iterations', output)
    if match:
        results['n_scf_iterations'] = int(match.group(1))
    
    # Total force
    match = re.search(r'Total force\s+=\s+([\d.]+)', output)
    if match:
        results['total_force_ry_bohr'] = float(match.group(1))
    
    # Pressure
    match = re.search(r'P=\s*([-\d.]+)', output)
    if match:
        results['pressure_kbar'] = float(match.group(1))
    
    # Timing
    match = re.search(r'PWSCF\s+:\s+(.+?)\s+CPU\s+(.+?)\s+WALL', output)
    if match:
        results['cpu_time'] = match.group(1).strip()
        results['wall_time'] = match.group(2).strip()
    
    return results


def extract_energy(output: str) -> float:
    """Extract total energy in eV from QE output."""
    import re
    match = re.search(r'!\s+total energy\s+=\s+([-\d.]+)\s+Ry', output)
    if match:
        return float(match.group(1)) * RY_TO_EV
    return None


# =============================================================================
# CONVENIENCE FUNCTIONS FOR NOTEBOOKS
# =============================================================================

def quick_scf_test(element: str = 'Si', functional: str = 'PBE', 
                   nprocs: int = 2) -> bool:
    """
    Run a quick SCF test to verify QE installation.
    
    Returns True if successful.
    """
    from ase.build import bulk
    from ase.io import write
    
    print(f"Running quick SCF test for {element} ({functional})...")
    
    # Setup
    test_dir = OUTPUT_DIR / 'quick_test'
    test_dir.mkdir(exist_ok=True)
    
    # Get pseudopotential
    pp_files = setup_pseudopotentials([element], functional, verbose=False)
    ecutwfc, ecutrho = get_recommended_cutoffs([element], functional)
    
    # Create simple structure
    if element == 'Si':
        atoms = bulk('Si', 'diamond', a=5.43)
    elif element == 'Al':
        atoms = bulk('Al', 'fcc', a=4.05)
    elif element == 'Fe':
        atoms = bulk('Fe', 'bcc', a=2.87)
    else:
        atoms = bulk(element)
    
    # Write QE input
    pp_filename = get_pseudopotential_filename(element, functional)
    input_content = f"""&CONTROL
    calculation = 'scf'
    prefix = 'test'
    outdir = './tmp'
    pseudo_dir = '{get_pseudo_dir(functional)}'
    tprnfor = .true.
/
&SYSTEM
    ibrav = 0
    nat = {len(atoms)}
    ntyp = 1
    ecutwfc = {min(ecutwfc, 40)}
    ecutrho = {min(ecutrho, 320)}
/
&ELECTRONS
    conv_thr = 1.0e-6
/
ATOMIC_SPECIES
    {element}  {atoms.get_masses()[0]:.4f}  {pp_filename}

CELL_PARAMETERS angstrom
"""
    for vec in atoms.cell:
        input_content += f"  {vec[0]:.10f}  {vec[1]:.10f}  {vec[2]:.10f}\n"
    
    input_content += "\nATOMIC_POSITIONS angstrom\n"
    for atom in atoms:
        input_content += f"  {atom.symbol}  {atom.position[0]:.10f}  {atom.position[1]:.10f}  {atom.position[2]:.10f}\n"
    
    input_content += "\nK_POINTS automatic\n  4 4 4 1 1 1\n"
    
    input_file = test_dir / 'test.in'
    input_file.write_text(input_content)
    
    # Run
    output, elapsed, converged = run_qe(input_file, nprocs=nprocs, timeout=120)
    
    if converged:
        results = parse_qe_output(output)
        print(f"  Total energy: {results['total_energy_ev']:.6f} eV")
        print(f"  SCF iterations: {results['n_scf_iterations']}")
    
    return converged

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
import json as _json

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
        'Ni': (60, 8, 'Ni.pbe-spn-kjpaw_psl.1.0.0.UPF'),
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
        'Ru': (50, 8, 'Ru.pbe-spn-kjpaw_psl.1.0.0.UPF'),
        'Rh': (50, 8, 'Rh.pbe-spn-kjpaw_psl.1.0.0.UPF'),
        'Pd': (45, 8, 'Pd.pbe-spn-kjpaw_psl.1.0.0.UPF'),
        'Ag': (45, 8, 'Ag.pbe-n-kjpaw_psl.1.0.0.UPF'),
        'Cd': (50, 8, 'Cd.pbe-n-kjpaw_psl.1.0.0.UPF'),
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
        'Pt': (50, 8, 'Pt.pbe-spfn-kjpaw_psl.1.0.0.UPF'),
        'Au': (50, 8, 'Au.pbe-spfn-kjpaw_psl.1.0.0.UPF'),
        'Hg': (50, 8, 'Hg.pbe-n-kjpaw_psl.1.0.0.UPF'),
        'Tl': (50, 8, 'Tl.pbe-dn-kjpaw_psl.1.0.0.UPF'),
        'Pb': (40, 8, 'Pb.pbe-dn-kjpaw_psl.1.0.0.UPF'),
        'Bi': (50, 8, 'Bi.pbe-dn-kjpaw_psl.1.0.0.UPF'),
    },
    'LDA': {
        # Verified against https://pseudopotentials.quantum-espresso.org/upf_files/
        # PSlibrary LDA files (confirmed available)
        'H':  (60, 8, 'H.pz-rrkjus_psl.1.0.0.UPF'),
        'K':  (50, 8, 'K.pz-spn-kjpaw_psl.1.0.0.UPF'),
        'Ca': (35, 8, 'Ca.pz-spn-kjpaw_psl.1.0.0.UPF'),
        'Ti': (60, 8, 'Ti.pz-spn-kjpaw_psl.1.0.0.UPF'),
        'V':  (55, 8, 'V.pz-spnl-kjpaw_psl.1.0.0.UPF'),
        'Cr': (60, 12, 'Cr.pz-spn-kjpaw_psl.1.0.0.UPF'),
        'Co': (55, 8, 'Co.pz-spn-kjpaw_psl.0.3.1.UPF'),
        'Sr': (40, 8, 'Sr.pz-spn-kjpaw_psl.1.0.0.UPF'),
        'Zr': (40, 8, 'Zr.pz-spn-kjpaw_psl.1.0.0.UPF'),
        'Ba': (35, 8, 'Ba.pz-spn-kjpaw_psl.1.0.0.UPF'),
        # Old-style LDA PPs (verified available, conservative cutoffs)
        'C':  (40, 4, 'C.pz-vbc.UPF'),
        'N':  (40, 4, 'N.pz-vbc.UPF'),
        'O':  (50, 8, 'O.pz-mt.UPF'),
        'Al': (25, 4, 'Al.pz-vbc.UPF'),
        'Si': (30, 4, 'Si.pz-vbc.UPF'),
        'Fe': (50, 8, 'Fe.pz-nd-rrkjus.UPF'),
        'Ni': (50, 8, 'Ni.pz-nd-rrkjus.UPF'),
        'Cu': (40, 8, 'Cu.pz-d-rrkjus.UPF'),
        'Ge': (40, 4, 'Ge.pz-bhs.UPF'),
        'Au': (40, 8, 'Au.pz-d-rrkjus.UPF'),
    },
    'PBEsol': {
        # Period 1-2
        'H':  (60, 8, 'H.pbesol-kjpaw_psl.0.1.UPF'),
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
        'Ca': (35, 8, 'Ca.pbesol-spn-kjpaw_psl.1.0.0.UPF'),
        'Ti': (60, 8, 'Ti.pbesol-spn-kjpaw_psl.1.0.0.UPF'),
        'V':  (55, 8, 'V.pbesol-spnl-kjpaw_psl.1.0.0.UPF'),
        'Cr': (60, 12, 'Cr.pbesol-spn-kjpaw_psl.1.0.0.UPF'),
        'Mn': (65, 12, 'Mn.pbesol-spn-kjpaw_psl.0.3.1.UPF'),
        'Fe': (90, 12, 'Fe.pbesol-spn-kjpaw_psl.1.0.0.UPF'),
        'Co': (55, 8, 'Co.pbesol-spn-kjpaw_psl.0.3.1.UPF'),
        'Ni': (60, 8, 'Ni.pbesol-spn-kjpaw_psl.1.0.0.UPF'),
        'Cu': (55, 8, 'Cu.pbesol-dn-kjpaw_psl.1.0.0.UPF'),
        'Zn': (50, 8, 'Zn.pbesol-dnl-kjpaw_psl.1.0.0.UPF'),
        'Ga': (70, 8, 'Ga.pbesol-dn-kjpaw_psl.1.0.0.UPF'),
        'Ge': (45, 8, 'Ge.pbesol-dn-kjpaw_psl.1.0.0.UPF'),
        # Period 5
        'Sr': (40, 8, 'Sr.pbesol-spn-kjpaw_psl.1.0.0.UPF'),
        'Zr': (40, 8, 'Zr.pbesol-spn-kjpaw_psl.1.0.0.UPF'),
        'Ag': (45, 8, 'Ag.pbesol-n-kjpaw_psl.1.0.0.UPF'),
        'Sn': (60, 8, 'Sn.pbesol-dn-kjpaw_psl.1.0.0.UPF'),
        # Period 6
        'Pt': (50, 8, 'Pt.pbesol-spfn-kjpaw_psl.1.0.0.UPF'),
        'Au': (50, 8, 'Au.pbesol-spfn-kjpaw_psl.1.0.0.UPF'),
        'Pb': (40, 8, 'Pb.pbesol-dn-kjpaw_psl.1.0.0.UPF'),
    },
}

# Backward compatibility
SSSP_EFFICIENCY = PSEUDO_DB['PBE']

# Canonical download URL — ALL PPs served from same directory
PP_BASE_URL = 'https://pseudopotentials.quantum-espresso.org/upf_files/'

# Legacy alias (backward compat)
PP_URLS = {
    'PBE': PP_BASE_URL,
    'LDA': PP_BASE_URL,
    'PBEsol': PP_BASE_URL,
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
# UPF HEADER PARSING — Extract metadata from downloaded PP files
# =============================================================================

# Map QE internal functional codes → standard names
_QE_FUNCTIONAL_MAP = {
    'SLA PW PBX PBC': 'PBE',
    'SLA PW PBE PBE': 'PBE',
    'SLA PZ NOGX NOGC': 'LDA',
    'SLA PZ': 'LDA',
    'PZ': 'LDA',
    'SLA PW PSX PSC': 'PBEsol',
    'SLA PW RPB PBC': 'revPBE',
    'SLA PW B88 P86': 'BP86',
    'SLA PW B88 LYP': 'BLYP',
    'SLA PW PW91 PW91': 'PW91',
    'SLA PW WC WC': 'WC',
    'SLA+HF PW PBX PBC': 'PBE0',
    'SLA+HF PW SE': 'HSE',
    'SLA PW R861 K010': 'SCAN',
}

# Map filename functional codes → standard names
_FILENAME_FUNCTIONAL_MAP = {
    'pbe': 'PBE', 'pz': 'LDA', 'pbesol': 'PBEsol',
    'pw91': 'PW91', 'blyp': 'BLYP', 'revpbe': 'revPBE',
    'wc': 'WC', 'bp': 'BP86',
    'rel-pbe': 'rel-PBE', 'rel-pz': 'rel-LDA', 'rel-pbesol': 'rel-PBEsol',
}

# Folder name → filename functional code mapping
_FOLDER_TO_FILECODE = {
    'PBE': 'pbe', 'LDA': 'pz', 'PBEsol': 'pbesol',
    'PW91': 'pw91', 'BLYP': 'blyp', 'revPBE': 'revpbe',
    'WC': 'wc', 'BP86': 'bp',
}


def parse_upf_header(filepath) -> dict:
    """
    Parse a UPF file header to extract element, functional, PP type, and cutoffs.

    Works with UPF v1 and v2 formats. Returns a dict with keys:
        element, functional, pp_type, ecutwfc, ecutrho, relativistic, filename
    """
    filepath = Path(filepath)
    info = {
        'element': None, 'functional': None, 'pp_type': None,
        'ecutwfc': None, 'ecutrho': None, 'relativistic': False,
        'filename': filepath.name,
    }
    # Read only the first 100 lines (header is always near the top)
    lines = []
    with open(filepath, 'r', errors='ignore') as f:
        for i, line in enumerate(f):
            if i > 120:
                break
            lines.append(line)
    header_text = ''.join(lines)

    # --- Element ---
    m = re.search(r'[Ee]lement\s*[:=]\s*"?\s*([A-Z][a-z]?)\b', header_text)
    if m:
        info['element'] = m.group(1).strip()

    # --- Functional ---
    m = re.search(r'[Ff]unctional\s*[:=]\s*"?\s*(.+)', header_text)
    if m:
        raw = m.group(1).strip().strip('"').strip()
        # Normalize whitespace
        raw_norm = ' '.join(raw.split())
        info['functional'] = _QE_FUNCTIONAL_MAP.get(raw_norm, raw_norm)

    # --- PP type ---
    m = re.search(r'[Pp]seudopotential\s+type\s*:\s*(\w+)', header_text)
    if not m:
        m = re.search(r'pseudo_type\s*=\s*"(\w+)"', header_text)
    if m:
        pt = m.group(1).upper()
        if 'PAW' in pt:
            info['pp_type'] = 'PAW'
        elif pt in ('US', 'USPP'):
            info['pp_type'] = 'US'
        elif pt in ('NC', 'NCPP', 'NORM', 'SL'):
            info['pp_type'] = 'NC'
        else:
            info['pp_type'] = pt

    # --- Cutoffs ---
    m = re.search(r'[Ss]uggested\s+minimum\s+cutoff\s+for\s+wavefunctions\s*:\s*([\d.]+)', header_text)
    if m:
        info['ecutwfc'] = float(m.group(1))
    m = re.search(r'[Ss]uggested\s+minimum\s+cutoff\s+for\s+charge\s+density\s*:\s*([\d.]+)', header_text)
    if m:
        info['ecutrho'] = float(m.group(1))

    # --- Relativistic ---
    if 'scalar-relativistic' in header_text.lower() or 'scalar_relativistic' in header_text.lower():
        info['relativistic'] = True

    # Fallback: extract element from filename if not in header
    if not info['element']:
        m = re.match(r'([A-Z][a-z]?)\.', filepath.name)
        if m:
            info['element'] = m.group(1)

    # Fallback: extract functional from filename
    if not info['functional']:
        for code, func in _FILENAME_FUNCTIONAL_MAP.items():
            if f'.{code}-' in filepath.name.lower() or f'.{code}.' in filepath.name.lower():
                info['functional'] = func
                break

    return info


def _parse_pp_filename(filename: str) -> dict:
    """
    Extract metadata from a PP filename (fast, no I/O).
    Pattern: Element.functional-config-type_library.version.UPF
    """
    info = {'element': None, 'functional': None, 'pp_type': None, 'library': None}
    m = re.match(r'([A-Z][a-z]?)\.(.+)\.UPF$', filename, re.IGNORECASE)
    if not m:
        return info
    info['element'] = m.group(1)
    rest = m.group(2)

    # Functional
    for code, func in sorted(_FILENAME_FUNCTIONAL_MAP.items(), key=lambda x: -len(x[0])):
        if rest.startswith(code + '-') or rest.startswith(code + '.'):
            info['functional'] = func
            break

    # PP type from known keywords
    rest_lower = rest.lower()
    if 'kjpaw' in rest_lower:
        info['pp_type'] = 'PAW'
    elif 'rrkjus' in rest_lower:
        info['pp_type'] = 'US'
    elif 'van' in rest_lower:
        info['pp_type'] = 'US'
    elif 'hgh' in rest_lower or 'bhs' in rest_lower or 'vbc' in rest_lower or 'mt' in rest_lower:
        info['pp_type'] = 'NC'

    # Library
    if '_psl.' in rest_lower:
        info['library'] = 'pslibrary'

    return info


# =============================================================================
# LOCAL PP MANIFEST — Auto-index of all downloaded pseudopotentials
# =============================================================================

_MANIFEST_PATH = PSEUDO_DIR / 'manifest.json'


def _load_manifest() -> dict:
    """Load the local PP manifest, or return empty structure."""
    if _MANIFEST_PATH.exists():
        with open(_MANIFEST_PATH) as f:
            return _json.load(f)
    return {}


def _save_manifest(manifest: dict):
    """Save manifest to disk."""
    with open(_MANIFEST_PATH, 'w') as f:
        _json.dump(manifest, f, indent=2, default=str)


def build_pp_manifest(verbose: bool = False) -> dict:
    """
    Scan all local pseudopotential directories and build an index
    from actual UPF file headers. This is the source of truth for
    what PPs are locally available and their properties.

    Returns: {functional: {element: {filename, ecutwfc, ecutrho, pp_type, filepath}}}
    """
    manifest = {}

    for subdir in sorted(PSEUDO_DIR.iterdir()):
        if not subdir.is_dir():
            continue
        func_name = subdir.name  # e.g., 'PBE', 'LDA', 'PBEsol'
        if func_name.startswith('.'):
            continue

        entries = {}
        upf_files = sorted(subdir.glob('*.UPF')) + sorted(subdir.glob('*.upf'))

        for upf_path in upf_files:
            info = parse_upf_header(upf_path)
            elem = info.get('element')
            if not elem:
                continue

            entry = {
                'filename': upf_path.name,
                'pp_type': info.get('pp_type'),
                'ecutwfc': info.get('ecutwfc'),
                'ecutrho': info.get('ecutrho'),
                'filepath': str(upf_path),
                'header_functional': info.get('functional'),
            }

            # If multiple PPs for same element, prefer PAW > US > NC
            if elem in entries:
                old_type = entries[elem].get('pp_type', '')
                new_type = entry.get('pp_type', '')
                type_rank = {'PAW': 3, 'US': 2, 'NC': 1}
                if type_rank.get(new_type, 0) <= type_rank.get(old_type, 0):
                    continue  # keep the existing (better) one

            entries[elem] = entry

        if entries:
            manifest[func_name] = entries
            if verbose:
                print(f"  {func_name}: {len(entries)} elements indexed")

    _save_manifest(manifest)
    if verbose:
        print(f"  Manifest saved: {_MANIFEST_PATH}")
    return manifest


# =============================================================================
# AUTO-DISCOVERY — Try filename variations when PSEUDO_DB entry fails
# =============================================================================

# Common valence configurations used in PSlibrary naming
_VALENCE_CONFIGS = ['n', 'dn', 'spn', 'spdn', 'spnl', 'dnl', 'nl', 'sl', 'spfn']
_PP_TYPES = ['kjpaw_psl', 'rrkjus_psl']
_VERSIONS = ['1.0.0', '0.3.1', '0.1']


def _generate_candidate_filenames(element: str, functional: str) -> List[str]:
    """
    Generate candidate PP filenames for an element + functional combo.
    Tries systematic naming variations used by PSlibrary.
    """
    func_code = _FOLDER_TO_FILECODE.get(functional, functional.lower())
    candidates = []

    # PSlibrary naming: Element.func-config-type_psl.version.UPF
    for pp_type in _PP_TYPES:
        for ver in _VERSIONS:
            for cfg in _VALENCE_CONFIGS:
                candidates.append(f"{element}.{func_code}-{cfg}-{pp_type}.{ver}.UPF")
            # Also try without config (e.g., H.pbe-rrkjus_psl.1.0.0.UPF)
            candidates.append(f"{element}.{func_code}-{pp_type}.{ver}.UPF")

    # Old-style naming for LDA
    if functional == 'LDA':
        old_suffixes = ['vbc', 'hgh', 'bhs', 'mt', 'van_ak',
                        'nd-rrkjus', 'd-rrkjus', 'n-rrkjus', 'sp-van_ak']
        for suffix in old_suffixes:
            candidates.append(f"{element}.pz-{suffix}.UPF")

    return candidates


def _url_exists(url: str, timeout: int = 10) -> bool:
    """Check if a URL exists using a HEAD request. Returns True/False."""
    req = urllib.request.Request(url, method='HEAD')
    resp = urllib.request.urlopen(req, timeout=timeout)
    return resp.status == 200


def _download_url(url: str, dest: Path, timeout: int = 30) -> bool:
    """Download a file from URL to dest. Caller must verify URL exists first."""
    req = urllib.request.Request(url)
    resp = urllib.request.urlopen(req, timeout=timeout)
    with open(dest, 'wb') as f:
        f.write(resp.read())
    return True


# =============================================================================
# ROBUST DOWNLOAD — Multi-attempt with auto-discovery fallback
# =============================================================================

def download_pseudopotential(element: str, functional: str = 'PBE',
                             force: bool = False) -> Path:
    """
    Download pseudopotential for an element with robust fallback.

    Strategy:
    1. Check if file already exists locally
    2. Try the filename from PSEUDO_DB
    3. Scan local directory for any matching UPF file
    4. Try systematic filename variations against QE PP site
    5. Update local manifest after download

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
    pp_dir = PSEUDO_DIR / functional
    pp_dir.mkdir(parents=True, exist_ok=True)

    # --- Step 1: Check if already present (via PSEUDO_DB or manifest) ---
    if not force:
        # Check PSEUDO_DB filename
        if element in PSEUDO_DB.get(functional, {}):
            _, _, filename = PSEUDO_DB[functional][element]
            filepath = pp_dir / filename
            if filepath.exists():
                return filepath

        # Check manifest
        manifest = _load_manifest()
        if functional in manifest and element in manifest[functional]:
            fp = Path(manifest[functional][element]['filepath'])
            if fp.exists():
                return fp

        # Scan local directory for any matching UPF
        for f in pp_dir.iterdir():
            if f.suffix.upper() == '.UPF':
                finfo = _parse_pp_filename(f.name)
                if finfo.get('element') == element:
                    return f

    # --- Step 2: Try PSEUDO_DB filename from QE PP site ---
    if element in PSEUDO_DB.get(functional, {}):
        _, _, filename = PSEUDO_DB[functional][element]
        filepath = pp_dir / filename
        url = PP_BASE_URL + filename
        print(f"  Downloading {element} ({functional}): {filename}...", end=" ", flush=True)

        if _url_exists(url):
            _download_url(url, filepath)
            print("✓")
            info = parse_upf_header(filepath)
            if info.get('element') and info['element'] != element:
                print(f"  ⚠ Warning: PP header says element={info['element']}, expected {element}")
            return filepath
        else:
            print("✗ (trying alternatives)")

    # --- Step 3: Auto-discovery — try filename variations ---
    print(f"  Searching for {element} ({functional}) PP on QE repository...")
    candidates = _generate_candidate_filenames(element, functional)
    for candidate in candidates:
        url = PP_BASE_URL + candidate
        filepath = pp_dir / candidate

        if not _url_exists(url):
            continue

        _download_url(url, filepath)
        info = parse_upf_header(filepath)
        if info.get('element') and info['element'] != element:
            filepath.unlink()
            continue
        print(f"  ✓ Found: {candidate}")
        return filepath

    # --- Step 4: All attempts failed ---
    avail_funcs = [f for f in PSEUDO_DB if element in PSEUDO_DB[f]]
    msg = f"Could not find pseudopotential for {element} ({functional})."
    if avail_funcs:
        msg += f" Available in: {', '.join(avail_funcs)}"
    print(f"  ✗ {msg}")
    return None


def get_nc_pseudopotential(element: str, functional: str = 'PBE') -> Path:
    """
    Download a norm-conserving (NC) pseudopotential for an element.

    NC PPs are required for meta-GGA calculations (TPSS, revTPSS) in QE
    when compiled without libxc. This function searches the QE PP repository
    for HGH, MT/FHI, or other NC-type pseudopotentials.

    Parameters
    ----------
    element : str
        Element symbol (e.g., 'Si', 'Fe')
    functional : str
        Base functional for the PP ('PBE' or 'LDA'). Meta-GGA calculations
        typically use PBE-generated NC PPs with input_dft override.

    Returns
    -------
    Path to downloaded NC PP file, or None if not found.
    """
    pp_dir = PSEUDO_DIR / f'{functional}_NC'
    pp_dir.mkdir(parents=True, exist_ok=True)

    # Check if already present locally
    for f in pp_dir.iterdir():
        if f.suffix.upper() == '.UPF':
            finfo = _parse_pp_filename(f.name)
            if finfo.get('element') == element:
                return f

    func_code = _FOLDER_TO_FILECODE.get(functional, functional.lower())

    # NC PP naming patterns on QE PP site (ordered by preference)
    nc_patterns = [
        f'{element}.{func_code}-hgh.UPF',             # HGH (Goedecker) — widely available
        f'{element}.{func_code}-mt_fhi.UPF',           # FHI/MT
        f'{element}.{func_code}-mt_gipaw.UPF',         # GIPAW MT
        f'{element}.{func_code}-tm-gipaw.UPF',         # GIPAW TM
        f'{element}.{func_code}-tm.UPF',               # Troullier-Martins
        f'{element}.{func_code}-bhs.UPF',              # BHS
        f'{element}.{func_code}-vbc.UPF',              # Von Barth-Car
        f'{element}.{func_code}-n-nc.UPF',             # PSlibrary NC
    ]

    print(f"  Searching for NC pseudopotential: {element} ({functional})...")
    for candidate in nc_patterns:
        url = PP_BASE_URL + candidate
        if not _url_exists(url):
            continue

        filepath = pp_dir / candidate
        _download_url(url, filepath)

        # Verify it's actually NC
        info = parse_upf_header(filepath)
        if info.get('element') and info['element'] != element:
            filepath.unlink()
            continue

        pp_type = info.get('pp_type', '')
        if pp_type in ('NC', 'SL', ''):
            print(f"  ✓ NC PP found: {candidate} (type: {pp_type or 'NC'})")
            return filepath

        # If it's US/PAW, it won't work for meta-GGA — skip it
        if pp_type in ('US', 'PAW'):
            filepath.unlink()
            continue

        # Accept if type is unclear (old-style PPs are often NC)
        print(f"  ✓ NC PP found: {candidate} (type: {pp_type or 'NC'})")
        return filepath

    print(f"  ✗ No NC pseudopotential found for {element} ({functional})")
    return None


def setup_pseudopotentials(elements: List[str], functional: str = 'PBE',
                          verbose: bool = True) -> Dict[str, Path]:
    """
    Download all required pseudopotentials with robust fallback.

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

    pp_dir = PSEUDO_DIR / functional
    pp_dir.mkdir(parents=True, exist_ok=True)

    result = {}
    to_download = []

    for elem in elements:
        # Check PSEUDO_DB first
        if elem in PSEUDO_DB.get(functional, {}):
            _, _, filename = PSEUDO_DB[functional][elem]
            filepath = pp_dir / filename
            if filepath.exists():
                if verbose:
                    print(f"  ✓ {elem}: {filename}")
                result[elem] = filepath
                continue

        # Check local directory for any matching UPF
        found_local = False
        for f in pp_dir.iterdir():
            if f.suffix.upper() == '.UPF':
                finfo = _parse_pp_filename(f.name)
                if finfo.get('element') == elem:
                    if verbose:
                        print(f"  ✓ {elem}: {f.name} (local)")
                    result[elem] = f
                    found_local = True
                    break

        if not found_local:
            to_download.append(elem)

    if to_download:
        if verbose:
            print(f"\n  Downloading {len(to_download)} pseudopotentials...")
        for elem in to_download:
            filepath = download_pseudopotential(elem, functional, force=False)
            if filepath and filepath.exists():
                result[elem] = filepath
            else:
                print(f"  ✗ {elem}: not found for {functional}")

    # Rebuild manifest after any downloads
    if to_download:
        build_pp_manifest(verbose=False)

    if verbose:
        print("=" * 60)
        print(f"Pseudopotentials ready in: {pp_dir}")
        print("=" * 60)

    return result


def get_recommended_cutoffs(elements: List[str], functional: str = 'PBE') -> Tuple[float, float]:
    """
    Get recommended ecutwfc and ecutrho for a set of elements.

    Priority: UPF header values (from manifest) → PSEUDO_DB static values → defaults.
    Returns the maximum cutoffs needed across all elements.
    """
    max_ecutwfc = 0
    max_ecutrho = 0

    manifest = _load_manifest()
    db = PSEUDO_DB.get(functional, PSEUDO_DB.get('PBE', {}))

    for elem in elements:
        ecutwfc, ecutrho = None, None

        # Try manifest first (parsed from actual UPF headers)
        if functional in manifest and elem in manifest[functional]:
            entry = manifest[functional][elem]
            ecutwfc = entry.get('ecutwfc') or None  # treat 0 as missing
            ecutrho = entry.get('ecutrho') or None

        # Fall back to PSEUDO_DB
        if ecutwfc is None and elem in db:
            wfc, dual, _ = db[elem]
            ecutwfc = wfc
            ecutrho = wfc * dual

        # Fall back to safe defaults
        if ecutwfc is None:
            print(f"⚠ {elem} not in database, using 60 Ry default")
            ecutwfc = 60
            ecutrho = 480

        if ecutrho is None:
            ecutrho = ecutwfc * 8

        max_ecutwfc = max(max_ecutwfc, ecutwfc)
        max_ecutrho = max(max_ecutrho, ecutrho)

    return max_ecutwfc, max_ecutrho


def get_pseudopotential_filename(element: str, functional: str = 'PBE') -> str:
    """Get pseudopotential filename for an element."""
    # Check manifest first
    manifest = _load_manifest()
    if functional in manifest and element in manifest[functional]:
        return manifest[functional][element]['filename']

    # Fall back to PSEUDO_DB
    if element in PSEUDO_DB.get(functional, {}):
        return PSEUDO_DB[functional][element][2]

    # Check local directory
    pp_dir = PSEUDO_DIR / functional
    if pp_dir.exists():
        for f in pp_dir.iterdir():
            if f.suffix.upper() == '.UPF':
                finfo = _parse_pp_filename(f.name)
                if finfo.get('element') == element:
                    return f.name

    raise ValueError(f"No pseudopotential found for {element} ({functional}). "
                     f"Run setup_pseudopotentials(['{element}'], '{functional}') first.")


def get_pseudo_dir(functional: str = 'PBE') -> Path:
    """Get the pseudopotential directory for a functional."""
    pp_dir = PSEUDO_DIR / functional
    pp_dir.mkdir(parents=True, exist_ok=True)
    return pp_dir


def download_all_pseudopotentials(functionals: List[str] = None,
                                   max_workers: int = 4,
                                   verbose: bool = True) -> Dict[str, Dict[str, Path]]:
    """
    Download ALL pseudopotentials in PSEUDO_DB for workshop use.

    Run this ONCE at the start of the workshop to ensure all PPs are available.
    Uses parallel downloads for speed with automatic fallback on failures.

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
    print(f"Source: {PP_BASE_URL}")
    print(f"Target: {PSEUDO_DIR}")
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

        for elem, filename in to_download:
            url = PP_BASE_URL + filename
            filepath = pp_dir / filename

            if _url_exists(url):
                _download_url(url, filepath)
                results[functional][elem] = filepath
                total_downloaded += 1
                if verbose:
                    print(f"    ✓ {elem}: {filename}")
            else:
                # Auto-discovery fallback
                discovered = download_pseudopotential(elem, functional)
                if discovered and discovered.exists():
                    results[functional][elem] = discovered
                    total_downloaded += 1
                    if verbose:
                        print(f"    ✓ {elem}: {discovered.name} (discovered)")
                else:
                    failed.append((functional, elem, f"not found on {PP_BASE_URL}"))
                    print(f"    ✗ {elem}: not available")

    # Build manifest from everything we have
    build_pp_manifest(verbose=False)

    print("\n" + "=" * 70)
    print("DOWNLOAD SUMMARY")
    print("=" * 70)
    print(f"  Already present:  {total_existing}")
    print(f"  Downloaded:       {total_downloaded}")
    if failed:
        print(f"  Failed:           {len(failed)}")
        for func, elem, err in failed:
            print(f"    - {func}/{elem}: {err}")
    else:
        print(f"  Failed:           0")
    print("=" * 70)

    return results


def list_available_elements(functional: str = 'PBE') -> List[str]:
    """List all elements available for a functional (DB + local files)."""
    elements = set(PSEUDO_DB.get(functional, {}).keys())

    # Also check local directory
    pp_dir = PSEUDO_DIR / functional
    if pp_dir.exists():
        for f in pp_dir.iterdir():
            if f.suffix.upper() == '.UPF':
                finfo = _parse_pp_filename(f.name)
                if finfo.get('element'):
                    elements.add(finfo['element'])

    return sorted(elements)


def get_pp_info(element: str, functional: str = 'PBE') -> dict:
    """Get pseudopotential info for an element (manifest + PSEUDO_DB)."""
    info = {
        'element': element,
        'functional': functional,
        'filename': None,
        'ecutwfc': None, 'ecutrho': None, 'dual': None,
        'pp_type': None,
        'filepath': None,
        'exists': False,
        'source': None,
    }

    # Check manifest first (has UPF header data)
    manifest = _load_manifest()
    if functional in manifest and element in manifest[functional]:
        entry = manifest[functional][element]
        info['filename'] = entry.get('filename')
        info['ecutwfc'] = entry.get('ecutwfc')
        info['ecutrho'] = entry.get('ecutrho')
        info['pp_type'] = entry.get('pp_type')
        info['filepath'] = Path(entry['filepath'])
        info['exists'] = info['filepath'].exists()
        info['source'] = 'manifest'
        if info['ecutwfc'] and info['ecutrho']:
            info['dual'] = info['ecutrho'] / info['ecutwfc']
        return info

    # Fall back to PSEUDO_DB
    if element in PSEUDO_DB.get(functional, {}):
        ecutwfc, dual, filename = PSEUDO_DB[functional][element]
        filepath = PSEUDO_DIR / functional / filename
        info['filename'] = filename
        info['ecutwfc'] = ecutwfc
        info['ecutrho'] = ecutwfc * dual
        info['dual'] = dual
        info['filepath'] = filepath
        info['exists'] = filepath.exists()
        info['source'] = 'database'
        return info

    # Check local directory
    pp_dir = PSEUDO_DIR / functional
    if pp_dir.exists():
        for f in pp_dir.iterdir():
            if f.suffix.upper() == '.UPF':
                finfo = _parse_pp_filename(f.name)
                if finfo.get('element') == element:
                    info['filename'] = f.name
                    info['filepath'] = f
                    info['exists'] = True
                    info['pp_type'] = finfo.get('pp_type')
                    info['source'] = 'local'
                    return info

    return info


def scan_available_pseudopotentials(verbose: bool = True) -> dict:
    """
    Scan all local PP directories, parse UPF headers, rebuild manifest.
    Useful after manually adding PP files.

    Returns the manifest dict.
    """
    if verbose:
        print("=" * 60)
        print("SCANNING LOCAL PSEUDOPOTENTIALS")
        print("=" * 60)
    manifest = build_pp_manifest(verbose=verbose)
    if verbose:
        total = sum(len(v) for v in manifest.values())
        print(f"\nTotal: {total} pseudopotentials across {len(manifest)} functionals")
        for func, entries in sorted(manifest.items()):
            elems = sorted(entries.keys())
            print(f"  {func} ({len(elems)}): {', '.join(elems)}")
        print("=" * 60)
    return manifest


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

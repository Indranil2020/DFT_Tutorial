# Research-Grade DFT Workshop with Quantum ESPRESSO

## "Structure Before Properties: A Rigorous Scientific Workflow"

[![License: MIT](https://img.shields.io/badge/License-MIT-blue.svg)](LICENSE)
[![QE Version](https://img.shields.io/badge/Quantum%20ESPRESSO-6.x%20%7C%207.x-green.svg)](https://www.quantum-espresso.org/)
[![Python](https://img.shields.io/badge/Python-3.8%2B-blue.svg)](https://python.org)

---

## Table of Contents

1. [Workshop Philosophy](#workshop-philosophy)
2. [Complete Workflow Overview](#complete-workflow-overview)
3. [Notebook Structure](#notebook-structure)
4. [Prerequisites](#prerequisites)
5. [Installation Instructions](#installation-instructions)
6. [Essential Resources](#essential-resources)
7. [Quick Start](#quick-start)
8. [For Instructors](#for-instructors)
9. [Validation](#validation)
10. [Citation and License](#citation-and-license)
11. [Contact and Contribution](#contact-and-contribution)

---

## Workshop Philosophy

### The "Garbage In, Garbage Out" Principle

> **The most sophisticated DFT calculation is worthless if built on a flawed structure.**

In computational materials science, there is a pervasive temptation to rush toward "interesting" calculations---band structures, optical properties, phonons---without first establishing a rigorous foundation. This workshop takes a fundamentally different approach: **we treat structure validation as the cornerstone of scientific credibility**.

### Why Structure Validation Matters More Than Fancy Calculations

Consider this scenario: A researcher downloads a crystal structure from a database, runs a band structure calculation, and publishes results showing a material is a semiconductor with a 1.2 eV gap. The problem? The downloaded structure had:

- **Incorrect space group** (the database entry was from a high-temperature polymorph)
- **Unrelaxed atomic positions** (residual forces of 0.5 eV/A)
- **Wrong lattice constant** (off by 3% due to different exchange-correlation functional)

The calculated band gap is meaningless---it describes a structure that doesn't exist in the regime being studied.

### What Makes This Workshop Different

| Typical Tutorial | This Workshop |
|------------------|---------------|
| "Download structure, run calculation" | "Validate structure, understand provenance, then calculate" |
| Skip convergence testing | Systematic convergence with quantified uncertainties |
| Single-point calculations | Full equation of state fitting |
| Ignore forces and stresses | Zero-force/zero-stress validation |
| Trust database structures blindly | Cross-reference multiple databases |
| Black-box pseudopotentials | Understand pseudopotential selection criteria |

**Our core principle**: Every number you report should have:
1. A validated input structure
2. Converged computational parameters
3. Quantified numerical uncertainty
4. Comparison to experimental/literature values

---

## Complete Workflow Overview

The workshop follows a six-phase workflow that mirrors best practices in computational materials research:

```
+============================================================================+
|                    RESEARCH-GRADE DFT WORKFLOW                              |
+============================================================================+

  PHASE 1: DATABASE SEARCH
  +------------------------------------------------------------------+
  |  Materials Project  --->  AFLOW  --->  OQMD  --->  JARVIS        |
  |       |                    |            |            |           |
  |       v                    v            v            v           |
  |  [Cross-reference structures, identify discrepancies]            |
  +------------------------------------------------------------------+
                                   |
                                   v
  PHASE 2: STRUCTURE VALIDATION
  +------------------------------------------------------------------+
  |  Check symmetry  --->  Verify stoichiometry  --->  Compare       |
  |       |                      |                    sources        |
  |       v                      v                       |           |
  |  [Spglib analysis]    [Chemical sense]    [Experimental refs]   |
  +------------------------------------------------------------------+
                                   |
                                   v
  PHASE 3: DFT SETUP
  +------------------------------------------------------------------+
  |  Select pseudopotentials  --->  Choose XC functional             |
  |       |                              |                           |
  |       v                              v                           |
  |  [SSSP/PSlibrary]          [PBE/PBEsol/LDA - justify choice]    |
  +------------------------------------------------------------------+
                                   |
                                   v
  PHASE 4: GROUND STATE DETERMINATION
  +------------------------------------------------------------------+
  |   ecutwfc         k-points        Lattice                        |
  |  convergence  --> convergence --> optimization                   |
  |      |               |                |                          |
  |      v               v                v                          |
  |  [<1 meV/atom]  [<1 meV/atom]   [P < 0.5 kbar]                  |
  |                                  [F < 0.001 Ry/Bohr]            |
  +------------------------------------------------------------------+
                                   |
                                   v
  PHASE 5: STABILITY TESTING
  +------------------------------------------------------------------+
  |  Verify forces ~ 0  --->  Verify stress ~ 0  --->  Check         |
  |       |                        |                  convergence    |
  |       v                        v                       |         |
  |  [Optimization    [Equation of state   [Compare to             |
  |   complete?]        Birch-Murnaghan]    experiment]            |
  +------------------------------------------------------------------+
                                   |
                                   v
  PHASE 6: PROPERTY CALCULATIONS
  +------------------------------------------------------------------+
  |  Band Structure  --->  DOS/PDOS  --->  Advanced Properties       |
  |       |                   |                   |                  |
  |       v                   v                   v                  |
  |  [High-symmetry     [Fermi level      [Phonons, optical,       |
  |   k-path]            analysis]         transport, etc.]        |
  +------------------------------------------------------------------+

  VALIDATION AT EVERY STEP:
  +------------------------------------------------------------------+
  |  - Compare to published values (experimental + computational)    |
  |  - Check internal consistency                                    |
  |  - Document all parameters and their justification              |
  |  - Report uncertainties                                          |
  +------------------------------------------------------------------+
```

---

## Notebook Structure

The workshop consists of 11 carefully sequenced notebooks, each building on concepts from previous modules:

| # | Notebook | Phase | Topic | Key Learning Outcomes |
|:-:|----------|:-----:|-------|----------------------|
| 00 | `00_Workshop_Overview.ipynb` | -- | Philosophy & Resources | Why rigor matters; overview of scientific workflow; available resources |
| 01 | `01_Database_Search.ipynb` | 1 | Finding Structures | Query Materials Project, AFLOW, OQMD; cross-reference structures; evaluate data quality |
| 02 | `02_Structure_Validation.ipynb` | 2 | Validating Structures | Symmetry analysis with spglib; detect inconsistencies; prepare clean input structures |
| 03 | `03_DFT_Setup.ipynb` | 3 | Calculation Setup | Pseudopotential selection (SSSP, PSlibrary); XC functional choice; input file anatomy |
| 04 | `04_Ecutwfc_Convergence.ipynb` | 4 | Wavefunction Cutoff | Systematic convergence testing; establish numerical precision; automation strategies |
| 05 | `05_Kpoint_Convergence.ipynb` | 4 | Brillouin Zone Sampling | k-point grid convergence; Monkhorst-Pack vs Gamma-centered; metallic vs insulating systems |
| 06 | `06_Lattice_Optimization.ipynb` | 4-5 | Equilibrium Structure | Equation of state fitting; Birch-Murnaghan EOS; extract bulk modulus; validate against experiment |
| 07 | `07_Full_Relaxation.ipynb` | 5 | Complete Optimization | Variable-cell relaxation; stress tensor analysis; force convergence criteria |
| 08 | `08_Band_Structure.ipynb` | 6 | Electronic Bands | High-symmetry k-paths; band gap determination; effective mass extraction |
| 09 | `09_DOS_Calculation.ipynb` | 6 | Density of States | Total DOS; projected DOS (PDOS); orbital character analysis |
| 10 | `10_Summary_Exercises.ipynb` | -- | Synthesis & Practice | Comprehensive exercises; complete workflow walkthrough; troubleshooting guide |

### Notebook Dependencies

```
00_Overview (start here)
    |
    v
01_Database --> 02_Validation --> 03_DFT_Setup
                                       |
                    +------------------+------------------+
                    |                  |                  |
                    v                  v                  v
            04_Ecutwfc ---------> 05_Kpoints -----> 06_Lattice
                                                        |
                                                        v
                                                  07_Full_Relax
                                                        |
                                       +----------------+----------------+
                                       |                                 |
                                       v                                 v
                                 08_Band_Structure              09_DOS_Calculation
                                       |                                 |
                                       +-----------------+---------------+
                                                         |
                                                         v
                                                   10_Summary
```

---

## Prerequisites

### Required Software

#### Python Environment

| Package | Minimum Version | Purpose |
|---------|----------------|---------|
| `numpy` | 1.20+ | Numerical operations, array handling |
| `scipy` | 1.7+ | Curve fitting (Birch-Murnaghan EOS), interpolation |
| `matplotlib` | 3.4+ | Plotting convergence curves, band structures, DOS |
| `ase` | 3.22+ | Atomic Simulation Environment - structure manipulation |

#### Optional but Recommended

| Package | Purpose |
|---------|---------|
| `pymatgen` | Advanced structure analysis, Materials Project API |
| `mp-api` | Direct Materials Project database access |
| `spglib` | Symmetry analysis (often bundled with ASE) |
| `seekpath` | Automatic high-symmetry k-path generation |

#### Quantum ESPRESSO

- **Version**: 6.x or 7.x (tested with 6.7, 7.0, 7.2)
- **Required executables**: `pw.x`, `bands.x`, `dos.x`, `projwfc.x`
- **Optional**: `pp.x` (post-processing), `plotband.x`

### Hardware Recommendations

| Use Case | CPU Cores | RAM | Storage |
|----------|-----------|-----|---------|
| Tutorial exercises | 2-4 | 4 GB | 2 GB |
| Small systems (< 20 atoms) | 4-8 | 8 GB | 10 GB |
| Production calculations | 16+ | 32+ GB | 100+ GB |

---

## Installation Instructions

### Option 1: Google Colab (Easiest)

Google Colab provides a pre-configured environment. Use this for workshops or quick exploration.

```python
# Run this cell at the start of each notebook

# Install Quantum ESPRESSO
!apt-get update -qq
!apt-get install -qq quantum-espresso

# Install Python packages
!pip install -q numpy scipy matplotlib ase

# Optional: Materials Project access
!pip install -q mp-api pymatgen

# Verify installation
!pw.x --version
import numpy as np
print(f"NumPy version: {np.__version__}")
```

### Option 2: Local Jupyter Installation

#### Ubuntu/Debian

```bash
# System dependencies
sudo apt update
sudo apt install quantum-espresso python3-pip python3-venv

# Create virtual environment (recommended)
python3 -m venv ~/qe-workshop
source ~/qe-workshop/bin/activate

# Install Python packages
pip install numpy scipy matplotlib ase jupyter

# Optional packages
pip install pymatgen mp-api spglib seekpath

# Download workshop materials
git clone https://github.com/Indranil2020/DFT_Tutorial.git
cd qe-workshop

# Start Jupyter
jupyter notebook
```

#### macOS (with Homebrew)

```bash
# Install Quantum ESPRESSO via Homebrew
brew install quantum-espresso

# Create virtual environment
python3 -m venv ~/qe-workshop
source ~/qe-workshop/bin/activate

# Install Python packages
pip install numpy scipy matplotlib ase jupyter pymatgen

# Start Jupyter
jupyter notebook
```

#### Windows (via WSL2)

```bash
# In WSL2 Ubuntu terminal:
sudo apt update
sudo apt install quantum-espresso python3-pip python3-venv

# Follow Ubuntu instructions above
```

### Option 3: HPC JupyterHub

Many HPC centers provide JupyterHub access. Typical setup:

```bash
# Load modules (example - adjust for your system)
module load quantum-espresso/7.2
module load python/3.10
module load jupyter

# Create conda environment
conda create -n qe-workshop python=3.10 numpy scipy matplotlib ase jupyter
conda activate qe-workshop

# Install additional packages
pip install pymatgen mp-api

# Launch Jupyter (may require port forwarding)
jupyter lab --no-browser --port=8888
```

### Verify Your Installation

Run this verification script:

```python
#!/usr/bin/env python3
"""Verify workshop installation."""

import subprocess
import sys

def check_python_packages():
    """Check required Python packages."""
    required = ['numpy', 'scipy', 'matplotlib', 'ase']
    optional = ['pymatgen', 'mp_api', 'spglib']

    print("Python packages:")
    for pkg in required:
        try:
            __import__(pkg)
            print(f"  [OK] {pkg}")
        except ImportError:
            print(f"  [MISSING] {pkg} - REQUIRED")
            return False

    for pkg in optional:
        try:
            __import__(pkg)
            print(f"  [OK] {pkg}")
        except ImportError:
            print(f"  [--] {pkg} (optional)")

    return True

def check_qe():
    """Check Quantum ESPRESSO installation."""
    print("\nQuantum ESPRESSO:")
    try:
        result = subprocess.run(['pw.x', '--version'],
                                capture_output=True, text=True, timeout=10)
        if result.returncode == 0 or 'PWSCF' in result.stdout + result.stderr:
            print("  [OK] pw.x found")
            return True
    except FileNotFoundError:
        print("  [MISSING] pw.x not found in PATH")
    except Exception as e:
        print(f"  [ERROR] {e}")
    return False

if __name__ == '__main__':
    py_ok = check_python_packages()
    qe_ok = check_qe()

    print("\n" + "="*40)
    if py_ok and qe_ok:
        print("Installation verified successfully!")
    else:
        print("Some components are missing. See above.")
        sys.exit(1)
```

---

## Essential Resources

### Structure Databases

| Database | URL | Best For | Access Method |
|----------|-----|----------|---------------|
| **Materials Project** | [materialsproject.org](https://materialsproject.org) | Comprehensive computed properties, API access | `mp-api` Python package |
| **OQMD** | [oqmd.org](http://oqmd.org) | Formation energies, phase diagrams | REST API, bulk download |
| **AFLOW** | [aflowlib.org](http://aflowlib.org) | Systematic high-throughput data | REST API |
| **JARVIS-DFT** | [jarvis.nist.gov](https://jarvis.nist.gov/jarvisdft) | 2D materials, NIST-curated | REST API |
| **COD** | [crystallography.net](http://crystallography.net) | Experimental crystal structures | CIF download |
| **ICSD** | [icsd.fiz-karlsruhe.de](https://icsd.fiz-karlsruhe.de) | Comprehensive experimental (subscription) | Institutional access |
| **NOMAD** | [nomad-lab.eu](https://nomad-lab.eu) | Raw calculation data, reproducibility | REST API |

### Pseudopotential Libraries

| Library | URL | Recommended For |
|---------|-----|-----------------|
| **SSSP** (Standard Solid-State Pseudopotentials) | [materialscloud.org/sssp](https://www.materialscloud.org/discover/sssp) | General-purpose, validated accuracy/efficiency |
| **PSlibrary** | [dalcorso.github.io/pslibrary](http://www.dalcorso.github.io/pslibrary/) | Systematic PAW/US sets |
| **SG15 ONCV** | [quantum-simulation.org](http://www.quantum-simulation.org/potentials/sg15_oncv/) | Norm-conserving, good for response |
| **Pseudo-Dojo** | [pseudo-dojo.org](http://www.pseudo-dojo.org) | Highly validated, multiple flavors |

**Recommendation**: Start with SSSP "efficiency" for rapid testing, switch to SSSP "precision" for production.

### Workflow Tools

| Tool | Purpose | URL |
|------|---------|-----|
| **AiiDA** | Workflow automation, provenance tracking | [aiida.net](https://www.aiida.net) |
| **Quantum Mobile** | Pre-configured virtual machine | [quantum-mobile.readthedocs.io](https://quantum-mobile.readthedocs.io) |
| **FireWorks** | Workflow management | [materialsproject.github.io/fireworks](https://materialsproject.github.io/fireworks/) |
| **ASE** | Structure manipulation, calculators | [wiki.fysik.dtu.dk/ase](https://wiki.fysik.dtu.dk/ase/) |

### Visualization Software

| Software | Platform | Best For |
|----------|----------|----------|
| **VESTA** | Windows, macOS, Linux | Crystal structures, charge densities |
| **XCrySDen** | Linux, macOS | Fermi surfaces, band structures |
| **Avogadro** | Cross-platform | Molecular systems |
| **OVITO** | Cross-platform | Large systems, trajectories |
| **py3Dmol** | Jupyter | In-notebook visualization |

### Official Quantum ESPRESSO Resources

- **Documentation**: [quantum-espresso.org/documentation](https://www.quantum-espresso.org/documentation/)
- **Tutorials**: [quantum-espresso.org/tutorials](https://www.quantum-espresso.org/tutorials/)
- **Input Reference**: [quantum-espresso.org/Doc/INPUT_PW.html](https://www.quantum-espresso.org/Doc/INPUT_PW.html)
- **Mailing List**: [lists.quantum-espresso.org](https://lists.quantum-espresso.org/mailman/listinfo/users)
- **GitLab**: [gitlab.com/QEF/q-e](https://gitlab.com/QEF/q-e)

---

## Quick Start

### Step 1: Verify Your Setup (5 minutes)

```bash
# Clone the repository
git clone https://github.com/Indranil2020/DFT_Tutorial.git
cd qe-workshop

# Run the validation script
python test_all_code.py
```

Expected output: `ALL TESTS PASSED!`

### Step 2: Start with the Overview (15 minutes)

Open `notebooks/00_Workshop_Overview.ipynb` and read through the philosophy and workflow description. This establishes the "why" before the "how."

### Step 3: Follow the Sequence (2-4 hours)

Work through notebooks 01-10 in order. Each notebook:
- States learning objectives at the top
- Provides worked examples with Silicon (Si)
- Includes exercises for self-assessment
- Ends with key takeaways and references

**Do not skip convergence testing** (Notebooks 04-06). These establish the numerical foundation for all subsequent calculations.

---

### Priority Notebooks

If time is limited, prioritize these notebooks:

1. **00_Overview** - Essential philosophy (can be assigned as pre-reading)
2. **04_Ecutwfc_Convergence** - Core numerical skill
3. **05_Kpoint_Convergence** - Core numerical skill
4. **06_Lattice_Optimization** - Connects to experimental validation

### Key Points to Emphasize

1. **"Always converge before calculating properties"**
   - Show what happens when you don't (provide example of non-converged band gap)

2. **"Compare to experiment and literature"**
   - Every calculation should reference known values
   - Systematic errors are informative

3. **"Document everything"**
   - Pseudopotential version, XC functional, convergence parameters
   - Future reproducibility depends on this

4. **"Garbage in, garbage out"**
   - Spend more time on structure preparation than on running calculations
   - A wrong structure cannot give right properties

### Common Student Mistakes

| Mistake | How to Address |
|---------|----------------|
| Skipping convergence tests | Show non-converged vs converged results side-by-side |
| Using random pseudopotentials | Explain validation sets (SSSP, Delta test) |
| Ignoring forces/stresses | Show example where unrelaxed structure gives wrong band gap |
| Not checking SCF convergence | Demonstrate failed SCF and its symptoms |
| Trusting database structures blindly | Show example of database errors |

---



## Citation and License



### Citing Quantum ESPRESSO

Always cite the Quantum ESPRESSO papers when publishing results:

```bibtex
@article{QE-2017,
  author = {Giannozzi, P. and others},
  title = {Advanced capabilities for materials modelling with Quantum ESPRESSO},
  journal = {J. Phys.: Condens. Matter},
  volume = {29},
  pages = {465901},
  year = {2017}
}

@article{QE-2009,
  author = {Giannozzi, P. and others},
  title = {QUANTUM ESPRESSO: a modular and open-source software project
           for quantum simulations of materials},
  journal = {J. Phys.: Condens. Matter},
  volume = {21},
  pages = {395502},
  year = {2009}
}
```

### License

This workshop is released under the **MIT License**.

You are free to:
- Use these materials for teaching and research
- Modify and adapt for your needs
- Distribute to students and colleagues

We only ask that you:
- Maintain attribution to the original authors
- Share improvements back with the community

---

## Contact and Contribution

### Reporting Issues

Found a bug, typo, or error? Please report it!

1. **GitHub Issues** (preferred): [github.com/Indranil2020/DFT_Tutorial/issues](https://github.com/Indranil2020/DFT_Tutorial/issues)
2. **Email**:  

When reporting issues, please include:
- Which notebook and cell number
- What you expected vs. what happened
- Your environment (OS, Python version, QE version)

### Contributing

We welcome contributions! Here's how:

1. **Fork the repository**
2. **Create a feature branch**: `git checkout -b feature/new-topic`
3. **Make your changes**
4. **Test**: Run `python test_all_code.py`
5. **Submit a pull request**

#### Contribution Ideas

- Additional example systems (beyond Silicon)
- Notebooks for advanced topics (phonons, response properties)
- Translations to other languages
- Improved visualizations
- Bug fixes and clarifications

### Acknowledgments

This workshop builds on the work of many contributors to the computational materials science community:

- The Quantum ESPRESSO developers
- The Materials Project team
- The SSSP pseudopotential developers
- The AiiDA team
- Countless tutorial authors and educators

---


---

**Remember**: In DFT calculations, **rigor is not optional**. Take the time to validate your structures, converge your parameters, and document your workflow. Your future self (and reviewers) will thank you.

*Happy calculating!*

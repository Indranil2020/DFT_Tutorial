#!/usr/bin/env python3
"""
Enhanced QE Workshop - Code Validation Script
==============================================

This script tests all Python functions used in the workshop notebooks.
Run with: python test_enhanced_workshop.py

All tests use mock data - no actual QE runs required.
"""

import numpy as np
from qe_workshop_utils import (
    # Unit conversions
    BOHR_TO_ANGSTROM, RY_TO_EV, RY_BOHR3_TO_GPA,
    bohr_to_angstrom, angstrom_to_bohr, ry_to_ev, ev_to_ry,
    ry_bohr3_to_gpa, kbar_to_gpa, volume_to_lattice_fcc, lattice_to_volume_fcc,
    # Shannon radii
    SHANNON_RADII, get_shannon_radius,
    # Structure validation
    check_charge_neutrality,
    # Input generators
    generate_scf_input,
    # Output parsers
    parse_scf_output,
    # Analysis
    birch_murnaghan, fit_birch_murnaghan, analyze_convergence,
    # Stability
    check_born_stability_cubic, check_born_stability_hexagonal,
    calculate_bulk_modulus_voigt, calculate_shear_modulus_voigt,
    # K-paths
    HIGH_SYMMETRY_POINTS, generate_kpath_card,
)


def test_passed(test_name: str) -> bool:
    """Report a passed test."""
    print(f"  ✓ {test_name}")
    return True


def test_failed(test_name: str, error: str) -> bool:
    """Report a failed test."""
    print(f"  ✗ {test_name}: {error}")
    return False


# ==============================================================================
# Test 1: Unit Conversions
# ==============================================================================
def test_unit_conversions():
    """Test unit conversion functions."""
    print("\n[Test 1] Unit Conversions")
    print("-" * 50)

    passed = 0
    total = 0

    # 1.1 Bohr to Angstrom
    total += 1
    result = bohr_to_angstrom(10.26)
    if abs(result - 5.43) < 0.01:
        passed += test_passed(f"Bohr to Å: 10.26 Bohr = {result:.3f} Å")
    else:
        test_failed("Bohr to Å", f"Expected ~5.43, got {result}")

    # 1.2 Angstrom to Bohr (inverse)
    total += 1
    result = angstrom_to_bohr(5.43)
    if abs(result - 10.26) < 0.1:
        passed += test_passed(f"Å to Bohr: 5.43 Å = {result:.3f} Bohr")
    else:
        test_failed("Å to Bohr", f"Expected ~10.26, got {result}")

    # 1.3 Ry to eV
    total += 1
    result = ry_to_ev(1.0)
    if abs(result - 13.606) < 0.001:
        passed += test_passed(f"Ry to eV: 1 Ry = {result:.4f} eV")
    else:
        test_failed("Ry to eV", f"Expected ~13.606, got {result}")

    # 1.4 eV to Ry (inverse)
    total += 1
    result = ev_to_ry(13.606)
    if abs(result - 1.0) < 0.001:
        passed += test_passed(f"eV to Ry: 13.606 eV = {result:.4f} Ry")
    else:
        test_failed("eV to Ry", f"Expected ~1.0, got {result}")

    # 1.5 Ry/Bohr³ to GPa
    total += 1
    result = ry_bohr3_to_gpa(0.0068)
    if abs(result - 100) < 5:
        passed += test_passed(f"Ry/Bohr³ to GPa: 0.0068 = {result:.1f} GPa")
    else:
        test_failed("Ry/Bohr³ to GPa", f"Expected ~100, got {result}")

    # 1.6 kbar to GPa
    total += 1
    result = kbar_to_gpa(100)
    if abs(result - 10.0) < 0.001:
        passed += test_passed(f"kbar to GPa: 100 kbar = {result:.1f} GPa")
    else:
        test_failed("kbar to GPa", f"Expected 10.0, got {result}")

    # 1.7 FCC volume/lattice conversions
    total += 1
    V = 270.0  # Bohr³
    a = volume_to_lattice_fcc(V)
    V_back = lattice_to_volume_fcc(a)
    if abs(V_back - V) < 0.001:
        passed += test_passed(f"FCC volume conversion: V={V} → a={a:.2f} → V={V_back:.1f}")
    else:
        test_failed("FCC volume conversion", f"Round-trip failed: {V} vs {V_back}")

    return passed, total


# ==============================================================================
# Test 2: Shannon Ionic Radii
# ==============================================================================
def test_shannon_radii():
    """Test Shannon ionic radii database and lookup."""
    print("\n[Test 2] Shannon Ionic Radii")
    print("-" * 50)

    passed = 0
    total = 0

    # 2.1 Ba²⁺ radius
    total += 1
    r = get_shannon_radius('Ba', 2, 12)
    if r is not None and abs(r - 1.61) < 0.01:
        passed += test_passed(f"Ba²⁺ (CN=12): {r:.3f} Å")
    else:
        test_failed("Ba²⁺ radius", f"Expected 1.61, got {r}")

    # 2.2 Ti⁴⁺ radius
    total += 1
    r = get_shannon_radius('Ti', 4, 6)
    if r is not None and abs(r - 0.605) < 0.01:
        passed += test_passed(f"Ti⁴⁺ (CN=6): {r:.3f} Å")
    else:
        test_failed("Ti⁴⁺ radius", f"Expected 0.605, got {r}")

    # 2.3 O²⁻ radius
    total += 1
    r = get_shannon_radius('O', -2, 6)
    if r is not None and abs(r - 1.40) < 0.01:
        passed += test_passed(f"O²⁻ (CN=6): {r:.3f} Å")
    else:
        test_failed("O²⁻ radius", f"Expected 1.40, got {r}")

    # 2.4 Invalid lookup returns None
    total += 1
    r = get_shannon_radius('Xx', 0, 0)
    if r is None:
        passed += test_passed("Invalid element returns None")
    else:
        test_failed("Invalid lookup", f"Should return None, got {r}")

    return passed, total


# ==============================================================================
# Test 3: Charge Neutrality
# ==============================================================================
def test_charge_neutrality():
    """Test charge neutrality checking."""
    print("\n[Test 3] Charge Neutrality")
    print("-" * 50)

    passed = 0
    total = 0

    # 3.1 BaTiO3 (should be neutral)
    total += 1
    comp = {'Ba': 1, 'Ti': 1, 'O': 3}
    ox = {'Ba': 2, 'Ti': 4, 'O': -2}
    is_neutral, charge = check_charge_neutrality(comp, ox)
    if is_neutral and abs(charge) < 0.001:
        passed += test_passed(f"BaTiO3: neutral (charge = {charge})")
    else:
        test_failed("BaTiO3", f"Should be neutral, got charge = {charge}")

    # 3.2 Fe2O3 (should be neutral)
    total += 1
    comp = {'Fe': 2, 'O': 3}
    ox = {'Fe': 3, 'O': -2}
    is_neutral, charge = check_charge_neutrality(comp, ox)
    if is_neutral:
        passed += test_passed(f"Fe2O3: neutral (charge = {charge})")
    else:
        test_failed("Fe2O3", f"Should be neutral, got charge = {charge}")

    # 3.3 Invalid composition (BaTiO2)
    total += 1
    comp = {'Ba': 1, 'Ti': 1, 'O': 2}
    ox = {'Ba': 2, 'Ti': 4, 'O': -2}
    is_neutral, charge = check_charge_neutrality(comp, ox)
    if not is_neutral and abs(charge - 2.0) < 0.001:
        passed += test_passed(f"BaTiO2: NOT neutral (charge = {charge})")
    else:
        test_failed("BaTiO2", f"Should have charge +2, got {charge}")

    return passed, total


# ==============================================================================
# Test 4: Input File Generation
# ==============================================================================
def test_input_generation():
    """Test input file generators."""
    print("\n[Test 4] Input File Generation")
    print("-" * 50)

    passed = 0
    total = 0

    # 4.1 Basic SCF input
    total += 1
    inp = generate_scf_input(
        prefix='test',
        ecutwfc=40.0,
        ecutrho=320.0,
        kpoints=8,
        pseudo_dir='/path/to/pseudo'
    )
    checks = [
        'ecutwfc = 40.0' in inp,
        'ecutrho = 320.0' in inp,
        '8 8 8 0 0 0' in inp,
        "calculation = 'scf'" in inp,
    ]
    if all(checks):
        passed += test_passed("Basic SCF input generation")
    else:
        test_failed("Basic SCF input", "Missing expected parameters")

    # 4.2 K-points tuple
    total += 1
    inp = generate_scf_input('test', 40.0, 320.0, (4, 4, 4), '/path')
    if '4 4 4 0 0 0' in inp:
        passed += test_passed("K-points tuple handling")
    else:
        test_failed("K-points tuple", "K-points not correct")

    # 4.3 Magnetic input
    total += 1
    inp = generate_scf_input(
        'test', 40.0, 320.0, 8, '/path',
        nspin=2,
        starting_magnetization=[0.5, -0.5]
    )
    if 'nspin = 2' in inp and 'starting_magnetization(1)' in inp:
        passed += test_passed("Magnetic input generation")
    else:
        test_failed("Magnetic input", "Missing spin parameters")

    return passed, total


# ==============================================================================
# Test 5: Output Parsing
# ==============================================================================
SAMPLE_SCF_OUTPUT = """
     Program PWSCF v.6.7 starts on  1Jan2024 at 12:00:00

     bravais-lattice index     =            2
     lattice parameter (alat)  =      10.2600  a.u.
     unit-cell volume          =     270.0114 (a.u.)^3
     number of atoms/cell      =            2
     number of electrons       =         8.00
     kinetic-energy cutoff     =      40.0000  Ry
     charge-density cutoff     =     320.0000  Ry

     iteration #  1     ecut=    40.00 Ry     beta= 0.70
     total energy              =     -15.83920000 Ry

     iteration #  2     ecut=    40.00 Ry     beta= 0.70
     total energy              =     -15.84500000 Ry

     iteration #  3     ecut=    40.00 Ry     beta= 0.70
     total energy              =     -15.84550000 Ry

     convergence has been achieved in   3 iterations

     Forces acting on atoms (cartesian axes, Ry/au):

     atom    1 type  1   force =     0.00000000    0.00000000    0.00000000
     atom    2 type  1   force =     0.00000000    0.00000000    0.00000000

     Total force =     0.000000     Total SCF correction =     0.000000

     total   stress  (Ry/bohr**3)                   (kbar)     P=       -5.50
        -0.00003740   0.00000000   0.00000000           -5.50        0.00        0.00
         0.00000000  -0.00003740   0.00000000            0.00       -5.50        0.00
         0.00000000   0.00000000  -0.00003740            0.00        0.00       -5.50


!    total energy              =     -15.84550000 Ry

     highest occupied, lowest unoccupied level (ev):     6.2500    6.8500

     PWSCF        :      1.23s CPU      1.45s WALL

"""

def test_output_parsing():
    """Test output file parsing."""
    print("\n[Test 5] Output Parsing")
    print("-" * 50)

    passed = 0
    total = 0

    results = parse_scf_output(SAMPLE_SCF_OUTPUT)

    # 5.1 Convergence detection
    total += 1
    if results['converged']:
        passed += test_passed("Convergence detection")
    else:
        test_failed("Convergence detection", "Should be converged")

    # 5.2 Energy parsing
    total += 1
    if results['total_energy_ry'] is not None:
        if abs(results['total_energy_ry'] - (-15.84550000)) < 1e-6:
            passed += test_passed(f"Energy parsing: {results['total_energy_ry']:.6f} Ry")
        else:
            test_failed("Energy parsing", f"Expected -15.84550000, got {results['total_energy_ry']}")
    else:
        test_failed("Energy parsing", "Energy not found")

    # 5.3 Volume parsing
    total += 1
    if results['volume_bohr3'] is not None:
        if abs(results['volume_bohr3'] - 270.0114) < 0.01:
            passed += test_passed(f"Volume parsing: {results['volume_bohr3']:.4f} Bohr³")
        else:
            test_failed("Volume parsing", f"Expected 270.0114, got {results['volume_bohr3']}")
    else:
        test_failed("Volume parsing", "Volume not found")

    # 5.4 Pressure parsing
    total += 1
    if results['pressure_kbar'] is not None:
        if abs(results['pressure_kbar'] - (-5.50)) < 0.01:
            passed += test_passed(f"Pressure parsing: {results['pressure_kbar']:.2f} kbar")
        else:
            test_failed("Pressure parsing", f"Expected -5.50, got {results['pressure_kbar']}")
    else:
        test_failed("Pressure parsing", "Pressure not found")

    # 5.5 Band edges
    total += 1
    if 'vbm' in results and 'cbm' in results:
        if results['vbm'] == 6.25 and results['cbm'] == 6.85:
            passed += test_passed(f"Band edges: VBM={results['vbm']}, CBM={results['cbm']} eV")
        else:
            test_failed("Band edges", f"Expected 6.25/6.85")
    else:
        test_failed("Band edges", "Band edges not found")

    return passed, total


# ==============================================================================
# Test 6: Birch-Murnaghan EOS
# ==============================================================================
def test_birch_murnaghan():
    """Test Birch-Murnaghan equation of state."""
    print("\n[Test 6] Birch-Murnaghan EOS")
    print("-" * 50)

    passed = 0
    total = 0

    # Parameters
    E0_true = -15.85
    V0_true = 270.0
    B0_true = 0.0067  # ~100 GPa in Ry/Bohr³
    B0p_true = 4.0

    # 6.1 EOS at equilibrium
    total += 1
    E_at_V0 = birch_murnaghan(V0_true, E0_true, V0_true, B0_true, B0p_true)
    if abs(E_at_V0 - E0_true) < 1e-10:
        passed += test_passed("EOS at V0 returns E0")
    else:
        test_failed("EOS at V0", f"Expected {E0_true}, got {E_at_V0}")

    # 6.2 EOS fitting
    total += 1
    V_test = np.linspace(V0_true * 0.95, V0_true * 1.05, 9)
    E_test = birch_murnaghan(V_test, E0_true, V0_true, B0_true, B0p_true)
    np.random.seed(42)
    E_test += np.random.normal(0, 1e-5, len(E_test))

    E0_fit, V0_fit, B0_fit, B0p_fit = fit_birch_murnaghan(V_test, E_test)

    if abs(V0_fit - V0_true) < 0.5:
        passed += test_passed(f"V0 recovery: {V0_fit:.2f} (true: {V0_true})")
    else:
        test_failed("V0 recovery", f"Expected {V0_true}, got {V0_fit}")

    # 6.3 Bulk modulus
    total += 1
    B0_GPa_fit = B0_fit * RY_BOHR3_TO_GPA
    B0_GPa_true = B0_true * RY_BOHR3_TO_GPA
    if abs(B0_GPa_fit - B0_GPa_true) < 5:
        passed += test_passed(f"B0 recovery: {B0_GPa_fit:.1f} GPa (true: {B0_GPa_true:.1f})")
    else:
        test_failed("B0 recovery", f"Expected {B0_GPa_true:.1f}, got {B0_GPa_fit:.1f}")

    return passed, total


# ==============================================================================
# Test 7: Convergence Analysis
# ==============================================================================
def test_convergence_analysis():
    """Test convergence analysis."""
    print("\n[Test 7] Convergence Analysis")
    print("-" * 50)

    passed = 0
    total = 0

    # Simulated convergence data (Ry)
    energies = np.array([-15.80, -15.84, -15.845, -15.8455, -15.8456, -15.8456])

    delta_e, conv_idx = analyze_convergence(energies, threshold_mev=1.0, n_atoms=2)

    # 7.1 Last point should be ~0
    total += 1
    if abs(delta_e[-1]) < 0.01:
        passed += test_passed("Reference energy subtraction")
    else:
        test_failed("Reference subtraction", f"Last point should be ~0, got {delta_e[-1]}")

    # 7.2 Convergence detection
    total += 1
    if conv_idx is not None and conv_idx > 0:
        passed += test_passed(f"Convergence at index {conv_idx}")
    else:
        test_failed("Convergence detection", "Should find convergence")

    return passed, total


# ==============================================================================
# Test 8: Born Stability
# ==============================================================================
def test_born_stability():
    """Test Born stability criteria."""
    print("\n[Test 8] Born Stability Criteria")
    print("-" * 50)

    passed = 0
    total = 0

    # Silicon elastic constants (GPa)
    C11, C12, C44 = 166.0, 64.0, 79.6

    # 8.1 Cubic stability
    total += 1
    is_stable, criteria = check_born_stability_cubic(C11, C12, C44)
    if is_stable:
        passed += test_passed("Silicon: mechanically stable")
    else:
        test_failed("Silicon stability", f"Should be stable, criteria: {criteria}")

    # 8.2 Unstable case
    total += 1
    is_stable, criteria = check_born_stability_cubic(100, 150, 50)  # C12 > C11
    if not is_stable:
        passed += test_passed("Unstable case detected (C12 > C11)")
    else:
        test_failed("Unstable detection", "Should be unstable")

    # 8.3 Bulk modulus
    total += 1
    B = calculate_bulk_modulus_voigt(C11, C12)
    if abs(B - 98.0) < 1:
        passed += test_passed(f"Bulk modulus: {B:.1f} GPa")
    else:
        test_failed("Bulk modulus", f"Expected ~98, got {B}")

    # 8.4 Shear modulus
    total += 1
    G = calculate_shear_modulus_voigt(C11, C12, C44)
    if abs(G - 68.12) < 1:
        passed += test_passed(f"Shear modulus: {G:.1f} GPa")
    else:
        test_failed("Shear modulus", f"Expected ~68, got {G}")

    return passed, total


# ==============================================================================
# Test 9: K-path Generation
# ==============================================================================
def test_kpath_generation():
    """Test k-path generation."""
    print("\n[Test 9] K-path Generation")
    print("-" * 50)

    passed = 0
    total = 0

    # 9.1 FCC k-path
    total += 1
    kpath = generate_kpath_card('FCC')
    if kpath and 'K_POINTS {crystal_b}' in kpath:
        passed += test_passed("FCC k-path generated")
    else:
        test_failed("FCC k-path", "Header not found")

    # 9.2 X point coordinates
    total += 1
    if kpath and '0.500000 0.000000 0.500000' in kpath:
        passed += test_passed("X point coordinates correct")
    else:
        test_failed("X point", "Coordinates not found")

    # 9.3 BCC k-path
    total += 1
    kpath_bcc = generate_kpath_card('BCC')
    if kpath_bcc and 'K_POINTS {crystal_b}' in kpath_bcc:
        passed += test_passed("BCC k-path generated")
    else:
        test_failed("BCC k-path", "Failed to generate")

    return passed, total


# ==============================================================================
# Main Test Runner
# ==============================================================================
def run_all_tests():
    """Run all tests and report results."""
    print("=" * 60)
    print("ENHANCED QE WORKSHOP - CODE VALIDATION")
    print("=" * 60)

    total_passed = 0
    total_tests = 0

    test_functions = [
        test_unit_conversions,
        test_shannon_radii,
        test_charge_neutrality,
        test_input_generation,
        test_output_parsing,
        test_birch_murnaghan,
        test_convergence_analysis,
        test_born_stability,
        test_kpath_generation,
    ]

    for test_func in test_functions:
        passed, total = test_func()
        total_passed += passed
        total_tests += total

    # Summary
    print("\n" + "=" * 60)
    print("SUMMARY")
    print("=" * 60)
    print(f"Total tests: {total_tests}")
    print(f"Passed:      {total_passed}")
    print(f"Failed:      {total_tests - total_passed}")
    print(f"Success rate: {100*total_passed/total_tests:.1f}%")
    print("=" * 60)

    if total_passed == total_tests:
        print("\n✓ ALL TESTS PASSED!")
        return True
    else:
        print(f"\n✗ {total_tests - total_passed} TESTS FAILED")
        return False


if __name__ == '__main__':
    success = run_all_tests()
    exit(0 if success else 1)

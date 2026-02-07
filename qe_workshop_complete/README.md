# Quantum ESPRESSO DFT Workshop

A hands-on workshop for learning Density Functional Theory (DFT) calculations using Quantum ESPRESSO 7.5.

Everything runs inside Docker — you do **not** need to install Quantum ESPRESSO, Python, or any libraries manually.

---

## For Students: How to Get Started

### 1. Read the Setup Guide for Your Operating System

Open **[DOCKER_SETUP_GUIDE.md](DOCKER_SETUP_GUIDE.md)** and follow the step-by-step instructions for your OS:

- **Windows** → 7 steps, starting from installing Docker Desktop
- **macOS** → 7 steps, starting from installing Docker Desktop
- **Linux** → 7 steps, starting from installing Docker Engine

Each section tells you exactly:
- How to check if your computer is compatible
- How to install Docker (with screenshots-level detail)
- How to download these workshop files from GitHub
- How to download the Docker image
- How to start the workshop environment
- How to open JupyterLab in your browser
- How to navigate to the notebooks and run them

### 2. What You Will See

After completing the setup guide, you will have **JupyterLab** open in your browser at `http://localhost:8888`. Inside, navigate to the `notebooks_enhanced/` folder. The workshop notebooks are:

| # | Notebook | What You Learn |
|---|---------|---------------|
| 00 | Overview and Philosophy | Workshop goals, DFT workflow overview |
| 01 | Database Search | Finding crystal structures from databases |
| 02 | Structure Preparation | Validating and preparing structures for DFT |
| 03 | DFT Fundamentals | Your first SCF calculation, input/output files |
| 04 | Convergence Testing | Systematically converging ecutwfc and k-points |
| 05 | Structure Optimization | Relaxing structures, equation of state |
| 06 | Magnetic Systems | Spin-polarized calculations, magnetic ordering |
| 07 | Stability Analysis | Phonons, elastic constants, convex hull, AIMD |
| 08 | Electronic Properties | Band structure and density of states |
| 09 | Advanced Properties | Optical, thermal, and transport properties |
| 10 | Research Workflow | Putting it all together for real research |

### 3. How to Run a Notebook

1. **Double-click** a notebook file (`.ipynb`) in JupyterLab to open it.
2. Read the text cells for explanations.
3. Click on a code cell and press **Shift + Enter** to run it.
4. Follow the notebooks **in order** (00 → 01 → 02 → ... → 10).

### 4. Your Files Are Safe

Everything you do inside JupyterLab is saved to the `qe_workshop_complete` folder on your computer. If Docker stops or your computer restarts, your work is preserved. Just start Docker again.

---

## What's Inside the Docker Image

You don't need to install any of this — it's all pre-installed in the Docker image:

| Software | Purpose |
|----------|---------|
| Quantum ESPRESSO 7.5 | DFT calculations (pw.x, ph.x, pp.x, dos.x, bands.x, epsilon.x) |
| Python 3 + JupyterLab | Running notebooks and scripts |
| ASE, pymatgen, spglib | Structure manipulation and analysis |
| phonopy, seekpath | Phonon calculations, automatic k-paths |
| BoltzTraP2 | Electronic transport (Seebeck, conductivity) |
| ALAMODE | Lattice thermal conductivity |
| matplotlib, plotly | Plotting and visualization |

---

## Files in This Repository

```
qe_workshop_complete/
│
├── DOCKER_SETUP_GUIDE.md        ← START HERE (setup instructions)
├── WORKSHOP_INSTRUCTOR_GUIDE.md ← For the instructor (presentation guide)
│
├── notebooks_enhanced/          ← THE WORKSHOP NOTEBOOKS
│   ├── 00_Workshop_Overview_and_Philosophy.ipynb
│   ├── 01_Database_Search_and_Structure_Discovery.ipynb
│   ├── 02_Structure_Validation_and_Preparation.ipynb
│   ├── 03_DFT_Setup_Fundamentals.ipynb
│   ├── 04_Convergence_Testing.ipynb
│   ├── 05_Structure_Optimization.ipynb
│   ├── 06_Magnetic_Systems.ipynb
│   ├── 07_Stability_Analysis.ipynb
│   ├── 08_Electronic_Properties.ipynb
│   ├── 09_Advanced_Properties.ipynb
│   └── 10_Complete_Research_Workflow.ipynb
│
├── pseudopotentials/            ← Pseudopotential files (auto-used by notebooks)
├── converged_parameters.json    ← Parameters shared between notebooks
├── outputs/                     ← Calculation results (created as you run)
│
├── start_workshop.sh            ← One-click launcher for Linux/macOS
├── start_workshop.bat           ← One-click launcher for Windows
├── docker-compose.yml           ← Alternative: Docker Compose config
├── Dockerfile                   ← How the Docker image was built
└── requirements.txt             ← Python dependencies list
```

---

## For Instructors

### Pre-Workshop: Send This to Students (1 Week Before)

> **Subject:** Workshop Setup — Please Complete Before the Session
>
> Dear Students,
>
> Please complete these steps **before** the workshop. They require internet and take 30-60 minutes.
>
> 1. Open this link: https://github.com/Indranil2020/DFT_Workshop_QE
> 2. Click the file **DOCKER_SETUP_GUIDE.md**
> 3. Find your operating system (Windows, macOS, or Linux)
> 4. Follow **Steps 1 through 4** (install Docker, download files, download image)
>
> On workshop day, we will do Steps 5-7 together (start Docker, open browser, run notebooks).
>
> If you have trouble, bring your laptop to the workshop and we will help you.

### Building and Pushing the Docker Image (Instructor Only)

```bash
cd qe_workshop_complete
docker build -t qe-workshop .
docker tag qe-workshop indranilm/qe-workshop:latest
docker login -u indranilm
docker push indranilm/qe-workshop:latest
```

### Workshop Presentation Guide

See **[WORKSHOP_INSTRUCTOR_GUIDE.md](WORKSHOP_INSTRUCTOR_GUIDE.md)** for a 2-hour presentation plan with timing, talking points, and navigation guide for each notebook.
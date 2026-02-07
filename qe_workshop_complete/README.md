# Quantum ESPRESSO Workshop

A comprehensive workshop for learning DFT calculations with Quantum ESPRESSO.

## Workshop Structure

### Notebooks (in order)

1. **01_Introduction_and_Setup.ipynb** - Environment setup, pseudopotentials, basic concepts
2. **02_SCF_Calculation_Basics.ipynb** - Input/output structure, parameter explanations
3. **03_Ecutwfc_Convergence.ipynb** - Wavefunction cutoff convergence testing
4. **04_Kpoint_Convergence.ipynb** - Brillouin zone sampling convergence
5. **05_Lattice_Optimization.ipynb** - Equation of state, equilibrium lattice
6. **06_Band_Structure.ipynb** - Electronic band structure calculations
7. **07_DOS_Calculation.ipynb** - Density of states and PDOS
8. **08_Summary_and_Exercises.ipynb** - Summary and practice exercises

### Supporting Files

- `QUICK_REFERENCE.md` - Quick reference card with formulas and parameters
- `test_all_code.py` - Validation script for all workshop code
- `pseudopotentials/` - Si pseudopotential file

## Prerequisites

- Python 3.8+
- numpy, scipy, matplotlib
- Quantum ESPRESSO 6.x or 7.x
- Jupyter Notebook/Lab or Google Colab

## Installation

```bash
# Install Python packages
pip install numpy scipy matplotlib jupyter

# Set up QE (Ubuntu/Debian)
sudo apt install quantum-espresso
```

## Usage

1. Start with Notebook 01 to verify your setup
2. Follow notebooks in sequence
3. Complete convergence testing (03-05) before any property calculations
4. Use the Quick Reference card for parameters and formulas

## Key Principle

**Always converge these parameters BEFORE calculating properties:**
1. ecutwfc (wavefunction cutoff)
2. k-points (Brillouin zone sampling)
3. Lattice parameter (equilibrium structure)

## Validation

Run the test script to verify all code functions correctly:
```bash
python test_all_code.py
```

Expected output: "ALL TESTS PASSED!"

## License

This workshop is provided for educational purposes.

## Author

Generated for DFT workshop training.



# --- Dockerfile ---

Comprehensive guide to set up a local Quantum Espresso environment using Docker.


***

# COMPLETE WORKSHOP GUIDE: Local Quantum Espresso via Docker

##  PART 1: INSTRUCTOR PREPARATION (Do this once)

As the instructor, you need to build the "Virtual Computer" (Docker Image) that contains Quantum Espresso, Python, Jupyter, and all necessary tools (ASE, Pymatgen, etc.).

### Step 1: Install Docker Desktop
If you haven't already, install [Docker Desktop](https://www.docker.com/products/docker-desktop) on your own machine to build the image.

### Step 2: Create the `Dockerfile`
Create a folder on your computer named `QE_Builder`. Inside, create a text file named `Dockerfile` (no extension) and paste this content.

**Note on Included Tools:** This setup includes Quantum Espresso (with all binary executables like `pw.x`, `pp.x`, `dos.x`), plus Python tools (`ASE`, `Pymatgen`, `Spglib`, `PyXtal`) for structure generation and analysis.

```dockerfile
# Use a stable Ubuntu base
FROM ubuntu:22.04

ENV DEBIAN_FRONTEND=noninteractive

# 1. Install System Dependencies, QE, and Editors
RUN apt-get update && apt-get install -y \
    quantum-espresso \
    quantum-espresso-data \
    python3-pip \
    python3-dev \
    build-essential \
    gfortran \
    openmpi-bin \
    libopenmpi-dev \
    git \
    nano \
    vim \
    nodejs \
    npm \
    && rm -rf /var/lib/apt/lists/*

# 2. Install Python Scientific Stack + Web Visualization Tools
RUN pip3 install --no-cache-dir \
    jupyterlab \
    numpy \
    scipy \
    matplotlib \
    pandas \
    ase \
    pymatgen \
    spglib \
    pyxtal \
    nglview \
    py3dmol

# 3. Enable Widgets for 3D visualization in Browser
RUN jupyter labextension install @jupyter-widgets/jupyterlab-manager
RUN jupyter-nbextension enable nglview --py --sys-prefix

WORKDIR /home/jovyan
EXPOSE 8888

# 4. Launch Command
CMD ["jupyter", "lab", "--ip=0.0.0.0", "--port=8888", "--no-browser", "--allow-root", "--NotebookApp.token=''", "--NotebookApp.password=''"]
```
*Note: I removed the token requirement in the last line (`token=''`) to make it even easier for students. They won't need to copy-paste a token; it will just open.*

### Step 3: Build and Upload
Open your terminal/CMD in the `QE_Builder` folder and run:

1.  **Build:**
    ```bash
    docker build -t yourdockerid/qe-workshop-full .
    ```
    *(Replace `yourdockerid` with your actual Docker Hub username)*

2.  **Push (Upload to Cloud):**
    ```bash
    docker push yourdockerid/qe-workshop-full
    ```

## Proposed Steps

### 1. Build the Image
First, we build the image locally. We'll give it a simple name like `qe-workshop`.
```bash
cd /home/niel/git/DFT_Tutorial/qe_workshop_complete
docker build -t qe-workshop .
```

### 2. Tag the Image for Docker Hub
To push an image, it must be tagged with your Docker ID. This tells Docker *where* to send it.
```bash
docker tag qe-workshop indranilm/qe-workshop:latest
```

### 3. Log In to Docker Hub
You need to authenticate your terminal with your Docker account.
```bash
docker login -u indranilm
```
*Note: It will prompt you for your password.*

### 4. Push the Image
Finally, upload the image to the cloud.
```bash
docker push indranilm/qe-workshop:latest
```

## Verification Plan

### Manual Verification
1.  Check [Docker Hub](https://hub.docker.com/u/indranilm) to see if the `qe-workshop` repository exists and has a `latest` tag.
2.  (Optional) Try pulling the image on a different machine or deleting the local one and pulling it:
    ```bash
    docker pull indranilm/qe-workshop:latest
    ```

sudo apt install docker-compose, how to do it in windows  and mac do not know 

docker-compose up
ERROR: Version in "./docker-compose.yml" is unsupported. You might be seeing this error because you're using the wrong Compose file version. Either specify a supported version (e.g "2.2" or "3.3") and place your service definitions under the `services` key, or omit the `version` key and place your service definitions at the root of the file to use version 1.
For more on the Compose file format versions, see https://docs.docker.com/compose/compose-file/
(base) niel@niel-hp:~/trial_docker$ 


vi docker-compose.yml 
(base) niel@niel-hp:~/trial_docker$ docker-compose up
WARNING: Some services (qe-workshop) use the 'deploy' key, which will be ignored. Compose does not support 'deploy' configuration - use `docker stack deploy` to deploy to a swarm.
ERROR: Couldn't connect to Docker daemon at http+docker://localhost - is it running?

If it's at a non-standard location, specify the URL with the DOCKER_HOST environment variable.



### Step 4: Create the "One-Click" Launchers
Students hate typing commands. You will provide them with files they just double-click. Create these two files.

**File A: `Start_Windows.bat` (For Windows Users)**
```batch
@echo off
TITLE Quantum Espresso Workshop
echo ==========================================================
echo      STARTING QUANTUM ESPRESSO WORKSHOP ENVIRONMENT
echo ==========================================================
echo.
echo 1. Checking for Docker...
docker --version >nul 2>&1
if %errorlevel% neq 0 (
    echo ERROR: Docker is not running or not installed!
    echo Please install Docker Desktop and try again.
    pause
    exit
)

echo 2. Downloading/Starting the environment (This may take time first run)...
echo.
echo ----------------------------------------------------------
echo IMPORTANT: 
echo A. Do NOT close this Black Window.
echo B. Open your browser and go to: http://localhost:8888
echo ----------------------------------------------------------
echo.

:: This command mounts the CURRENT folder (%cd%) to the Docker container
docker run -it --rm -p 8888:8888 -v "%cd%":/home/jovyan yourdockerid/qe-workshop-full

pause
```

**File B: `Start_Mac_Linux.sh` (For Mac/Linux Users)**
```bash
#!/bin/bash
echo "=========================================================="
echo "     STARTING QUANTUM ESPRESSO WORKSHOP ENVIRONMENT"
echo "=========================================================="
echo ""

# Check for Docker
if ! command -v docker &> /dev/null
then
    echo "ERROR: Docker is not found. Please install Docker Desktop."
    exit 1
fi

echo "Starting Server..."
echo "1. Do NOT close this terminal window."
echo "2. Open your browser and go to: http://localhost:8888"
echo ""

# Run Docker mounting current directory
docker run -it --rm -p 8888:8888 -v "$(pwd)":/home/jovyan yourdockerid/qe-workshop-full
```

### Step 5: The "Course Material" Zip
Create a folder named `QE_Workshop_Materials`. Put the following inside:
1.  `Start_Windows.bat`
2.  `Start_Mac_Linux.sh`
3.  Your Jupyter Notebooks (`.ipynb`) with the lesson plans.
4.  Any `CIF` files or input files needed.

**Zip this folder.** This is what you email to students.

---

##  PART 2: EMAIL TO STUDENTS (Pre-Workshop)

**Subject:** Important Setup Instructions for [Workshop Name]

Dear Students,

In our upcoming workshop, we will be performing heavy Quantum Mechanical calculations. To ensure these run fast, we will use your laptop's full power (8+ cores) instead of the limited cloud servers.

** YOU MUST COMPLETE THESE 2 STEPS BEFORE THE WORKSHOP **

**Step 1: Install the Engine (Docker)**
We need a tool called "Docker" to run the scientific software.
1.  Download **Docker Desktop**: [https://www.docker.com/products/docker-desktop/](https://www.docker.com/products/docker-desktop/)
2.  Install it (Standard installation).
3.  **Run it once** to ensure it opens. You should see a small "Whale" icon in your system tray/menu bar.
    *   *Windows Users:* It may ask you to update WSL2. Follow the prompt instructions.

**Step 2: Install Visualization Tool (VESTA)**
To see the atoms and crystals, install VESTA.
1.  Download here: [https://jp-minerals.org/vesta/en/download.html](https://jp-minerals.org/vesta/en/download.html)
2.  Install it on your computer.

See you at the workshop!

---

##  PART 3: IN-CLASS INSTRUCTIONS (For Students)

*(Print this out or put it on the projector)*

###  Launching the Laboratory

1.  **Unzip** the `QE_Workshop_Materials` file to your **Desktop**.
2.  Open the folder.

**For Windows Users:**
1.  Double-click `Start_Windows.bat`.
2.  A black window will appear. **Wait.** (The first time, it downloads 500MB+ of data).
3.  Once the text stops moving, open Chrome/Edge.
4.  Type `localhost:8888` in the address bar.

**For Mac/Linux Users:**
1.  Right-click `Start_Mac_Linux.sh` -> Open with -> Terminal.
    *   *Alternative:* Open Terminal, type `sh `, drag the file into the terminal, and hit Enter.
2.  Open Safari/Chrome and go to `localhost:8888`.

---

###  How to use the Workshop Environment

You will see **Jupyter Lab**. It looks like Google Colab, but it is running on *your* computer.

**1. Running Calculations (Quantum Espresso)**
In the notebook cells, you can run terminal commands using the `!` symbol.
Example to run a Self-Consistent Field (SCF) calculation using 4 CPU cores:

```python
import os
# Run QE using MPI (Parallel processing)
!mpirun -np 4 pw.x -in scf.in > scf.out
```

**2. Using Python Tools (ASE/Pymatgen)**
All tools are pre-installed. You can use them immediately in Python cells:

```python
from ase.build import bulk
from ase.visualize import view

# Create Silicon crystal
si = bulk('Si', 'diamond', a=5.43)
print("Crystal Created Successfully!")
```

**3. Visualizing Results (The "Magic Folder")**
This system uses a **Shared Folder**.
1.  Look at the `QE_Workshop_Materials` folder on your actual Desktop.
2.  Any file you save in Jupyter Lab (like `charge_density.xsf`) will **instantly appear** in that folder on your Desktop.
3.  **To visualize:** Open **VESTA** on your computer, drag the file from your Desktop folder into VESTA.

**4. Stopping the Workshop**
1.  Save your work in the Notebook (File -> Save).
2.  Close the browser tab.
3.  Go to the Black Terminal Window and press `Ctrl+C` (or just close the window) to stop the Docker engine.

---

##  PART 4: FAQ / Troubleshooting

**Q: The black window says "Docker is not recognized".**
*   **A:** You did not install Docker Desktop, or it is not running. Search for "Docker Desktop" in your Start Menu and open it. Wait for the whale icon to stop animating.

**Q: I closed the black window by mistake!**
*   **A:** Your calculation stopped. Double-click the `Start` script again to restart. Your files are safe, but the calculation progress is lost.

**Q: The internet is disconnected. Will it work?**
*   **A:** YES. Once the black window is running, you can be offline. It runs 100% on your laptop.

**Q: Can I use this for my own thesis project later?**
*   **A:** Yes! Just keep the `Start` script. Put your own input files in that folder and run the script. You have a full research-grade Quantum Espresso station on your laptop forever.
Here's a step-by-step guide to **install Quantum ESPRESSO (QE) on Windows via WSL (Ubuntu)**, transfer data from external drives, and run QE:

---

### **Step 1: Install WSL and Ubuntu**
1. **Enable WSL**:  
   Open PowerShell as Administrator and run:  
   ```powershell
   wsl --install
   ```
   Reboot your PC when prompted.

2. **Install Ubuntu**:
   ```powershell
   wsl --install -d <distribution name>
   ```
   - After reboot, open the Microsoft Store and install **Ubuntu (latest LTS version)**.  
   - Launch Ubuntu from the Start menu to complete setup (create a username/password).
   - If you encounter any issues during the installation, you can refer to the official Microsoft documentation for troubleshooting: https://learn.microsoft.com/en-us/windows/wsl/install

---

### **Step 2: Update Ubuntu**
```bash
sudo apt update && sudo apt upgrade -y
```

---

### **Step 3: Install Python 3 and Conda**
1. **Python 3** (already pre-installed in Ubuntu):  
   Verify with:  
   ```bash
   python3 --version
   ```

2. **Install Miniconda**:  
   ```bash
   wget https://repo.anaconda.com/miniconda/Miniconda3-latest-Linux-x86_64.sh
   chmod +x Miniconda3-latest-Linux-x86_64.sh
   ./Miniconda3-latest-Linux-x86_64.sh
   ```
   Follow prompts (agree to license, install to default location, and allow `conda init`).  
   Close/reopen the terminal afterward.

---

### **Step 4: Create a Conda Environment for QE**
1. **Create and activate `qe_env`**:  
   ```bash
   conda create --name qe_env python=3.9 -y
   conda activate qe_env
   ```

2. **Install Quantum ESPRESSO**:  
   ```bash
   conda install conda-forge::qe -y
   conda install conda-forge::qe-tools -y
   ```

---

### **Step 5: Transfer Data from External Drive to WSL**
1. **Access External Drive**:  
   - Connect your external drive (e.g., `D:` or `E:`).  
   - In WSL, navigate to the drive:  
     ```bash
     cd /mnt/[drive_letter]/   # e.g., cd /mnt/e/
     ```
     Use `ls` to view files.

2. **Copy Files to WSL**:  
   ```bash
   mkdir ~/qe_data   # Create a directory in WSL home
   cp -r /mnt/e/path/to/data/* ~/qe_data   # Copy files
   ```

---

### **Step 6: Run QE in WSL**
1. **Activate the Conda environment**:  
   ```bash
   conda activate qe_env
   ```

2. **Navigate to your data**:  
   ```bash
   cd ~/qe_data
   ```

3. **Run QE Commands**:  
   Example for `pw.x`:  
   ```bash
   pw.x -input input_file.in > output_file.out
   ```

---

### **Data Management Tips**
- **Mount External Drives**: All Windows drives are auto-mounted under `/mnt/[drive_letter]`.  
- **Performance**: For large files, work directly in WSL’s native file system (`~/` or `/home/`) for faster I/O.  
- **Backup**: Copy results back to Windows using:  
  ```bash
  cp ~/qe_data/output_file.out /mnt/c/Users/YourName/Desktop/
  ```

---

### **Troubleshooting**
1. **QE Not Found**:  
   Ensure `quantum-espresso` is installed in the active Conda environment.  
   Verify with:  
   ```bash
   conda list | grep espresso
   ```

2. **Permission Denied**:  
   Run:  
   ```bash
   sudo chmod -R 755 ~/qe_data
   ```

3. **MPI Issues**:  
   Install MPI libraries:  
   ```bash
   sudo apt install openmpi-bin libopenmpi-dev
   ```

4. **GUI Tools (XCrySDen, etc.)**:  
   Install X Server for Windows (e.g., [VcXsrv](https://sourceforge.net/projects/vcxsrv/)) to display Linux GUI apps.

---

### **Compile QE from Source (Optional)**
1. Install dependencies:  
   ```bash
   sudo apt install gfortran libfftw3-dev libopenmpi-dev libblas-dev liblapack-dev
   ```

2. Clone QE repository:  
   ```bash
   git clone https://github.com/QEF/q-e.git
   cd q-e
   ```

3. Configure and compile:  
   ```bash
   ./configure
   make all
   ```

---


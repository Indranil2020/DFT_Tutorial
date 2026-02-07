# Quantum ESPRESSO Workshop — Setup Guide for Students

This guide will take you from zero to running the workshop notebooks.  
**Pick your operating system below and follow EVERY step in order.**

> **What is Docker?** Docker is a tool that creates a self-contained "virtual computer" on your laptop. Inside it, Quantum ESPRESSO, Python, Jupyter, and all required libraries are pre-installed. You don't need to install anything else.

> **What are the workshop notebooks?** They are Jupyter notebooks (`.ipynb` files) that contain the lessons, code, and exercises. They are stored in this GitHub repository. You will download them and open them inside the Docker environment.

---

# Choose Your Operating System

- [WINDOWS (Step-by-Step)](#windows-step-by-step)
- [macOS (Step-by-Step)](#macos-step-by-step)
- [LINUX (Step-by-Step)](#linux-step-by-step)

---

---

# WINDOWS (Step-by-Step)

Follow steps 1 through 7 in exact order. Do not skip any step.

## Step 1: Check Your Windows Version

1. Press the **Windows key** on your keyboard.
2. Type **"About your PC"** and press Enter.
3. Look at **"Edition"** — it must say **Windows 10** or **Windows 11**.
4. Look at **"System type"** — it must say **64-bit**.

> If you have Windows 7/8 or 32-bit, this workshop will not work on your machine. Please use a university computer.

## Step 2: Install Docker Desktop

1. Open your web browser (Chrome or Edge).
2. Go to: **https://www.docker.com/products/docker-desktop/**
3. Click the blue button **"Download for Windows"**.
4. A file called `Docker Desktop Installer.exe` will download.
5. Double-click `Docker Desktop Installer.exe` to start installation.
6. Accept all defaults. Click **OK** and **Install**.
7. **If it asks about WSL2**: Click **Yes**. This is required.
   - If you see a message *"WSL 2 installation is incomplete"*:
     - Click the **Start menu**, type **PowerShell**, right-click **Windows PowerShell**, click **Run as Administrator**.
     - Type this command and press Enter:
       ```
       wsl --update
       ```
     - Close PowerShell.
     - Restart Docker Desktop.
8. When installation is done, click **Close and restart** (your computer will reboot).
9. After reboot, Docker Desktop should open automatically. If not, click the **Start menu**, type **Docker Desktop**, and open it.
10. Wait until the whale icon in the bottom-right system tray **stops animating**. This means Docker is ready.

> **Important:** Docker Desktop must be running (whale icon visible) every time you use the workshop.

## Step 3: Download the Workshop Files

The workshop notebooks and files are on GitHub. You need to download them to your computer.

1. Open your web browser.
2. Go to: **https://github.com/Indranil2020/DFT_Workshop_QE**
3. Click the green button **"<> Code"**.
4. Click **"Download ZIP"**.
5. A file called `DFT_Workshop_QE-main.zip` will download (usually to your Downloads folder).
6. Go to your **Downloads** folder.
7. Right-click `DFT_Workshop_QE-main.zip` → click **"Extract All..."** → click **"Extract"**.
8. You will now have a folder called `DFT_Workshop_QE-main`. Inside it is a folder called `qe_workshop_complete`.
9. **Move** the `qe_workshop_complete` folder to your **Desktop** for easy access.

> You now have all the workshop files on your computer at: `Desktop\qe_workshop_complete\`

## Step 4: Download the Docker Image

This downloads the pre-built environment (~2-3 GB). Do this on a good internet connection.

1. Click the **Start menu**, type **PowerShell**, and open **Windows PowerShell**.
2. Type this command and press Enter:
   ```
   docker pull indranilm/qe-workshop:latest
   ```
3. Wait for it to finish. You will see progress bars and then a message like `Status: Downloaded newer image`.
4. Verify it worked by typing:
   ```
   docker images
   ```
   You should see a line with `indranilm/qe-workshop` in the output.

## Step 5: Start the Workshop

**Option A — Double-click the launcher (easiest):**

1. Open the `qe_workshop_complete` folder on your Desktop.
2. Find the file called **`start_workshop.bat`**.
3. **Double-click** it.
4. A black terminal window will open. **Do NOT close it.** It will show messages — wait until you see something like:
   ```
   Jupyter Server is running at: http://localhost:8888
   ```
5. Go to Step 6.

**Option B — Run the command manually (if Option A doesn't work):**

1. Open **Windows PowerShell** (Start menu → type PowerShell).
2. Navigate to your workshop folder. Type:
   ```
   cd $HOME\Desktop\qe_workshop_complete
   ```
3. Run this command (copy-paste the whole thing):
   ```
   docker run -it --rm -p 8888:8888 -v "${PWD}:/workspace" -e OMPI_ALLOW_RUN_AS_ROOT=1 -e OMPI_ALLOW_RUN_AS_ROOT_CONFIRM=1 indranilm/qe-workshop:latest
   ```
4. Wait until you see `Jupyter Server is running at: http://localhost:8888`.
5. **Do NOT close** the PowerShell window.

## Step 6: Open the Workshop in Your Browser

1. Open your web browser (Chrome, Edge, or Firefox).
2. In the address bar, type exactly:
   ```
   http://localhost:8888
   ```
3. Press Enter.
4. You will see **JupyterLab** — a web-based code editor. It shows the files on the left side.

## Step 7: Navigate to the Notebooks and Start

1. In JupyterLab, look at the **left panel** (file browser).
2. Double-click the folder **`notebooks_enhanced`**.
3. You will see the workshop notebooks listed:
   - `00_Workshop_Overview_and_Philosophy.ipynb`
   - `01_Database_Search_and_Structure_Discovery.ipynb`
   - `02_Structure_Validation_and_Preparation.ipynb`
   - ... and so on up to `10_Complete_Research_Workflow.ipynb`
4. **Double-click** any notebook to open it.
5. Start with **`00_Workshop_Overview_and_Philosophy.ipynb`** or follow the instructor.
6. To run a cell: click on it, then press **Shift + Enter**.

## Stopping the Workshop (Windows)

1. Save your work in JupyterLab: click **File → Save All**.
2. Close the browser tab.
3. Go to the black terminal window (or PowerShell).
4. Press **Ctrl + C**.
5. The Docker container will stop. Your files are safe on your Desktop.

## Restarting the Workshop (Windows)

Just repeat Step 5 — double-click `start_workshop.bat` again, then open `http://localhost:8888` in your browser. All your files are still there.

---

---

# macOS (Step-by-Step)

Follow steps 1 through 7 in exact order. Do not skip any step.

## Step 1: Check Your Mac

1. Click the **Apple menu** (top-left corner) → **About This Mac**.
2. Note the chip:
   - **Apple M1, M2, M3, or M4** → you have an Apple Silicon Mac.
   - **Intel Core i5, i7, i9** → you have an Intel Mac.
3. Note the macOS version — you need macOS **10.15 (Catalina)** or newer.

## Step 2: Install Docker Desktop

1. Open Safari or Chrome.
2. Go to: **https://www.docker.com/products/docker-desktop/**
3. Click the download button:
   - If you have an **Apple M1/M2/M3/M4**: click **"Mac with Apple chip"**.
   - If you have an **Intel Mac**: click **"Mac with Intel chip"**.
4. A `.dmg` file will download.
5. Double-click the `.dmg` file.
6. **Drag** the Docker icon into the Applications folder (as shown).
7. Open **Finder → Applications**, then double-click **Docker**.
8. macOS will ask for permission — click **Open** and enter your password if asked.
9. Docker will start. Look at the **menu bar** at the top of the screen — you will see a **whale icon**.
10. Wait until the whale icon **stops animating**. This means Docker is ready.

> **Important:** Docker must be running (whale icon visible in menu bar) every time you use the workshop.

## Step 3: Download the Workshop Files

1. Open your web browser.
2. Go to: **https://github.com/Indranil2020/DFT_Workshop_QE**
3. Click the green button **"<> Code"**.
4. Click **"Download ZIP"**.
5. The file `DFT_Workshop_QE-main.zip` will download to your **Downloads** folder.
6. Double-click the ZIP file to unzip it. A folder `DFT_Workshop_QE-main` will appear.
7. Inside it, find the folder `qe_workshop_complete`.
8. **Drag** `qe_workshop_complete` to your **Desktop**.

> You now have all workshop files at: `~/Desktop/qe_workshop_complete/`

## Step 4: Download the Docker Image

1. Open **Terminal**: press **Cmd + Space**, type **Terminal**, press Enter.
2. Type this command and press Enter:
   ```
   docker pull indranilm/qe-workshop:latest
   ```
3. Wait for it to finish (2-3 GB download).
4. Verify it worked:
   ```
   docker images
   ```
   You should see `indranilm/qe-workshop` listed.

## Step 5: Start the Workshop

**Option A — Run the launcher script (easiest):**

1. Open **Terminal** (Cmd + Space → type Terminal → press Enter).
2. Type this command and press Enter:
   ```
   bash ~/Desktop/qe_workshop_complete/start_workshop.sh
   ```
3. Wait until you see `Jupyter Server is running at: http://localhost:8888`.
4. **Do NOT close** the Terminal window.
5. Go to Step 6.

**Option B — Run the command manually (if Option A doesn't work):**

1. Open **Terminal**.
2. Type:
   ```
   cd ~/Desktop/qe_workshop_complete
   ```
3. Then type (copy-paste the whole thing):
   ```
   docker run -it --rm -p 8888:8888 -v "$(pwd)":/workspace -e OMPI_ALLOW_RUN_AS_ROOT=1 -e OMPI_ALLOW_RUN_AS_ROOT_CONFIRM=1 indranilm/qe-workshop:latest
   ```
4. Wait until you see `Jupyter Server is running at: http://localhost:8888`.
5. **Do NOT close** the Terminal window.

## Step 6: Open the Workshop in Your Browser

1. Open **Safari**, **Chrome**, or **Firefox**.
2. In the address bar, type exactly:
   ```
   http://localhost:8888
   ```
3. Press Enter.
4. You will see **JupyterLab**.

## Step 7: Navigate to the Notebooks and Start

1. In JupyterLab, look at the **left panel** (file browser).
2. Double-click the folder **`notebooks_enhanced`**.
3. You will see the notebooks listed (`00_...`, `01_...`, etc.).
4. **Double-click** any notebook to open it.
5. Start with **`00_Workshop_Overview_and_Philosophy.ipynb`** or follow the instructor.
6. To run a cell: click on it, then press **Shift + Enter**.

## Stopping the Workshop (macOS)

1. Save your work: **File → Save All** in JupyterLab.
2. Close the browser tab.
3. Go to the Terminal window.
4. Press **Ctrl + C** (not Cmd+C — use the Ctrl key).
5. Your files are safe on your Desktop.

## Restarting the Workshop (macOS)

Repeat Step 5. All your files are still there.

---

---

# LINUX (Step-by-Step)

Follow steps 1 through 7 in exact order. Do not skip any step.

These instructions are for **Ubuntu 20.04, 22.04, or 24.04**. For other distributions (Fedora, Arch, etc.), adapt the package manager commands accordingly.

## Step 1: Check Your System

1. Open a terminal (Ctrl + Alt + T).
2. Check your Ubuntu version:
   ```
   lsb_release -a
   ```
3. Check your architecture (must be 64-bit):
   ```
   uname -m
   ```
   You should see `x86_64` or `aarch64`.

## Step 2: Install Docker

1. Open a terminal (Ctrl + Alt + T).
2. Run these commands **one by one** (copy-paste each line separately):

   ```
   sudo apt-get update
   ```

   ```
   sudo apt-get install -y ca-certificates curl gnupg
   ```

   ```
   sudo install -m 0755 -d /etc/apt/keyrings
   ```

   ```
   curl -fsSL https://download.docker.com/linux/ubuntu/gpg | sudo gpg --dearmor -o /etc/apt/keyrings/docker.gpg
   ```

   ```
   sudo chmod a+r /etc/apt/keyrings/docker.gpg
   ```

   ```
   echo "deb [arch=$(dpkg --print-architecture) signed-by=/etc/apt/keyrings/docker.gpg] https://download.docker.com/linux/ubuntu $(lsb_release -cs) stable" | sudo tee /etc/apt/sources.list.d/docker.list > /dev/null
   ```

   ```
   sudo apt-get update
   ```

   ```
   sudo apt-get install -y docker-ce docker-ce-cli containerd.io docker-compose-plugin
   ```

3. Allow your user to run Docker without `sudo`:
   ```
   sudo usermod -aG docker $USER
   ```

4. **LOG OUT and LOG BACK IN** (or reboot your computer). This step is required.

5. After logging back in, open a terminal and verify Docker works:
   ```
   docker run hello-world
   ```
   You should see `Hello from Docker!` in the output.

## Step 3: Download the Workshop Files

**Option A — Using git (recommended):**

1. Open a terminal.
2. Install git if not already installed:
   ```
   sudo apt-get install -y git
   ```
3. Clone the repository:
   ```
   git clone https://github.com/Indranil2020/DFT_Workshop_QE.git ~/Desktop/DFT_Workshop_QE
   ```
4. The workshop files are now at: `~/Desktop/DFT_Workshop_QE/qe_workshop_complete/`

**Option B — Download ZIP (if you don't have git):**

1. Open your web browser.
2. Go to: **https://github.com/Indranil2020/DFT_Workshop_QE**
3. Click the green **"<> Code"** button → click **"Download ZIP"**.
4. Extract the ZIP:
   ```
   cd ~/Downloads
   unzip DFT_Workshop_QE-main.zip
   mv DFT_Workshop_QE-main ~/Desktop/DFT_Workshop_QE
   ```
5. The workshop files are now at: `~/Desktop/DFT_Workshop_QE/qe_workshop_complete/`

## Step 4: Download the Docker Image

1. Open a terminal.
2. Run:
   ```
   docker pull indranilm/qe-workshop:latest
   ```
3. Wait for the download to finish (2-3 GB).
4. Verify:
   ```
   docker images
   ```
   You should see `indranilm/qe-workshop` listed.

## Step 5: Start the Workshop

**Option A — Run the launcher script:**

1. Open a terminal.
2. Run:
   ```
   bash ~/Desktop/DFT_Workshop_QE/qe_workshop_complete/start_workshop.sh
   ```
3. Wait until you see `Jupyter Server is running at: http://localhost:8888`.
4. **Do NOT close** the terminal.
5. Go to Step 6.

**Option B — Run the command manually:**

1. Open a terminal.
2. Navigate to the workshop folder:
   ```
   cd ~/Desktop/DFT_Workshop_QE/qe_workshop_complete
   ```
3. Run:
   ```
   docker run -it --rm -p 8888:8888 -v "$(pwd)":/workspace -e OMPI_ALLOW_RUN_AS_ROOT=1 -e OMPI_ALLOW_RUN_AS_ROOT_CONFIRM=1 indranilm/qe-workshop:latest
   ```
4. Wait until you see `Jupyter Server is running at: http://localhost:8888`.
5. **Do NOT close** the terminal.

## Step 6: Open the Workshop in Your Browser

1. Open **Firefox** or **Chrome**.
2. In the address bar, type exactly:
   ```
   http://localhost:8888
   ```
3. Press Enter.
4. You will see **JupyterLab**.

## Step 7: Navigate to the Notebooks and Start

1. In JupyterLab, look at the **left panel** (file browser).
2. Double-click the folder **`notebooks_enhanced`**.
3. You will see notebooks listed (`00_...`, `01_...`, etc.).
4. **Double-click** any notebook to open it.
5. Start with **`00_Workshop_Overview_and_Philosophy.ipynb`** or follow the instructor.
6. To run a cell: click on it, then press **Shift + Enter**.

## Stopping the Workshop (Linux)

1. Save your work: **File → Save All** in JupyterLab.
2. Close the browser tab.
3. Go to the terminal.
4. Press **Ctrl + C**.
5. Your files are safe in the folder on your Desktop.

## Restarting the Workshop (Linux)

Repeat Step 5. All your files are still there.

---

---

# Troubleshooting (All Platforms)

## "Docker is not recognized" / "docker: command not found"

| Platform | Fix |
|----------|-----|
| Windows | Docker Desktop is not running. Click Start menu → Docker Desktop → wait for whale icon. |
| macOS | Open Docker from Applications → wait for whale icon in menu bar. |
| Linux | Run `sudo systemctl start docker`. If not installed, go back to Step 2. |

## "Couldn't connect to Docker daemon" / "Is Docker running?"

Docker is installed but not started. Open Docker Desktop (Windows/macOS) or run `sudo systemctl start docker` (Linux).

## The browser shows "This site can't be reached" at localhost:8888

- Wait 10-20 seconds after starting the container. Jupyter takes time to initialize.
- Make sure you typed **http://** (not https://).
- Make sure the terminal still shows the Docker container running.
- Make sure you typed **localhost:8888** (not localhost:888 or any other number).

## "Port 8888 is already in use"

Another program is using port 8888. Either:
- Stop the other program, or
- Use a different port by changing `-p 8888:8888` to `-p 9999:8888`, then open `http://localhost:9999` instead.

## QE calculations fail with "permission denied" or MPI errors

The MPI environment variables are missing. Make sure you used the `start_workshop.bat` / `start_workshop.sh` script, or included these flags in your `docker run` command:
```
-e OMPI_ALLOW_RUN_AS_ROOT=1 -e OMPI_ALLOW_RUN_AS_ROOT_CONFIRM=1
```

## Calculations are very slow

- **Windows/macOS**: Open Docker Desktop → Settings → Resources → increase CPU to **4+ cores** and Memory to **4+ GB**.
- Close other heavy applications (Chrome tabs, video calls, etc.).

## "No space left on device"

Docker images take disk space. Free space with:
```
docker system prune -a
```
**Warning:** This deletes ALL unused Docker images.

## Windows: "WSL 2 installation is incomplete"

Open PowerShell as Administrator and run:
```
wsl --update
wsl --set-default-version 2
```
Then restart Docker Desktop.

## I accidentally closed the terminal / Docker stopped

Your files are safe! They are stored on your computer in the `qe_workshop_complete` folder. Just repeat Step 5 for your OS to start again.

---

# Install VESTA (Optional — for 3D Crystal Visualization)

VESTA lets you view crystal structures and charge densities in 3D.

1. Go to: **https://jp-minerals.org/vesta/en/download.html**
2. Download the version for your OS.
3. Install it.
4. To use: save a `.xsf` or `.cube` file from JupyterLab, then open it in VESTA.

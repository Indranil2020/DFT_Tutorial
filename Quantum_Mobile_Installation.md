Here’s a **Windows-only guide** to install **Quantum Mobile 24.04.0** with maximum CPU/RAM allocation and seamless file transfer between your local system and the VM:

---

### **Step 1: Install VirtualBox (Windows)**
1. **Download VirtualBox 7.1.6**:  
   - Get the installer from [this link](https://download.virtualbox.org/virtualbox/7.1.6/VirtualBox-7.1.6-167084-Win.exe).  
2. **Run the Installer**:  
   - Double-click the `.exe` file.  
   - Follow the prompts (use default settings).  
   - Reboot your PC if required.

---

### **Step 2: Download Quantum Mobile 24.04.0 VM**
1. **Get the VM Image**:  
   - Visit [Quantum Mobile 24.04.0](https://quantum-mobile.readthedocs.io/en/latest/releases/versions/24.04.0.html).  
   - Under **Download**, click the **VirtualBox image** link (`quantum-mobile-24.04.0.ova`).  

---

### **Step 3: Import the VM with Max CPU/RAM Allocation**
1. **Import the VM**:  
   - Open VirtualBox → **File → Import Appliance**.  
   - Select the `.ova` file → **Next**.  
   - **Before clicking "Import"**:  
     - Click the **⚙️ Settings** icon.  
     - **System → Motherboard**:  
       - Allocate **Maximum RAM** (leave at least 2 GB for your host OS).  
     - **System → Processor**:  
       - Set CPU cores to **maximum available** (e.g., 4/4 cores).  
   - Click **Import** (takes 5–10 minutes).  

---

### **Step 4: Start the VM**
1. **Launch Quantum Mobile**:  
   - Select the VM → Click **Start**.  
2. **Log In**:  
   - **Username**: `max`  
   - **Password**: `laboratory`  

---

### **Step 5: Set Up File Transfer Between Host and VM**
#### **Method 1: Shared Folders (Recommended)**  
1. **Shut Down the VM** (if running).  
2. **Configure Shared Folders**:  
   - In VirtualBox: Select the VM → **Settings → Shared Folders**.  
   - Click **Add Folder** (📁 icon):  
     - **Folder Path**: Choose a host folder (e.g., `C:\Users\YourName\Desktop`).  
     - **Folder Name**: Assign a name (e.g., `desktop_shared`).  
     - Check **Auto-mount** and **Make Permanent**.  
3. **Install VirtualBox Guest Additions** (inside the VM):  
   - Start the VM.  
   - Open a terminal in the VM and run:  
     ```bash
     sudo apt update && sudo apt install -y virtualbox-guest-utils
     ```  
   - Reboot the VM:  
     ```bash
     sudo reboot
     ```  
4. **Access Shared Folders**:  
   - After reboot, shared folders appear at `/media/sf_[folder_name]` (e.g., `/media/sf_desktop_shared`).  
   - To access files:  
     ```bash
     # Navigate to the shared folder
     cd /media/sf_desktop_shared
     ```  

#### **Method 2: Drag-and-Drop**  
1. Enable **Drag-and-Drop** in VM settings:  
   - Shut down the VM.  
   - Go to **Settings → General → Advanced → Shared Clipboard & Drag'n'Drop → Bidirectional**.  
2. **Copy files** by dragging them directly between your Windows desktop and the VM.

---

### **Post-Installation Tips**
- **Maximize Performance**:  
  - Close background apps on your host PC to free up resources.  
- **Troubleshooting Shared Folders**:  
  - If `/media/sf_*` isn’t visible, run:  
    ```bash
    sudo usermod -aG vboxsf max
    sudo reboot
    ```  
- **Backup Important Files**: Use shared folders to copy critical data to your host machine.  

---


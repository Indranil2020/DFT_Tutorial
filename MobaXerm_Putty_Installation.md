Step-by-step guide to connect to a **remote machine** using **MobaXterm** or **PuTTY** on Windows, including file transfers and running commands (e.g., Quantum ESPRESSO):

---

### **Option 1: MobaXterm (Recommended for Integrated Tools)**
#### **Step 1: Install MobaXterm**
1. Download the **Portable Edition** (free) from [https://mobaxterm.mobatek.net](https://mobaxterm.mobatek.net).  
2. Extract the ZIP file and run `MobaXterm.exe`.

---

#### **Step 2: Connect to the Remote Machine**
1. **Start a New Session**:  
   - Click **Session → SSH**.  
   - Enter:  
     - **Remote host**: `your_remote_server_ip_or_hostname`  
     - **Username**: Your remote server username.  
     - **Port**: `22` (default for SSH).  
   - Click **OK**.  
2. **Authenticate**:  
   - Enter your password when prompted.  
   - (Optional) Use SSH keys (see **SSH Key Setup** below).

---

#### **Step 3: Transfer Files to/from Remote Machine**
1. **Integrated File Browser**:  
   - After connecting, MobaXterm shows the remote file system on the left pane.  
   - Drag-and-drop files between your local Windows system and the remote server.  
2. **SCP/SFTP Commands**:  
   Use the terminal to run:  
   ```bash
   # Upload to remote
   scp local_file.txt username@remote_host:/path/to/destination

   # Download from remote
   scp username@remote_host:/path/to/remote_file.txt .
   ```

---


### **Option 2: PuTTY (Lightweight SSH Client)**
#### **Step 1: Install PuTTY**
1. Download from [https://www.putty.org](https://www.putty.org).  
2. Install using the `.msi` installer (default settings).  

---

#### **Step 2: Connect to the Remote Machine**
1. **Configure PuTTY**:  
   - Open PuTTY.  
   - Under **Session**:  
     - **Host Name**: `username@remote_host`  
     - **Port**: `22`  
     - **Connection Type**: `SSH`.  
   - Save the session for future use (type a name under **Saved Sessions** → **Save**).  
2. **Authenticate**:  
   - Click **Open** and enter your password.  

---

#### **Step 3: Transfer Files with PSCP/WinSCP**
1. **Using PSCP (Command Line)**:  
   - Download `pscp.exe` from [PuTTY’s website](https://www.chiark.greenend.org.uk/~sgtatham/putty/latest.html).  
   - Open **Command Prompt** and run:  
     ```cmd
     # Upload to remote
     pscp C:\local_file.txt username@remote_host:/remote/path

     # Download from remote
     pscp username@remote_host:/remote/path/file.txt C:\Downloads
     ```  
2. **Using WinSCP (GUI)**:  
   - Install [WinSCP](https://winscp.net).  
   - Connect via SFTP/SCP and drag files between local/remote systems.  

---

### **SSH Key Setup (Passwordless Login)**
1. **Generate Keys**:  
   In MobaXterm/PuTTY:  
   ```bash
   ssh-keygen -t rsa   # Save to ~/.ssh/id_rsa (no passphrase if desired)
   ```  
2. **Copy Public Key to Remote**:  
   ```bash
   ssh-copy-id username@remote_host
   ```  
3. **Test Login**:  
   ```bash
   ssh username@remote_host   # Should connect without a password
   ```

---

### **Troubleshooting**
1. **Connection Refused**:  
   - Verify the remote server’s IP/port and SSH service status (`sudo systemctl status sshd`).  
2. **Permission Denied**:  
   - Check SSH key permissions:  
     ```bash
     chmod 600 ~/.ssh/id_rsa
     ```  
3. **File Transfer Errors**:  
   - Use absolute paths (e.g., `/home/username/data` instead of `~/data`).  

---

### **Notes**
- **MobaXterm Advantages**: Built-in SFTP, X11 forwarding for GUIs, and tabbed sessions.  
- **PuTTY + WinSCP**: Lightweight but requires separate tools for file transfers.  
- **Remote QE Execution**: Ensure QE is installed on the remote machine and MPI is configured.  

Step-by-step guide to install and run **BURAI** (version 1.3.1) on **Windows** and **Linux**, including Java setup:

---

### **Prerequisite: Install Java**
BURAI requires Java. Follow these steps first:

#### **Windows**
1. **Download Java**
   - Go to [Java’s official download page](https://java.com/download/).
   - Click **Agree and Start Free Download** to get the installer.
2. **Install Java**
   - Run the downloaded `.exe` file (e.g., `jre-8uXXX-windows-x64.exe`).
   - Follow the installer prompts (use default settings).
3. **Verify Installation**
   - Open **Command Prompt** and run:
     ```cmd
     java -version
     ```
   - Ensure it prints Java version details (e.g., `java version "1.8.0_XXX"`).

#### **Linux**
1. **Install OpenJDK**
   - Open a terminal and run:
     ```bash
     sudo apt update && sudo apt install openjdk-11-jre  # For Debian/Ubuntu
     # OR
     sudo dnf install java-11-openjdk                   # For Fedora/CentOS
     ```
2. **Verify Installation**
   ```bash
   java -version
   ```
   - Confirm it shows a version like `openjdk 11.0.XX`.

---

### **Install and Run BURAI**

#### **Windows**
1. **Download BURAI**
   - Visit [BURAI Releases](https://github.com/BURAI-team/burai/releases/tag/ver.1.3.1).
   - Download `BURAI-1.3.1.jar` (the executable JAR file).
2. **Create a Dedicated Folder**
   - Create a folder (e.g., `C:\BURAI`) and move `BURAI-1.3.1.jar` there.
3. **Run BURAI**
   - Double-click the JAR file. If Java is installed, it should launch.
   - **If it doesn’t open**:
     - Right-click the JAR file → **Open With** → **Java(TM) Platform SE binary**.
4. **Create a Desktop Shortcut (Optional)**
   - Right-click the JAR file → **Send to** → **Desktop (create shortcut)**.
   - Rename the shortcut to `BURAI`.

#### **Linux**
1. **Download BURAI**
   - Open a terminal and run:
     ```bash
     wget https://github.com/BURAI-team/burai/releases/download/ver.1.3.1/BURAI-1.3.1.jar
     ```
   - Or download via browser and move it to a directory like `~/BURAI`.
2. **Run BURAI**
   - Open a terminal, navigate to the JAR’s location, and run:
     ```bash
     java -jar BURAI-1.3.1.jar
     ```
3. **Create a Desktop Shortcut (Optional)**
   - Create a `.desktop` file:
     ```bash
     nano ~/.local/share/applications/burai.desktop
     ```
   - Add:
     ```ini
     [Desktop Entry]
     Name=BURAI
     Exec=java -jar /path/to/BURAI-1.3.1.jar
     Icon=/path/to/any/icon.png  # Optional: Download an icon
     Terminal=false
     Type=Application
     Categories=Science;
     ```
   - Save and make it executable:
     ```bash
     chmod +x ~/.local/share/applications/burai.desktop
     ```

---

### **Troubleshooting**
1. **Java Not Detected**:
   - Reinstall Java and ensure the `JAVA_HOME` environment variable is set.
2. **JAR File Won’t Open**:
   - Run it via terminal: `java -jar BURAI-1.3.1.jar` to see error logs.
3. **Linux Dependencies**:
   - Install missing libraries (e.g., GTK) using your package manager.

---


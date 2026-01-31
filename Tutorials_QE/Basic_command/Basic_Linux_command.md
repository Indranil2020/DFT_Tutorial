Here's a list of **basic Linux commands** categorized by their purpose:

---

### **Navigation & Directory Management**
- `pwd` - Print the current working directory.  
- `ls` - List directory contents (use `ls -a` to show hidden files).  
- `cd [directory]` - Change directory (e.g., `cd /home` or `cd ..` to go back).  
- `mkdir [directory]` - Create a new directory.  
- `rmdir [directory]` - Remove an empty directory.  

---

### **File Operations**
- `touch [file]` - Create an empty file or update file timestamp.  
- `cp [source] [destination]` - Copy files/directories.  
- `mv [source] [destination]` - Move or rename files/directories.  
- `rm [file]` - Remove a file (use `rm -r` for directories).  
- `cat [file]` - Display file content.  
- `nano [file]` / `vim [file]` - Edit a file using a text editor.  

---

### **File Permissions**
- `chmod [permissions] [file]` - Change file permissions (e.g., `chmod 755 script.sh`).  
- `chown [user]:[group] [file]` - Change file ownership.  
- `sudo [command]` - Run a command with superuser privileges.  

---

### **System Information**
- `uname -a` - Display system/kernel information.  
- `df -h` - Show disk space usage.  
- `free -h` - Check memory usage.  
- `top` / `htop` - Monitor active processes and resource usage.  
- `uptime` - View system uptime and load averages.  

---

### **Networking**
- `ping [host]` - Test network connectivity to a host.  
- `ifconfig` / `ip addr` - Display network interface information.  
- `wget [URL]` - Download files from the internet.  
- `curl [URL]` - Transfer data from/to a server.  
- `ssh [user@host]` - Connect to a remote server securely.  
- `scp [file] [user@host:path]` - Securely copy files over SSH.  

---

### **Process Management**
- `ps` - List active processes (use `ps aux` for detailed info).  
- `kill [PID]` - Terminate a process by its ID.  
- `killall [process-name]` - Terminate all processes by name.  
- `bg` / `fg` - Move a job to the background/foreground.  

---

### **Searching**
- `grep [pattern] [file]` - Search for text patterns in files.  
- `find [path] -name [filename]` - Search for files/directories.  
- `locate [file]` - Find files using a prebuilt database (faster than `find`).  

---

### **Compression/Archiving**
- `tar -czvf [archive.tar.gz] [files]` - Create a compressed tar archive.  
- `tar -xzvf [archive.tar.gz]` - Extract a tar archive.  
- `gzip [file]` / `gunzip [file.gz]` - Compress or decompress files.  

---

### **Miscellaneous**
- `echo [text]` - Print text to the terminal.  
- `man [command]` - Display the manual for a command.  
- `history` - View command history.  
- `clear` - Clear the terminal screen.  
- `exit` - Close the terminal session.  

---

**Tip:** Use `[command] --help` or `man [command]` to learn more about any command!

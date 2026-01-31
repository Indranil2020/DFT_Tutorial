Here’s a list of **basic `vi` (or `vim`) commands** to help you navigate and edit files in the `vi` text editor, a powerful but sometimes intimidating tool for beginners:

---

### **Starting and Exiting**
- Open a file:  
  ```bash
  vi filename
  ```
- Save and exit:  
  ```vim
  :wq  # Write (save) and quit
  ```
- Quit without saving:  
  ```vim
  :q!  # Force quit (discard changes)
  ```
- Save without exiting:  
  ```vim
  :w   # Write (save) changes
  ```

---

### **Modes in `vi`**
1. **Command Mode** (default mode when you open `vi`):  
   - Navigate, delete, copy, paste, search, etc.  
   - Press `Esc` to return to Command Mode from other modes.  

2. **Insert Mode** (to edit text):  
   - Press `i` to start inserting text at the cursor.  
   - Other insert commands:  
     - `a` – Insert **after** the cursor.  
     - `o` – Insert a new line **below** the current line.  
     - `O` – Insert a new line **above** the current line.  

---

### **Navigation (Command Mode)**
- Move cursor:  
  ```vim
  h (left), j (down), k (up), l (right)  
  # Or use arrow keys
  ```
- Jump to line:  
  ```vim
  :10  # Jump to line 10
  ```
- Move to start/end of line:  
  ```vim
  0    # Start of line
  $    # End of line
  ```
- Move by words:  
  ```vim
  w    # Next word
  b    # Previous word
  ```
- Scroll:  
  ```vim
  Ctrl + f  # Page down
  Ctrl + b  # Page up
  ```

---

### **Editing (Command Mode)**
- Delete:  
  ```vim
  x     # Delete character under cursor
  dd    # Delete entire line
  dw    # Delete word
  ```
- Undo/Redo:  
  ```vim
  u     # Undo last change
  Ctrl + r  # Redo
  ```
- Copy/Paste:  
  ```vim
  yy    # Copy (yank) a line
  p     # Paste after the cursor
  P     # Paste before the cursor
  ```
- Replace text:  
  ```vim
  r     # Replace character under cursor
  R     # Enter replace mode (overwrite text)
  ```

---

### **Search and Replace**
- Search forward:  
  ```vim
  /pattern  # Search for "pattern" (press `n` for next match)
  ```
- Search backward:  
  ```vim
  ?pattern  # Search backward
  ```
- Replace in entire file:  
  ```vim
  :%s/old/new/g  # Replace all "old" with "new" globally
  ```

---

### **Visual Mode**
- Enter Visual Mode (to select text):  
  ```vim
  v     # Character-wise selection
  V     # Line-wise selection
  ```
- After selecting, use `y` to yank (copy) or `d` to delete.

---

### **Helpful Tips**
- Show line numbers:  
  ```vim
  :set number  # Hide with `:set nonumber`
  ```
- Split screen:  
  ```vim
  :split  # Horizontal split
  :vsplit # Vertical split
  ```
- Reload a file (discard changes):  
  ```vim
  :e!  # Re-open the file
  ```

---

**Practice Tip:** Open a test file (e.g., `vi test.txt`) and experiment with these commands. Remember, `vi` mastery takes time—start with basic navigation and editing!  

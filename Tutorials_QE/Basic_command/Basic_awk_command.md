Here’s a **basic guide to `awk`** with practical examples. `awk` is a powerful text-processing tool for parsing and manipulating structured data (like columns in files):

---

### **1. Basic Syntax**
```bash
awk 'pattern { action }' [file]
```
- **Pattern**: Optional condition (e.g., `NR > 1` for skipping headers).
- **Action**: What to do when the pattern matches (e.g., `print $1`).

---

### **2. Basic Examples**

#### **Print All Lines**
```bash
awk '{print}' file.txt    # Print all lines
```

#### **Print Specific Columns**
```bash
awk '{print $1}' file.txt       # Print first column
awk '{print $1, $3}' file.txt   # Print first and third columns
awk '{print $NF}' file.txt      # Print last column (NF = Number of Fields)
```

#### **Print Line Numbers**
```bash
awk '{print NR, $0}' file.txt   # NR = current line number, $0 = entire line
```

---

### **3. Filtering Data**

#### **Print Lines Matching a Condition**
```bash
awk '$3 > 50 {print}' file.txt         # Print lines where column 3 > 50
awk '/error/ {print}' file.txt         # Print lines containing "error"
awk '$1 ~ /^A/ {print}' file.txt       # Print lines where column 1 starts with "A"
```

#### **Combine Conditions**
```bash
awk '$2 == "FAIL" && $3 > 10 {print}' file.txt
```

---

### **4. Built-in Variables**
- **`NR`**: Current line number.
- **`NF`**: Number of fields (columns) in the current line.
- **`FS`**: Field separator (default: whitespace).
- **`OFS`**: Output field separator (default: space).

#### **Examples**
```bash
awk '{print NF}' file.txt        # Print number of columns per line
awk -F',' '{print $2}' file.csv  # Use comma as field separator
awk 'BEGIN {FS=":"} {print $1}' /etc/passwd   # Split by colon
```

---

### **5. BEGIN and END Blocks**
Run actions **before** or **after** processing lines:
```bash
# Add a header and footer
awk 'BEGIN {print "Start"} {print} END {print "End"}' file.txt

# Calculate total of column 1
awk '{sum += $1} END {print sum}' file.txt
```

---

### **6. Formatting Output with `printf`**
```bash
awk '{printf "Name: %-10s Score: %d\n", $1, $2}' file.txt
# %-10s = left-aligned string (10 characters), %d = integer
```

---

### **7. String Functions**
```bash
awk '{print toupper($1)}' file.txt           # Convert column 1 to uppercase
awk '{print substr($1, 1, 3)}' file.txt      # Extract first 3 characters of column 1
awk '{print length($0)}' file.txt            # Print line length
```

---

### **8. Conditional Statements (if-else)**
```bash
awk '{if ($2 > 50) print "High"; else print "Low"}' file.txt
```

---

### **9. Using Script Files**
For complex tasks, save commands in a script (e.g., `script.awk`):
```awk
# script.awk
BEGIN {FS=","; OFS=" | "}
NR == 1 {print "Header:", $0; next}
{print NR, $1, $NF}
```
Run it with:
```bash
awk -f script.awk data.csv
```

---

### **10. Practical Use Cases**

#### **Process CSV Files**
```bash
awk -F',' '{print $1, $3}' data.csv
```

#### **Sum Values in a Column**
```bash
awk '{sum += $2} END {print "Total:", sum}' sales.txt
```

#### **Filter Logs**
```bash
awk '/ERROR/ && $4 == "2023-10-01" {print}' app.log
```

#### **Calculate Average**
```bash
awk '{sum += $1; count++} END {print "Average:", sum/count}' numbers.txt
```

---

### **Sample Data File (`data.txt`)**
```plaintext
Name    Age  Score
Alice   25   90
Bob     30   85
Charlie 22   95
```

---

### **Key Notes**
- Columns are **1-indexed** (`$1`, `$2`, etc.).
- `$0` refers to the entire line.
- Use `-F` to specify a custom field separator (e.g., `-F':'` for colon-separated files).
- `awk` works on streams (you can pipe input to it).

---

With these basics, you can slice, filter, and transform text data efficiently! 

Here’s a detailed guide to **gnuplot** with a focus on **multi-column data handling**, customization, and advanced plotting features:

---

### **1. Basic Multi-Column Plotting**
Assume you have a data file `data.txt` with multiple columns:
```plaintext
# X    Y1    Y2    Y3
1    2     5     8
2    3     6     9
3    4     7     10
```

#### **Plot a Single Column**:
```gnuplot
plot "data.txt" using 1:2 with lines  # Plot X (col1) vs Y1 (col2)
```

#### **Plot Multiple Columns**:
```gnuplot
plot "data.txt" using 1:2 with lines, \
     "data.txt" using 1:3 with points, \
     "data.txt" using 1:4 with linespoints
# Plots col1 vs col2 (lines), col1 vs col3 (points), col1 vs col4 (lines+points)
```

#### **Combine Columns in Math Operations**:
```gnuplot
plot "data.txt" using 1:($2+$3) with lines  # Plot X vs (Y1 + Y2)
```

---

### **2. Multi-Column Data from a Single File**
#### **Plot Multiple Columns Against the Same X**:
```gnuplot
plot "data.txt" using 1:2, "" using 1:3, "" using 1:4
# The `""` reuses the previous filename (data.txt)
```

#### **Label Columns with Titles**:
```gnuplot
plot "data.txt" using 1:2 title "Y1", \
     "" using 1:3 title "Y2", \
     "" using 1:4 title "Y3"
```

---

### **3. Plotting Multiple Files**
If you have two files, `data1.txt` and `data2.txt`:
```gnuplot
plot "data1.txt" using 1:2 with lines, \
     "data2.txt" using 1:3 with points
```

---

### **4. Error Bars (Using Multiple Columns)**
For data with errors (e.g., `X Y Y_error`):
```plaintext
# X    Y    Y_err
1    2     0.5
2    3     0.6
3    4     0.7
```
Plot with error bars:
```gnuplot
plot "data.txt" using 1:2:3 with yerrorbars
```

---

### **5. Data Manipulation with `using`**
#### **Column Arithmetic**:
```gnuplot
plot "data.txt" using 1:(log($2))  # Plot log(Y1)
```

#### **Select Columns by Index**:
Columns are referenced as `$1`, `$2`, etc. (1-based indexing):
```gnuplot
plot "data.txt" using ($1):($2/$3)  # Plot X vs (Y1/Y2)
```

---

### **6. Multiplot (Subplots)**
Arrange multiple plots in one figure:
```gnuplot
set multiplot layout 2,1  # 2 rows, 1 column
plot "data.txt" using 1:2  # Top plot
plot "data.txt" using 1:3  # Bottom plot
unset multiplot
```

---

### **7. Customization**
#### **Labels, Titles, and Ranges**:
```gnuplot
set xlabel "X-axis"
set ylabel "Y-axis"
set title "Multi-Column Plot"
set xrange [0:5]
set yrange [0:10]
```

#### **Line Styles and Colors**:
```gnuplot
plot "data.txt" using 1:2 with lines lt rgb "red" lw 2, \
     "" using 1:3 with points pt 7 ps 1.5 lc "blue"
# lt = linetype, lw = linewidth, pt = point type, ps = point size
```

---

### **8. Save Plots to Files**
```gnuplot
set terminal pngcairo enhanced  # High-quality PNG
set output "plot.png"
plot "data.txt" using 1:2 with lines
set terminal wxt  # Switch back to interactive window (if needed)
```

---

### **9. Advanced: Statistical Operations**
Calculate averages or sums:
```gnuplot
stats "data.txt" using 2  # Compute stats for column 2 (Y1)
print STATS_mean  # Print the mean of Y1
```

---

### **Example Workflow**
1. **Data File** (`data.txt`):
   ```plaintext
   # Time   Temperature   Pressure   Humidity
   0       25            1010       60
   1       26            1005       58
   2       27            1000       55
   ```

2. **Gnuplot Commands**:
   ```gnuplot
   set xlabel "Time (hours)"
   set ylabel "Temperature (°C)"
   set y2label "Pressure (hPa)"  # Second y-axis
   set y2tics  # Enable second y-axis
   plot "data.txt" using 1:2 with lines axes x1y1 title "Temperature", \
        "" using 1:3 with lines axes x1y2 title "Pressure"
   ```

---

### **Key Tips**
- Use `help [command]` in gnuplot for documentation (e.g., `help plot`).
- Column indices start at **1** (`$1`, `$2`, etc.).
- Combine columns with math: `($2 + $3)`, `($4/$5)`, etc.
- Use `\` to split commands across lines.

---

With these tools, you can handle **multi-column data**, customize plots, and create publication-quality figures in gnuplot!

**Curve Editor written in PyQt6**

**Description:**

This project is an educational project for 'Curves and Surfaces in Computer Graphics' class held at IIUwr. It is designed to provide hands-on experience in learning about different types of curves commonly used in computer graphics and design. Developed using the PyQt6 framework, this curve editor offers an interactive platform for creating and manipulating various types of curves. While not optimized for speed or extensive usability, the project serves as an insightful introduction to curve manipulation algorithms and their implementation.

The curve editor offers the following built-in curves, each implemented primarily from scratch using Python and NumPy. It has minimal interface allowing to edit the curve inside the program.

**Running the project:**

```
pip install -r requirements.txt
python curve_editor.py
```

**Install standalone version:**

```
pip install -r requirements.txt
pyinstaller -F curve_editor.py
```
The program will be located in */dist* folder.

**Curves available:**

1. **Control Curve.** 

2. **NIFS3 Curve.** 

3. **Bezier Curve - with degree reduction and elevation, split, as well as joining two Bezier curves.** 

4. **Weighted Bezier Curve - should be adjusted.** 

5. **Cubic Bezier Interpolation Curve.** 

6. **Lagrange Curve.** 

7. **B-Spline Curve.** 

8. **B-Spline DeBoor Curve.** 

**Educational Purpose:**

The primary objective of this project is to serve as a learning tool for university students studying computer graphics, computer-aided design, and related fields. By interacting with the curve editor, students can visualize the effects of different control points, interpolation techniques, and curve types. While the application may not prioritize speed or comprehensive user experience, it focuses on demystifying curve mathematics and algorithms through hands-on experimentation.

**Implementation:**

The project is developed using the PyQt6 framework, allowing for a user-friendly graphical interface. Python is used extensively for algorithm implementation, and NumPy is utilized for efficient numerical operations.

**Note:**

This project does not prioritize high performance or advanced usability but aims to provide hands-on experience with creating and manipulating curves.

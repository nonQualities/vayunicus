# Vayunicus: Micro-Climate Pathogen Engine 🌬️🦠

**Vayunicus** is an open-source, high-performance simulation engine (prototype) designed to model airflow and airborne pathogen transport (TB, SARS-CoV-2) in high-density informal settlements.

Standard CFD tools often fail in these "urban canyons" due to complex, jagged geometries that are nearly impossible to mesh.Vayunicus solves this by using the **Lattice Boltzmann Method (LBM)** and a "Bottom-Up" statistical mechanics approach.

$$f_{i}(\vec{x}+\vec{c}_{i}\Delta t,t+\Delta t)=f_{i}(\vec{x},t)-\frac{1}{\tau}[f_{i}(\vec{x},t)-f_{i}^{eq}(\vec{x},t)]$$

Where $\tau$ is the relaxation time linked to air viscosity3333. Pathogens are modeled as a passive scalar distribution $g_i$ that advects with the air but diffuses at its own rate

## 🛠️ Installation & Build
[cite_start]Vayunicus uses **CMake** for a cross-platform build experience[cite: 47].

### Prerequisites
* [cite_start]C++17 compatible compiler (GCC, Clang, MSVC) [cite: 47]
* CMake 3.12+
* Python 3.x (for visualization)

### Build Instructions
```bash
mkdir build && cd build
cmake ..
make
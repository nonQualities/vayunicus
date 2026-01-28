
# Vayunicus: Meso-scopic Urban Micro-Climate Engine

**Vayunicus** is a lightweight, high-performance Lattice Boltzmann Method (LBM) solver designed to simulate airflow and pathogen transport in complex, irregular urban environments—specifically informal settlements and "urban canyons."

Based on the **Open-LBM** architecture, this engine moves beyond traditional CFD by utilizing voxel-based geometry, making it robust against "messy" real-world data (scans/point clouds).

## 🚀 Key Features

* [cite_start]**Lattice Boltzmann Method (D2Q9):** Uses the BGK collision operator for efficient, parallelizable fluid dynamics[cite: 83, 86].
* [cite_start]**Thermal Buoyancy:** Implements the **Boussinesq Approximation** to simulate thermal updrafts caused by heated surfaces (e.g., tin roofs in slums)[cite: 106].
* [cite_start]**Porous Media Modeling:** Simulates airflow attenuation through dense housing or vegetation without requiring high-fidelity meshing[cite: 26, 53].
* [cite_start]**Passive Scalar Transport:** Simultaneous tracking of temperature and pathogen load (future update) alongside momentum[cite: 100].
* [cite_start]**Voxel Geometry:** Directly accepts CSV/Raster maps, avoiding complex mesh generation[cite: 8].

---

## 📂 Project Structure

The project has been restructured to separate the core physics engine from input/output handling and the driver logic.

```text
vayunicus/
├── src/
│   ├── Core/           # Constants and Data Types
│   │   ├── Constants.hpp
│   │   └── Types.hpp
│   ├── Engine/         # The Physics Solver (LBM implementation)
│   │   ├── Solver.hpp
│   │   └── Solver.cpp
│   ├── IO/             # Data Parsing (Config & Geometry)
│   │   ├── DataLoader.hpp
│   │   └── DataLoader.cpp
│   └── main.cpp        # Entry point and orchestration
├── config.txt          # Runtime simulation parameters
├── geometry.csv        # The map layout (0=Fluid, 1=Solid, etc.)
├── CMakeLists.txt      # Build configuration
└── README.md           # This file

```

---

## 🛠️ Build Instructions

### Prerequisites

* **C++ Compiler:** C++17 or later (GCC, Clang, or MSVC).
* **CMake:** Version 3.10 or higher.

### Compiling

1. Create a build directory:
```bash
mkdir build
cd build

```


2. Run CMake and compile:
```bash
cmake ..
make

```


3. The executable `Vayunicus` will be created in the `build` directory.

---

## ⚙️ Usage & Configuration

Run the simulation by passing the configuration file and geometry map:

```bash
./Vayunicus ../config.txt ../geometry.csv

```

### 1. Configuration (`config.txt`)

You can adjust physics and simulation settings at runtime without recompiling.

```ini
# Simulation Domain
width=200
height=80
maxSteps=10000

# Fluid Properties
viscosity=0.02          # Kinematic viscosity of air
inletVelocity=0.05      # Wind speed at the inlet

# Advanced Physics
buoyancyCoef=0.005      # Thermal expansion (Beta) - Controls updraft strength
porousResistance=0.15   # Drag factor (0.0 to 1.0) for porous zones
ambientTemp=300.0       # Base temperature (Kelvin)
sourceTemp=320.0        # Temperature of heated surfaces/sources

# Output
outputName=results.csv

```

### 2. Geometry Input (`geometry.csv`)

The engine reads a grid of integers representing the physical world. This grid can be generated from raster images or point clouds.

**Cell Types:**

* `0`: **Fluid** (Air)
* `1`: **Solid** (Walls, ground - Bounce-back boundary)
* `2`: **Porous** (Dense housing, vegetation - Slows flow)
* `3`: **Inlet** (Wind source)

**Example CSV Content:**

```csv
1,1,1,1,1
1,3,0,2,1
1,3,0,2,1
1,1,1,1,1

```

---

## 🔬 Physics Modules

### Thermal Buoyancy (The "Tin Roof" Effect)

In informal settlements, metal roofs absorb solar radiation, creating localized hot spots. This heats the surrounding air, causing it to rise and altering ventilation patterns.

* **Implementation:** We couple the temperature scalar field to the velocity field using an external force term .

### Porous Media

Modeling every individual brick in a slum is computationally impossible. We approximate dense regions as "Porous Media."

* **Implementation:** Cells marked as type `2` apply a drag force, attenuating velocity by a factor of `(1 - porousResistance)` at every time step.

---

## 📊 Visualization

The simulation outputs a CSV file (e.g., `results.csv`) containing `x, y, u_x, u_y, temp, type` for every cell.

You can visualize this easily using Python:

```python
import pandas as pd
import matplotlib.pyplot as plt

# Load Data
df = pd.read_csv('build/results.csv')

# Plot Velocity Magnitude
plt.figure(figsize=(10, 4))
plt.scatter(df['x'], df['y'], c=df['temp'], cmap='inferno', marker='s', s=15)
plt.colorbar(label='Temperature (K)')
plt.title("Micro-Climate Thermal Map")
plt.axis('equal')
plt.show()

```


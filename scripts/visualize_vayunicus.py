import pandas as pd
import numpy as np
import matplotlib.pyplot as plt

# 1. Load simulation data
df = pd.read_csv('simulation_results.csv')

# 2. Extract grid size
width = df['x'].max() + 1
height = df['y'].max() + 1

# 3. Convert flat table → 2D grids
pathogen_grid = df['pathogen_concentration'].values.reshape(height, width)
velocity_grid = df['velocity_magnitude'].values.reshape(height, width)
wall_grid = df['is_wall'].values.reshape(height, width)

# 4. Plotting
fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(12, 10))

# --- Pathogen Heat Map ---
im1 = ax1.imshow(pathogen_grid, cmap='YlOrRd', origin='lower')
ax1.contour(wall_grid, levels=[0.5], colors='black', linewidths=2)
ax1.set_title("PATHOGEN DISPERSION (Infection Risk Map)", fontsize=14, fontweight='bold')
ax1.set_xlabel("Distance Along Alleyway (Units)")
ax1.set_ylabel("Width of Alleyway (Units)")
plt.colorbar(im1, ax=ax1, label="Concentration")

# --- Wind Field Map ---
im2 = ax2.imshow(velocity_grid, cmap='Blues', origin='lower')
ax2.contour(wall_grid, levels=[0.5], colors='black', linewidths=2)
ax2.set_title("WIND SPEED FIELD (Ventilation Effectiveness)", fontsize=14, fontweight='bold')
ax2.set_xlabel("Distance Along Alleyway (Units)")
ax2.set_ylabel("Width of Alleyway (Units)")
plt.colorbar(im2, ax=ax2, label="Wind Speed")

plt.tight_layout()
plt.show()

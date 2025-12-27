import pandas as pd
import numpy as np
import matplotlib.pyplot as plt

# 1. Load the data
df = pd.read_csv('simulation_results.csv')

# 2. Reshape data into grids for the map
width = df['x'].max() + 1
height = df['y'].max() + 1
pathogen_map = df['density'].values.reshape(height, width)
wind_map = df['velocity_mag'].values.reshape(height, width)
wall_map = df['is_wall'].values.reshape(height, width)

# 3. Create the Visualization
fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(12, 10))

# --- Plot 1: Pathogen Risk ---
im1 = ax1.imshow(pathogen_map, cmap='YlOrRd', origin='lower')
ax1.contour(wall_map, levels=[0.5], colors='black', linewidths=2) # Draw the walls
ax1.set_title("PATHOGEN DISPERSION (Infection Risk Map)", fontsize=14, fontweight='bold')
ax1.set_xlabel("Distance along Alleyway (Meters)")
ax1.set_ylabel("Width of Alleyway (Meters)")
plt.colorbar(im1, ax=ax1, label='Concentration (Darker = Higher Risk)')

# --- Plot 2: Wind Speed ---
im2 = ax2.imshow(wind_map, cmap='Blues', origin='lower')
ax2.contour(wall_map, levels=[0.5], colors='black', linewidths=2)
ax2.set_title("WIND FLOW (Ventilation Effectiveness)", fontsize=14, fontweight='bold')
ax2.set_xlabel("Distance along Alleyway (Meters)")
ax2.set_ylabel("Width of Alleyway (Meters)")
plt.colorbar(im2, ax=ax2, label='Wind Speed (Lighter = Stagnant Air)')

plt.tight_layout()
plt.show()
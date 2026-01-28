import pandas as pd
import matplotlib.pyplot as plt
import numpy as np

def plot_micro_climate(file_path):
    # 1. Load Data
    try:
        df = pd.read_csv(file_path)
    except FileNotFoundError:
        print(f"Error: Could not find {file_path}. Run the simulation first.")
        return

    # 2. Reshape Data into Grids (Logic for LBM structured grids)
    # We pivot the flat CSV data back into 2D matrices
    temp_grid = df.pivot(index='y', columns='x', values='temp').values
    ux_grid = df.pivot(index='y', columns='x', values='u_x').values
    uy_grid = df.pivot(index='y', columns='x', values='u_y').values
    type_grid = df.pivot(index='y', columns='x', values='type').values
    
    # Create coordinate meshes
    X = df.pivot(index='y', columns='x', values='x').values
    Y = df.pivot(index='y', columns='x', values='y').values

    # 3. Setup the Plot
    fig, ax = plt.subplots(figsize=(12, 6))
    
    # --- Layer A: Thermal Heatmap ---
    # We use pcolormesh to show the temperature field
    # vmin/vmax can be adjusted based on your config (e.g., 300K to 320K)
    heatmap = ax.pcolormesh(X, Y, temp_grid, cmap='inferno', shading='auto', alpha=0.9)
    cbar = plt.colorbar(heatmap, ax=ax, label='Temperature (K)')

    # --- Layer B: Airflow Streamlines ---
    # Streamlines are better than arrows for seeing circulation/stagnation
    speed = np.sqrt(ux_grid**2 + uy_grid**2)
    lw = 2 * (speed / speed.max()) # Line width proportional to speed
    
    # Mask zero velocity (solids) to avoid warnings
    mask = type_grid != 1
    
    ax.streamplot(X, Y, ux_grid, uy_grid, 
                  color='cyan', 
                  linewidth=1, 
                  density=1.5, 
                  arrowsize=1.2,
                  alpha=0.6)

    # --- Layer C: Geometry Masks ---
    # Overlay Solids (Type 1) in Gray
    # We create a masked array where only Solids are visible
    solid_mask = np.ma.masked_where(type_grid != 1, type_grid)
    ax.pcolormesh(X, Y, solid_mask, cmap='Greys', vmin=0, vmax=2, shading='auto', zorder=5)

    # Overlay Porous Media (Type 2) in Green Hatch pattern
    porous_mask = np.ma.masked_where(type_grid != 2, type_grid)
    # We use a distinct color or hatch for porous zones
    ax.pcolormesh(X, Y, porous_mask, cmap='Greens', alpha=0.3, shading='auto', zorder=4)

    # 4. Final Formatting
    ax.set_title("Vayunicus Micro-Climate: Thermal Buoyancy & Airflow", fontsize=14)
    ax.set_xlabel("Lattice X")
    ax.set_ylabel("Lattice Y")
    ax.set_aspect('equal')
    
    # Add a custom legend
    from matplotlib.lines import Line2D
    custom_lines = [Line2D([0], [0], color='cyan', lw=2),
                    Line2D([0], [0], color='black', lw=4, alpha=0.5),
                    Line2D([0], [0], color='green', lw=4, alpha=0.3)]
    ax.legend(custom_lines, ['Airflow', 'Solid Walls', 'Porous Zone'])

    plt.tight_layout()
    plt.show()

if __name__ == "__main__":
    # Point this to your output file
    # If you built in 'build/', the path might be 'build/results.csv'
    plot_micro_climate('results.csv')
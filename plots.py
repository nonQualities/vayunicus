import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.colors as mcolors
from matplotlib.lines import Line2D
from matplotlib.patches import Patch
import os
import sys

# ==================================================
# Matplotlib style: Soft & Minimal
# ==================================================
plt.rcParams.update({
    "font.family": "serif",
    "font.size": 11,
    "axes.titlesize": 13,
    "axes.labelsize": 11,
    "figure.dpi": 150,
    "savefig.dpi": 300,
    "xtick.direction": "in",
    "ytick.direction": "in",
    "axes.grid": False,
})

def plot_micro_climate(csv_file):
    if not os.path.exists(csv_file):
        print(f"File not found: {csv_file}")
        return

    # 1. Load Data
    try:
        df = pd.read_csv(csv_file).drop_duplicates(subset=["x", "y"])
    except Exception as e:
        print(f"Error reading CSV: {e}")
        return

    # 2. Robust Grid Generation
    # We build the grid from unique coordinates to handle missing points (sparse data)
    try:
        unique_x = np.sort(df['x'].unique())
        unique_y = np.sort(df['y'].unique())
        X, Y = np.meshgrid(unique_x, unique_y)

        # Helper to align data to the perfect grid
        def get_grid(col, fill_val):
            return df.pivot(index='y', columns='x', values=col)\
                     .reindex(index=unique_y, columns=unique_x)\
                     .fillna(fill_val).values

        # Load fields with defaults for missing data
        T   = get_grid('temp', 300.0)
        ux  = get_grid('u_x', 0.0)
        uy  = get_grid('u_y', 0.0)
        typ = get_grid('type', 0.0)
        
    except ValueError as e:
        print(f"Data shape error: {e}")
        return

    # 3. Setup Figure
    fig, ax = plt.subplots(figsize=(10, 5.5))

    # ==================================================
    # Layer 1: Temperature Field (Custom Spectral)
    # ==================================================
    
    # Custom Colormap: Light Grey -> Spectral
    old_cmap = plt.get_cmap("Spectral_r")
    colors = old_cmap(np.linspace(0, 1, 256))
    
    # Blend bottom 15% to Light Grey
    num_grey = 40 
    grey_start = np.array([0.9, 0.9, 0.9, 1.0]) 
    for i in range(num_grey):
        alpha = i / num_grey
        colors[i] = (1 - alpha) * grey_start + alpha * colors[num_grey]

    new_cmap = mcolors.LinearSegmentedColormap.from_list("GreySpectral", colors)

    # SAFETY: Handle Constant Temperature Case (min == max)
    t_min, t_max = np.min(T), np.max(T)
    if t_max - t_min < 1e-6:
        # Create artificial range if temp is constant
        levels = np.linspace(t_min - 0.5, t_max + 0.5, 40)
    else:
        levels = np.linspace(t_min, t_max, 40)
    
    cf = ax.contourf(
        X, Y, T,
        levels=levels,
        cmap=new_cmap, 
        alpha=0.9,
        extend='both'
    )

    # Thin isolines
    ax.contour(
        X, Y, T,
        levels=levels[::5], # Only plot every 5th level to avoid clutter
        colors="black",
        linewidths=0.2,
        alpha=0.3
    )

    cbar = plt.colorbar(cf, ax=ax, pad=0.02, aspect=25)
    cbar.set_label("Temperature ($K$)", rotation=270, labelpad=15)
    cbar.outline.set_linewidth(0.5)


    # Layer 2: Geometry

    
    # Solid Walls (Type 1): Dark Grey
    solid_mask = np.ma.masked_where(typ != 1, typ)
    ax.pcolormesh(
        X, Y, solid_mask,
        cmap="Greys",
        vmin=0, vmax=1.2,
        shading="nearest",
        zorder=10,
        alpha=1.0
    )

    # Porous Media (Type 2): Hatch pattern
    ax.contourf(
        X, Y, typ == 2,
        levels=[0.5, 1.5],
        colors="none",
        hatches=["///"],
        zorder=9
    )
    ax.contour(
        X, Y, typ == 2,
        levels=[0.5],
        colors="#444444",
        linewidths=0.8,
        linestyles="--",
        zorder=9
    )

    # ==================================================
    # Layer 3: Airflow Streamlines
    # ==================================================
    speed = np.sqrt(ux**2 + uy**2)
    max_speed = speed.max() if speed.max() > 0 else 1.0
    
    # Thinner lines
    lw = 0.3 + 1.0 * (speed / max_speed)

    # 1. White Halo
    ax.streamplot(
        X, Y, ux, uy,
        color=(1, 1, 1, 0.5), 
        linewidth=lw + 0.4,
        density=1.4,
        arrowsize=0.0,
        zorder=7
    )
    
    # 2. Dark Blue Streamlines
    ax.streamplot(
        X, Y, ux, uy,
        color=(0.0, 0.0, 0.55, 0.85), 
        linewidth=lw,
        density=1.4,
        arrowsize=0.7,
        zorder=8
    )

    # ==================================================
    # Annotations
    # ==================================================
    ax.set_title("Urban Micro-Climate Simulation", pad=12, fontweight="bold")
    ax.set_xlabel("Lattice Width ($x$)")
    ax.set_ylabel("Lattice Height ($y$)")
    ax.set_aspect("equal")

    # Legend
    legend_elements = [
        Line2D([0], [0], color="#00008B", lw=1.5, label="Airflow Streamlines"),
        Patch(facecolor="#404040", edgecolor="none", label="Solid Obstacle"),
        Patch(facecolor="white", hatch="///", edgecolor="#444444", label="Porous Zone")
    ]
    
    ax.legend(
        handles=legend_elements,
        loc="upper center",
        bbox_to_anchor=(0.5, -0.15),
        frameon=False,
        ncol=3,
        fontsize=10
    )

    plt.tight_layout()
    print("Displaying visualization...")
    plt.show()

if __name__ == "__main__":
    filename = sys.argv[1] if len(sys.argv) > 1 else "results.csv"
    plot_micro_climate(filename)
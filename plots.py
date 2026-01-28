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

    # 2. Pivot to Grid
    try:
        X = df.pivot(index="y", columns="x", values="x").values
        Y = df.pivot(index="y", columns="x", values="y").values
        T = df.pivot(index="y", columns="x", values="temp").fillna(300.0).values
        ux = df.pivot(index="y", columns="x", values="u_x").fillna(0.0).values
        uy = df.pivot(index="y", columns="x", values="u_y").fillna(0.0).values
        typ = df.pivot(index="y", columns="x", values="type").fillna(0).values
    except ValueError as e:
        print(f"Data shape error: {e}")
        return

    # 3. Setup Figure
    fig, ax = plt.subplots(figsize=(10, 5.5))

    # ==================================================
    # Layer 1: Temperature Field (Custom Spectral)
    # ==================================================
    
    # Custom Colormap: Modify Spectral_r to start with Light Grey
    # 1. Get the standard Spectral_r colormap
    old_cmap = plt.get_cmap("Spectral_r")
    
    # 2. Extract colors as an array (0.0 to 1.0)
    colors = old_cmap(np.linspace(0, 1, 256))
    
    # 3. Force the bottom 15% (lowest temps) to transition from Light Grey
    #    We blend 'lightgrey' into the existing blue/purple of Spectral_r
    num_grey = 40 
    grey_start = np.array([0.9, 0.9, 0.9, 1.0]) # Light Grey (RGBA)
    
    for i in range(num_grey):
        # Linear interpolation from Grey to the original color at index 'num_grey'
        alpha = i / num_grey
        colors[i] = (1 - alpha) * grey_start + alpha * colors[num_grey]

    # 4. Create the new colormap object
    new_cmap = mcolors.LinearSegmentedColormap.from_list("GreySpectral", colors)

    levels = np.linspace(np.min(T), np.max(T), 40)
    
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
        levels=8,
        colors="black",
        linewidths=0.2,
        alpha=0.3
    )

    cbar = plt.colorbar(cf, ax=ax, pad=0.02, aspect=25)
    cbar.set_label("Temperature ($K$)", rotation=270, labelpad=15)
    cbar.outline.set_linewidth(0.5)

    # ==================================================
    # Layer 2: Geometry
    # ==================================================
    
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
    
    # UPDATED: Thinner lines (Reduced base and multiplier)
    lw = 0.3 + 1.0 * (speed / max_speed)

    # UPDATED: Colors are now RGBA tuples
    
    # 1. White Halo (for contrast)
    ax.streamplot(
        X, Y, ux, uy,
        color=(1, 1, 1, 0.5), 
        linewidth=lw + 0.4,
        density=1.4,
        arrowsize=0.0,
        zorder=7
    )
    
    # 2. Dark Blue Streamlines (Deep Navy)
    # RGB for Dark Blue is roughly (0, 0, 0.5)
    ax.streamplot(
        X, Y, ux, uy,
        color=(0.0, 0.0, 0.55, 0.85), # Dark Blue with slight transparency
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
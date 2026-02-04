import numpy as np
import matplotlib.pyplot as plt

def generate_city():
    # Matches the config dimensions
    W, H = 300, 120
    
    # 0 = Fluid, 1 = Solid, 2 = Porous (Hot), 3 = Inlet
    grid = np.zeros((W, H), dtype=int)
    
    # --- 1. Boundaries ---
    grid[:, 0] = 1   # Ground
    grid[:, -1] = 1  # Sky/Ceiling (to keep pressure stable)
    grid[0, 1:-1] = 3 # Inlet (Left wall)
    
    # --- 2. The "Urban Canyon" Formation ---
    
    # Block A: Tall Skyscraper (Front) acts as a wind shield
    # Solid concrete (1)
    grid[40:70, 0:60] = 1 
    
    # Zone B: The "Heat Trap" (Behind Skyscraper)
    # Dense porous settlement (2) hidden in the wake of Block A
    # This area will become very hot because wind is blocked
    grid[75:110, 0:25] = 2 
    
    # Block C: The "Overhang" (Floating Structure)
    # Forces air down into the heat trap or up over it
    grid[60:100, 70:85] = 1
    
    # Zone D: Step-Like Slum Hill
    # A rising hill of porous heat sources
    grid[140:160, 0:15] = 2
    grid[160:180, 0:30] = 2
    grid[180:200, 0:45] = 2
    
    # Block E: The "Ventilation Barrier"
    # A massive wall at the back that forces air to rise sharply
    grid[240:270, 0:80] = 1

    # --- 3. Save to CSV ---
    # Transpose (.T) so that X is columns and Y is rows in the file
    np.savetxt("geometry.csv", grid.T, fmt='%d', delimiter=',')
    print("generated geometry.csv (300x120)")

    # Optional: Preview
    plt.imshow(grid.T, origin='lower', cmap='tab10')
    plt.title("Generated City Geometry")
    plt.colorbar(label="Type (1=Solid, 2=Porous/Hot)")
    plt.show()

if __name__ == "__main__":
    generate_city()
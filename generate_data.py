import numpy as np
import os

def save_scenario(name, grid, config_dict):
    # Create folder
    if not os.path.exists(name):
        os.makedirs(name)
    
    # Save Geometry CSV
    # Transpose so it matches visual x,y logic (x=col, y=row)
    np.savetxt(f"{name}/geometry.csv", grid.T, fmt='%d', delimiter=',')
    
    # Save Config
    with open(f"{name}/config.txt", 'w') as f:
        for k, v in config_dict.items():
            f.write(f"{k}={v}\n")
    
    print(f"Generated Scenario: {name}/ (Size: {config_dict['width']}x{config_dict['height']})")

def generate_scenarios():
    # Standard dimensions for basic tests
    WIDTH = 200
    HEIGHT = 80

    # ==========================================
    # Scenario 1: The "Urban Canyon"
    # Description: Two large solid buildings with a "porous" 
    # informal settlement (slum) in between.
    # ==========================================
    grid_canyon = np.zeros((WIDTH, HEIGHT), dtype=int)
    
    # Walls (Top/Bottom boundary)
    grid_canyon[:, 0] = 1
    grid_canyon[:, -1] = 1
    
    # Inlet (Left)
    grid_canyon[0, 1:-1] = 3
    
    # Building 1 (Solid Block)
    grid_canyon[50:80, 0:50] = 1 
    
    # Building 2 (Solid Block)
    grid_canyon[120:150, 0:50] = 1
    
    # The "Slum" (Porous Zone between buildings)
    grid_canyon[80:120, 0:30] = 2 
    
    config_canyon = {
        'width': WIDTH, 'height': HEIGHT, 'maxSteps': 60000,
        'viscosity': 0.02, 'inletVelocity': 0.08,
        'buoyancyCoef': 0.001, 'porousResistance': 0.25,
        'ambientTemp': 300.0, 'sourceTemp': 305.0,
        'outputName': 'results_canyon.csv'
    }
    save_scenario("Scenario_UrbanCanyon", grid_canyon, config_canyon)

    # ==========================================
    # Scenario 2: "Tin Roof" Updraft
    # Description: Low wind speed, but very high temperature difference.
    # Testing the buoyancy physics (hot air rising).
    # ==========================================
    grid_thermal = np.zeros((WIDTH, HEIGHT), dtype=int)
    grid_thermal[:, 0] = 1; grid_thermal[:, -1] = 1 
    
    # Fixed Inlet ID (was 5, changed to 3 to match engine logic)
    grid_thermal[0, 1:-1] = 3 
    
    # Obstacle in the middle to force air up
    grid_thermal[90:110, 0:20] = 2
    
    config_thermal = {
        'width': WIDTH, 'height': HEIGHT, 'maxSteps': 20000,
        'viscosity': 0.01, 
        'inletVelocity': 0.01, 
        'buoyancyCoef': 0.015, 
        'porousResistance': 0.0,
        'ambientTemp': 100.0, 'sourceTemp': 350.0, 
        'outputName': 'results_thermal.csv'
    }
    save_scenario("Scenario_TinRoof", grid_thermal, config_thermal)

    # ==========================================
    # Scenario 3: Validation Channel
    # Description: Empty channel to verify basic flow profile.
    # ==========================================
    grid_valid = np.zeros((WIDTH, HEIGHT), dtype=int)
    grid_valid[:, 0] = 1; grid_valid[:, -1] = 1
    grid_valid[0, 1:-1] = 3
    
    config_valid = {
        'width': WIDTH, 'height': HEIGHT, 'maxSteps': 30000,
        'viscosity': 0.05, 'inletVelocity': 0.1,
        'buoyancyCoef': 0.0, 'porousResistance': 0.0,
        'ambientTemp': 300.0, 'sourceTemp': 300.0,
        'outputName': 'results_validation.csv'
    }
    save_scenario("Scenario_Validation", grid_valid, config_valid)

    # ==========================================
    # Scenario 4: "Complex Heat Island" (NEW)
    # Description: Larger domain with skyscrapers, overhangs, 
    # and stepped settlements. 
    # ==========================================
    CW, CH = 300, 120 # Larger dimensions
    grid_complex = np.zeros((CW, CH), dtype=int)
    
    # Boundaries
    grid_complex[:, 0] = 1   # Floor
    grid_complex[:, -1] = 1  # Ceiling
    grid_complex[0, 1:-1] = 3 # Inlet (Left wall)
    
    # 1. Tall Skyscraper (Front Shield)
    grid_complex[40:70, 0:60] = 1 
    
    # 2. The "Heat Trap" (Hidden Porous Slum)
    # Dense settlement hidden behind the skyscraper
    grid_complex[75:110, 0:25] = 2 
    
    # 3. Floating Overhang (Forces flow compression)
    grid_complex[60:100, 70:85] = 1
    
    # 4. Stepped Slum Hill (Rising heat source)
    grid_complex[140:160, 0:15] = 2
    grid_complex[160:180, 0:30] = 2
    grid_complex[180:200, 0:45] = 2
    
    # 5. Rear Ventilation Barrier (Forces air up)
    grid_complex[240:270, 0:80] = 1

    config_complex = {
        'width': CW, 'height': CH, 'maxSteps': 40000,
        'viscosity': 0.015,      # Low viscosity = more turbulence
        'inletVelocity': 0.08,
        'buoyancyCoef': 0.008,   # Strong thermal updrafts
        'porousResistance': 0.35,
        'ambientTemp': 300.0, 
        'sourceTemp': 345.0,     # Significant heat delta
        'outputName': 'results_complex.csv'
    }
    save_scenario("Scenario_ComplexCity", grid_complex, config_complex)

if __name__ == "__main__":
    generate_scenarios()
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
    
    print(f"Generated Scenario: {name}/")

def generate_scenarios():
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
    # Represents dense tin shacks that slow down air
    grid_canyon[80:120, 0:30] = 2 
    
    config_canyon = {
        'width': WIDTH, 'height': HEIGHT, 'maxSteps': 60000,
        'viscosity': 0.02, 'inletVelocity': 0.08,
        'buoyancyCoef': 0.001, 'porousResistance': 0.25, # Strong drag
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
    grid_thermal[:, 0] = 1; grid_thermal[:, -1] = 1 # Floor/Ceiling
    grid_thermal[0, 1:-1] = 3 # Inlet
    
    # Obstacle in the middle to force air up
    grid_thermal[90:110, 0:20] = 2
    
    config_thermal = {
        'width': WIDTH, 'height': HEIGHT, 'maxSteps': 20000,
        'viscosity': 0.01, 
        'inletVelocity': 0.01, # Very low wind
        'buoyancyCoef': 0.015, # HIGH Buoyancy (Hot roof effect)
        'porousResistance': 0.0,
        'ambientTemp': 300.0, 'sourceTemp': 350.0, # 50 degree difference!
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

if __name__ == "__main__":
    generate_scenarios()
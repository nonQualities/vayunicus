#include "io/dataLoader.hpp"
#include "engine/solver.hpp"
#include <iostream>

int main(int argc, char** argv) {
    std::string configFile = "config.txt";
    std::string geoFile = "geometry.csv";

    // Simple CLI Args override
    if(argc > 1) configFile = argv[1];
    if(argc > 2) geoFile = argv[2];

    std::cout << "=== Vayunicus LBM Engine ===\n";
    std::cout << "Loading Config: " << configFile << "\n";
    
    // 1. Load Parameters
    auto params = Vayunicus::DataLoader::loadConfig(configFile);

    // 2. Load Geometry
    std::cout << "Loading Geometry: " << geoFile << "\n";
    std::vector<std::vector<int>> geoMap = Vayunicus::DataLoader::loadGeometry(geoFile, params.width, params.height);
    
    std::cout << "Domain Size: " << params.width << " x " << params.height << "\n";
    std::cout << "Viscosity: " << params.viscosity << " | Buoyancy Coef: " << params.buoyancyCoef << "\n";

    // 3. Initialize Solver
    Vayunicus::Solver solver(params, geoMap);

    // 4. Run Simulation
    solver.run();

    return 0;
}
#pragma once
#include "constants.hpp"
#include <vector>
#include <string>

namespace Vayunicus {

    enum class CellType {
        FLUID = 0,
        SOLID = 1,
        POROUS = 2,  // New: For semi-permeable informal settlements
        INLET = 3,
        OUTLET = 4
    };

    struct SimulationParams {
        int width = 200;
        int height = 80;
        int maxSteps = 10000;
        double viscosity = 0.02;
        double thermalDiffusivity = 0.02;
        double inletVelocity = 0.05;
        double porousResistance = 0.15; // Resistance factor for porous zones
        double buoyancyCoef = 0.005;    // Thermal expansion (Beta)
        double ambientTemp = 300.0;     // Kelvin
        double sourceTemp = 310.0;      // Kelvin (e.g., body heat/stove)
        std::string outputName = "output.csv";
    };

    struct Node {
        // Flow distributions
        double f[Q];
        double f_next[Q];

        // Temperature distributions (Passive Scalar)
        double g[Q];
        double g_next[Q];

        // Macroscopic properties
        double rho;
        double u_x;
        double u_y;
        double temp; // Temperature

        CellType type;

        Node() : rho(1.0), u_x(0.0), u_y(0.0), temp(300.0), type(CellType::FLUID) {
            for(int i=0; i<Q; ++i) {
                f[i] = WEIGHTS[i];
                f_next[i] = WEIGHTS[i];
                g[i] = WEIGHTS[i] * 300.0;
                g_next[i] = WEIGHTS[i] * 300.0;
            }
        }
    };
}
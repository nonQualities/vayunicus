#pragma once
#include "../core/types.hpp"
#include <vector>

namespace Vayunicus {

    class Solver {
    public:
        Solver(const SimulationParams& params, const std::vector<std::vector<int>>& geometryMap);
        
        // Main loop driver
        void run();

    private:
        SimulationParams m_params;
        std::vector<std::vector<Node>> m_grid;
        
        // LBM Relaxation times
        double m_tau_flow;
        double m_tau_temp;

        void initialize();
        void step(int t);
        
        // Physics Steps
        void collide_and_stream();
        void apply_boundary_conditions();
        void update_macroscopic();
        
        // Helper
        double calculate_equilibrium(int k, double rho, double ux, double uy);
        double calculate_temp_equilibrium(int k, double temp, double ux, double uy);
        
        void export_results(int step);
    };
}
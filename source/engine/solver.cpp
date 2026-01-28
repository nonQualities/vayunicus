#include "solver.hpp"
#include "../core/constants.hpp"
#include <iostream>
#include <fstream>
#include <cmath>
#include <algorithm>

namespace Vayunicus {

    Solver::Solver(const SimulationParams& params, const std::vector<std::vector<int>>& geometryMap)
        : m_params(params) 
    {
        // 1. Calculate Tau (Relaxation time) from Viscosity
        // nu = (tau - 0.5) / 3  =>  tau = 3*nu + 0.5
        m_tau_flow = 3.0 * m_params.viscosity + 0.5;
        m_tau_temp = 3.0 * m_params.thermalDiffusivity + 0.5;

        // 2. Resize Grid
        m_grid.resize(m_params.width, std::vector<Node>(m_params.height));

        // 3. Map Geometry from CSV Input
        for(int x=0; x<m_params.width; ++x) {
            for(int y=0; y<m_params.height; ++y) {
                int inputVal = 0;
                // Safety check for map size mismatch
                if(x < (int)geometryMap.size() && y < (int)geometryMap[0].size()) {
                    inputVal = geometryMap[x][y];
                }
                
                // Map integer to CellType
                switch(inputVal) {
                    case 1: m_grid[x][y].type = CellType::SOLID; break;
                    case 2: m_grid[x][y].type = CellType::POROUS; break;
                    case 3: m_grid[x][y].type = CellType::INLET; break;
                    default: m_grid[x][y].type = CellType::FLUID; break;
                }
                
                // Set initial ambient temp
                m_grid[x][y].temp = m_params.ambientTemp;
            }
        }
        initialize();
    }

    void Solver::initialize() {
        for(int x=0; x<m_params.width; ++x) {
            for(int y=0; y<m_params.height; ++y) {
                // Initialize equilibrium distributions
                double u_x_init = (m_grid[x][y].type == CellType::INLET) ? m_params.inletVelocity : 0.0;
                
                for(int i=0; i<Q; ++i) {
                    m_grid[x][y].f[i] = calculate_equilibrium(i, 1.0, u_x_init, 0.0);
                    m_grid[x][y].g[i] = calculate_temp_equilibrium(i, m_params.ambientTemp, u_x_init, 0.0);
                }
            }
        }
    }

    void Solver::run() {
        std::cout << "Starting Simulation: " << m_params.maxSteps << " steps.\n";
        
        for(int t=0; t < m_params.maxSteps; ++t) {
            step(t);
            if(t % 100 == 0) std::cout << "Step: " << t << "\r" << std::flush;
        }
        std::cout << "\nSimulation Complete.\n";
        export_results(m_params.maxSteps);
    }

    void Solver::step(int t) {
        collide_and_stream();
        apply_boundary_conditions();
        update_macroscopic();
    }

    void Solver::collide_and_stream() {
        for(int x=0; x<m_params.width; ++x) {
            for(int y=0; y<m_params.height; ++y) {
                Node& node = m_grid[x][y];

                if(node.type == CellType::SOLID) continue; // Skip solids

                // 1. Calculate Macroscopic for Collision
                double rho = 0.0, ux = 0.0, uy = 0.0, temp = 0.0;
                for(int i=0; i<Q; ++i) {
                    rho += node.f[i];
                    ux  += node.f[i] * LX[i];
                    uy  += node.f[i] * LY[i];
                    temp += node.g[i];
                }
                if(rho > 0) { ux /= rho; uy /= rho; }

                // --- SOPHISTICATED PHYSICS EXTENSIONS ---

                // Extension A: Porous Media Resistance
                // If porous, apply drag force (reduce velocity)
                if(node.type == CellType::POROUS) {
                    ux *= (1.0 - m_params.porousResistance);
                    uy *= (1.0 - m_params.porousResistance);
                }

                // Extension B: Thermal Buoyancy (Boussinesq Force)
                // F_buoyancy = rho * beta * g * (T - T_ambient)
                // We add this force to the vertical velocity component used in equilibrium
                double buoyancy_force = m_params.buoyancyCoef * (node.temp - m_params.ambientTemp);
                uy += buoyancy_force * m_tau_flow; // Apply force scaling

                // ----------------------------------------

                // Collision Step (BGK)
                for(int i=0; i<Q; ++i) {
                    // Flow Collision
                    double feq = calculate_equilibrium(i, rho, ux, uy);
                    double f_out = node.f[i] - (node.f[i] - feq) / m_tau_flow;

                    // Temperature Collision
                    double geq = calculate_temp_equilibrium(i, temp, ux, uy);
                    double g_out = node.g[i] - (node.g[i] - geq) / m_tau_temp;

                    // Streaming (Push to neighbors)
                    int nextX = (x + LX[i] + m_params.width) % m_params.width;
                    int nextY = (y + LY[i] + m_params.height) % m_params.height;

                    // Handle Solid Boundaries during streaming (Bounce-back)
                    if(m_grid[nextX][nextY].type == CellType::SOLID) {
                        m_grid[x][y].f_next[OPPOSITE[i]] = f_out;
                        m_grid[x][y].g_next[OPPOSITE[i]] = g_out;
                    } else {
                        m_grid[nextX][nextY].f_next[i] = f_out;
                        m_grid[nextX][nextY].g_next[i] = g_out;
                    }
                }
            }
        }

        // Swap buffers
        for(auto& col : m_grid) {
            for(auto& node : col) {
                for(int i=0; i<Q; ++i) {
                    node.f[i] = node.f_next[i];
                    node.g[i] = node.g_next[i];
                }
            }
        }
    }

    void Solver::apply_boundary_conditions() {
        // 1. Inlet Condition (Left Wall)
        for(int y=0; y<m_params.height; ++y) {
            if(m_grid[0][y].type != CellType::SOLID) {
                 // Force equilibrium at inlet velocity
                for(int i=0; i<Q; ++i) {
                     m_grid[0][y].f[i] = calculate_equilibrium(i, 1.0, m_params.inletVelocity, 0.0);
                     // Inlet air is ambient temperature (cool wind)
                     m_grid[0][y].g[i] = calculate_temp_equilibrium(i, m_params.ambientTemp, m_params.inletVelocity, 0.0);
                }
            }
        }

        // 2. Distributed Heat Source Logic (Tin Roof Effect)
        // Any cell marked as POROUS (Type 2) or Source acts as a heater.
        for(int x=0; x<m_params.width; ++x) {
            for(int y=0; y<m_params.height; ++y) {
                if(m_grid[x][y].type == CellType::POROUS) {
                    // Force the temperature to the source temperature
                    m_grid[x][y].temp = m_params.sourceTemp; 
                    
                    // Reset the thermal distribution to match this fixed temperature
                    // We assume zero velocity inside the "roof" material for the thermal equilibrium
                    for(int i=0; i<Q; ++i) {
                        m_grid[x][y].g[i] = calculate_temp_equilibrium(i, m_params.sourceTemp, 0.0, 0.0);
                    }
                }
            }
        }
    }

    void Solver::update_macroscopic() {
        for(auto& col : m_grid) {
            for(auto& node : col) {
                double rho = 0, ux = 0, uy = 0, temp = 0;
                for(int i=0; i<Q; ++i) {
                    rho += node.f[i];
                    ux += node.f[i] * LX[i];
                    uy += node.f[i] * LY[i];
                    temp += node.g[i];
                }
                node.rho = rho;
                node.temp = temp;
                if(rho > 0) {
                    node.u_x = ux / rho;
                    node.u_y = uy / rho;
                }
            }
        }
    }

    double Solver::calculate_equilibrium(int i, double rho, double ux, double uy) {
        double cu = 3.0 * (LX[i]*ux + LY[i]*uy);
        double usq = 1.5 * (ux*ux + uy*uy);
        return WEIGHTS[i] * rho * (1.0 + cu + 0.5*cu*cu - usq);
    }

    double Solver::calculate_temp_equilibrium(int i, double temp, double ux, double uy) {
        // Scalar equilibrium (Advection-Diffusion)
        double cu = 3.0 * (LX[i]*ux + LY[i]*uy);
        return WEIGHTS[i] * temp * (1.0 + cu);
    }

    void Solver::export_results(int step) {
        std::ofstream file(m_params.outputName);
        file << "x,y,u_x,u_y,temp,type\n";
        for(int x=0; x<m_params.width; ++x) {
            for(int y=0; y<m_params.height; ++y) {
                file << x << "," << y << "," 
                     << m_grid[x][y].u_x << "," 
                     << m_grid[x][y].u_y << ","
                     << m_grid[x][y].temp << ","
                     << (int)m_grid[x][y].type << "\n";
            }
        }
        std::cout << "Results saved to " << m_params.outputName << "\n";
    }
}
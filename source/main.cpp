#include <iostream>
#include <vector>
#include <fstream>
#include <string>
#include <cmath>

// =============================================================
// Simulation Parameters
// =============================================================
const int GRID_WIDTH  = 200;
const int GRID_HEIGHT = 80;
const int MAX_TIME_STEPS = 3000;

// Collision relaxation rates
const double OMEGA_AIR = 1.0 / 0.6;
const double OMEGA_PATHOGEN = 1.0 / 0.8;

// Lattice Boltzmann D2Q9 Model
const double WEIGHT[9] = {4/9., 1/9., 1/9., 1/9., 1/9., 1/36., 1/36., 1/36., 1/36.};
const int VX[9]        = {0, 1, 0, -1, 0, 1, -1, -1, 1};
const int VY[9]        = {0, 0, 1,  0,-1, 1,  1, -1,-1};
const int OPPOSITE[9]  = {0, 3, 4, 1, 2, 7,  8, 5, 6};

struct Cell {
    double airDist[9], airDistNext[9];
    double pathogenDist[9], pathogenDistNext[9];
    bool isWall = false;
};

// =============================================================
// Utility: Write CSV Output
// =============================================================
void write_simulation_data(const std::vector<std::vector<Cell>>& domain, const std::string& filename) {
    std::ofstream file(filename);
    file << "x,y,pathogen_concentration,velocity_magnitude,is_wall\n";

    for (int y = 0; y < GRID_HEIGHT; ++y) {
        for (int x = 0; x < GRID_WIDTH; ++x) {

            double densityAir = 0.0, velX = 0.0, velY = 0.0;
            double pathogenDensity = 0.0;

            for (int i = 0; i < 9; ++i) {
                densityAir       += domain[x][y].airDist[i];
                velX             += domain[x][y].airDist[i] * VX[i];
                velY             += domain[x][y].airDist[i] * VY[i];
                pathogenDensity  += domain[x][y].pathogenDist[i];
            }

            if (densityAir > 0) {
                velX /= densityAir;
                velY /= densityAir;
            }

            double speedMagnitude = std::sqrt(velX*velX + velY*velY);
            file << x << "," << y << "," << pathogenDensity << "," << speedMagnitude
                 << "," << (domain[x][y].isWall ? 1 : 0) << "\n";
        }
    }
}

// =============================================================
// Initialization
// =============================================================
void initialize_domain(std::vector<std::vector<Cell>>& domain) {
    for (int x = 0; x < GRID_WIDTH; ++x) {
        for (int y = 0; y < GRID_HEIGHT; ++y) {

            // L-shaped wall (geometry)
            if ((x == 60 && y > 20 && y < 60) ||
                (x > 60 && x < 100 && y == 20))
                domain[x][y].isWall = true;

            // Initial airflow
            double rho = 1.0;
            double uX = 0.05;
            double uY = 0.0;

            for (int i = 0; i < 9; ++i) {
                double cu = 3.0 * (VX[i]*uX + VY[i]*uY);
                domain[x][y].airDist[i] = WEIGHT[i] * rho * (1.0 + cu);
                domain[x][y].pathogenDist[i] = 0.0;
            }
        }
    }
}

// =============================================================
// Core: Single timestep update
// =============================================================
void simulate_step(std::vector<std::vector<Cell>>& domain, int timestep) {

    // coughing source: inject pathogen
    if (timestep < 500) {
        for (int i = 0; i < 9; ++i)
            domain[40][40].pathogenDist[i] += 0.2 * WEIGHT[i];
    }

    // Collision + Streaming
    for (int x = 0; x < GRID_WIDTH; ++x) {
        for (int y = 0; y < GRID_HEIGHT; ++y) {

            if (domain[x][y].isWall) continue;

            double rho = 0.0, velX = 0.0, velY = 0.0, pathogenDensity = 0.0;
            for (int i = 0; i < 9; ++i) {
                rho += domain[x][y].airDist[i];
                velX += domain[x][y].airDist[i] * VX[i];
                velY += domain[x][y].airDist[i] * VY[i];
                pathogenDensity += domain[x][y].pathogenDist[i];
            }
            velX /= rho;
            velY /= rho;
            double velSquared = velX*velX + velY*velY;

            for (int i = 0; i < 9; ++i) {
                double cu = 3.0 * (VX[i]*velX + VY[i]*velY);

                // Equilibrium for air
                double feq = WEIGHT[i]*rho*(1.0 + cu + 0.5*cu*cu - 1.5*velSquared);
                domain[x][y].airDist[i] -= OMEGA_AIR * (domain[x][y].airDist[i] - feq);

                // Equilibrium for pathogen scalar
                double geq = WEIGHT[i]*pathogenDensity*(1.0 + cu);
                domain[x][y].pathogenDist[i] -= OMEGA_PATHOGEN * (domain[x][y].pathogenDist[i] - geq);

                int nextX = (x + VX[i] + GRID_WIDTH)  % GRID_WIDTH;
                int nextY = (y + VY[i] + GRID_HEIGHT) % GRID_HEIGHT;

                if (domain[nextX][nextY].isWall) {
                    domain[x][y].airDistNext[OPPOSITE[i]] = domain[x][y].airDist[i];
                } else {
                    domain[nextX][nextY].airDistNext[i]      = domain[x][y].airDist[i];
                    domain[nextX][nextY].pathogenDistNext[i] = domain[x][y].pathogenDist[i];
                }
            }
        }
    }

    // Swap buffers
    for (auto& column : domain) {
        for (auto& cell : column) {
            for (int i = 0; i < 9; ++i) {
                cell.airDist[i] = cell.airDistNext[i];
                cell.pathogenDist[i] = cell.pathogenDistNext[i];
            }
        }
    }
}

// =============================================================
// Entry Point
// =============================================================
int main() {
    std::vector<std::vector<Cell>> domain(GRID_WIDTH, std::vector<Cell>(GRID_HEIGHT));

    initialize_domain(domain);

    for (int t = 0; t < MAX_TIME_STEPS; ++t)
        simulate_step(domain, t);

    write_simulation_data(domain, "simulation_results.csv");
    return 0;
}

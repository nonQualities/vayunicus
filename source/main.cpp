#include <iostream>
#include <vector>
#include <fstream>
#include <string>
#include <cmath>

// --- Simulation Parameters ---
const int WIDTH = 200;  // X-axis (e.g., length of an alleyway)
const int HEIGHT = 80;  // Y-axis (e.g., width of the alleyway)
const double OMEGA = 1.0 / 0.6; // Collision frequency (1/tau) [cite: 30]
const double OMEGA_S = 1.0 / 0.8; // Pathogen diffusion rate [cite: 36]
const int TIME_STEPS = 3000;

// D2Q9 Lattice constants
const double w[9] = {4/9., 1/9., 1/9., 1/9., 1/9., 1/36., 1/36., 1/36., 1/36.};
const int cx[9] = {0, 1, 0, -1, 0, 1, -1, -1, 1};
const int cy[9] = {0, 0, 1, 0, -1, 1, 1, -1, -1};
const int opposite[9] = {0, 3, 4, 1, 2, 7, 8, 5, 6}; // For Bounce-back 

struct Cell {
    double f[9], f_new[9]; // Air distributions [cite: 22]
    double g[9], g_new[9]; // Pathogen distributions [cite: 35]
    bool is_wall = false;
};

void save_data(const std::vector<std::vector<Cell>>& grid, std::string filename) {
    std::ofstream file(filename);
    // Header for clear identification
    file << "x,y,density,velocity_mag,is_wall\n"; 
    for (int y = 0; y < HEIGHT; ++y) {
        for (int x = 0; x < WIDTH; ++x) {
            double rho = 0, ux = 0, uy = 0, rho_s = 0;
            for (int i = 0; i < 9; ++i) {
                rho += grid[x][y].f[i];
                ux += grid[x][y].f[i] * cx[i];
                uy += grid[x][y].f[i] * cy[i];
                rho_s += grid[x][y].g[i];
            }
            if (rho > 0) { ux /= rho; uy /= rho; }
            double v_mag = sqrt(ux*ux + uy*uy);
            file << x << "," << y << "," << rho_s << "," << v_mag << "," << (grid[x][y].is_wall ? 1 : 0) << "\n";
        }
    }
}

int main() {
    std::vector<std::vector<Cell>> grid(WIDTH, std::vector<Cell>(HEIGHT));

    // Initial Conditions & Geometry [cite: 8, 42]
    for (int x = 0; x < WIDTH; ++x) {
        for (int y = 0; y < HEIGHT; ++y) {
            // Define an L-shaped "Slum Wall" [cite: 12]
            if ((x == 60 && y > 20 && y < 60) || (x > 60 && x < 100 && y == 20)) grid[x][y].is_wall = true;
            
            double rho = 1.0, ux = 0.05, uy = 0.0; // Steady inlet breeze 
            for (int i = 0; i < 9; ++i) {
                double cu = 3.0 * (cx[i]*ux + cy[i]*uy);
                grid[x][y].f[i] = w[i] * rho * (1.0 + cu);
                grid[x][y].g[i] = 0.0;
            }
        }
    }

    for (int t = 0; t < TIME_STEPS; ++t) {
        // 1. Pathogen Source (The "Cough") [cite: 56, 60]
        if (t < 500) { // Temporary release
            for(int i=0; i<9; i++) grid[40][40].g[i] += 0.2 * w[i];
        }

        // 2. Stream and Collide [cite: 23, 30]
        for (int x = 0; x < WIDTH; ++x) {
            for (int y = 0; y < HEIGHT; ++y) {
                if (grid[x][y].is_wall) continue;

                double rho = 0, ux = 0, uy = 0, rho_s = 0;
                for (int i = 0; i < 9; ++i) {
                    rho += grid[x][y].f[i];
                    ux += grid[x][y].f[i] * cx[i];
                    uy += grid[x][y].f[i] * cy[i];
                    rho_s += grid[x][y].g[i];
                }
                ux /= rho; uy /= rho;

                for (int i = 0; i < 9; ++i) {
                    // Air Collision (BGK) [cite: 29]
                    double cu = 3.0*(cx[i]*ux + cy[i]*uy);
                    double feq = w[i]*rho*(1.0 + cu + 0.5*cu*cu - 1.5*(ux*ux+uy*uy));
                    grid[x][y].f[i] -= OMEGA * (grid[x][y].f[i] - feq);

                    // Pathogen Collision (Passive Scalar) [cite: 36]
                    double geq = w[i]*rho_s*(1.0 + cu); 
                    grid[x][y].g[i] -= OMEGA_S * (grid[x][y].g[i] - geq);

                    // Streaming 
                    int nx = (x + cx[i] + WIDTH) % WIDTH;
                    int ny = (y + cy[i] + HEIGHT) % HEIGHT;
                    if (grid[nx][ny].is_wall) {
                        grid[x][y].f_new[opposite[i]] = grid[x][y].f[i]; // Bounce-back 
                    } else {
                        grid[nx][ny].f_new[i] = grid[x][y].f[i];
                        grid[nx][ny].g_new[i] = grid[x][y].g[i];
                    }
                }
            }
        }
        // Update buffers
        for(auto &col : grid) for(auto &c : col) { 
            for(int i=0; i<9; i++) { c.f[i] = c.f_new[i]; c.g[i] = c.g_new[i]; }
        }
    }
    save_data(grid, "simulation_results.csv");
    return 0;
}
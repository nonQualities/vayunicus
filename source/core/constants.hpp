#pragma once

namespace Vayunicus {
    // D2Q9 Lattice Constants
    constexpr int Q = 9;
    
    // Direction weights
    constexpr double WEIGHTS[9] = {
        4.0/9.0, 1.0/9.0, 1.0/9.0, 1.0/9.0, 1.0/9.0, 
        1.0/36.0, 1.0/36.0, 1.0/36.0, 1.0/36.0
    };

    // Lattice velocities (e_x, e_y)
    constexpr int LX[9] = { 0, 1, 0, -1, 0, 1, -1, -1, 1 };
    constexpr int LY[9] = { 0, 0, 1, 0, -1, 1, 1, -1, -1 };

    // Opposite direction indices (for bounce-back)
    constexpr int OPPOSITE[9] = { 0, 3, 4, 1, 2, 7, 8, 5, 6 };
}
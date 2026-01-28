#pragma once
#include "../core/types.hpp"
#include <string>
#include <map>
#include <vector>

namespace Vayunicus {
    class DataLoader {
    public:
        // Reads key=value pairs from a text file
        static SimulationParams loadConfig(const std::string& filepath);
        
        // Reads a CSV of integers for geometry
        static std::vector<std::vector<int>> loadGeometry(const std::string& filepath, int& width, int& height);
    };
}
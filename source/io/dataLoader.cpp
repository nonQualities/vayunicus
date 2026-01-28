#include "dataLoader.hpp"
#include <fstream>
#include <sstream>
#include <iostream>
#include <algorithm>

namespace Vayunicus {

    SimulationParams DataLoader::loadConfig(const std::string& filepath) {
        SimulationParams params;
        std::ifstream file(filepath);
        if(!file.is_open()) {
            std::cerr << "Warning: Could not open config file. Using defaults.\n";
            return params;
        }

        std::string line;
        while(std::getline(file, line)) {
            if(line.empty() || line[0] == '#') continue;
            
            std::stringstream ss(line);
            std::string key, valStr;
            if(std::getline(ss, key, '=') && std::getline(ss, valStr)) {
                // Trim logic usually goes here, skipping for brevity
                
                if(key == "width") params.width = std::stoi(valStr);
                else if(key == "height") params.height = std::stoi(valStr);
                else if(key == "maxSteps") params.maxSteps = std::stoi(valStr);
                else if(key == "viscosity") params.viscosity = std::stod(valStr);
                else if(key == "inletVelocity") params.inletVelocity = std::stod(valStr);
                else if(key == "porousResistance") params.porousResistance = std::stod(valStr);
                else if(key == "buoyancyCoef") params.buoyancyCoef = std::stod(valStr);
                else if(key == "sourceTemp") params.sourceTemp = std::stod(valStr);
                else if(key == "outputName") params.outputName = valStr;
            }
        }
        return params;
    }

    std::vector<std::vector<int>> DataLoader::loadGeometry(const std::string& filepath, int& width, int& height) {
        std::vector<std::vector<int>> map;
        std::ifstream file(filepath);
        
        if(!file.is_open()) {
            std::cerr << "Error: Geometry file not found. Generating empty box.\n";
            width = 100; height = 50;
            return std::vector<std::vector<int>>(width, std::vector<int>(height, 0));
        }

        std::string line;
        int y = 0;
        
        // Temporary storage to transpose later (CSV is usually row-major, we want x-major)
        std::vector<std::vector<int>> tempRows;

        while(std::getline(file, line)) {
            std::vector<int> row;
            std::stringstream ss(line);
            std::string cell;
            while(std::getline(ss, cell, ',')) {
                try {
                    row.push_back(std::stoi(cell));
                } catch(...) { row.push_back(0); }
            }
            tempRows.push_back(row);
        }

        if(tempRows.empty()) return map;

        height = tempRows.size();
        width = tempRows[0].size();
        
        // Transpose to match [x][y] structure
        map.resize(width, std::vector<int>(height));
        for(int j=0; j<height; ++j) {
            for(int i=0; i<width; ++i) {
                if(i < tempRows[j].size())
                    map[i][j] = tempRows[j][i];
                else
                    map[i][j] = 0;
            }
        }
        
        return map;
    }
}
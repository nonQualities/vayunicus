#!/bin/bash

# ==============================================================================
# Vayunicus Automation Script
# Automates: Build -> Generate Data -> Simulate -> Visualize
# ==============================================================================

# 1. Configuration
PROJECT_ROOT=$(pwd)
BUILD_DIR="build"
EXE_NAME="vayunicus"
GENERATOR_SCRIPT="generate_data.py"
PLOT_SCRIPT="plots.py"

# Stop on errors
set -e

echo "=========================================="
echo "   Starting Vayunicus Full Pipeline"
echo "=========================================="

# ------------------------------------------------------------------------------
# Step 1: Build the C++ Engine
# ------------------------------------------------------------------------------
echo -e "\n[Step 1] Building Engine..."

if [ ! -d "$BUILD_DIR" ]; then
    mkdir $BUILD_DIR
fi

cd $BUILD_DIR
# Run CMake and Make
cmake ..
make -j$(nproc) # Use all CPU cores for faster compilation
cd $PROJECT_ROOT

# Locate the executable (handles different CMake configurations)
if [ -f "$BUILD_DIR/bin/$EXE_NAME" ]; then
    EXE_PATH="$BUILD_DIR/bin/$EXE_NAME"
elif [ -f "$BUILD_DIR/$EXE_NAME" ]; then
    EXE_PATH="$BUILD_DIR/$EXE_NAME"
elif [ -f "$PROJECT_ROOT/$EXE_NAME" ]; then
    EXE_PATH="$PROJECT_ROOT/$EXE_NAME"
else
    echo "❌ Error: Could not find executable '$EXE_NAME' after build."
    exit 1
fi

echo "✅ Build Successful. Using executable: $EXE_PATH"

# ------------------------------------------------------------------------------
# Step 2: Generate Test Data
# ------------------------------------------------------------------------------
echo -e "\n[Step 2] Generating Physics Scenarios..."

if [ ! -f "$GENERATOR_SCRIPT" ]; then
    echo "❌ Error: $GENERATOR_SCRIPT not found!"
    echo "Please save the python generator code from the previous step."
    exit 1
fi

python3 $GENERATOR_SCRIPT

# ------------------------------------------------------------------------------
# Step 3: Run Simulations & Visualize
# ------------------------------------------------------------------------------
echo -e "\n[Step 3] Running Simulations..."

# List of scenarios created by generate_data.py
SCENARIOS=("Scenario_UrbanCanyon" "Scenario_TinRoof" "Scenario_Validation")

for SCENARIO in "${SCENARIOS[@]}"; do
    echo "----------------------------------------------------------------"
    echo "▶ Processing: $SCENARIO"
    
    CONFIG_FILE="$SCENARIO/config.txt"
    GEOMETRY_FILE="$SCENARIO/geometry.csv"

    # 1. Extract the expected output filename from config.txt
    # (The engine writes this file to the current folder)
    OUTPUT_CSV=$(grep "outputName" "$CONFIG_FILE" | cut -d'=' -f2 | tr -d '\r')
    
    # 2. Run the Engine
    # Usage: ./Vayunicus <config> <geometry>
    $EXE_PATH "$CONFIG_FILE" "$GEOMETRY_FILE"
    
    # 3. Move output to the scenario folder (to keep things organized)
    if [ -f "$OUTPUT_CSV" ]; then
        mv "$OUTPUT_CSV" "$SCENARIO/$OUTPUT_CSV"
        echo "   -> Saved results to: $SCENARIO/$OUTPUT_CSV"
    else
        echo "⚠️ Warning: Output file $OUTPUT_CSV was not generated."
        continue
    fi

    # 4. Run Visualization
    echo "   -> Generating Plot..."
    python3 $PLOT_SCRIPT "$SCENARIO/$OUTPUT_CSV" &
    
    # Note: The '&' runs plotting in background so you can see them pop up.
    # Remove '&' if you want to close each window before the next starts.
done

echo "----------------------------------------------------------------"
echo "✅ All simulations completed successfully!"
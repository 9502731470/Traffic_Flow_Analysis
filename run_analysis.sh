#!/bin/bash

echo "========================================"
echo "Traffic Flow Analysis System"
echo "========================================"
echo

# Check Python installation
echo "Checking Python installation..."
if ! command -v python3 &> /dev/null; then
    if ! command -v python &> /dev/null; then
        echo "ERROR: Python is not installed"
        echo "Please install Python 3.8+ and try again"
        exit 1
    else
        PYTHON_CMD="python"
    fi
else
    PYTHON_CMD="python3"
fi

echo "Python found: $($PYTHON_CMD --version)"
echo

# Check pip
echo "Checking pip installation..."
if ! command -v pip3 &> /dev/null; then
    if ! command -v pip &> /dev/null; then
        echo "ERROR: pip is not installed"
        echo "Please install pip and try again"
        exit 1
    else
        PIP_CMD="pip"
    fi
else
    PIP_CMD="pip3"
fi

echo "pip found: $($PIP_CMD --version)"
echo

# Install dependencies
echo "Installing/updating required packages..."
$PIP_CMD install -r requirements.txt

if [ $? -ne 0 ]; then
    echo "ERROR: Failed to install dependencies"
    echo "Please check your internet connection and try again"
    exit 1
fi

echo
echo "Dependencies installed successfully!"
echo

# Run system test
echo "Running system test..."
$PYTHON_CMD test_setup.py

if [ $? -ne 0 ]; then
    echo "WARNING: System test failed. Continuing anyway..."
fi

echo
echo "========================================"
echo "Starting Traffic Flow Analysis..."
echo "========================================"
echo
echo "This will:"
echo "1. Download the traffic video from YouTube"
echo "2. Process the video with vehicle detection"
echo "3. Generate output.csv with tracking data"
echo "4. Create demo_video.mp4 with annotations"
echo
echo "Processing may take several minutes depending on your system..."
echo

# Run the main analysis
$PYTHON_CMD traffic_flow.py

echo
echo "========================================"
echo "Analysis Complete!"
echo "========================================"
echo
echo "Check the following files:"
echo "- output.csv (vehicle tracking data)"
echo "- demo_video.mp4 (annotated video)"
echo "- lane_config.json (lane configuration)"
echo

# Make the script executable
chmod +x run_analysis.sh 
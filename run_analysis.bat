@echo off
echo ========================================
echo Traffic Flow Analysis System
echo ========================================
echo.

echo Checking Python installation...
python --version >nul 2>&1
if errorlevel 1 (
    echo ERROR: Python is not installed or not in PATH
    echo Please install Python 3.8+ and try again
    pause
    exit /b 1
)

echo Python found. Checking dependencies...
echo.

echo Installing/updating required packages...
pip install -r requirements.txt

if errorlevel 1 (
    echo ERROR: Failed to install dependencies
    echo Please check your internet connection and try again
    pause
    exit /b 1
)

echo.
echo Dependencies installed successfully!
echo.

echo Running system test...
python test_setup.py

echo.
echo ========================================
echo Starting Traffic Flow Analysis...
echo ========================================
echo.
echo This will:
echo 1. Download the traffic video from YouTube
echo 2. Process the video with vehicle detection
echo 3. Generate output.csv with tracking data
echo 4. Create demo_video.mp4 with annotations
echo.
echo Processing may take several minutes depending on your system...
echo.

python traffic_flow.py

echo.
echo ========================================
echo Analysis Complete!
echo ========================================
echo.
echo Check the following files:
echo - output.csv (vehicle tracking data)
echo - demo_video.mp4 (annotated video)
echo - lane_config.json (lane configuration)
echo.

pause 
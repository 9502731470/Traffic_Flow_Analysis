# Traffic Flow Analysis System

A computer vision-based traffic flow analysis system using YOLOv8 + DeepSORT for vehicle detection, tracking, and lane-based counting.

##  New Features (Refactored Version)

###  **Visual Improvements**
- **Frame Resizing**: Automatically resizes frames to 960x540 for optimal YOLO detection
- **Lane Transparency**: Semi-transparent lane overlays (20% opacity) that don't block vehicle view
- **Cleaner Bounding Boxes**: Blue boxes with green IDs, smaller text for better visibility
- **Improved Count Display**: Lane counts above each lane, total counts at top in yellow

###  **Configuration Management**
- **Easy Lane Adjustment**: Use `configure_lanes.py` to modify lane coordinates without editing code
- **JSON Configuration**: All settings stored in `lane_config.json` for easy modification
- **Automatic Scaling**: Lane coordinates automatically scale with frame resizing

###  **Technical Enhancements**
- **YOLO Confidence**: Set to 0.4 for reduced false positives
- **Optimized Processing**: Frame resizing before detection ensures accurate bounding boxes
- **Modular Design**: Clean, well-commented code structure

##  Quick Start

### 1. Install Dependencies
   ```bash
   pip install -r requirements.txt
   ```

### 2. Run Analysis
   ```bash
   python traffic_flow.py
   ```

### 3. Adjust Lane Positions (Optional)
```bash
python configure_lanes.py
```

## 📁 Project Structure

```
Traffic Flow Analysis/
├── traffic_flow.py          # Main analysis script (refactored)
├── configure_lanes.py       # Lane configuration utility
├── lane_config.json         # Lane coordinates and settings
├── test_setup.py           # System testing script
├── requirements.txt         # Python dependencies
├── README.md               # This file
└── PROJECT_SUMMARY.md      # Detailed project overview
```

##  Visual Features

### Lane Display
- **Thickness**: 2 pixels (thin and clean)
- **Transparency**: 20% opacity using `cv2.addWeighted()`
- **Colors**: Cyan (0, 255, 255) for lane boundaries
- **Labels**: White text showing lane counts above each lane

### Vehicle Detection
- **Bounding Boxes**: Blue (255, 0, 0) with thickness 2
- **Vehicle IDs**: Green (0, 255, 0) text, smaller size (0.4 scale)
- **Frame Size**: 960x540 for optimal YOLO performance
- **Confidence**: 0.4 threshold to reduce false positives

### Count Display
- **Lane Counts**: White text above each lane (L1: xx, L2: xx, L3: xx)
- **Total Count**: Yellow text at top (Total - L1: xx | L2: xx | L3: xx)

##  Configuration

### Lane Configuration (`lane_config.json`)
```json
{
  "lanes": [
    [[100, 720], [500, 400]],   # Lane 1: bottom-left to top-right
    [[550, 720], [900, 400]],   # Lane 2: bottom-left to top-right
    [[950, 720], [1300, 400]]   # Lane 3: bottom-left to top-right
  ],
  "target_frame_size": [960, 540],
  "description": "Lane coordinates for traffic flow analysis"
}
```

### Adjusting Lane Positions
1. **Interactive Mode**: Run `python configure_lanes.py`
2. **Manual Edit**: Modify `lane_config.json` directly
3. **Coordinate Format**: `[x1, y1]` (bottom-left) to `[x2, y2]` (top-right)

##  Technical Details

### Frame Processing Pipeline
1. **Input**: Original video frame (any resolution)
2. **Resize**: Scale to 960x540 for YOLO detection
3. **Detection**: YOLOv8 with confidence threshold 0.4
4. **Tracking**: DeepSORT for vehicle ID assignment
5. **Scaling**: Convert coordinates back to original frame size
6. **Overlay**: Apply semi-transparent lanes and bounding boxes

### Performance Optimizations
- **Frame Resizing**: Reduces YOLO processing time while maintaining accuracy
- **Confidence Threshold**: Balances detection accuracy vs. false positives
- **Efficient Drawing**: Uses `cv2.addWeighted()` for smooth transparency

## 📊 Output Files

### CSV Output (`output.csv`)
- **VehicleID**: Unique tracking identifier
- **Lane**: Lane number (1, 2, or 3)
- **Frame**: Frame number when vehicle was detected
- **Timestamp**: Time in HH:MM:SS format

### Video Output (`demo_video.mp4`)
- **Resolution**: Same as input video
- **Overlays**: All lanes, bounding boxes, and counts
- **Format**: MP4 with H.264 codec

##  Testing

Run the test suite to verify system functionality:
```bash
python test_setup.py
```

Tests cover:
- Lane configuration loading/saving
- Frame resizing functionality
- Lane drawing with transparency
- Configuration file operations
- YOLO model integration

##  Troubleshooting

### Common Issues
1. **Lane Misalignment**: Use `configure_lanes.py` to adjust coordinates
2. **Poor Detection**: Check if frame resizing is working correctly
3. **Performance Issues**: Ensure GPU acceleration is available for YOLO

### Performance Tips
- **GPU Usage**: Install CUDA-enabled PyTorch for faster YOLO inference
- **Frame Skip**: Modify the main loop to process every Nth frame for speed
- **Resolution**: Lower target frame size for faster processing (trade-off with accuracy)

##  Future Enhancements

- **Multi-lane Support**: Dynamic lane detection
- **Traffic Light Integration**: Count vehicles during green/red phases
- **Speed Estimation**: Calculate vehicle speeds using frame analysis
- **Web Interface**: Real-time monitoring dashboard

##  Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests for new functionality
5. Submit a pull request


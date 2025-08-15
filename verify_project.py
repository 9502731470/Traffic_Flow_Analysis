#!/usr/bin/env python3
"""
Project Verification Script for Refactored Traffic Flow Analysis

This script verifies that all refactored components are working correctly
and the project is ready to run.
"""

import os
import json
import importlib
import sys

def check_files():
    """Check if all required files exist"""
    print("Checking project files...")
    
    required_files = [
        "traffic_flow.py",
        "configure_lanes.py", 
        "lane_config.json",
        "test_setup.py",
        "requirements.txt",
        "README.md"
    ]
    
    missing_files = []
    for file in required_files:
        if os.path.exists(file):
            print(f"✓ {file}")
        else:
            print(f"✗ {file} (missing)")
            missing_files.append(file)
    
    if missing_files:
        print(f"\n❌ Missing files: {', '.join(missing_files)}")
        return False
    
    print("✓ All required files present")
    return True

def check_dependencies():
    """Check if required Python packages can be imported"""
    print("\nChecking Python dependencies...")
    
    required_packages = [
        ("cv2", "OpenCV"),
        ("numpy", "NumPy"),
        ("pandas", "Pandas"),
        ("ultralytics", "Ultralytics (YOLOv8)"),
        ("deep_sort_realtime", "DeepSORT Realtime"),
        ("yt_dlp", "yt-dlp")
    ]
    
    missing_packages = []
    for package, name in required_packages:
        try:
            importlib.import_module(package)
            print(f"✓ {name}")
        except ImportError:
            print(f"✗ {name} ({package})")
            missing_packages.append(name)
    
    if missing_packages:
        print(f"\n❌ Missing packages: {', '.join(missing_packages)}")
        print("Install with: pip install -r requirements.txt")
        return False
    
    print("✓ All dependencies available")
    return True

def check_lane_config():
    """Check if lane configuration is valid"""
    print("\nChecking lane configuration...")
    
    try:
        with open("lane_config.json", "r") as f:
            config = json.load(f)
        
        # Check required fields
        required_fields = ["lanes", "target_frame_size", "description"]
        for field in required_fields:
            if field not in config:
                print(f"✗ Missing field: {field}")
                return False
        
        # Check lanes structure
        lanes = config["lanes"]
        if not isinstance(lanes, list) or len(lanes) != 3:
            print(f"✗ Invalid lanes structure: expected 3 lanes, got {len(lanes)}")
            return False
        
        # Check target frame size
        target_size = config["target_frame_size"]
        if target_size != [960, 540]:
            print(f"✗ Invalid target frame size: expected [960, 540], got {target_size}")
            return False
        
        print("✓ Lane configuration is valid")
        return True
        
    except Exception as e:
        print(f"✗ Error reading lane configuration: {e}")
        return False

def check_code_quality():
    """Check if refactored code has expected improvements"""
    print("\nChecking code quality improvements...")
    
    try:
        with open("traffic_flow.py", "r") as f:
            code = f.read()
        
        improvements = [
            ("Frame resizing to 960x540", "target_width = 960" in code and "target_height = 540" in code),
            ("YOLO confidence threshold 0.4", "conf=0.4" in code),
            ("Lane transparency", "cv2.addWeighted" in code),
            ("Thinner lane rectangles", "cv2.rectangle" in code and "2)" in code),
            ("Blue bounding boxes", "(255, 0, 0)" in code),
            ("Green vehicle IDs", "(0, 255, 0)" in code),
            ("Frame resizing before detection", "cv2.resize(frame, (self.target_width, self.target_height)" in code)
        ]
        
        all_improvements = True
        for improvement, found in improvements:
            if found:
                print(f"✓ {improvement}")
                else:
                print(f"✗ {improvement}")
                all_improvements = False
        
        return all_improvements
        
    except Exception as e:
        print(f"✗ Error checking code: {e}")
                    return False

def run_basic_test():
    """Run a basic test to ensure the system works"""
    print("\nRunning basic functionality test...")
    
    try:
        # Import the main class
        from traffic_flow import TrafficFlowAnalyzer
        
        # Create instance
        analyzer = TrafficFlowAnalyzer("test_url")
        
        # Check key attributes
        assert analyzer.target_width == 960, "Target width should be 960"
        assert analyzer.target_height == 540, "Target height should be 540"
        assert len(analyzer.lanes) == 3, "Should have 3 lanes"
        
        print("✓ Basic functionality test passed")
        return True
        
    except Exception as e:
        print(f"✗ Basic functionality test failed: {e}")
        return False

def main():
    """Main verification function"""
    print("=" * 60)
    print("TRAFFIC FLOW ANALYSIS - PROJECT VERIFICATION")
    print("=" * 60)
    
    checks = [
        ("Project Files", check_files),
        ("Dependencies", check_dependencies),
        ("Lane Configuration", check_lane_config),
        ("Code Quality", check_code_quality),
        ("Basic Functionality", run_basic_test)
    ]
    
    results = []
    for check_name, check_func in checks:
        try:
            result = check_func()
            results.append((check_name, result))
    except Exception as e:
            print(f"✗ {check_name} check failed with error: {e}")
            results.append((check_name, False))
    
    # Summary
    print("\n" + "=" * 60)
    print("VERIFICATION SUMMARY")
    print("=" * 60)
    
    passed = sum(1 for _, result in results if result)
    total = len(results)
    
    for check_name, result in results:
        status = "✓ PASS" if result else "✗ FAIL"
        print(f"{check_name}: {status}")
    
    print(f"\nOverall: {passed}/{total} checks passed")
    
    if passed == total:
        print("\n🎉 PROJECT VERIFICATION COMPLETE!")
        print("Your refactored Traffic Flow Analysis system is ready to use.")
        print("\nNext steps:")
        print("1. Run: python traffic_flow.py")
        print("2. Adjust lanes if needed: python configure_lanes.py")
        print("3. Run tests: python test_setup.py")
    else:
        print(f"\n⚠️  {total - passed} check(s) failed.")
        print("Please fix the issues before running the system.")
    
    print("=" * 60)
    return passed == total

if __name__ == "__main__":
    main() 
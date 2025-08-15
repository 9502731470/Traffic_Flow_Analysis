#!/usr/bin/env python3
"""
Lane Configuration Utility for Traffic Flow Analysis

This script helps you easily adjust lane coordinates for your traffic video.
Run this script to interactively modify lane positions.
"""

import json
import os
import cv2
import numpy as np

def load_lane_config():
    """Load existing lane configuration or create default"""
        if os.path.exists("lane_config.json"):
                with open("lane_config.json", "r") as f:
            return json.load(f)
        else:
        # Default configuration
        return {
            "lanes": [
                [[100, 720], [500, 400]],  # Lane 1
                [[550, 720], [900, 400]],  # Lane 2
                [[950, 720], [1300, 400]]  # Lane 3
            ],
            "target_frame_size": [960, 540],
            "description": "Lane coordinates for traffic flow analysis"
        }

def save_lane_config(config):
    """Save lane configuration to JSON file"""
        with open("lane_config.json", "w") as f:
            json.dump(config, f, indent=2)
    print("✓ Lane configuration saved to lane_config.json")

def draw_lanes_on_frame(frame, lanes, lane_counts=None):
    """Draw lanes on a frame for visualization"""
    frame_copy = frame.copy()
    
    # Draw lanes with transparency
    overlay = frame_copy.copy()
    for i, (p1, p2) in enumerate(lanes, 1):
        # Draw lane rectangle
        cv2.rectangle(overlay, tuple(p1), tuple(p2), (0, 255, 255), 2)
        
        # Draw lane number
        cv2.putText(frame_copy, f"L{i}", (p1[0], p1[1] - 10), 
                   cv2.FONT_HERSHEY_SIMPLEX, 0.8, (255, 255, 255), 2)
        
        # Draw count if provided
        if lane_counts:
            count_text = f"Count: {lane_counts.get(i, 0)}"
            cv2.putText(frame_copy, count_text, (p1[0], p1[1] - 35), 
                       cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255, 255, 255), 2)
    
    # Apply transparency
    alpha = 0.2
    result = cv2.addWeighted(overlay, alpha, frame_copy, 1 - alpha, 0)
    
    # Draw total count at top
    if lane_counts:
        total = sum(lane_counts.values())
        total_text = f"Total: {total} vehicles"
        cv2.putText(result, total_text, (10, 30), 
                       cv2.FONT_HERSHEY_SIMPLEX, 0.8, (0, 255, 255), 2)
    
    return result

def adjust_lane_coordinates():
    """Interactive lane coordinate adjustment"""
    config = load_lane_config()
    lanes = config["lanes"]
    
    print("Current lane configuration:")
    for i, (p1, p2) in enumerate(lanes, 1):
        print(f"Lane {i}: Start({p1[0]}, {p1[1]}) -> End({p2[0]}, {p2[1]})")
    
    print("\nOptions:")
    print("1. Adjust lane coordinates")
    print("2. View current configuration")
    print("3. Reset to defaults")
    print("4. Exit")
    
    while True:
        choice = input("\nEnter your choice (1-4): ").strip()
        
        if choice == "1":
            print("\nAdjusting lane coordinates...")
            print("Enter new coordinates for each lane.")
            print("Format: x1,y1 x2,y2 (e.g., 100,720 500,400)")
            
            for i in range(len(lanes)):
                while True:
                    try:
                        coords = input(f"Lane {i+1} (current: {lanes[i]}): ").strip()
                        if coords.lower() == 'skip':
                            break
                        
                        # Parse coordinates
                        parts = coords.split()
                        if len(parts) != 2:
                            print("Invalid format. Use: x1,y1 x2,y2")
                            continue
                        
                        p1 = [int(x) for x in parts[0].split(',')]
                        p2 = [int(x) for x in parts[1].split(',')]
                        
                        if len(p1) != 2 or len(p2) != 2:
                            print("Invalid coordinates. Use: x1,y1 x2,y2")
                            continue
                        
                        lanes[i] = [p1, p2]
                        print(f"✓ Lane {i+1} updated: {lanes[i]}")
                        break
                        
                    except ValueError:
                        print("Invalid input. Please enter valid numbers.")
                    except KeyboardInterrupt:
                        print("\nOperation cancelled.")
            return
        
        elif choice == "2":
            print("\nCurrent lane configuration:")
            for i, (p1, p2) in enumerate(lanes, 1):
                print(f"Lane {i}: Start({p1[0]}, {p1[1]}) -> End({p2[0]}, {p2[1]})")
        
        elif choice == "3":
            confirm = input("Reset to default configuration? (y/N): ").strip().lower()
            if confirm == 'y':
                lanes = [
                    [[100, 720], [500, 400]],  # Lane 1
                    [[550, 720], [900, 400]],  # Lane 2
                    [[950, 720], [1300, 400]]  # Lane 3
                ]
                print("✓ Reset to default configuration")
        
        elif choice == "4":
            break
        
        else:
            print("Invalid choice. Please enter 1-4.")
    
    # Save configuration
    config["lanes"] = lanes
    save_lane_config(config)
    
    print("\nLane configuration updated successfully!")
    return config

def preview_lanes():
    """Preview lanes on a sample frame if video exists"""
    if not os.path.exists("traffic_video.mp4"):
        print("No traffic_video.mp4 found. Please run the main analysis first.")
        return
    
    config = load_lane_config()
    lanes = config["lanes"]
    
    # Open video and get first frame
    cap = cv2.VideoCapture("traffic_video.mp4")
    ret, frame = cap.read()
    cap.release()
    
    if not ret:
        print("Could not read video frame.")
        return
    
    # Resize frame for better viewing
    height, width = frame.shape[:2]
    if width > 1200:
        scale = 1200 / width
        new_width = int(width * scale)
        new_height = int(height * scale)
        frame = cv2.resize(frame, (new_width, new_height))
        
        # Scale lane coordinates accordingly
        scale_x = new_width / width
        scale_y = new_height / height
        scaled_lanes = []
        for p1, p2 in lanes:
            scaled_p1 = [int(p1[0] * scale_x), int(p1[1] * scale_y)]
            scaled_p2 = [int(p2[0] * scale_x), int(p2[1] * scale_y)]
            scaled_lanes.append([scaled_p1, scaled_p2])
        lanes = scaled_lanes
    
    # Draw lanes on frame
    result_frame = draw_lanes_on_frame(frame, lanes)
    
    # Display frame
    cv2.imshow("Lane Preview (Press any key to close)", result_frame)
    cv2.waitKey(0)
        cv2.destroyAllWindows()

def main():
    """Main function"""
    print("=" * 50)
    print("LANE CONFIGURATION UTILITY")
    print("=" * 50)
    print("This utility helps you adjust lane coordinates for traffic flow analysis.")
    print("Make sure your traffic_video.mp4 is in the current directory.")
    
    while True:
        print("\nOptions:")
        print("1. Adjust lane coordinates")
        print("2. Preview lanes on video")
        print("3. View current configuration")
        print("4. Exit")
        
        choice = input("\nEnter your choice (1-4): ").strip()
        
        if choice == "1":
            adjust_lane_coordinates()
        elif choice == "2":
            preview_lanes()
        elif choice == "3":
            config = load_lane_config()
            print("\nCurrent lane configuration:")
            for i, (p1, p2) in enumerate(config["lanes"], 1):
                print(f"Lane {i}: Start({p1[0]}, {p1[1]}) -> End({p2[0]}, {p2[1]})")
        elif choice == "4":
            print("Exiting...")
            break
        else:
            print("Invalid choice. Please enter 1-4.")

if __name__ == "__main__":
    main() 
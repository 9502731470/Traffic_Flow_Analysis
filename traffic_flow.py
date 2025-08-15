import cv2
import numpy as np
import pandas as pd
import time
import yt_dlp
import os
from ultralytics import YOLO
from deep_sort_realtime.deepsort_tracker import DeepSort
import json

class TrafficFlowAnalyzer:
    def __init__(self, video_url, output_video_path="demo_video.mp4"):
        self.video_url = video_url
        self.output_video_path = output_video_path
        self.video_file = "traffic_video.mp4"
        
        # Target frame size for YOLO detection
        self.target_width = 960
        self.target_height = 540
        
        # Initialize models and tracker
        print("Loading YOLO model...")
        self.model = YOLO("yolov8n.pt")  # Pre-trained COCO model
        self.tracker = DeepSort(max_age=30)
        
        # Lane definitions (adjustable coordinates)
        self.lanes = [
            [(100, 720), (500, 400)],  # Lane 1 area points
            [(550, 720), (900, 400)],  # Lane 2 area points
            [(950, 720), (1300, 400)]  # Lane 3 area points
        ]
        
        # Initialize counters and data storage
        self.lane_counts = {1: 0, 2: 0, 3: 0}
        self.counted_ids = set()
        self.output_data = []
        
        # Video writer for demo video
        self.video_writer = None
        self.frame_width = 0
        self.frame_height = 0
        self.fps = 0
        
        # Load lane configuration if exists
        self.load_lane_config()
        
    def download_video(self):
        """Download video from YouTube URL"""
        if os.path.exists(self.video_file):
            print(f"Video file {self.video_file} already exists. Skipping download.")
            return
            
        print(f"Downloading video from {self.video_url}...")
        ydl_opts = {
            'outtmpl': self.video_file,
            'format': 'best[height<=720]',  # Limit to 720p for performance
            'quiet': True
        }
        
        try:
            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                ydl.download([self.video_url])
            print("Video download completed successfully!")
        except Exception as e:
            print(f"Error downloading video: {e}")
            raise
    
    def save_lane_config(self):
        """Save lane configuration to JSON file"""
        config = {
            "lanes": self.lanes,
            "description": "Lane coordinates for traffic flow analysis",
            "target_frame_size": [self.target_width, self.target_height]
        }
        with open("lane_config.json", "w") as f:
            json.dump(config, f, indent=2)
        print("Lane configuration saved to lane_config.json")
    
    def load_lane_config(self):
        """Load lane configuration from JSON file if it exists"""
        if os.path.exists("lane_config.json"):
            try:
                with open("lane_config.json", "r") as f:
                    config = json.load(f)
                    self.lanes = config["lanes"]
                    if "target_frame_size" in config:
                        self.target_width, self.target_height = config["target_frame_size"]
                    print("Lane configuration loaded from lane_config.json")
            except Exception as e:
                print(f"Error loading lane config: {e}")
                print("Using default lane configuration")
        else:
            print("No lane_config.json found. Using default configuration.")
            self.save_lane_config()
    
    def is_vehicle_in_lane(self, cx, cy):
        """Check if a vehicle center point is within any lane"""
        for lane_num, (p1, p2) in enumerate(self.lanes, start=1):
            # Check if point is within lane boundaries
            if p1[0] <= cx <= p2[0] and p1[1] >= cy >= p2[1]:
                return lane_num
        return None
    
    def process_frame(self, frame, frame_number):
        """Process a single frame for vehicle detection and tracking"""
        # Resize frame to target size for YOLO detection
        frame_resized = cv2.resize(frame, (self.target_width, self.target_height))
        
        # Run YOLO detection with confidence threshold 0.4
        results = self.model(frame_resized, verbose=False, conf=0.4)
        detections = []
        
        for r in results:
            for box in r.boxes:
                cls = int(box.cls[0])
                # Filter for vehicle classes
                if self.model.names[cls] in ["car", "truck", "bus", "motorbike"]:
                    x1, y1, x2, y2 = box.xyxy[0]
                    # Scale coordinates back to original frame size
                    scale_x = self.frame_width / self.target_width
                    scale_y = self.frame_height / self.target_height
                    x1, x2 = x1 * scale_x, x2 * scale_x
                    y1, y2 = y1 * scale_y, y2 * scale_y
                    detections.append(([x1, y1, x2, y2], box.conf[0], cls))
        
        # Update tracker
        tracks = self.tracker.update_tracks(detections, frame=frame)
        
        # Process tracked vehicles
        for track in tracks:
            if not track.is_confirmed():
                continue
                
            track_id = track.track_id
            ltrb = track.to_ltrb()
            x1, y1, x2, y2 = map(int, ltrb)
            cx, cy = (x1 + x2) // 2, (y1 + y2) // 2
            
            # Check lane assignment
            lane_num = self.is_vehicle_in_lane(cx, cy)
            if lane_num and track_id not in self.counted_ids:
                self.lane_counts[lane_num] += 1
                self.counted_ids.add(track_id)
                
                # Calculate timestamp
                timestamp = time.strftime("%H:%M:%S", time.gmtime(frame_number / self.fps))
                
                # Store data for CSV
                self.output_data.append({
                    "VehicleID": track_id,
                    "Lane": lane_num,
                    "Frame": frame_number,
                    "Timestamp": timestamp
                })
            
            # Draw vehicle bounding box (blue) and ID (green) with smaller text
            cv2.rectangle(frame, (x1, y1), (x2, y2), (255, 0, 0), 2)  # Blue box
            cv2.putText(frame, f"ID:{track_id}", (x1, y1-5), 
                       cv2.FONT_HERSHEY_SIMPLEX, 0.4, (0, 255, 0), 1)  # Green ID, smaller text
        
        # Draw lanes and counts
        self.draw_lanes_and_counts(frame)
        
        return frame
    
    def draw_lanes_and_counts(self, frame):
        """Draw lane boundaries and vehicle counts on frame with transparency"""
        # Create overlay for lanes
        overlay = frame.copy()
        
        for lane_num, (p1, p2) in enumerate(self.lanes, start=1):
            # Draw lane boundary (thinner, semi-transparent)
            cv2.rectangle(overlay, p1, p2, (0, 255, 255), 2)  # Thickness = 2
            
            # Draw lane count above each lane in white
            count_text = f"L{lane_num}: {self.lane_counts[lane_num]}"
            cv2.putText(frame, count_text, (p1[0], p1[1] - 10), 
                       cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255, 255, 255), 2)
        
        # Apply transparency to lanes (alpha=0.2 for 20% solid color)
        alpha = 0.2
        frame_with_lanes = cv2.addWeighted(overlay, alpha, frame, 1 - alpha, 0)
        
        # Draw total counts at top in yellow
        total_text = f"Total - L1: {self.lane_counts[1]} | L2: {self.lane_counts[2]} | L3: {self.lane_counts[3]}"
        cv2.putText(frame_with_lanes, total_text, (10, 30), 
                   cv2.FONT_HERSHEY_SIMPLEX, 0.8, (0, 255, 255), 2)
        
        # Copy the result back to original frame
        frame[:] = frame_with_lanes[:]
    
    def process_video(self):
        """Process the entire video and create demo output"""
        print("Processing video...")
        
        cap = cv2.VideoCapture(self.video_file)
        if not cap.isOpened():
            raise ValueError(f"Could not open video file: {self.video_file}")
        
        # Get video properties
        self.frame_width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
        self.frame_height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
        self.fps = cap.get(cv2.CAP_PROP_FPS)
        total_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
        
        print(f"Video properties: {self.frame_width}x{self.frame_height}, {self.fps} FPS, {total_frames} frames")
        print(f"Processing at target size: {self.target_width}x{self.target_height}")
        
        # Initialize video writer for demo
        fourcc = cv2.VideoWriter_fourcc(*'mp4v')
        self.video_writer = cv2.VideoWriter(
            self.output_video_path, fourcc, self.fps, 
            (self.frame_width, self.frame_height)
        )
        
        frame_count = 0
        start_time = time.time()
        
        while True:
            ret, frame = cap.read()
            if not ret:
                break
            
            frame_count += 1
            
            # Process frame
            processed_frame = self.process_frame(frame, frame_count)
            
            # Write to demo video
            self.video_writer.write(processed_frame)
            
            # Display progress
            if frame_count % 30 == 0:  # Update every 30 frames
                elapsed = time.time() - start_time
                fps_processing = frame_count / elapsed
                progress = (frame_count / total_frames) * 100
                print(f"Progress: {progress:.1f}% | FPS: {fps_processing:.1f} | Frame: {frame_count}/{total_frames}")
            
            # Show frame (optional - comment out for headless processing)
            # cv2.imshow("Traffic Flow Analysis", processed_frame)
            # if cv2.waitKey(1) & 0xFF == ord('q'):
            #     break
        
        # Cleanup
        cap.release()
        self.video_writer.release()
        cv2.destroyAllWindows()
        
        print("Video processing completed!")
    
    def save_results(self):
        """Save results to CSV and display summary"""
        # Save to CSV
        df = pd.DataFrame(self.output_data)
        df.to_csv("output.csv", index=False)
        print(f"Results saved to output.csv ({len(df)} records)")
        
        # Display summary
        print("\n" + "="*50)
        print("TRAFFIC FLOW ANALYSIS SUMMARY")
        print("="*50)
        print(f"Lane 1: {self.lane_counts[1]} vehicles")
        print(f"Lane 2: {self.lane_counts[2]} vehicles")
        print(f"Lane 3: {self.lane_counts[3]} vehicles")
        print(f"Total: {sum(self.lane_counts.values())} vehicles")
        print("="*50)
        
        # Save lane configuration
        self.save_lane_config()
    
    def run_analysis(self):
        """Run the complete traffic flow analysis"""
        try:
            # Step 1: Download video
            self.download_video()
            
            # Step 2: Process video
            self.process_video()
            
            # Step 3: Save results
            self.save_results()
            
            print(f"\nDemo video saved as: {self.output_video_path}")
            print("Analysis completed successfully!")
            
        except Exception as e:
            print(f"Error during analysis: {e}")
            raise

def main():
    """Main function to run the traffic flow analysis"""
    print("Traffic Flow Analysis System")
    print("="*40)
    
    # YouTube video URL
    video_url = "https://www.youtube.com/watch?v=MNn9qKG2UFI"
    
    # Create analyzer instance
    analyzer = TrafficFlowAnalyzer(video_url)

    analyzer.run_analysis()

if __name__ == "__main__":
    main() 
"""
PeopleCounter - Main Entry Point
A system for counting people using computer vision and object detection.
"""

import cv2
import numpy as np
from ultralytics import YOLO
import os
import sys
import webbrowser
import subprocess
import time

# Add utils to path
sys.path.append(os.path.dirname(__file__))
from utils.sort_tracker import Sort
from utils.report_generator import ReportGenerator

# If the web UI passed the uploaded filepath as an argument, capture it
UPLOADED_FILEPATH = sys.argv[1] if len(sys.argv) > 1 else None


def main():
    """Main function to run the people counter application."""
    print("PeopleCounter Application Starting...")
    
    # Load YOLO model
    print("Loading YOLOv8 model...")
    model = YOLO("yolov8n.pt")
    print("Model loaded successfully")
    
    # Initialize SORT tracker
    tracker = Sort(max_age=30, min_hits=3, iou_threshold=0.3)
    print("SORT tracker initialized")
    
    # Initialize report generator
    report_gen = ReportGenerator()
    
    # Initialize counters
    entry_count = 0
    exit_count = 0
    
    # Dictionary to track centroid positions for crossing detection
    # Format: {track_id: {'previous_y': y_coord, 'counted': False}}
    track_positions = {}
    
    # Set up video source
    video_path = os.path.join("data", "mall_entry.mp4")
    
    if not os.path.exists(video_path):
        print(f"Video file not found at {video_path}.")
        print("Launching web upload UI so you can upload a video.")

        # Try to start the Flask web UI (app.py) using the same Python executable
        try:
            python_exe = sys.executable
            app_py = os.path.join(os.path.dirname(__file__), 'app.py')
            if os.path.exists(app_py):
                subprocess.Popen([python_exe, app_py], cwd=os.path.dirname(__file__))
                # Give the server a moment to start
                time.sleep(1.5)
                webbrowser.open('http://127.0.0.1:5000')
                print("Web UI launched. Opened browser to http://127.0.0.1:5000")
            else:
                print("Web UI (app.py) not found. Please place your video in the data/ folder and rerun.")
        except Exception as e:
            print(f"Failed to launch web UI: {e}")

        return
    
    # Load video file
    cap = cv2.VideoCapture(video_path)
    
    if not cap.isOpened():
        print(f"Error: Could not open video file {video_path}")
        return
    
    print(f"Successfully loaded video: {video_path}")
    frame_width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
    frame_height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
    
    # Configure counting line position (configurable - default at 50% of frame height)
    counting_line_position = 0.5  # 0.0 to 1.0 (percentage of frame height)
    counting_line_y = int(frame_height * counting_line_position)
    
    # Margin for crossing detection (pixels)
    crossing_margin = 10
    
    print(f"Video Properties:")
    print(f"  Frame Width: {frame_width}")
    print(f"  Frame Height: {frame_height}")
    print(f"  FPS: {int(cap.get(cv2.CAP_PROP_FPS))}")
    print(f"  Total Frames: {int(cap.get(cv2.CAP_PROP_FRAME_COUNT))}")
    print(f"  Counting Line Y: {counting_line_y}")
    print("\nPress 'q' to quit")
    
    # Read and display frames
    frame_count = 0
    while True:
        ret, frame = cap.read()
        
        # Break if no more frames
        if not ret:
            print("End of video or cannot read frame")
            break
        
        frame_count += 1
        
        # Run YOLOv8 detection
        results = model(frame, verbose=False)
        
        # Extract detections for person class only (class 0)
        detections = []
        for result in results:
            boxes = result.boxes
            for box in boxes:
                # Get class ID
                class_id = int(box.cls[0])
                
                # Filter only persons (class 0)
                if class_id == 0:
                    # Get bounding box coordinates (x1, y1, x2, y2)
                    x1, y1, x2, y2 = box.xyxy[0].cpu().numpy()
                    confidence = float(box.conf[0])
                    
                    # Format for SORT: [x1, y1, x2, y2, confidence]
                    detections.append([x1, y1, x2, y2, confidence])
        
        # Convert to numpy array for SORT
        detections_np = np.array(detections) if len(detections) > 0 else np.empty((0, 5))
        
        # Update tracker with detections
        tracks = tracker.update(detections_np)
        
        # Track current active IDs
        current_track_ids = set()
        
        # Draw tracked objects and detect line crossings
        for track in tracks:
            bbox = track['bbox']
            track_id = track['track_id']
            current_centroid = track['current_centroid']
            previous_centroid = track['previous_centroid']
            
            current_track_ids.add(track_id)
            
            x1, y1, x2, y2 = bbox
            current_y = current_centroid[1]
            
            # Initialize tracking for new IDs
            if track_id not in track_positions:
                track_positions[track_id] = {
                    'previous_y': current_y,
                    'counted': False
                }
            
            # Check for line crossing
            previous_y = track_positions[track_id]['previous_y']
            
            # Detect crossing: person must move from one side to the other
            # ENTRY: crossing from top (y < line_y) to bottom (y > line_y) - downward
            # EXIT: crossing from bottom (y > line_y) to top (y < line_y) - upward
            
            if not track_positions[track_id]['counted']:
                # Check if crossing downward (ENTRY)
                if previous_y < counting_line_y and current_y > counting_line_y:
                    entry_count += 1
                    track_positions[track_id]['counted'] = True
                    report_gen.add_event('entry', track_id, frame_count)
                    print(f"ENTRY detected: ID {track_id} | Total Entry: {entry_count}")
                    
                    # Visual feedback - flash green
                    cv2.putText(frame, "ENTRY!", (x1, y1 - 30),
                               cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 0), 2)
                
                # Check if crossing upward (EXIT)
                elif previous_y > counting_line_y and current_y < counting_line_y:
                    exit_count += 1
                    track_positions[track_id]['counted'] = True
                    report_gen.add_event('exit', track_id, frame_count)
                    print(f"EXIT detected: ID {track_id} | Total Exit: {exit_count}")
                    
                    # Visual feedback - flash red
                    cv2.putText(frame, "EXIT!", (x1, y1 - 30),
                               cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 0, 255), 2)
            
            # Update previous position for next frame
            track_positions[track_id]['previous_y'] = current_y
            
            # Draw bounding box
            cv2.rectangle(frame, (x1, y1), (x2, y2), (0, 255, 0), 2)
            
            # Draw track ID
            cv2.putText(frame, f"ID: {track_id}", 
                       (x1, y1 - 10),
                       cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 255, 0), 2)
            
            # Draw current centroid
            cv2.circle(frame, (int(current_centroid[0]), int(current_centroid[1])), 
                      5, (0, 0, 255), -1)
            
            # Draw previous centroid and trajectory line if available
            if previous_centroid is not None:
                cv2.circle(frame, (int(previous_centroid[0]), int(previous_centroid[1])), 
                          3, (255, 0, 0), -1)
                cv2.line(frame, 
                        (int(previous_centroid[0]), int(previous_centroid[1])),
                        (int(current_centroid[0]), int(current_centroid[1])),
                        (255, 255, 0), 2)
        
        # Clean up old track positions for IDs no longer active
        track_positions = {tid: data for tid, data in track_positions.items() 
                          if tid in current_track_ids}
        
        # Draw counting line
        cv2.line(frame, (0, counting_line_y), (frame_width, counting_line_y), (0, 255, 255), 3)
        cv2.putText(frame, "COUNTING LINE", (frame_width - 200, counting_line_y - 10),
                   cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 255, 255), 2)
        
        # Draw ENTRY zone indicator (above the line)
        entry_zone_y = counting_line_y - 60
        cv2.putText(frame, "ENTRY ZONE", (10, entry_zone_y),
                   cv2.FONT_HERSHEY_SIMPLEX, 1.0, (0, 255, 0), 3)
        cv2.putText(frame, "(Cross DOWN = Entry)", (10, entry_zone_y + 30),
                   cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 0), 2)
        cv2.arrowedLine(frame, (200, entry_zone_y + 10), (200, counting_line_y - 20),
                       (0, 255, 0), 3, tipLength=0.3)
        
        # Draw EXIT zone indicator (below the line)
        exit_zone_y = counting_line_y + 80
        cv2.putText(frame, "EXIT ZONE", (10, exit_zone_y),
                   cv2.FONT_HERSHEY_SIMPLEX, 1.0, (0, 0, 255), 3)
        cv2.putText(frame, "(Cross UP = Exit)", (10, exit_zone_y + 30),
                   cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 0, 255), 2)
        cv2.arrowedLine(frame, (200, exit_zone_y - 10), (200, counting_line_y + 20),
                       (0, 0, 255), 3, tipLength=0.3)
        
        # Create semi-transparent overlay panel for statistics
        overlay = frame.copy()
        panel_width = 400
        panel_height = 320
        panel_x = 10
        panel_y = 10
        
        # Draw background rectangle
        cv2.rectangle(overlay, (panel_x, panel_y), 
                     (panel_x + panel_width, panel_y + panel_height), 
                     (0, 0, 0), -1)
        
        # Blend overlay with frame for transparency
        alpha = 0.6
        frame = cv2.addWeighted(overlay, alpha, frame, 1 - alpha, 0)
        
        # Information Panel - Header
        y_offset = panel_y + 30
        cv2.putText(frame, "=== COUNTING SYSTEM ===", 
                   (panel_x + 20, y_offset), 
                   cv2.FONT_HERSHEY_SIMPLEX, 0.8, (255, 255, 255), 2)
        
        y_offset += 45
        cv2.putText(frame, f"Frame: {frame_count} | Active Tracks: {len(tracks)}", 
                   (panel_x + 20, y_offset), 
                   cv2.FONT_HERSHEY_SIMPLEX, 0.6, (200, 200, 200), 2)
        
        # Divider line
        y_offset += 25
        cv2.line(frame, (panel_x + 20, y_offset), 
                (panel_x + panel_width - 20, y_offset), (150, 150, 150), 2)
        
        # Entry Statistics
        y_offset += 40
        cv2.putText(frame, "TOTAL ENTERED:", 
                   (panel_x + 20, y_offset), 
                   cv2.FONT_HERSHEY_SIMPLEX, 0.8, (0, 255, 0), 2)
        cv2.putText(frame, f"{entry_count}", 
                   (panel_x + 280, y_offset), 
                   cv2.FONT_HERSHEY_SIMPLEX, 1.2, (0, 255, 0), 3)
        
        # Divider line
        y_offset += 35
        cv2.line(frame, (panel_x + 20, y_offset), 
                (panel_x + panel_width - 20, y_offset), (150, 150, 150), 2)
        
        # Exit Statistics
        y_offset += 40
        cv2.putText(frame, "TOTAL EXITED:", 
                   (panel_x + 20, y_offset), 
                   cv2.FONT_HERSHEY_SIMPLEX, 0.8, (0, 0, 255), 2)
        cv2.putText(frame, f"{exit_count}", 
                   (panel_x + 280, y_offset), 
                   cv2.FONT_HERSHEY_SIMPLEX, 1.2, (0, 0, 255), 3)
        
        # Divider line
        y_offset += 35
        cv2.line(frame, (panel_x + 20, y_offset), 
                (panel_x + panel_width - 20, y_offset), (150, 150, 150), 2)
        
        # Current Inside
        y_offset += 40
        current_inside = entry_count - exit_count
        
        cv2.putText(frame, "CURRENTLY INSIDE:", 
                   (panel_x + 20, y_offset), 
                   cv2.FONT_HERSHEY_SIMPLEX, 0.8, (255, 255, 0), 2)
        cv2.putText(frame, f"{current_inside}", 
                   (panel_x + 280, y_offset), 
                   cv2.FONT_HERSHEY_SIMPLEX, 1.2, (255, 255, 0), 3)
        
        # Display the frame
        cv2.imshow("PeopleCounter - Mall Entry", frame)
        
        # Wait for 'q' key to quit (25ms delay between frames)
        if cv2.waitKey(25) & 0xFF == ord('q'):
            print("User requested exit")
            break
    
    # Release resources
    cap.release()
    cv2.destroyAllWindows()
    print("Application closed successfully")
    
    # Generate and open HTML report
    print("\n" + "="*50)
    print("GENERATING REPORT...")
    print("="*50)
    
    # Update final statistics
    report_gen.update_stats(
        entry_count=entry_count,
        exit_count=exit_count,
        total_frames=frame_count,
        video_file=video_path
    )
    
    # Generate HTML report
    report_path = report_gen.generate_html_report('people_counter_report.html')
    print(f"\n✅ Report generated: {report_path}")
    
    # Open report in default browser
    print("📊 Opening report in browser...")
    webbrowser.open('file://' + report_path)

    # Cleanup: remove the original uploaded file (in uploads/) and the copied data file
    try:
        if UPLOADED_FILEPATH and os.path.exists(UPLOADED_FILEPATH):
            os.remove(UPLOADED_FILEPATH)
            print(f"Removed uploaded file: {UPLOADED_FILEPATH}")
    except Exception as e:
        print(f"Warning: failed to remove uploaded file: {e}")

    try:
        copied_path = os.path.join(os.path.dirname(__file__), 'data', 'mall_entry.mp4')
        if os.path.exists(copied_path):
            os.remove(copied_path)
            print(f"Removed copied data file: {copied_path}")
    except Exception as e:
        print(f"Warning: failed to remove copied data file: {e}")
    
    print("\n" + "="*50)
    print("FINAL STATISTICS")
    print("="*50)
    print(f"Total Entries: {entry_count}")
    print(f"Total Exits: {exit_count}")
    print(f"Currently Inside: {entry_count - exit_count}")
    print(f"Total Frames Processed: {frame_count}")
    print("="*50)


if __name__ == "__main__":
    main()

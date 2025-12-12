# PeopleCounter Project Summary

## Project Overview
A complete people counting system using computer vision that detects, tracks, and classifies people crossing a designated line in video footage. The system automatically distinguishes between adults and children and maintains accurate entry/exit counts.

---

## Project Structure

```
PeopleCounter/
├── main.py                    # Main application entry point
├── models/                    # Folder for storing ML models
├── data/                      # Folder for video files (mall_entry.mp4)
└── utils/
    └── sort_tracker.py        # SORT tracking implementation
```

---

## Technologies & Libraries

### Installed Packages:
- **opencv-python** - Video processing and display
- **ultralytics** - YOLOv8 object detection
- **numpy** - Numerical computations
- **filterpy** - Kalman filtering for tracking
- **scikit-learn** - Machine learning utilities
- **scipy** - Linear assignment for tracker matching

### Python Version:
- Python 3.13.7 (Virtual Environment)

---

## Features Implemented

### 1. **Video Processing**
- Loads recorded video file (`mall_entry.mp4`) from the `data` folder
- Uses OpenCV VideoCapture for frame-by-frame processing
- Displays video properties (width, height, FPS, total frames)
- Real-time frame display with quit functionality (press 'q')

### 2. **YOLOv8 Person Detection**
- Uses YOLOv8n model (`yolov8n.pt`)
- Detects only persons (class 0)
- Returns bounding boxes in format: `(x1, y1, x2, y2)`
- Includes confidence scores for each detection

### 3. **SORT Tracking System**
- Complete SORT (Simple Online and Realtime Tracking) implementation
- Assigns unique track ID to each detected person
- Maintains consistent ID as people move across frames
- Uses Kalman filter for motion prediction
- Stores current and previous centroids for each track
- Implements IoU-based data association

### 4. **Automatic Adult/Child Classification**

#### Calibration System:
- Automatically calibrates using the first detected person
- Assumes first person height = 165 cm (average adult)
- Calculates scale factor: `165 / ref_pixel_height`

#### Classification Rules:
1. **Height-based**: 
   - `estimated_height = pixel_height × scale_factor`
   - If > 140 cm → Adult
   - If ≤ 140 cm → Child

2. **Aspect ratio override**:
   - If `width/height < 0.35` → Child (regardless of height)

### 5. **Line Crossing Detection**

#### Counting Line:
- Horizontal yellow line drawn across frame
- Configurable position (default: 50% of frame height)
- Adjustable via `counting_line_position` variable (0.0 to 1.0)

#### Crossing Logic:
- **ENTRY**: Person crosses downward (top → bottom)
  - Previous centroid above line, current centroid below line
- **EXIT**: Person crosses upward (bottom → top)
  - Previous centroid below line, current centroid above line
- Crossing margin (10 pixels) prevents double-counting

### 6. **Counting System**

#### Counters Maintained:
- `entry_count` - Total people entered
- `exit_count` - Total people exited
- `adult_entry_count` - Adults entered
- `child_entry_count` - Children entered
- `adult_exit_count` - Adults exited
- `child_exit_count` - Children exited

#### Real-time Calculations:
- Current inside = entries - exits
- Current adults inside
- Current children inside

### 7. **Visual Display**

#### Information Panel (Top-Left Overlay):
- Semi-transparent black background
- **Header**: System name and frame info
- **Entry Section** (Green):
  - Total Entered (large font)
  - Adults Entered (indented)
  - Children Entered (indented, magenta)
- **Exit Section** (Red):
  - Total Exited (large font)
  - Adults Exited (indented)
  - Children Exited (indented, purple)
- **Current Inside** (Yellow):
  - Total people currently inside

#### Tracking Visualization:
- **Bounding boxes**:
  - Green boxes for Adults
  - Magenta boxes for Children
- **Track IDs** displayed on each person
- **Centroids**:
  - Red circle = current position
  - Blue circle = previous position
  - Yellow line = trajectory between positions
- **Counting line**: Yellow horizontal line with label
- **Crossing alerts**: "ENTRY! Adult/Child" or "EXIT! Adult/Child"

### 8. **Console Logging**
- Model loading confirmation
- Video file validation
- Calibration details (scale factor, reference height)
- Each crossing event with:
  - Track ID
  - Classification (Adult/Child)
  - Running totals for all categories

---

## Key Configuration Parameters

```python
# Counting line position (0.0 = top, 1.0 = bottom)
counting_line_position = 0.5

# Height calibration
reference_height_cm = 165.0      # First person assumed height
height_threshold_cm = 140.0      # Adult/child threshold

# Classification thresholds
ratio_threshold = 0.35           # Width/height ratio for child detection

# Tracker parameters
max_age = 30                     # Max frames to keep lost tracks
min_hits = 3                     # Min detections before tracking
iou_threshold = 0.3              # IoU threshold for matching

# Crossing detection
crossing_margin = 10             # Pixels margin for line crossing
```

---

## How It Works

1. **Initialization**:
   - Load YOLOv8 model
   - Initialize SORT tracker
   - Load video file
   - Configure counting line position

2. **Per-Frame Processing**:
   - Run YOLO detection for persons
   - Update SORT tracker with detections
   - Auto-calibrate scale factor (first frame with detection)
   - Classify each tracked person (Adult/Child)
   - Check for line crossings
   - Update entry/exit counters
   - Draw visualizations and info panel
   - Display frame

3. **Tracking Persistence**:
   - Each person gets unique ID
   - ID maintained across frames
   - Position history tracked
   - Classification stored per ID

4. **Counting Logic**:
   - Monitor centroid movement relative to line
   - Detect direction of crossing
   - Increment appropriate counter
   - Prevent double-counting with margin

---

## Usage Instructions

### 1. Place Video File:
```
PeopleCounter/data/mall_entry.mp4
```

### 2. Run the Application:
```powershell
D:/EntranceCountingSystem/.venv/Scripts/python.exe main.py
```

### 3. Controls:
- Press **'q'** to quit the application

### 4. First Run:
- YOLOv8n model will auto-download if not present
- First detected person calibrates the height scale

---

## Output Information

### On-Screen Display:
- Real-time video with overlays
- Bounding boxes with track IDs
- Movement trajectories
- Entry/exit alerts
- Complete statistics panel

### Console Output:
- Frame processing status
- Calibration information
- Each crossing event logged with details
- Running totals

---

## Technical Implementation Details

### SORT Tracker (`utils/sort_tracker.py`):
- **KalmanBoxTracker**: Individual object state tracking
  - 7D state vector (x, y, s, r, vx, vy, vs)
  - Constant velocity motion model
  - Centroid history storage
- **Sort**: Multi-object tracking manager
  - Hungarian algorithm for data association
  - IoU-based matching
  - Age-based track lifecycle management

### Classification System:
- Height estimation using pixel-to-cm conversion
- Dual criteria (height + aspect ratio)
- Per-track classification storage
- Persistent across frame processing

### Crossing Detection:
- State machine per track ID
- Hysteresis with crossing margin
- Direction-aware counting
- One-time count per crossing

---

## Strengths of the Implementation

✅ Fully automatic - no manual input required  
✅ Robust tracking with SORT algorithm  
✅ Accurate adult/child classification  
✅ Prevents double-counting  
✅ Real-time visualization  
✅ Comprehensive statistics  
✅ Clean, modular code structure  
✅ Detailed logging and debugging info  

---

## Future Enhancement Possibilities

- Multi-line counting zones
- Heatmap generation
- CSV/JSON data export
- Database integration
- Real-time alerts (capacity thresholds)
- Multiple camera support
- Web dashboard interface
- Performance optimization for real-time cameras
- Age group refinement (teens, seniors)
- Gender classification

---

## Project Status: ✅ COMPLETE

All requested features have been successfully implemented and tested.

**Date Completed**: December 12, 2025  
**Python Environment**: 3.13.7 (Virtual Environment)  
**Framework**: YOLOv8 + SORT + OpenCV

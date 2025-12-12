"""
Web Report Generator for PeopleCounter
Generates an HTML report with all counting statistics
"""

import json
from datetime import datetime
import os


class ReportGenerator:
    """Generate HTML report for people counting results"""
    
    def __init__(self):
        self.data = {
            'timestamp': None,
            'video_file': None,
            'total_frames': 0,
            'entry_count': 0,
            'exit_count': 0,
            'current_inside': 0,
            'events': []
        }
    
    def add_event(self, event_type, track_id, frame_number):
        """Add a counting event"""
        self.data['events'].append({
            'type': event_type,
            'track_id': track_id,
            'frame': frame_number,
            'timestamp': datetime.now().strftime('%H:%M:%S')
        })
    
    def update_stats(self, entry_count, exit_count, total_frames, video_file):
        """Update overall statistics"""
        self.data['entry_count'] = entry_count
        self.data['exit_count'] = exit_count
        self.data['current_inside'] = entry_count - exit_count
        self.data['total_frames'] = total_frames
        self.data['video_file'] = video_file
        self.data['timestamp'] = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    
    def generate_html_report(self, output_path='report.html'):
        """Generate HTML report"""
        
        html_content = f"""
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>People Counter Report</title>
    <style>
        * {{
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }}
        
        body {{
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            padding: 20px;
            min-height: 100vh;
        }}
        
        .container {{
            max-width: 1200px;
            margin: 0 auto;
            background: white;
            border-radius: 15px;
            box-shadow: 0 20px 60px rgba(0,0,0,0.3);
            overflow: hidden;
        }}
        
        .header {{
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            padding: 40px;
            text-align: center;
        }}
        
        .header h1 {{
            font-size: 2.5em;
            margin-bottom: 10px;
            text-shadow: 2px 2px 4px rgba(0,0,0,0.2);
        }}
        
        .header p {{
            font-size: 1.1em;
            opacity: 0.9;
        }}
        
        .stats-grid {{
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
            gap: 20px;
            padding: 40px;
            background: #f8f9fa;
        }}
        
        .stat-card {{
            background: white;
            padding: 30px;
            border-radius: 10px;
            box-shadow: 0 4px 6px rgba(0,0,0,0.1);
            text-align: center;
            transition: transform 0.3s ease;
        }}
        
        .stat-card:hover {{
            transform: translateY(-5px);
            box-shadow: 0 8px 12px rgba(0,0,0,0.15);
        }}
        
        .stat-card h3 {{
            color: #6c757d;
            font-size: 0.9em;
            text-transform: uppercase;
            letter-spacing: 1px;
            margin-bottom: 15px;
        }}
        
        .stat-card .value {{
            font-size: 3em;
            font-weight: bold;
            margin-bottom: 10px;
        }}
        
        .stat-card.entry .value {{
            color: #28a745;
        }}
        
        .stat-card.exit .value {{
            color: #dc3545;
        }}
        
        .stat-card.inside .value {{
            color: #ffc107;
        }}
        
        .stat-card.frames .value {{
            color: #17a2b8;
        }}
        
        .info-section {{
            padding: 40px;
            background: white;
        }}
        
        .info-section h2 {{
            color: #343a40;
            margin-bottom: 20px;
            padding-bottom: 10px;
            border-bottom: 3px solid #667eea;
        }}
        
        .info-item {{
            display: flex;
            justify-content: space-between;
            padding: 15px;
            border-bottom: 1px solid #e9ecef;
        }}
        
        .info-item:last-child {{
            border-bottom: none;
        }}
        
        .info-label {{
            font-weight: 600;
            color: #495057;
        }}
        
        .info-value {{
            color: #6c757d;
        }}
        
        .events-section {{
            padding: 40px;
            background: #f8f9fa;
        }}
        
        .events-section h2 {{
            color: #343a40;
            margin-bottom: 20px;
            padding-bottom: 10px;
            border-bottom: 3px solid #667eea;
        }}
        
        .events-table {{
            width: 100%;
            background: white;
            border-radius: 10px;
            overflow: hidden;
            box-shadow: 0 2px 4px rgba(0,0,0,0.1);
        }}
        
        .events-table table {{
            width: 100%;
            border-collapse: collapse;
        }}
        
        .events-table th {{
            background: #343a40;
            color: white;
            padding: 15px;
            text-align: left;
            font-weight: 600;
            text-transform: uppercase;
            font-size: 0.85em;
            letter-spacing: 1px;
        }}
        
        .events-table td {{
            padding: 15px;
            border-bottom: 1px solid #e9ecef;
        }}
        
        .events-table tr:last-child td {{
            border-bottom: none;
        }}
        
        .events-table tr:hover {{
            background: #f8f9fa;
        }}
        
        .event-badge {{
            display: inline-block;
            padding: 5px 15px;
            border-radius: 20px;
            font-size: 0.85em;
            font-weight: 600;
            text-transform: uppercase;
        }}
        
        .event-badge.entry {{
            background: #d4edda;
            color: #155724;
        }}
        
        .event-badge.exit {{
            background: #f8d7da;
            color: #721c24;
        }}
        
        .footer {{
            background: #343a40;
            color: white;
            text-align: center;
            padding: 20px;
            font-size: 0.9em;
        }}
        
        @media print {{
            body {{
                background: white;
                padding: 0;
            }}
            
            .stat-card:hover {{
                transform: none;
            }}
        }}
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>📊 People Counter Report</h1>
            <p>Video Analysis Results</p>
        </div>
        
        <div class="stats-grid">
            <div class="stat-card entry">
                <h3>Total Entered</h3>
                <div class="value">{self.data['entry_count']}</div>
                <p>People entered the area</p>
            </div>
            
            <div class="stat-card exit">
                <h3>Total Exited</h3>
                <div class="value">{self.data['exit_count']}</div>
                <p>People left the area</p>
            </div>
            
            <div class="stat-card inside">
                <h3>Currently Inside</h3>
                <div class="value">{self.data['current_inside']}</div>
                <p>Net people count</p>
            </div>
            
            <div class="stat-card frames">
                <h3>Total Frames</h3>
                <div class="value">{self.data['total_frames']}</div>
                <p>Frames processed</p>
            </div>
        </div>
        
        <div class="info-section">
            <h2>Session Information</h2>
            <div class="info-item">
                <span class="info-label">Video File:</span>
                <span class="info-value">{self.data['video_file']}</span>
            </div>
            <div class="info-item">
                <span class="info-label">Analysis Date & Time:</span>
                <span class="info-value">{self.data['timestamp']}</span>
            </div>
            <div class="info-item">
                <span class="info-label">Total Events Detected:</span>
                <span class="info-value">{len(self.data['events'])}</span>
            </div>
        </div>
        
        <div class="events-section">
            <h2>Detailed Events Log</h2>
            <div class="events-table">
                <table>
                    <thead>
                        <tr>
                            <th>#</th>
                            <th>Event Type</th>
                            <th>Track ID</th>
                            <th>Frame Number</th>
                            <th>Time</th>
                        </tr>
                    </thead>
                    <tbody>
"""
        
        # Add events to table
        if self.data['events']:
            for idx, event in enumerate(self.data['events'], 1):
                event_type = event['type'].upper()
                badge_class = event['type'].lower()
                html_content += f"""
                        <tr>
                            <td>{idx}</td>
                            <td><span class="event-badge {badge_class}">{event_type}</span></td>
                            <td>ID: {event['track_id']}</td>
                            <td>{event['frame']}</td>
                            <td>{event['timestamp']}</td>
                        </tr>
"""
        else:
            html_content += """
                        <tr>
                            <td colspan="5" style="text-align: center; color: #6c757d;">No events recorded</td>
                        </tr>
"""
        
        html_content += """
                    </tbody>
                </table>
            </div>
        </div>
        
        <div class="footer">
            <p>&copy; 2025 PeopleCounter System | Generated with YOLOv8 + SORT Tracking</p>
        </div>
    </div>
    
    <script>
        // Auto-refresh animation
        document.addEventListener('DOMContentLoaded', function() {
            const statCards = document.querySelectorAll('.stat-card');
            statCards.forEach((card, index) => {
                card.style.animation = `fadeIn 0.5s ease-in-out ${index * 0.1}s both`;
            });
        });
        
        // Add CSS animation
        const style = document.createElement('style');
        style.textContent = `
            @keyframes fadeIn {
                from {
                    opacity: 0;
                    transform: translateY(20px);
                }
                to {
                    opacity: 1;
                    transform: translateY(0);
                }
            }
        `;
        document.head.appendChild(style);
    </script>
</body>
</html>
"""
        
        # Write HTML file
        with open(output_path, 'w', encoding='utf-8') as f:
            f.write(html_content)
        
        return os.path.abspath(output_path)

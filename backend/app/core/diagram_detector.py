import cv2
import numpy as np
from typing import List, Dict, Tuple, Optional
from enum import Enum

class DiagramType(Enum):
    FLOWCHART = "flowchart"
    CIRCUIT = "circuit"
    GRAPH = "graph"
    TABLE = "table"
    TREE = "tree"
    UNKNOWN = "unknown"

class DiagramDetector:
    """Detect and classify diagrams in images"""
    
    def __init__(self):
        self.min_diagram_area = 5000  # Minimum area for diagram detection
        
    def detect_diagrams(self, image_path: str) -> List[Dict]:
        """Detect diagrams in image"""
        image = cv2.imread(image_path)
        gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
        
        diagrams = []
        
        # Detect different types of diagrams
        diagrams.extend(self._detect_circuits(gray))
        diagrams.extend(self._detect_flowcharts(gray))
        diagrams.extend(self._detect_graphs(gray))
        diagrams.extend(self._detect_tables(gray))
        
        return diagrams
    
    def _detect_circuits(self, gray: np.ndarray) -> List[Dict]:
        """Detect circuit diagrams"""
        circuits = []
        
        # Look for circuit-specific patterns
        # Circles (components)
        circles = cv2.HoughCircles(
            gray, 
            cv2.HOUGH_GRADIENT, 
            dp=1, 
            minDist=20,
            param1=50, 
            param2=30, 
            minRadius=10, 
            maxRadius=50
        )
        
        if circles is not None and len(circles[0]) > 3:
            # Multiple circles connected might be a circuit
            x_coords = circles[0][:, 0]
            y_coords = circles[0][:, 1]
            
            x_min, x_max = int(np.min(x_coords)), int(np.max(x_coords))
            y_min, y_max = int(np.min(y_coords)), int(np.max(y_coords))
            
            circuits.append({
                'type': DiagramType.CIRCUIT.value,
                'bbox': (x_min, y_min, x_max - x_min, y_max - y_min),
                'confidence': min(len(circles[0]) / 10, 1.0),
                'components': len(circles[0])
            })
        
        return circuits
    
    def _detect_flowcharts(self, gray: np.ndarray) -> List[Dict]:
        """Detect flowchart diagrams"""
        flowcharts = []
        
        # Detect rectangles and diamonds (flowchart shapes)
        edges = cv2.Canny(gray, 50, 150)
        contours, _ = cv2.findContours(edges, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
        
        rectangles = []
        for contour in contours:
            # Approximate contour to polygon
            epsilon = 0.02 * cv2.arcLength(contour, True)
            approx = cv2.approxPolyDP(contour, epsilon, True)
            
            # Rectangle has 4 vertices
            if len(approx) == 4:
                x, y, w, h = cv2.boundingRect(contour)
                if w * h > self.min_diagram_area:
                    rectangles.append((x, y, w, h))
        
        # If multiple rectangles are found in proximity, likely a flowchart
        if len(rectangles) > 2:
            # Find bounding box of all rectangles
            x_coords = [r[0] for r in rectangles] + [r[0] + r[2] for r in rectangles]
            y_coords = [r[1] for r in rectangles] + [r[1] + r[3] for r in rectangles]
            
            x_min, x_max = min(x_coords), max(x_coords)
            y_min, y_max = min(y_coords), max(y_coords)
            
            flowcharts.append({
                'type': DiagramType.FLOWCHART.value,
                'bbox': (x_min, y_min, x_max - x_min, y_max - y_min),
                'confidence': min(len(rectangles) / 5, 1.0),
                'shapes': len(rectangles)
            })
        
        return flowcharts
    
    def _detect_graphs(self, gray: np.ndarray) -> List[Dict]:
        """Detect graph/tree structures"""
        graphs = []
        
        # Detect nodes (circles) and edges (lines)
        # This is simplified - real implementation would be more complex
        
        # Detect lines using Hough transform
        edges = cv2.Canny(gray, 50, 150)
        lines = cv2.HoughLinesP(edges, 1, np.pi/180, threshold=50, minLineLength=30, maxLineGap=10)
        
        if lines is not None and len(lines) > 5:
            # Multiple connected lines might be a graph
            x_coords = []
            y_coords = []
            
            for line in lines:
                x1, y1, x2, y2 = line[0]
                x_coords.extend([x1, x2])
                y_coords.extend([y1, y2])
            
            if x_coords and y_coords:
                x_min, x_max = min(x_coords), max(x_coords)
                y_min, y_max = min(y_coords), max(y_coords)
                
                area = (x_max - x_min) * (y_max - y_min)
                if area > self.min_diagram_area:
                    graphs.append({
                        'type': DiagramType.GRAPH.value,
                        'bbox': (x_min, y_min, x_max - x_min, y_max - y_min),
                        'confidence': min(len(lines) / 20, 1.0),
                        'edges': len(lines)
                    })
        
        return graphs
    
    def _detect_tables(self, gray: np.ndarray) -> List[Dict]:
        """Detect table structures"""
        tables = []
        
        # Detect horizontal and vertical lines
        horizontal_kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (40, 1))
        vertical_kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (1, 40))
        
        # Apply morphology operations
        _, binary = cv2.threshold(gray, 127, 255, cv2.THRESH_BINARY_INV)
        
        h_lines = cv2.morphologyEx(binary, cv2.MORPH_OPEN, horizontal_kernel)
        v_lines = cv2.morphologyEx(binary, cv2.MORPH_OPEN, vertical_kernel)
        
        # Find intersections
        intersections = cv2.bitwise_and(h_lines, v_lines)
        
        # Count intersections
        intersection_points = cv2.findNonZero(intersections)
        
        if intersection_points is not None and len(intersection_points) > 4:
            # Multiple intersections suggest a table
            points = intersection_points.reshape(-1, 2)
            x_min, y_min = np.min(points, axis=0)
            x_max, y_max = np.max(points, axis=0)
            
            tables.append({
                'type': DiagramType.TABLE.value,
                'bbox': (x_min, y_min, x_max - x_min, y_max - y_min),
                'confidence': min(len(intersection_points) / 20, 1.0),
                'cells': len(intersection_points)
            })
        
        return tables
    
    def classify_diagram(self, image_region: np.ndarray) -> DiagramType:
        """Classify a diagram region"""
        # This is a placeholder - implement actual classification
        # Could use a trained model or more sophisticated heuristics
        return DiagramType.UNKNOWN

# Global instance
diagram_detector = DiagramDetector()
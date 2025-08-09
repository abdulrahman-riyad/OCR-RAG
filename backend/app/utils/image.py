import cv2
import numpy as np
from PIL import Image, ImageEnhance, ImageFilter
from typing import Tuple, Optional
import io

class ImageProcessor:
    """Image preprocessing utilities"""
    
    @staticmethod
    def enhance_image(image_path: str, output_path: Optional[str] = None) -> str:
        """Enhance image for better OCR"""
        # Open image with PIL
        image = Image.open(image_path)
        
        # Convert to RGB if necessary
        if image.mode != 'RGB':
            image = image.convert('RGB')
        
        # Enhance contrast
        enhancer = ImageEnhance.Contrast(image)
        image = enhancer.enhance(1.5)
        
        # Enhance sharpness
        enhancer = ImageEnhance.Sharpness(image)
        image = enhancer.enhance(2.0)
        
        # Apply slight denoising
        image = image.filter(ImageFilter.MedianFilter(size=3))
        
        # Save enhanced image
        if output_path is None:
            output_path = image_path.replace('.', '_enhanced.')
        
        image.save(output_path, quality=95)
        return output_path
    
    @staticmethod
    def deskew_image(image_path: str) -> np.ndarray:
        """Deskew a scanned image"""
        image = cv2.imread(image_path)
        gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
        
        # Detect edges
        edges = cv2.Canny(gray, 50, 150, apertureSize=3)
        
        # Detect lines using Hough transform
        lines = cv2.HoughLines(edges, 1, np.pi/180, 200)
        
        if lines is not None:
            # Calculate the average angle
            angles = []
            for rho, theta in lines[:, 0]:
                angle = (theta * 180 / np.pi) - 90
                if -45 < angle < 45:  # Filter out vertical lines
                    angles.append(angle)
            
            if angles:
                median_angle = np.median(angles)
                
                # Rotate image
                if abs(median_angle) > 0.5:  # Only rotate if skew is significant
                    (h, w) = image.shape[:2]
                    center = (w // 2, h // 2)
                    M = cv2.getRotationMatrix2D(center, median_angle, 1.0)
                    image = cv2.warpAffine(image, M, (w, h), 
                                         flags=cv2.INTER_CUBIC,
                                         borderMode=cv2.BORDER_REPLICATE)
        
        return image
    
    @staticmethod
    def remove_shadows(image_path: str) -> np.ndarray:
        """Remove shadows from image"""
        image = cv2.imread(image_path)
        
        # Convert to LAB color space
        lab = cv2.cvtColor(image, cv2.COLOR_BGR2LAB)
        l, a, b = cv2.split(lab)
        
        # Apply CLAHE to L channel
        clahe = cv2.createCLAHE(clipLimit=3.0, tileGridSize=(8, 8))
        l = clahe.apply(l)
        
        # Merge channels
        enhanced = cv2.merge([l, a, b])
        
        # Convert back to BGR
        result = cv2.cvtColor(enhanced, cv2.COLOR_LAB2BGR)
        
        return result
    
    @staticmethod
    def segment_image(image_path: str) -> list:
        """Segment image into regions (text, diagrams, etc.)"""
        image = cv2.imread(image_path)
        gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
        
        # Apply threshold
        _, binary = cv2.threshold(gray, 0, 255, cv2.THRESH_BINARY_INV + cv2.THRESH_OTSU)
        
        # Find connected components
        num_labels, labels, stats, centroids = cv2.connectedComponentsWithStats(binary, connectivity=8)
        
        regions = []
        for i in range(1, num_labels):  # Skip background (label 0)
            x, y, w, h, area = stats[i]
            
            if area > 100:  # Filter small noise
                regions.append({
                    'bbox': (x, y, w, h),
                    'area': area,
                    'centroid': centroids[i].tolist()
                })
        
        return regions
    
    @staticmethod
    def resize_image(image_path: str, max_width: int = 2048) -> str:
        """Resize image if too large"""
        image = Image.open(image_path)
        
        if image.width > max_width:
            ratio = max_width / image.width
            new_height = int(image.height * ratio)
            image = image.resize((max_width, new_height), Image.Resampling.LANCZOS)
            
            output_path = image_path.replace('.', '_resized.')
            image.save(output_path, quality=95)
            return output_path
        
        return image_path

# Global instance
image_processor = ImageProcessor()
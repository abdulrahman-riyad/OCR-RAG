import cv2
import numpy as np
from typing import List, Dict, Tuple, Optional
import re

class MathOCR:
    """Specialized OCR for mathematical expressions"""
    
    def __init__(self):
        # Mathematical symbols mapping
        self.math_symbols = {
            'integral': '∫',
            'sum': '∑',
            'product': '∏',
            'sqrt': '√',
            'infinity': '∞',
            'alpha': 'α',
            'beta': 'β',
            'gamma': 'γ',
            'delta': 'δ',
            'theta': 'θ',
            'lambda': 'λ',
            'mu': 'μ',
            'pi': 'π',
            'sigma': 'σ',
            'phi': 'φ',
            'omega': 'ω'
        }
        
    def detect_math_regions(self, image_path: str) -> List[Dict]:
        """Detect regions likely containing mathematical expressions"""
        image = cv2.imread(image_path)
        gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
        
        # Apply edge detection
        edges = cv2.Canny(gray, 50, 150)
        
        # Find contours
        contours, _ = cv2.findContours(edges, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
        
        math_regions = []
        for contour in contours:
            x, y, w, h = cv2.boundingRect(contour)
            
            # Filter based on aspect ratio and size (math expressions tend to be horizontal)
            aspect_ratio = w / h if h > 0 else 0
            area = w * h
            
            if 0.5 < aspect_ratio < 10 and area > 500:
                math_regions.append({
                    'bbox': (x, y, w, h),
                    'confidence': self._calculate_math_confidence(gray[y:y+h, x:x+w])
                })
        
        return sorted(math_regions, key=lambda r: r['confidence'], reverse=True)
    
    def _calculate_math_confidence(self, region: np.ndarray) -> float:
        """Calculate confidence that a region contains math"""
        # Simple heuristic based on density of non-text patterns
        _, binary = cv2.threshold(region, 127, 255, cv2.THRESH_BINARY)
        
        # Count horizontal and vertical lines (common in fractions, matrices)
        horizontal_kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (25, 1))
        vertical_kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (1, 25))
        
        h_lines = cv2.morphologyEx(binary, cv2.MORPH_OPEN, horizontal_kernel)
        v_lines = cv2.morphologyEx(binary, cv2.MORPH_OPEN, vertical_kernel)
        
        h_count = cv2.countNonZero(h_lines)
        v_count = cv2.countNonZero(v_lines)
        
        # More lines = more likely to be math
        line_score = min((h_count + v_count) / (region.shape[0] * region.shape[1]), 1.0)
        
        return line_score
    
    def extract_latex_from_text(self, text: str) -> List[str]:
        """Extract and convert mathematical expressions to LaTeX"""
        latex_expressions = []
        
        # Pattern for simple equations
        equation_pattern = r'([a-zA-Z0-9\s\+\-\*\/\=\(\)]+)'
        equations = re.findall(equation_pattern, text)
        
        for eq in equations:
            if '=' in eq and len(eq) > 3:
                latex = self._convert_to_latex(eq)
                if latex:
                    latex_expressions.append(latex)
        
        return latex_expressions
    
    def _convert_to_latex(self, expression: str) -> str:
        """Convert simple expression to LaTeX format"""
        # Clean expression
        expr = expression.strip()
        
        # Simple conversions
        replacements = {
            '^2': '^{2}',
            '^3': '^{3}',
            'x2': 'x^2',
            'x3': 'x^3',
            'sqrt': r'\sqrt',
            '+-': r'\pm',
            '>=': r'\geq',
            '<=': r'\leq',
            '!=': r'\neq',
            'sum': r'\sum',
            'int': r'\int',
        }
        
        for old, new in replacements.items():
            expr = expr.replace(old, new)
        
        # Wrap in math mode if not already
        if not expr.startswith('$'):
            expr = f'${expr}$'
        
        return expr
    
    def process_math_image(self, image_path: str, text: str) -> Dict:
        """Process image for mathematical content"""
        math_regions = self.detect_math_regions(image_path)
        latex_expressions = self.extract_latex_from_text(text)
        
        return {
            'math_regions': len(math_regions),
            'latex_expressions': latex_expressions,
            'has_complex_math': len(math_regions) > 2 or any('\\' in expr for expr in latex_expressions),
            'recommended_processing': 'latex' if latex_expressions else 'standard'
        }

# Global instance
math_ocr = MathOCR()
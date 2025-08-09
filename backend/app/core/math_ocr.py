import cv2
import numpy as np
from typing import List, Dict, Tuple, Optional
import re
from pix2tex import cli as pix2tex_cli
from PIL import Image
import tempfile
import os

class MathOCR:
    """Specialized OCR for mathematical expressions using pix2tex"""
    
    def __init__(self):
        # Initialize pix2tex model
        self.model = None
        self._load_model()
        
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
    
    def _load_model(self):
        """Load pix2tex model"""
        try:
            # Initialize pix2tex
            from pix2tex.cli import LatexOCR
            self.model = LatexOCR()
            print("Pix2tex model loaded successfully")
        except Exception as e:
            print(f"Failed to load pix2tex model: {str(e)}")
            self.model = None
    
    def extract_math_from_image(self, image_path: str) -> Dict[str, any]:
        """Extract mathematical expressions from image using pix2tex"""
        results = {
            'latex_expressions': [],
            'math_regions': [],
            'success': False
        }
        
        if not self.model:
            print("Pix2tex model not available")
            return results
        
        try:
            # Open image
            img = Image.open(image_path)
            
            # Convert to RGB if necessary
            if img.mode != 'RGB':
                img = img.convert('RGB')
            
            # Extract LaTeX using pix2tex
            latex_result = self.model(img)
            
            if latex_result:
                results['latex_expressions'].append(latex_result)
                results['success'] = True
                
            # Detect math regions for more targeted extraction
            math_regions = self.detect_math_regions(image_path)
            
            # Extract LaTeX from each region
            for region in math_regions[:5]:  # Limit to 5 regions
                x, y, w, h = region['bbox']
                
                # Crop region
                region_img = img.crop((x, y, x + w, y + h))
                
                # Save to temporary file
                with tempfile.NamedTemporaryFile(suffix='.png', delete=False) as tmp:
                    region_img.save(tmp.name)
                    
                    try:
                        # Extract LaTeX from region
                        region_latex = self.model(Image.open(tmp.name))
                        if region_latex and region_latex not in results['latex_expressions']:
                            results['latex_expressions'].append(region_latex)
                            results['math_regions'].append({
                                'bbox': region['bbox'],
                                'latex': region_latex
                            })
                    except:
                        pass
                    finally:
                        os.unlink(tmp.name)
            
            return results
            
        except Exception as e:
            print(f"Error in pix2tex extraction: {str(e)}")
            return results
    
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
    
    def process_math_image(self, image_path: str, text: str = "") -> Dict:
        """Process image for mathematical content"""
        # Extract math using pix2tex
        pix2tex_results = self.extract_math_from_image(image_path)
        
        # Also try to extract from OCR text
        text_expressions = self.extract_latex_from_text(text) if text else []
        
        # Combine results
        all_expressions = list(set(pix2tex_results['latex_expressions'] + text_expressions))
        
        return {
            'latex_expressions': all_expressions,
            'math_regions': pix2tex_results['math_regions'],
            'has_complex_math': len(all_expressions) > 0,
            'recommended_processing': 'latex' if all_expressions else 'standard',
            'pix2tex_success': pix2tex_results['success']
        }
    
    def extract_latex_from_text(self, text: str) -> List[str]:
        """Extract and convert mathematical expressions to LaTeX from text"""
        latex_expressions = []
        
        # Pattern for simple equations
        equation_pattern = r'([a-zA-Z0-9\s\+\-\*\/\=\(\)]+)='
        equations = re.findall(equation_pattern, text)
        
        for eq in equations:
            if len(eq) > 3:
                latex = self._convert_to_latex(eq + '=')
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

# Global instance
math_ocr = MathOCR()
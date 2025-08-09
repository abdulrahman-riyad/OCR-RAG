from pylatex import Document, Section, Subsection, Package, Command, NewPage
from pylatex.utils import NoEscape, bold
import os
from typing import Dict, Any, List, Optional
import re

class LaTeXGenerator:
    def __init__(self):
        self.doc = None
        
    def create_document(self, title: str = "Digitized Notes") -> Document:
        """Create a new LaTeX document"""
        # Create document with standard packages
        doc = Document(documentclass='article')
        
        # Add packages
        doc.packages.append(Package('geometry', options=['margin=1in']))
        doc.packages.append(Package('amsmath'))
        doc.packages.append(Package('amssymb'))
        doc.packages.append(Package('graphicx'))
        doc.packages.append(Package('hyperref'))
        doc.packages.append(Package('fancyhdr'))
        doc.packages.append(Package('enumitem'))
        
        # Add title
        doc.preamble.append(Command('title', title))
        doc.preamble.append(Command('date', NoEscape(r'\today')))
        doc.append(NoEscape(r'\maketitle'))
        
        self.doc = doc
        return doc
    
    def add_text_content(self, text: str, structure: Optional[Dict] = None):
        """Add text content with proper formatting"""
        if not self.doc:
            self.create_document()
        
        # Process text into paragraphs
        paragraphs = text.split('\n\n')
        
        for para in paragraphs:
            if para.strip():
                # Check for equations
                if self._is_equation(para):
                    self._add_equation(para)
                # Check for lists
                elif self._is_list(para):
                    self._add_list(para)
                # Regular paragraph
                else:
                    self.doc.append(para.strip())
                    self.doc.append(NoEscape(r'\par'))
    
    def _is_equation(self, text: str) -> bool:
        """Check if text is likely an equation"""
        equation_indicators = ['=', '∫', '∑', '∂', '√', 'x²', 'y²']
        return any(indicator in text for indicator in equation_indicators)
    
    def _add_equation(self, equation: str):
        """Add equation with proper LaTeX formatting"""
        # Clean up equation
        equation = equation.strip()
        
        # Simple replacements for common patterns
        replacements = {
            'x²': 'x^2',
            'y²': 'y^2',
            '√': r'\sqrt',
            '∫': r'\int',
            '∑': r'\sum',
            '±': r'\pm',
            '≤': r'\leq',
            '≥': r'\geq',
            '≠': r'\neq',
            'α': r'\alpha',
            'β': r'\beta',
            'γ': r'\gamma',
            'θ': r'\theta',
            'π': r'\pi',
        }
        
        for old, new in replacements.items():
            equation = equation.replace(old, new)
        
        # Add equation environment
        self.doc.append(NoEscape(r'\begin{equation}'))
        self.doc.append(NoEscape(equation))
        self.doc.append(NoEscape(r'\end{equation}'))
    
    def _is_list(self, text: str) -> bool:
        """Check if text is a list"""
        lines = text.strip().split('\n')
        if len(lines) < 2:
            return False
        
        # Check for numbered lists or bullet points
        list_patterns = [r'^\d+\.', r'^-', r'^\*', r'^•']
        return any(re.match(pattern, lines[0].strip()) for pattern in list_patterns)
    
    def _add_list(self, text: str):
        """Add list with proper formatting"""
        lines = text.strip().split('\n')
        
        # Determine list type
        if re.match(r'^\d+\.', lines[0].strip()):
            self.doc.append(NoEscape(r'\begin{enumerate}'))
            list_type = 'enumerate'
        else:
            self.doc.append(NoEscape(r'\begin{itemize}'))
            list_type = 'itemize'
        
        for line in lines:
            # Clean line
            line = re.sub(r'^[\d\.\-\*•]\s*', '', line.strip())
            if line:
                self.doc.append(NoEscape(r'\item ' + line))
        
        self.doc.append(NoEscape(r'\end{' + list_type + '}'))
    
    def add_section(self, title: str):
        """Add a new section"""
        if self.doc:
            self.doc.append(Section(title))
    
    def add_subsection(self, title: str):
        """Add a new subsection"""
        if self.doc:
            self.doc.append(Subsection(title))
    
    def generate_pdf(self, output_path: str, clean_tex: bool = True) -> str:
        """Generate PDF from LaTeX document"""
        if not self.doc:
            raise ValueError("No document to generate")
        
        # Generate PDF
        try:
            # Save without extension - pylatex adds it
            base_path = output_path.replace('.pdf', '')
            self.doc.generate_pdf(base_path, clean_tex=clean_tex, compiler='pdflatex')
            
            return f"{base_path}.pdf"
        except Exception as e:
            print(f"Error generating PDF: {str(e)}")
            # Try to at least save the .tex file
            tex_path = f"{base_path}.tex"
            self.doc.generate_tex(tex_path)
            return tex_path

# Global instance
latex_generator = LaTeXGenerator()
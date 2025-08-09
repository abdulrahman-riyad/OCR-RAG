from reportlab.lib.pagesizes import letter, A4
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, PageBreak
from reportlab.platypus import Table, TableStyle
from reportlab.lib import colors
from typing import List, Dict, Any
import os

class PDFGenerator:
    """Alternative PDF generator using ReportLab (doesn't require LaTeX)"""
    
    def __init__(self):
        self.styles = getSampleStyleSheet()
        self._create_custom_styles()
    
    def _create_custom_styles(self):
        """Create custom paragraph styles"""
        self.styles.add(ParagraphStyle(
            name='CustomTitle',
            parent=self.styles['Heading1'],
            fontSize=24,
            textColor=colors.HexColor('#1a1a1a'),
            spaceAfter=30,
            alignment=1  # Center
        ))
        
        self.styles.add(ParagraphStyle(
            name='CustomHeading',
            parent=self.styles['Heading2'],
            fontSize=16,
            textColor=colors.HexColor('#333333'),
            spaceBefore=20,
            spaceAfter=10
        ))
        
        self.styles.add(ParagraphStyle(
            name='CustomBody',
            parent=self.styles['BodyText'],
            fontSize=11,
            leading=16,
            spaceBefore=6,
            spaceAfter=6
        ))
    
    def create_pdf(self, 
                   output_path: str,
                   title: str,
                   content: str,
                   metadata: Dict[str, Any] = None) -> str:
        """Create a PDF from text content"""
        
        # Create document
        doc = SimpleDocTemplate(
            output_path,
            pagesize=letter,
            rightMargin=72,
            leftMargin=72,
            topMargin=72,
            bottomMargin=18
        )
        
        # Container for the 'Flowable' objects
        elements = []
        
        # Add title
        elements.append(Paragraph(title, self.styles['CustomTitle']))
        elements.append(Spacer(1, 0.2 * inch))
        
        # Add metadata if provided
        if metadata:
            self._add_metadata_table(elements, metadata)
            elements.append(Spacer(1, 0.3 * inch))
        
        # Process content
        self._process_content(elements, content)
        
        # Build PDF
        doc.build(elements)
        
        return output_path
    
    def _add_metadata_table(self, elements: List, metadata: Dict[str, Any]):
        """Add metadata as a table"""
        data = []
        for key, value in metadata.items():
            data.append([key.replace('_', ' ').title(), str(value)])
        
        if data:
            table = Table(data, colWidths=[2*inch, 4*inch])
            table.setStyle(TableStyle([
                ('BACKGROUND', (0, 0), (0, -1), colors.grey),
                ('TEXTCOLOR', (0, 0), (0, -1), colors.whitesmoke),
                ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
                ('FONTNAME', (0, 0), (0, -1), 'Helvetica-Bold'),
                ('FONTSIZE', (0, 0), (-1, -1), 10),
                ('BOTTOMPADDING', (0, 0), (-1, -1), 6),
                ('GRID', (0, 0), (-1, -1), 1, colors.black)
            ]))
            elements.append(table)
    
    def _process_content(self, elements: List, content: str):
        """Process content into PDF elements"""
        # Split content into paragraphs
        paragraphs = content.split('\n\n')
        
        for para in paragraphs:
            para = para.strip()
            if not para:
                continue
            
            # Check if it's a heading (simple heuristic)
            if len(para) < 50 and not para.endswith('.'):
                elements.append(Paragraph(para, self.styles['CustomHeading']))
            else:
                # Process lists
                if self._is_list_item(para):
                    self._add_list(elements, para)
                else:
                    elements.append(Paragraph(para, self.styles['CustomBody']))
    
    def _is_list_item(self, text: str) -> bool:
        """Check if text is a list item"""
        patterns = [r'^\d+\.', r'^-', r'^\*', r'^•']
        import re
        return any(re.match(pattern, text.strip()) for pattern in patterns)
    
    def _add_list(self, elements: List, text: str):
        """Add list items"""
        lines = text.split('\n')
        for line in lines:
            if line.strip():
                # Add bullet point
                bullet_text = "• " + line.strip().lstrip('•*-0123456789. ')
                elements.append(Paragraph(bullet_text, self.styles['CustomBody']))

# Global instance
pdf_generator = PDFGenerator()
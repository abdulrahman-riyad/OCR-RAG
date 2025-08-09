from PIL import Image, ImageDraw, ImageFont
import random
import os

def generate_test_image(text, output_path, image_size=(800, 600)):
    """Generate a test image with text"""
    
    # Create white background
    img = Image.new('RGB', image_size, color='white')
    draw = ImageDraw.Draw(img)
    
    # Try to use a font, fallback to default if not available
    try:
        font = ImageFont.truetype("arial.ttf", 24)
    except:
        font = ImageFont.load_default()
    
    # Add text
    y_offset = 50
    for line in text.split('\n'):
        draw.text((50, y_offset), line, fill='black', font=font)
        y_offset += 40
    
    # Add some noise for realism
    for _ in range(100):
        x = random.randint(0, image_size[0])
        y = random.randint(0, image_size[1])
        draw.point((x, y), fill='gray')
    
    # Save image
    img.save(output_path, 'JPEG', quality=95)
    print(f"Generated: {output_path}")

def generate_math_test_image(output_path):
    """Generate test image with mathematical content"""
    
    math_content = """Mathematical Equations Test

Linear Equation:
y = mx + b

Quadratic Formula:
x = (-b ± √(b² - 4ac)) / 2a

Integration:
∫ x² dx = x³/3 + C

Summation:
∑(i=1 to n) i = n(n+1)/2

Matrix:
[1  2  3]
[4  5  6]
[7  8  9]

Trigonometry:
sin²θ + cos²θ = 1
"""
    
    generate_test_image(math_content, output_path, (800, 800))

def generate_diagram_test_image(output_path):
    """Generate test image with simple diagrams"""
    
    img = Image.new('RGB', (800, 600), color='white')
    draw = ImageDraw.Draw(img)
    
    # Draw a simple flowchart
    # Box 1
    draw.rectangle([100, 50, 250, 100], outline='black', width=2)
    draw.text((140, 65), "Start", fill='black')
    
    # Arrow
    draw.line([175, 100, 175, 150], fill='black', width=2)
    draw.polygon([175, 150, 170, 140, 180, 140], fill='black')
    
    # Box 2
    draw.rectangle([100, 150, 250, 200], outline='black', width=2)
    draw.text((130, 165), "Process", fill='black')
    
    # Arrow
    draw.line([175, 200, 175, 250], fill='black', width=2)
    draw.polygon([175, 250, 170, 240, 180, 240], fill='black')
    
    # Box 3
    draw.rectangle([100, 250, 250, 300], outline='black', width=2)
    draw.text((145, 265), "End", fill='black')
    
    # Add title
    draw.text((50, 20), "Simple Flowchart Diagram", fill='black')
    
    # Draw a simple graph on the right
    # Axes
    draw.line([400, 300, 400, 100], fill='black', width=2)  # Y-axis
    draw.line([400, 300, 600, 300], fill='black', width=2)  # X-axis
    
    # Plot points
    points = [(420, 280), (460, 240), (500, 220), (540, 180), (580, 160)]
    for i in range(len(points)-1):
        draw.line([points[i], points[i+1]], fill='blue', width=2)
    
    for point in points:
        draw.ellipse([point[0]-3, point[1]-3, point[0]+3, point[1]+3], fill='red')
    
    draw.text((450, 320), "Simple Graph", fill='black')
    
    img.save(output_path, 'JPEG', quality=95)
    print(f"Generated: {output_path}")

def generate_test_dataset(output_dir="test_images"):
    """Generate a complete test dataset"""
    
    os.makedirs(output_dir, exist_ok=True)
    
    # Generate text samples
    samples = [
        ("simple_text.jpg", "This is a simple test document.\nIt contains multiple lines.\nFor testing OCR accuracy."),
        ("paragraph.jpg", """This is a longer paragraph of text that contains multiple sentences. 
It is designed to test how well the OCR system handles continuous text with proper spacing and punctuation. 
The goal is to ensure that the system can accurately extract text from images that resemble real documents."""),
        ("list.jpg", """Shopping List:
1. Milk
2. Bread
3. Eggs
4. Butter
5. Cheese

Notes:
- Buy organic if possible
- Check expiration dates
- Use coupons"""),
    ]
    
    for filename, content in samples:
        generate_test_image(content, os.path.join(output_dir, filename))
    
    # Generate special test images
    generate_math_test_image(os.path.join(output_dir, "math_equations.jpg"))
    generate_diagram_test_image(os.path.join(output_dir, "diagrams.jpg"))
    
    print(f"\nGenerated {len(samples) + 2} test images in {output_dir}/")

if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description="Generate test images for OCR")
    parser.add_argument("--output", default="test_images", help="Output directory")
    
    args = parser.parse_args()
    
    generate_test_dataset(args.output)
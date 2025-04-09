from PIL import Image, ImageDraw, ImageFont
import os

def create_icon():
    # Create a 256x256 image with a white background
    size = 256
    image = Image.new('RGBA', (size, size), (255, 255, 255, 0))
    draw = ImageDraw.Draw(image)
    
    # Draw a medical cross
    cross_color = (0, 120, 212)  # Blue color
    cross_width = 40
    margin = 50
    
    # Draw vertical line
    draw.rectangle(
        [(size//2 - cross_width//2, margin),
         (size//2 + cross_width//2, size - margin)],
        fill=cross_color
    )
    
    # Draw horizontal line
    draw.rectangle(
        [(margin, size//2 - cross_width//2),
         (size - margin, size//2 + cross_width//2)],
        fill=cross_color
    )
    
    # Add text
    try:
        font = ImageFont.truetype("arial.ttf", 40)
    except:
        font = ImageFont.load_default()
    
    text = "MNT"
    text_bbox = draw.textbbox((0, 0), text, font=font)
    text_width = text_bbox[2] - text_bbox[0]
    text_height = text_bbox[3] - text_bbox[1]
    
    text_position = (
        (size - text_width) // 2,
        (size - text_height) // 2
    )
    
    draw.text(text_position, text, fill=(255, 255, 255), font=font)
    
    # Save as ICO file
    image.save('icon.ico', format='ICO', sizes=[(256, 256)])
    print("Icon created successfully: icon.ico")

if __name__ == "__main__":
    create_icon() 
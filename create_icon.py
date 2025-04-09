from PIL import Image, ImageDraw, ImageFont
import os
from pathlib import Path
import sys

def create_icon():
    try:
        # Create a 256x256 image with a transparent background
        size = 256
        image = Image.new('RGBA', (size, size), (0, 0, 0, 0))
        draw = ImageDraw.Draw(image)
        
        # Colors
        primary_color = (0, 120, 212)     # Microsoft blue
        accent_color = (255, 255, 255)    # White
        
        # Draw a rounded rectangle background
        padding = 20
        corner_radius = 30
        rect_bounds = [padding, padding, size - padding, size - padding]
        
        # Helper function to draw rounded rectangle
        def rounded_rectangle(draw, bounds, radius, color):
            x1, y1, x2, y2 = bounds
            diameter = radius * 2
            
            # Draw main rectangle
            draw.rectangle([x1 + radius, y1, x2 - radius, y2], fill=color)
            draw.rectangle([x1, y1 + radius, x2, y2 - radius], fill=color)
            
            # Draw corners
            draw.ellipse([x1, y1, x1 + diameter, y1 + diameter], fill=color)
            draw.ellipse([x2 - diameter, y1, x2, y1 + diameter], fill=color)
            draw.ellipse([x1, y2 - diameter, x1 + diameter, y2], fill=color)
            draw.ellipse([x2 - diameter, y2 - diameter, x2, y2], fill=color)
        
        # Draw background
        rounded_rectangle(draw, rect_bounds, corner_radius, primary_color)
        
        # Draw medical cross
        cross_padding = 60
        cross_width = 30
        
        # Vertical line of cross
        draw.rectangle(
            [size//2 - cross_width//2, cross_padding,
             size//2 + cross_width//2, size - cross_padding],
            fill=accent_color
        )
        
        # Horizontal line of cross
        draw.rectangle(
            [cross_padding, size//2 - cross_width//2,
             size - cross_padding, size//2 + cross_width//2],
            fill=accent_color
        )
        
        # Add text
        try:
            # Try to use Arial font, fallback to default if not available
            font_size = 48
            try:
                font = ImageFont.truetype("arial.ttf", font_size)
            except:
                try:
                    # Try common font locations
                    font_paths = [
                        "C:\\Windows\\Fonts\\arial.ttf",
                        "/usr/share/fonts/truetype/arial.ttf",
                        "/Library/Fonts/Arial.ttf"
                    ]
                    for path in font_paths:
                        try:
                            font = ImageFont.truetype(path, font_size)
                            break
                        except:
                            continue
                    else:
                        raise Exception("Could not find Arial font")
                except:
                    font = ImageFont.load_default()
            
            text = "MNT"
            # Get text size
            text_bbox = draw.textbbox((0, 0), text, font=font)
            text_width = text_bbox[2] - text_bbox[0]
            text_height = text_bbox[3] - text_bbox[1]
            
            # Position text at bottom
            text_x = (size - text_width) // 2
            text_y = size - cross_padding - text_height - 10
            
            # Draw text with slight shadow for depth
            shadow_offset = 2
            draw.text((text_x + shadow_offset, text_y + shadow_offset), text, 
                     fill=(0, 0, 0, 100), font=font)  # Shadow
            draw.text((text_x, text_y), text, 
                     fill=accent_color, font=font)     # Main text
        except Exception as e:
            print(f"Warning: Could not add text to icon: {e}")
        
        # Save in multiple sizes for better quality
        icon_sizes = [(16, 16), (32, 32), (48, 48), (64, 64), (128, 128), (256, 256)]
        
        # Create temporary images for each size
        images = []
        for size in icon_sizes:
            resized_image = image.resize(size, Image.Resampling.LANCZOS)
            images.append(resized_image)
        
        # Save as ICO file with multiple sizes
        icon_path = Path('icon.ico')
        image.save(icon_path, format='ICO', sizes=icon_sizes)
        print(f"Icon created successfully: {icon_path.absolute()}")
        
    except Exception as e:
        print(f"Error creating icon: {e}")
        raise

if __name__ == "__main__":
    try:
        create_icon()
    except Exception as e:
        print(f"Failed to create icon: {e}")
        sys.exit(1) 
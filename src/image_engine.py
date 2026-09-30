import os
import textwrap
from typing import Tuple, List, Optional
from PIL import Image, ImageDraw, ImageFont

WIDTH = 1080
HEIGHT = 1080

def get_font(size: int, bold: bool = False) -> ImageFont.ImageFont:
    """
    Attempts to load high-quality system TrueType fonts with cross-platform fallback.
    """
    font_candidates: List[str] = []
    
    if bold:
        font_candidates = [
            "C:/Windows/Fonts/segoeuib.ttf",
            "C:/Windows/Fonts/arialbd.ttf",
            "C:/Windows/Fonts/calibrib.ttf",
            "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf",
            "/usr/share/fonts/truetype/liberation/LiberationSans-Bold.ttf",
            "/System/Library/Fonts/HelveticaNeue-Bold.otf",
            "/Library/Fonts/Arial Bold.ttf",
            "arialbd.ttf",
            "DejaVuSans-Bold.ttf"
        ]
    else:
        font_candidates = [
            "C:/Windows/Fonts/segoeui.ttf",
            "C:/Windows/Fonts/arial.ttf",
            "C:/Windows/Fonts/calibri.ttf",
            "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf",
            "/usr/share/fonts/truetype/liberation/LiberationSans-Regular.ttf",
            "/System/Library/Fonts/HelveticaNeue.otf",
            "/Library/Fonts/Arial.ttf",
            "arial.ttf",
            "DejaVuSans.ttf"
        ]

    for candidate in font_candidates:
        if os.path.exists(candidate):
            try:
                return ImageFont.truetype(candidate, size)
            except Exception:
                continue

    # Try simple name loading
    for name in (["arialbd.ttf", "segoeuib.ttf"] if bold else ["arial.ttf", "segoeui.ttf"]):
        try:
            return ImageFont.truetype(name, size)
        except Exception:
            pass

    return ImageFont.load_default()

def draw_gradient_background(draw: ImageDraw.ImageDraw, width: int, height: int):
    """
    Renders a premium dark radial/linear gradient background with subtle ambient color.
    """
    # Base dark gradient from #0A0D14 to #121826
    top_color = (10, 13, 20)
    bottom_color = (18, 24, 38)
    
    for y in range(height):
        factor = y / height
        r = int(top_color[0] + (bottom_color[0] - top_color[0]) * factor)
        g = int(top_color[1] + (bottom_color[1] - top_color[1]) * factor)
        b = int(top_color[2] + (bottom_color[2] - top_color[2]) * factor)
        draw.line([(0, y), (width, y)], fill=(r, g, b))

def draw_ambient_glow(img: Image.Image):
    """
    Adds subtle ambient glow accents to give a modern tech agency aesthetic.
    """
    glow_overlay = Image.new("RGBA", (WIDTH, HEIGHT), (0, 0, 0, 0))
    glow_draw = ImageDraw.Draw(glow_overlay)
    
    # Top-right cyan accent
    glow_draw.ellipse([WIDTH - 300, -100, WIDTH + 300, 500], fill=(56, 189, 248, 25))
    # Bottom-left purple accent
    glow_draw.ellipse([-200, HEIGHT - 450, 400, HEIGHT + 150], fill=(139, 92, 246, 25))
    
    # Subtle decorative grid dots
    for x in range(80, WIDTH - 80, 80):
        for y in range(80, 240, 80):
            glow_draw.ellipse([x-2, y-2, x+2, y+2], fill=(255, 255, 255, 18))
            
    img.paste(Image.alpha_composite(img.convert("RGBA"), glow_overlay), (0, 0))

def render_post_image(
    headline: str,
    badge: str = "WEB DEVELOPMENT INSIGHT",
    output_path: str = "output/post.jpg"
) -> str:
    """
    Renders a 1080x1080 Instagram post graphic with custom branding for blackman.in.
    """
    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    
    img = Image.new("RGB", (WIDTH, HEIGHT), color=(10, 13, 20))
    draw = ImageDraw.Draw(img)
    
    # 1. Background
    draw_gradient_background(draw, WIDTH, HEIGHT)
    draw_ambient_glow(img)
    draw = ImageDraw.Draw(img)  # Re-acquire draw context after alpha paste
    
    # 2. Outer Border / Card Outline
    card_margin = 50
    card_rect = [card_margin, card_margin, WIDTH - card_margin, HEIGHT - card_margin]
    draw.rounded_rectangle(card_rect, radius=28, outline=(40, 50, 75), width=2)

    # 3. Top Category Badge
    badge_font = get_font(24, bold=True)
    badge_text = badge.upper()
    badge_bbox = draw.textbbox((0, 0), badge_text, font=badge_font)
    badge_w = badge_bbox[2] - badge_bbox[0]
    badge_h = badge_bbox[3] - badge_bbox[1]
    
    badge_x = (WIDTH - badge_w) // 2
    badge_y = 145
    pill_pad_x = 28
    pill_pad_y = 14
    pill_rect = [
        badge_x - pill_pad_x,
        badge_y - pill_pad_y,
        badge_x + badge_w + pill_pad_x,
        badge_y + badge_h + pill_pad_y
    ]
    # Pill background and border
    draw.rounded_rectangle(pill_rect, radius=20, fill=(18, 28, 48), outline=(56, 189, 248), width=2)
    draw.text((badge_x, badge_y - 1), badge_text, font=badge_font, fill=(56, 189, 248))

    # 4. Central Headline Text
    headline_font_size = 54 if len(headline) < 70 else 46
    headline_font = get_font(headline_font_size, bold=True)
    
    wrap_width = 24 if len(headline) < 70 else 28
    wrapped_lines = textwrap.wrap(headline, width=wrap_width)
    
    # Calculate vertical centering
    line_height = int(headline_font_size * 1.35)
    total_text_height = len(wrapped_lines) * line_height
    start_y = 360 + (280 - total_text_height) // 2
    
    # Draw quotes icon / aesthetic quotation mark
    quote_font = get_font(80, bold=True)
    draw.text((120, start_y - 75), "\u201C", font=quote_font, fill=(56, 189, 248, 120))

    for i, line in enumerate(wrapped_lines):
        line_bbox = draw.textbbox((0, 0), line, font=headline_font)
        line_w = line_bbox[2] - line_bbox[0]
        line_x = (WIDTH - line_w) // 2
        line_y = start_y + (i * line_height)
        draw.text((line_x, line_y), line, font=headline_font, fill=(255, 255, 255))

    # 5. Middle CTA Container
    cta_font = get_font(26, bold=True)
    cta_text = "Designed for Speed & High Conversion  •  blackman.in"
    cta_bbox = draw.textbbox((0, 0), cta_text, font=cta_font)
    cta_w = cta_bbox[2] - cta_bbox[0]
    cta_h = cta_bbox[3] - cta_bbox[1]
    
    cta_x = (WIDTH - cta_w) // 2
    cta_y = 740
    cta_pill = [cta_x - 32, cta_y - 14, cta_x + cta_w + 32, cta_y + cta_h + 14]
    draw.rounded_rectangle(cta_pill, radius=24, fill=(17, 24, 39), outline=(139, 92, 246), width=2)
    draw.text((cta_x, cta_y - 2), cta_text, font=cta_font, fill=(224, 231, 255))

    # 6. Bottom Divider & Footer Watermark
    divider_y = 910
    draw.line([(120, divider_y), (WIDTH - 120, divider_y)], fill=(30, 41, 59), width=2)
    
    footer_font = get_font(24, bold=False)
    footer_text = "blackman.in  |  Web Design & High-Performance Engineering"
    footer_bbox = draw.textbbox((0, 0), footer_text, font=footer_font)
    footer_w = footer_bbox[2] - footer_bbox[0]
    footer_x = (WIDTH - footer_w) // 2
    draw.text((footer_x, 950), footer_text, font=footer_font, fill=(148, 163, 184))

    # 7. Save image
    img.save(output_path, "JPEG", quality=95, optimize=True)
    print(f"[ImageEngine] Rendered branded graphic saved to: {output_path}")
    return output_path

if __name__ == "__main__":
    test_headline = "A 1-Second Page Delay Can Cost You 7% In Conversions."
    render_post_image(test_headline, badge="SPEED & PERFORMANCE", output_path="output/test_post.jpg")
